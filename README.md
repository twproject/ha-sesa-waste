# SESA Raccolta Rifiuti per Home Assistant

Integrazione custom per Home Assistant che importa automaticamente il calendario raccolta rifiuti da `www.sesaeste.it` direttamente nel calendario di Home Assistant.

---

## Funzioni

- Configurazione da UI Home Assistant
- Caricamento live di comuni e vie dal sito SESA
- Calendario Home Assistant nativo
- Sensore **Raccolta oggi**
- Sensore **Raccolta domani**
- Download calendario annuale completo, incluso il pregresso
- Nessun polling continuo verso SESA
- Refresh manuale calendario
- Options Flow per modificare Comune/Via senza reinstallare l'integrazione
- Compatibile con HACS come Custom Repository
- Compatibilità opzionale con HA Separate Garbage Collection Card
- Supporto eventi multimateriale
- Colori custom per materiale raccolta

---

# Installazione

## Tramite HACS (consigliato)

[![Open your Home Assistant instance and add this repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=twproject&repository=ha-sesa-waste&category=integration)

1. Apri **HACS → Integrazioni**
2. Clicca **⋮ → Repository personalizzati**
3. Aggiungi:

```text
https://github.com/twproject/ha-sesa-waste
```

4. Categoria:

```text
Integration
```

5. Clicca **Aggiungi**
6. Cerca:

```text
SESA Raccolta Rifiuti
```

7. Installa l'integrazione
8. Riavvia Home Assistant

---

## Manuale

1. Copia:

```text
custom_components/sesa_waste
```

in:

```text
/config/custom_components/
```

2. Riavvia Home Assistant

---

# Configurazione

[![Open your Home Assistant instance and show the add integration dialog.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=sesa_waste)

1. In Home Assistant vai su:

```text
Impostazioni → Dispositivi e Servizi → Aggiungi integrazione
```

2. Cerca:

```text
SESA Raccolta Rifiuti
```

3. Seleziona:
   - Comune
   - Via

4. Opzionalmente abilita:

```text
HA Separate Garbage Collection Card
```

5. Il calendario verrà importato automaticamente.

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
Umido, Plastica Lattine
Nessuna raccolta
```

---

### Raccolta domani

Mostra il tipo di raccolta previsto per domani.

---

## Calendario

L'integrazione crea un calendario Home Assistant nativo:

```text
calendar.*_calendario_rifiuti
```

Il calendario è compatibile con:

- Vista calendario Home Assistant
- Trigger calendario
- Dashboard
- Reminder
- Automazioni

---

# HA Separate Garbage Collection Card

L'integrazione supporta opzionalmente la card:

```text
HA Separate Garbage Collection Card
```

Repository ufficiale:

```text
https://github.com/RedFoxy/HA-Separate-Garbage-Collection
```

Quando abilitata:

- gli eventi calendario vengono separati per materiale
- ogni materiale può avere un colore HEX personalizzato
- la descrizione evento contiene automaticamente:

```text
color: #HEX
```

compatibile con la card RedFoxy.

---

# Eventi multimateriale

Il calendario Home Assistant espone sempre eventi separati per materiale.

Esempio:

```text
28/05 → Umido
28/05 → Plastica Lattine
```

I sensori invece continuano a mostrare i materiali aggregati:

```text
Umido, Plastica Lattine
```

Questo migliora:

- compatibilità dashboard
- trigger calendario
- automazioni
- supporto RedFoxy

---

# Refresh manuale calendario

L'integrazione **NON INTERROGA** continuamente SESA.

Il calendario viene scaricato solo:

- all'avvio di Home Assistant
- al reload dell'integrazione
- quando richiesto manualmente

## Service manuale

Da:

```text
Developer Tools → Services
```

eseguire:

```yaml
service: sesa_waste.aggiorna_calendario
```

Questo forza:

- nuova sessione PHP
- nuova registrazione UUID
- nuovo download calendario annuale

---

# Modifica Comune/Via

Dopo l'installazione puoi modificare Comune e Via dalle opzioni dell'integrazione:

```text
Impostazioni → Dispositivi e Servizi → SESA Raccolta Rifiuti → Configura
```

L'integrazione ricarica automaticamente il calendario dopo la modifica.

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

- registrazione UUID
- gestione sessione PHP
- endpoint AJAX
- parsing HTML
- download calendario JSON

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

- Home Assistant 2026.5+
- Home Assistant OS
- HACS
- HA Separate Garbage Collection Card

---

# Disclaimer

Questo progetto non è affiliato ufficialmente a SESA.

Tutti i dati provengono da:

```text
https://www.sesaeste.it
```

---

# Licenza

MIT License

