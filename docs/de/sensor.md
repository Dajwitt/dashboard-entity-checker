# Result-Sensor

Die Integration erstellt eine Sensor-Entity. Der Standardname ist `sensor.dashboard_entity_checker`; Home Assistant kann die Entity-ID bei Namenskonflikten oder nach manueller Umbenennung abweichend vergeben.

## Zustand

| Wert | Bedeutung |
|---|---|
| `0` | keine aktuell fehlenden, nicht ignorierten Entity-IDs |
| positive Ganzzahl | Anzahl eindeutiger aktiver Funde |

Der numerische Zustand bleibt auch bei einem partiellen Dashboard-Fehler das Ergebnis der erfolgreich geladenen Dashboards. Deshalb müssen für eine vollständige Bewertung zusätzlich `status`, `dashboard_loaded` und `dashboard_errors` geprüft werden.

## Attribute

| Attribut | Typ | Bedeutung |
|---|---|---|
| `dashboard` | String | erstes konfiguriertes Dashboard, Kompatibilitätsfeld |
| `dashboards` | Liste | alle konfigurierten Dashboard-URL-Pfade |
| `dashboards_loaded` | Liste | im letzten Lauf erfolgreich geladene Dashboards |
| `dashboard_errors` | Liste | nicht geladene Dashboards mit Fehlermeldung |
| `scan_interval_minutes` | Zahl | konfiguriertes Scan-Intervall |
| `dashboard_loaded` | Boolean | `true`, wenn alle Dashboards geladen wurden |
| `status` | String | zusammengefasster Laufstatus |
| `missing_entities` | Liste | aktive fehlende IDs mit Standorten |
| `ignored_entities` | Liste | konfigurierte exakte Ignore-IDs |
| `ignored_matches` | Liste | tatsächlich gefundene, aber ignorierte IDs |
| `checked_entities` | Zahl | eindeutige Referenzen vor Existenzprüfung |
| `templates_resolved` | Zahl | insgesamt aufgelöste Decluttering-Templates |
| `template_diagnostics` | Liste | nicht fatale Auflösungsprobleme |
| `views` | Objekt | geladene View-Titel je Dashboard |
| `views_scanned` | Zahl | Summe der gescannten Views |
| `last_scan` | String | ISO-Zeitpunkt des letzten abgeschlossenen Scans |
| `last_error` | String oder `null` | letzter Dashboard- oder Coordinator-Fehler |

## Beispiel für einen Fund

```json
[
  {
    "entity": "sensor.example_retired_temperature",
    "locations": [
      {"dashboard": "example-main", "views": ["Overview", "Climate"]},
      {"dashboard": "example-tablet", "views": ["Details"]}
    ]
  }
]
```

## Statuswerte

| Status | Bedeutung |
|---|---|
| `OK` | vollständiger Scan ohne aktive Funde |
| `Fehler gefunden` | vollständiger Scan mit aktiven Funden |
| `Teilweise fehlgeschlagen` | mindestens ein Dashboard nicht ladbar, mindestens eines erfolgreich |
| `Fehler` | der letzte Coordinator-Lauf ist vollständig fehlgeschlagen |
| `Warte auf ersten Scan` | Integration geladen, erster Scan noch nicht abgeschlossen |

Die Statuswerte stammen derzeit aus der Integration und sind deutsch, unabhängig von der gewählten Oberflächensprache.
