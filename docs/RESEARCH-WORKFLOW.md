# Quellenbasiertes historisch-soziologisches Sachbuch

## Forschungsprotokoll vor Recherchebeginn

1. Leitfrage und untersuchte Gegenhypothesen notieren. Keine Bestätigung als Auftragsziel.
2. Raum und Zeit als vorläufige Eingrenzung markieren und begründen.
3. Rechtsstand, soziale Klasse, Elite, Besitz, Herrschaft, religiöse Autorität und
   soziale Mobilität definieren. Begriffe nicht unbemerkt zwischen Epochen wechseln.
4. Direkte personelle/institutionelle Kontinuität, funktionale Ähnlichkeit und neu entstandene
   Ungleichheit getrennt untersuchen. Für jede Erklärung widerlegende Befunde festlegen.
5. Vergleichskriterien: Rechtsprivilegien, Zugang zu Ämtern, Besitz-/Erbregeln,
   Bildungszugang, Netzwerke, politische Partizipation und Rechtfertigung von Hierarchie.
6. Wertmaßstäbe und gewünschte Veränderungen getrennt von empirischen Ergebnissen ausweisen.

## Recherche und Quellenkritik

Suchprotokoll mit Suchbegriffen, Datum, Datenbank, Filtern und Ausschlussgründen führen.
Zuerst Forschungsliteratur kartieren, dann gezielt Primärquellen prüfen. Katalogtreffer,
Abstracts und Suchausschnitte sind keine gelesenen Volltexte. Nicht erreichbare Literatur
als nicht geprüft kennzeichnen; keine bibliografischen Angaben aus Modellgedächtnis übernehmen.
Offen zugängliche Archive, Bibliothekskataloge, Fachrepositorien und amtliche Daten als
Suchorte verwenden. Ihre Eignung muss je Forschungsfrage geprüft werden.

Für jede Quelle: Autor, Titel, Ausgabe/Jahr, URL/DOI/Archivsignatur, Zugriffstag,
Quellentyp, Entstehungskontext, Perspektive/Interesse und genaue Fundstelle festhalten.
Originalpassage mit Kontext archivieren, Übersetzungen kennzeichnen. Widersprechende
Befunde und Forschungskontroversen ebenso erfassen wie unterstützende Ergebnisse.

Belegbündel-JSON hat Arrays `sources`, `passages`, `claims`, `evidence` (siehe Modul
research.py). Behauptungen sind `fact`, `interpretation`, `hypothesis` oder `normative`.
Belegrelationen sind `supports`, `contradicts`, `qualifies`. Ein Import setzt keine
Behauptung auf verified. `verify --original-checked` ist eine bewusste Bestätigung nach
Originalprüfung; kein automatisches Modellurteil.

## Historischer Vergleich und Gegenwartsdaten

Vergleichseinheiten, Zeiträume und Definitionen vor Auswertung bestimmen. Nominale und reale
Geldwerte, Personen und Haushalte, Bestände und Einkommen, Brutto und Netto sowie
Messänderungen getrennt behandeln. Datensatzversion, Berechnung und fehlende Werte
protokollieren. Aus Analogie folgt keine Kausalität. Erklärungen benötigen Mechanismen,
Zeitfolge, alternative Ursachen und Gegenfälle. Maßnahmen nach gemessener Wirkung,
Übertragbarkeit, Nebenwirkungen und Unsicherheit bewerten.

## Schreiben und Prüfung

Kapitel erst aus überprüften Belegpaketen erstellen. Prüfbare Aussagen mit [claim:ID]
verknüpfen. Fehlende Belege bleiben offene Aufgaben. Vor jedem Kapitel Gegenargumente und
Definitionskonflikte bearbeiten. Für die Endprüfung sind Kapitelprüfung und separate
Gesamtprüfung der Argumentation erforderlich. Der mechanische Audit findet unbekannte und
ungeprüfte Marker; er erkennt NICHT zuverlässig unmarkierte Tatsachen oder Fehlinterpretationen.
Ein grüner Audit ist kein wissenschaftliches Gütesiegel.

## Kosten und Betrieb

Keine kostenpflichtigen APIs oder Server vorgesehen. Lokaler Ollama-Adapter nutzt ausschließlich
127.0.0.1, umgeht Proxys und lädt keine Modelle herunter. Vor Verwendung muss ein installiertes
lokales Modell gewählt werden. Kein Cloud-Fallback. Strom-/Geräteverbrauch bleibt bestehen.
Der bisherige Schreibtest belegt keine Eignung für wissenschaftliche Quellenarbeit.

Prüfen: wörtliche Fundstellen korrekt extrahieren, unzureichende Belege zurückweisen,
Gegenbelege bewahren, Interpretation kennzeichnen, mehrere Abschnitte konsistent vergleichen.
Erst nach dokumentiertem Bestehen automatisches Schreiben aktivieren.

## Aktuelle technische Grenzen

Vorbereitet: persistente Buchjobs, lokaler Textadapter, Quellen-/Passagen-/Behauptungsregister,
Gegenbelege, Belegpakete und mechanischer Audit. Noch NICHT vorhanden: automatische
wissenschaftliche Literatursuche, PDF/OCR-Import, verlässliche semantische Belegprüfung,
Kontextauswahl für ein ganzes Buch, kostenlose lokale Gesamtprüfung, Rückkopplung aus
Review in gezielte Überarbeitung, Word-/EPUB-Satz und unattended Scheduler.
`lionelos-book run` ist deshalb noch kein betriebsfertiger Komplettlauf für ein Forschungsbuch.
Nicht durch automatische Zustimmung oder stilles Abschneiden von Kontext umgehen.

Der private Forschungsordner liegt außerhalb des öffentlichen Code-Repositories.
Nur ein Prozess pro Projekt. Sicherungen des Projektordners einschließlich SQLite nach
Schließen der Datenbank anlegen. Kein Fernzugriff und kein Hintergrunddienst wird eingerichtet.
