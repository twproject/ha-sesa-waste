# SESA Raccolta Rifiuti per Home Assistant

Integrazione custom per Home Assistant che importa automaticamente il calendario raccolta rifiuti da `app.sesaeste.it` direttamente nel calendario di Home Assistant.

[![Open your Home Assistant instance and add this repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=twproject&repository=ha-sesa-waste&category=integration)
[![Open your Home Assistant instance and show the add integration dialog.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=sesa_waste)

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
- Compatibilità opzionale con [HA Separate Garbage Collection Card](https://github.com/RedFoxy/HA-Separate-Garbage-Collection)
- Compatibile con HACS come Custom Repository

---

# Installazione

## Tramite HACS (consigliato)

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

3. In Home Assistant vai su:

```text
Impostazioni → Dispositivi e Servizi → Aggiungi integrazione
```

4. Cerca:

```text
SESA Raccolta Rifiuti
```

5. Seleziona Comune, Via ed eventualmente **HA Separate Garbage Collection Card**

6. Il calendario verrà importato automaticamente.

---

# Entità create

## Sensori

### Raccolta oggi

Mostra il tipo di raccolta previsto per oggi.

### Raccolta domani

Mostra il tipo di raccolta previsto per domani.

## Calendario

L'integrazione crea un calendario Home Assistant nativo:

```text
calendar.*_calendario_rifiuti
```

Compatibile con vista calendario, dashboard, trigger calendario, reminder e automazioni.

---

# Eventi multimateriale

Il calendario espone sempre eventi atomici, uno per materiale:

```text
Umido
Plastica Lattine
```

I sensori `Raccolta oggi` e `Raccolta domani` continuano invece a mostrare i materiali aggregati separati da virgola:

```text
Umido, Plastica Lattine
```

Se la compatibilità con **HA Separate Garbage Collection Card** è attiva, ogni evento atomico riceve il proprio colore nella descrizione:

```text
color: #FFD600
```

# HA Separate Garbage Collection Card

L'integrazione può generare eventi compatibili con la card:

```text
HA Separate Garbage Collection Card
```

Repository della card:

```text
https://github.com/RedFoxy/HA-Separate-Garbage-Collection
```

Durante la prima configurazione puoi abilitare l'opzione:

```text
HA Separate Garbage Collection Card
```

Quando l'opzione è attiva, l'integrazione:

1. scarica il calendario annuale
2. identifica i materiali univoci presenti
3. mostra una schermata con un colore HEX per ciascun materiale
4. salva i colori nella configurazione
5. scrive nella descrizione degli eventi il metadato richiesto dalla card

Esempio descrizione evento:

```text
color: #00A651
```

Esempio configurazione colori:

```text
Umido              #8B5A2B
Secco              #9E9E9E
Vetro              #00A651
Verde              #4CAF50
Plastica Lattine   #FFD600
Carta              #2196F3
```

Per modificare questa opzione o cambiare i colori, rimuovere e ricreare l'integrazione.

---

# Refresh manuale calendario

L'integrazione non interroga continuamente SESA.

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

---

# Modifica Comune/Via

Dopo l'installazione puoi modificare Comune e Via dalle opzioni dell'integrazione:

```text
Impostazioni → Dispositivi e Servizi → SESA Raccolta Rifiuti → Configura
```

L'integrazione ricarica automaticamente il calendario dopo la modifica.

Nota: la compatibilità con **HA Separate Garbage Collection Card** e i colori custom vengono scelti durante la prima configurazione. Per modificarli, rimuovi e ricrea l'integrazione.

---

# Logging debug

```yaml
logger:
  default: info
  logs:
    custom_components.sesa_waste: debug
```

---

# Architettura tecnica

Il backend SESA non espone API pubbliche documentate.

L'integrazione replica il comportamento dell'app ufficiale Android tramite registrazione UUID, gestione sessione PHP, endpoint AJAX, parsing HTML e download calendario JSON.

---

# Compatibilità

Testato su:

- Home Assistant 2026.5+
- Home Assistant OS
- HACS

---

# Disclaimer

Questo progetto non è affiliato ufficialmente a SESA.

Tutti i dati provengono da:

```text
https://app.sesaeste.it
```

---

# Licenza

MIT License
