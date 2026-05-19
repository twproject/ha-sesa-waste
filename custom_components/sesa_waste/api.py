from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import re
import uuid as uuidlib

from bs4 import BeautifulSoup

import requests


@dataclass(slots=True)
class WasteEvent:
    date: date
    types: list[str]


class SesaApiError(Exception):
    """Raised when SESA API calls fail."""


class SesaClient:
    """Minimal client for app.sesaeste.it.

    Flow discovered from the Cordova app:
    1. Register UUID via /controller/controllerRegistration.php
    2. Save settings via /controller/controllerUserSettings.php
    3. Fetch calendar via /controller/controllerCalendario.php
    """

    def __init__(
        self,
        base_url: str,
        comune_id: int,
        via_id: int,
        notifiche: bool = False,
        session_id: str | None = None,
        device_uuid: str | None = None,
        timeout: int = 20,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.comune_id = int(comune_id)
        self.via_id = int(via_id)
        self.notifiche = bool(notifiche)
        self.timeout = timeout
        self.device_uuid = device_uuid or str(uuidlib.uuid4())
        self.session = requests.Session()
        if session_id:
            self.session.cookies.set("PHPSESSID", session_id, domain="app.sesaeste.it", path="/")

    @property
    def session_id(self) -> str | None:
        return self.session.cookies.get("PHPSESSID")

    def register(self) -> None:
        url = f"{self.base_url}/controller/controllerRegistration.php"
        payload = {
            "action": "registration",
            "token": "home-assistant",
            "uuid": self.device_uuid,
            "ip": "",
            "platform": "Android",
            "model": "HomeAssistant",
            "lastLogin": str(int(datetime.now().timestamp())),
        }
        response = self.session.post(url, data=payload, timeout=self.timeout)
        response.raise_for_status()
        if response.text.strip() not in {"200", "201", "400"}:
            raise SesaApiError(f"Unexpected registration response: {response.text[:200]}")

    def save_settings(self) -> None:
        url = f"{self.base_url}/controller/controllerUserSettings.php"
        payload = {
            "action": "saveSettings",
            "orario": "-1",
            "comune": str(self.comune_id),
            "via": str(self.via_id),
            "notifiche": "1" if self.notifiche else "0",
        }
        response = self.session.post(url, data=payload, timeout=self.timeout)
        response.raise_for_status()
        if response.text.strip() != "200":
            raise SesaApiError(f"Unexpected saveSettings response: {response.text[:200]}")

    def ensure_configured(self) -> None:
        self.register()
        self.save_settings()

    def get_calendar(self, start: date | None = None, end: date | None = None) -> list[WasteEvent]:
        if start is None:
            start = date.today()
        if end is None:
            end = date(start.year, 12, 31)

        url = f"{self.base_url}/controller/controllerCalendario.php"
        payload = {
            "action": "calendario",
            "today": start.isoformat(),
            "lastday": end.isoformat(),
        }
        response = self.session.post(url, data=payload, timeout=self.timeout)
        response.raise_for_status()

        try:
            raw = response.json()
        except ValueError as exc:
            raise SesaApiError(f"Calendar did not return JSON: {response.text[:300]}") from exc

        events: list[WasteEvent] = []
        for item in raw:
            day = datetime.strptime(item["Giorno"], "%Y-%m-%d").date()
            types = self._parse_waste_types(item.get("Stile", ""))
            if types:
                events.append(WasteEvent(day, types))

        return events

    @staticmethod
    def _parse_waste_types(html: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        values = []
        for tag in soup.select(".rifiuto p"):
            text = " ".join(tag.get_text(" ", strip=True).split())
            if text:
                values.append(text)
        if values:
            return values

        # Fallback if HTML parsing fails.
        return [x.strip() for x in re.findall(r"<p>(.*?)</p>", html, re.I) if x.strip()]
