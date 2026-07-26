# Dashboard Entity Checker

**Dokumentation für Preview-Version 0.3.6b2** · Home-Assistant-Custom-Integration

Dashboard Entity Checker prüft ausgewählte Lovelace-Dashboards auf Entity-Referenzen, die weder in Home Assistants State-Machine noch in der Entity Registry vorhanden sind.

Die Integration liest Dashboard-Konfigurationen über Home Assistants Python-Schnittstellen. Sie liest oder verändert keine `.storage`-Dateien, führt kein JavaScript aus und repariert keine Karten oder Entity-IDs.

## Warum diese Integration?

In komplexen Custom-Dashboards können fehlende Referenzen in verschachtelten Karten, Decluttering-Card-Templates oder Button-Card-JavaScript verborgen sein. Dashboard Entity Checker löst die ausdrücklich unterstützten Strukturen auf und ergänzt damit allgemeine Wartungswerkzeuge wie [Spook](https://spook.boo/). Er ersetzt deren weitergehende Home-Assistant-Prüfungen nicht und ist nicht mit Spook verbunden.

## Wichtigste Funktionen

- ein oder mehrere ausgewählte Dashboards prüfen
- direkte Entity-IDs, unterstützte Button-Card-JavaScript-Referenzen und verschachtelte Decluttering-Templates erfassen
- vollständige Standorte nach Dashboard und Ansicht melden
- bewusst fehlende Entity-IDs transparent ausschließen
- einen Result-Sensor, eine optionale persistente Benachrichtigung und ein Änderungs-Event bereitstellen
- Teilausfälle einzelner Dashboards sichtbar machen, ohne gültige Ergebnisse anderer Dashboards zu verlieren
- redigierte Diagnostik für Fehlerberichte bereitstellen

## Schnellstart

1. [Integration installieren](./installation.md).
2. [Dashboards und Scan-Optionen konfigurieren](./configuration.md).
3. `sensor.dashboard_entity_checker` unter [Result-Sensor](./sensor.md) prüfen.
4. Bei Bedarf `dashboard_entity_checker.scan_now` ausführen.

Die folgenden Themen decken Einrichtung, Funktionsumfang und Fehleranalyse ab. Für einen neuen Einsatz mit Installation, Konfiguration und Funktionsweise beginnen.

## Dokumentation

## Sicherheit und Datenschutz

Die Verarbeitung erfolgt lokal in Home Assistant. Vor dem Veröffentlichen von Diagnostik müssen private Dashboard-Namen, URLs und andere sensible Angaben trotzdem geprüft werden. Zugangsdaten gehören niemals in Issues oder Forenbeiträge.
