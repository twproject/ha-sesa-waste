from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import html
import logging
import re
import uuid as uuidlib

from bs4 import BeautifulSoup
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class WasteEvent:
    date: date
    types: list[str]


class SesaApiError(Exception):
    """Raised when SESA API calls fail."""


class SesaClient:
    def __init__(
        self,
        base_url: str,
        comune_id: str | int | None = None,
        via_id: str | int | None = None,
        notifiche: bool = False,
        device_uuid: str | None = None,
        timeout: int = 20,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.comune_id = str(comune_id) if comune_id is not None else None
        self.via_id = str(via_id) if via_id is not None else None
        self.notifiche = bool(notifiche)
        self.timeout = timeout
        self.device_uuid = device_uuid or str(uuidlib.uuid4())
        self.session = requests.Session()
        self.session.verify = False

    @property
    def session_id(self) -> str | None:
        return self.session.cookies.get("PHPSESSID")

    def _post(self, path: str, data: dict[str, str]) -> requests.Response:
        response = self.session.post(
            f"{self.base_url}{path}",
            data=data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response

    def _get(self, path: str) -> requests.Response:
        response = self.session.get(
            f"{self.base_url}{path}",
            timeout=self.timeout,
            allow_redirects=True,
        )
        response.raise_for_status()
        return response

    def register(self) -> None:
        payload = {
            "action": "registration",
            "token": f"home-assistant-{self.device_uuid}",
            "uuid": self.device_uuid,
            "ip": "",
            "platform": "Android",
            "model": "HomeAssistant",
            "lastLogin": str(int(datetime.now().timestamp())),
        }
        response = self._post("/controller/controllerRegistration.php", payload)
        body = response.text.strip()

        _LOGGER.debug(
            "Registrazione SESA response=%s uuid=%s cookies=%s",
            body,
            self.device_uuid,
            self.session.cookies.get_dict(),
        )

        if body not in {"200", "201", "304", "400"}:
            raise SesaApiError(f"Risposta registrazione inattesa: {response.text[:200]}")

    def initialize_address_flow(self) -> None:
        """Bind PHP session to the current UUID before saving settings."""
        for path in (
            f"/?p=set-indirizzo&showheader=false&uuid={self.device_uuid}",
            f"/?p=new-indirizzo&uuid={self.device_uuid}",
        ):
            response = self._get(path)
            _LOGGER.debug(
                "Inizializzazione SESA path=%s status=%s bytes=%s cookies=%s",
                path,
                response.status_code,
                len(response.text or ""),
                self.session.cookies.get_dict(),
            )

    def open_home(self) -> None:
        response = self._get(f"/?p=home&uuid={self.device_uuid}")
        _LOGGER.debug(
            "Home SESA status=%s bytes=%s cookies=%s",
            response.status_code,
            len(response.text or ""),
            self.session.cookies.get_dict(),
        )

    def list_municipalities(self) -> dict[str, str]:
        """Fetch municipalities live from the web app."""
        self.register()
        self.initialize_address_flow()

        response = self._get(f"/?p=new-indirizzo&uuid={self.device_uuid}")
        soup = BeautifulSoup(response.text, "html.parser")

        results: dict[str, str] = {}
        for option in soup.select("select#comuni option"):
            value = option.get("value")
            if not value:
                continue
            text = html.unescape(option.get_text(" ", strip=True))
            if text and text.lower() != "comune":
                results[str(value)] = text

        _LOGGER.debug("Comuni SESA caricati: %s", len(results))
        return results

    def list_addresses(self) -> dict[str, str]:
        if not self.comune_id:
            raise SesaApiError("comune_id richiesto per leggere le vie")

        response = self._post(
            "/controller/controllerIndirizzi.php",
            {"action": "asyncAddress", "comune": self.comune_id},
        )
        soup = BeautifulSoup(response.text, "html.parser")

        results: dict[str, str] = {}
        for option in soup.find_all("option"):
            value = option.get("value")
            if not value:
                continue
            text = html.unescape(option.get_text(" ", strip=True))
            if text and text.lower() != "indirizzo":
                results[str(value)] = text

        _LOGGER.debug("Vie SESA caricate per comune=%s: %s", self.comune_id, len(results))
        return results

    def save_settings(self) -> None:
        if not self.comune_id or not self.via_id:
            raise SesaApiError("comune_id e via_id richiesti per salvare le impostazioni")

        payload = {
            "action": "saveSettings",
            "orario": "-1",
            "comune": self.comune_id,
            "via": self.via_id,
            "notifiche": "1" if self.notifiche else "0",
        }
        response = self._post("/controller/controllerUserSettings.php", payload)
        body = response.text.strip()

        _LOGGER.debug(
            "Salvataggio impostazioni SESA payload=%s response=%s cookies=%s",
            payload,
            body,
            self.session.cookies.get_dict(),
        )

        if body != "200":
            raise SesaApiError(f"Risposta saveSettings inattesa: {response.text[:200]}")

    def ensure_configured(self) -> None:
        # This order is required by SESA:
        # register -> set/new-indirizzo -> saveSettings -> home -> calendar.
        self.register()
        self.initialize_address_flow()
        self.save_settings()
        self.open_home()

    def get_calendar(self, start: date, end: date) -> list[WasteEvent]:
        payload = {
            "action": "calendario",
            "today": start.isoformat(),
            "lastday": end.isoformat(),
        }
        response = self._post("/controller/controllerCalendario.php", payload)

        _LOGGER.debug(
            "Calendario SESA payload=%s response_preview=%s cookies=%s",
            payload,
            response.text[:1200],
            self.session.cookies.get_dict(),
        )

        try:
            raw = response.json()
        except ValueError as exc:
            raise SesaApiError(f"Il calendario non ha restituito JSON: {response.text[:300]}") from exc

        events: list[WasteEvent] = []
        seen: set[tuple[date, tuple[str, ...]]] = set()

        for item in raw:
            giorno = item.get("Giorno")
            stile = item.get("Stile", "")
            if not giorno:
                continue

            day = datetime.strptime(giorno, "%Y-%m-%d").date()
            types = self._parse_waste_types(stile)
            if not types:
                continue

            key = (day, tuple(types))
            if key not in seen:
                events.append(WasteEvent(day, types))
                seen.add(key)

        events.sort(key=lambda event: event.date)
        return events

    @staticmethod
    def _parse_waste_types(html_fragment: str) -> list[str]:
        soup = BeautifulSoup(html_fragment, "html.parser")
        values: list[str] = []

        for tag in soup.select(".raccolta .rifiuto > p"):
            text = " ".join(tag.get_text(" ", strip=True).split())
            if text:
                values.append(text)

        if values:
            return values

        return [
            " ".join(x.strip().split())
            for x in re.findall(r"<p>(.*?)</p>", html_fragment, re.I | re.S)
            if x.strip()
        ]
