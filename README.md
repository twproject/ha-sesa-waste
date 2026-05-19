# SESA Raccolta Rifiuti per Home Assistant

Integrazione custom per Home Assistant che importa automaticamente il calendario raccolta rifiuti da `app.sesaeste.it` direttamente nel calendario di Home Assistant.

Supporta configurazione completamente da interfaccia grafica, caricamento live di comuni e vie, sensori dedicati e calendario annuale completo.

---

# Funzioni

✅ Configurazione da UI Home Assistant
✅ Caricamento live di comuni e vie dal sito SESA
✅ Calendario Home Assistant nativo
✅ Sensore "Raccolta oggi"
✅ Sensore "Raccolta domani"
✅ Download calendario annuale completo
✅ Nessun polling continuo verso SESA
✅ Refresh manuale calendario
✅ Options Flow per modificare comune/via senza reinstallare l'integrazione
✅ Compatibile con HACS (Custom Repository)

---

# Screenshot

## Dashboard

* Sensore raccolta oggi
* Sensore raccolta domani
* Calendario rifiuti

## Calendario Home Assistant

Visualizzazione completa del calendario raccolta rifiuti direttamente nella vista calendario di Home Assistant.

---

# Installazione tramite HACS

[![Open your Home Assistant instance and add this repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=twproject&repository=ha-sesa-waste&category=integration)

## 1. Aggiungere la repository custom

In HACS:

```text
HACS → Integrations → ⋮ → Custom repositories
```

Aggiungere:

```text
https://github.com/twproject/ha-sesa-waste
```

Categoria:

```text
Integration
```

---

## 2. Installare l'integrazione

Cercare:

```text
SESA Raccolta Rifiuti
```

Installare e riavviare Home Assistant.

---

# Installazione manuale

Copiare:

```text
custom_components/sesa_waste
```

in:

```text
/config/custom_components/
```

Riavviare Home Assistant.

---

# Configurazione

Dopo il riavvio:

```text
Impostazioni → Dispositivi e Servizi → Aggiungi integrazione
```

Cercare:

```text
SESA Raccolta Rifiuti
```

L'integrazione:

1. scarica automaticamente l'elenco comuni
2. scarica automaticamente le vie del comune selezionato
3. crea il calendario annuale completo

---

# Entità create

## Sensori

### Raccolta oggi

Mostra il tipo di raccolta previsto per oggi.

Esempi:

```text
Verde
Umido
Secco
Nessuna raccolta
```

---

### Raccolta domani

Mostra il tipo di raccolta previsto per domani.

---

## Calendario

```text
calendar.sesa_calendario_rifiuti
```

Calendario annuale compatibile con:

* Vista calendario Home Assistant
* Trigger calendario
* Dashboard
* Reminder
* Automazioni

---

# Refresh manuale

L'integrazione non interroga continuamente SESA.

Il calendario viene scaricato solo:

* all'avvio di Home Assistant
* al reload dell'integrazione
* quando richiesto manualmente

## Service manuale

Developer Tools → Services:

```yaml
service: sesa_waste.aggiorna_calendario
```

Questo forza:

* nuova sessione PHP
* nuova registrazione UUID
* nuovo download calendario annuale

---

# Logging debug

Per attivare il debug:

```yaml
logger:
  default: info
  logs:
    custom_components.sesa_waste: debug
```

---

# Architettura tecnica

Il backend SESA non espone API pubbliche documentate.

L'integrazione replica il comportamento dell'app ufficiale Android tramite:

* registrazione UUID
* gestione sessione PHP
* endpoint AJAX
* parsing HTML
* download calendario JSON

La sequenza backend richiesta da SESA è:

1. registrazione dispositivo
2. inizializzazione sessione
3. setup indirizzo
4. salvataggio impostazioni
5. apertura homepage
6. download calendario

---

# Compatibilità

Testato su:

* Home Assistant 2026.5+

---

# Disclaimer

Questo progetto non è affiliato ufficialmente a SESA.

Tutti i dati provengono da:

```text
https://app.sesaeste.it
```

---

# Roadmap

Possibili evoluzioni future:

* notifiche automatiche Home Assistant
* icone specifiche per tipo rifiuto
* cache persistente su disco
* traduzioni complete EN/IT
* ricerca inline/filterable per comuni e vie
* pubblicazione HACS ufficiale

---

# Licenza

MIT License
