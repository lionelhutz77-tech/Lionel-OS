# Open LionelOS – Arbeitsregeln

- Dieses Verzeichnis ist die oeffentliche, bereinigte Produktfassung. Keine Dateien aus dem
  internen Lionel-OS-Betrieb ungeprueft kopieren.
- Keine `.env`, Schluessel, Zugangsdaten, Datenbanken, Logs, persoenlichen Pfade oder Laufbelege.
- Provider sind standardmaessig read-only und erhalten nur den explizit begrenzten Aufgabentext.
- Neue Funktionen brauchen deterministische Offline-Tests. Netzwerkaufrufe gehoeren nicht in CI.
- Ein Lauf gilt nur dann als erfolgreich, wenn Evidence geschrieben und das Quality Gate bestanden ist.

