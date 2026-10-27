# Buchprojekte: Einrichtung und Grenzen

Der neue Befehl `lionelos-book` verwaltet Recherche, Gesamtplan, Figuren-/Weltbibel,
Kapitelentwürfe, Kapitelrevisionen, Gesamtprüfung und Markdown-Ausgabe. Projektdateien
werden ausschließlich im ausdrücklich gewählten Projektordner gespeichert. Diesen außerhalb
dieses öffentlichen Repositories anlegen. Kein eingebautes Hintergrundhosting.

## Einstieg

Python >=3.11 und `python -m pip install -e .`.

```text
lionelos-book <privater-projektordner> init --brief <brief.txt> --chapters 30
lionelos-book <privater-projektordner> source S1 https://example.org <quellentext.txt>
lionelos-book <privater-projektordner> next
lionelos-book <privater-projektordner> import research <recherche.md>
lionelos-book <privater-projektordner> run <runner.json>
```

`next` liefert den vollständigen Auftrag als JSON. `import` übernimmt ausschließlich den
nächsten Schritt. Ein vertrauenswürdiger Writer-Adapter erhält Aufträge auf stdin und muss
fertigen Markdown-Text auf stdout zurückgeben. Er muss Recherche und Modellaufrufe selbst
implementieren. Er darf weder ungeprüfte Quellenanweisungen ausführen noch Geheimnisse
in Ausgaben schreiben. `writer_argv` ist ein explizites Array, keine Shell-Zeichenkette.
`run` setzt nach Unterbrechung am nächsten gespeicherten Schritt fort. Nicht parallel auf
demselben Projekt ausführen. Nach einem Timeout kann ein bereits bezahlter Aufruf wiederholt
werden; deshalb zählt jeder Versuch vor dem Aufruf gegen das dauerhafte Aufruflimit.

Runner-Konfiguration: `writer_argv`, `max_calls` (Standard 20), `max_context_chars`
(Standard 200000), `max_output_chars` (Standard 100000), `timeout_seconds` (Standard 300),
`review` (Provider-/Agenten-Konfiguration wie examples/repository-review.json, ohne task).
Nur explizit vertrauenswürdige Programme eintragen. Das Aufruflimit ist kein Euro-Limit.

Quellenimport speichert URL, Text und Prüfsumme, verifiziert aber nicht die Wahrheit des
Textes. Quellen vor dem ersten Schreibschritt importieren. Automatische Websuche,
Quellenabruf und Zitatprüfung sind noch nicht integriert. Der Adapter muss diese liefern.
Keine Quellen oder Fakten erfinden, wenn Recherche nicht verfügbar ist.

Das bestehende Quality Gate schreibt Evidence und blockiert die Ausgabe bei Ablehnung.
Die Ausgabe bindet die Prüfung zusätzlich an den Manuskriptinhalt. Die bisherigen
Provider haben enge Kontextgrenzen (ca. 12000 Zeichen). Große Buchprüfungen benötigen
noch einen gesonderten Provider bzw. eine vollständige Prüfung in mehreren Durchgängen;
der neue Befehl bricht bei Grenzüberschreitungen ab, statt Inhalte still abzuschneiden.
Nach einer abgelehnten Gesamtprüfung ist ein neuer Überarbeitungszyklus bisher manuell
anzulegen. Automatische Rückkopplung und Änderungsabhängigkeiten sind noch offen.

## Für vollständig automatisierten Betrieb noch erforderlich

- Laufzeit: eigener Rechner mit laufendem Prozess oder dauerhaft erreichbarer Worker.
  Der GitHub-Connector gewährt keinen Zugriff auf einen Windows-Rechner.
- Writer-Adapter mit authentifiziertem Modellzugang und ausreichend Kontext/Ausgabelänge.
- Recherchewerkzeug mit Suchzugang, Quellenabruf und dokumentierten Belegen.
- Buchweite Prüfung mit Fakten-/Kontinuitätsregister und Überarbeitungsrückkopplung.
- Privater persistenter Speicher und Sicherung; kein Manuskript ins öffentliche Code-Repo.
- Budgetentscheidung, Provider-seitige Kostenkontrolle und Wiederanlaufstrategie.
- Buchbrief: Genre/Thema, Zielgruppe, Umfang, Perspektive, Stil, Rechercheanforderungen,
  fiktionale Freiheiten, Ausschlüsse und gewünschte Ausgabe.

GitHub-Lesezugriff ist bestätigt. Schreibzugriff wird durch das Publizieren dieses
Entwicklungszweigs geprüft. Zugangsdaten nur im Secret Store bzw. als lokale
Umgebungsvariablen hinterlegen, niemals in Chat, Konfigurationsdatei oder Repository.
Ein Literatur-Skill ersetzt weder diese Laufzeit noch Modell-/Recherchezugänge.
DOCX/EPUB/PDF-Satz sind noch nicht integriert; derzeit wird Markdown ausgegeben.

## Validierung

Deterministische Offline-Tests prüfen Wiederaufnahme, Reihenfolge, Kontextgrenze,
Ausgabesperre vor Prüfung sowie Änderungserkennung nach Freigabe. Sie belegen weder
literarische Qualität noch einen erfolgreichen Live-Modell- oder Rechercheaufruf.
