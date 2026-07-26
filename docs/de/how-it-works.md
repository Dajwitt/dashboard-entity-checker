# Funktionsweise

## Ablauf eines Scans

```text
Home Assistant vollständig gestartet
        ↓
ausgewählte Dashboards über Lovelace laden
        ↓
Ansichten und unterstützte Referenzen parsen
        ↓
Decluttering-Templates und statische JavaScript-Referenzen auflösen
        ↓
Referenzen nach Dashboard und Ansicht zusammenführen
        ↓
gegen State-Machine und Entity Registry prüfen
        ↓
exakte Ignore-Liste anwenden
        ↓
Sensor aktualisieren, Benachrichtigung anpassen, ggf. Event senden
```

## Dashboard-Zugriff

Die Integration verwendet Home Assistants Lovelace-Python-Schnittstellen und lädt die aktuelle Konfiguration mit erzwungener Aktualisierung. Sie greift nicht direkt auf `.storage` zu und schreibt nichts in ein Dashboard. Nur die in der Config Entry ausgewählten Dashboards werden geprüft.

## Wann gilt eine Entity als fehlend?

Eine Referenz wird nur gemeldet, wenn sie an beiden Stellen fehlt:

- kein aktueller State in Home Assistants State-Machine
- kein Eintrag in der Entity Registry

Dadurch zählen `unavailable`, deaktivierte oder vorübergehend zustandslose Entities nicht als fehlend, solange der Registry-Eintrag noch vorhanden ist.

## Zuordnung und Deduplizierung

Eine fehlende ID wird einmal ausgegeben. Alle Fundorte bleiben erhalten:

```json
{
  "entity": "sensor.example_retired_temperature",
  "locations": [
    {"dashboard": "example-main", "views": ["Overview", "Climate"]},
    {"dashboard": "example-tablet", "views": ["Details"]}
  ]
}
```

Dashboard-Werte sind URL-Pfade, View-Werte sind die sichtbaren Titel. Mehrere Vorkommen in derselben Ansicht erhöhen den Fundzähler nicht.

## Automatische und manuelle Scans

Der erste Scan beginnt erst, nachdem Home Assistant vollständig gestartet ist. Danach läuft die Prüfung im konfigurierten Intervall. `dashboard_entity_checker.scan_now` fordert einen sofortigen Scan an. Manuelle und zeitgesteuerte Scans werden nacheinander ausgeführt und überlappen sich nicht.

## Teilausfall

Kann mindestens ein ausgewähltes Dashboard nicht geladen werden, bleiben die Ergebnisse der erfolgreich geladenen Dashboards erhalten. Der Sensor meldet `Teilweise fehlgeschlagen` und führt Details unter `dashboard_errors` und `last_error` auf.

Ein unvollständiger Scan verändert keine bestehende Fund-Benachrichtigung und sendet kein Result-Changed-Event. So wird ein früheres vollständiges Ergebnis nicht durch unvollständige Daten ersetzt. Der erste anschließende vollständige Scan wird wieder als Vergleichsbasis verwendet und sendet ebenfalls noch kein Änderungs-Event.

Können alle ausgewählten Dashboards nicht geladen werden, schlägt der Coordinator-Lauf fehl. Der Sensor bleibt verfügbar, zeigt den Fehlerzustand und erhält die letzte erfolgreiche Datenbasis, soweit Home Assistant sie noch hält.
