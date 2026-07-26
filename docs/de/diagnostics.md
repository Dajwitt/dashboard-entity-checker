# Diagnostik

Diagnostik wird unter **Einstellungen → Geräte & Dienste → Dashboard Entity Checker → Dreipunkt-Menü → Diagnostik herunterladen** erzeugt. Sie enthält Konfiguration und das letzte Scanergebnis in einer Form, die für Fehlerberichte geeignet ist.

## Enthaltene Daten

- Integrationsversion
- konfigurierte, geladene und fehlerhafte Dashboards
- Scan-Intervall und Ladezustand
- Ansichten und Anzahl geprüfter Referenzen
- aktive Funde, konfigurierte Ausschlüsse und `ignored_matches`
- aufgelöste Decluttering-Templates und Template-Diagnosen
- Zeitpunkt und Fehlertext des letzten Scans

Ist der Coordinator beim Download nicht verfügbar, erzeugt die Integration einen reduzierten Diagnostiksatz mit Konfigurationswerten, leeren Ergebnislisten und dem Hinweis `Coordinator ist nicht verfügbar.`

## Beispielauszug

```json
{
  "integration_version": "0.3.6b2",
  "dashboards": ["example-main", "example-tablet"],
  "dashboards_loaded": ["example-main"],
  "dashboard_errors": [
    {"dashboard": "example-tablet", "error": "Dashboard could not be loaded"}
  ],
  "entities_checked": 42,
  "missing_entities": [
    {
      "entity": "sensor.example_retired_temperature",
      "locations": [
        {"dashboard": "example-main", "views": ["Climate"]}
      ]
    }
  ],
  "template_diagnostics": []
}
```

## Redaktion

Felder mit den Schlüsseln `access_token`, `token` und `password` werden über Home Assistants Diagnosefunktion geschwärzt. Das ist eine zusätzliche Schutzmaßnahme, ersetzt aber keine manuelle Prüfung.

## Vor dem Hochladen

- Datei vollständig ansehen.
- Private Dashboard-Namen, View-Titel und Entity-IDs bei Bedarf anonymisieren.
- Keine Tokens, Passwörter, privaten URLs oder internen Netzwerkadressen veröffentlichen.
- Im Issue Integrationsversion, Home-Assistant-Version und klare Reproduktionsschritte nennen.
