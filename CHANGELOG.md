# Changelog

## v1.3.2

- Gli eventi calendario vengono sempre splittati per materiale
- Migliorata compatibilità con HA Separate Garbage Collection Card per giorni multimateriale
- I sensori Raccolta oggi/Raccolta domani continuano a mostrare i materiali aggregati con `, `
- Ogni evento atomico riceve il proprio metadato `color: #HEX` quando la compatibilità card è attiva


## v1.3.1

- Aggiunta compatibilità opzionale con HA Separate Garbage Collection Card
- Rilevamento automatico materiali univoci dal calendario annuale
- Configurazione colore HEX per ogni materiale
- Descrizione eventi calendario con metadato `color: #HEX`
- Aggiornato README e metadata HACS

## v1.1.0

- Configurazione da UI
- Options Flow per modificare Comune/Via
- Calendario annuale completo senza polling periodico
- Sensori Raccolta oggi/Raccolta domani
- Service manuale `sesa_waste.aggiorna_calendario`
- Supporto HACS come custom repository
