# Events

## `dashboard_entity_checker_result_changed`

Nach einem vollständigen Baseline-Scan sendet die Integration dieses Event, wenn sich das vollständige aktive Ergebnis ändert.

## Wann wird es gesendet?

| Situation | Event |
|---|---|
| aktives Ergebnis ändert sich nach Baseline | ja |
| Ergebnis bleibt identisch | nein |
| erster vollständiger Scan erstellt Baseline | nein |
| mindestens ein Dashboard konnte nicht geladen werden | nein |
| nur `ignored_matches` ändern sich, aktive Liste bleibt gleich | nein |

Ein Standortwechsel zählt als Ergebnisänderung, weil `missing_entities` einschließlich der Standorte verglichen wird. `added_entities` und `removed_entities` können dabei trotzdem leer sein.

## Event-Daten

| Feld | Typ | Bedeutung |
|---|---|---|
| `dashboards` | Liste | konfigurierte Dashboard-URL-Pfade |
| `previous_count` | Zahl | vorherige Anzahl aktiver IDs |
| `current_count` | Zahl | aktuelle Anzahl aktiver IDs |
| `added_entities` | Liste | neu fehlende IDs, sortiert |
| `removed_entities` | Liste | nicht mehr fehlende IDs, sortiert |
| `missing_entities` | Liste | vollständiges aktuelles Ergebnis mit Standorten |
| `scan_time` | String | ISO-Zeitpunkt des Scans |

## Automations-Beispiel

```yaml
automation:
  - alias: "Beispiel: Dashboard-Funde geändert"
    triggers:
      - trigger: event
        event_type: dashboard_entity_checker_result_changed
    conditions:
      - condition: template
        value_template: "{{ trigger.event.data.added_entities | count > 0 }}"
    actions:
      - action: persistent_notification.create
        data:
          title: "Neue Dashboard-Referenzen"
          message: >
            {{ trigger.event.data.added_entities | join(', ') }}
```

Das Beispiel nutzt absichtlich keine gerätespezifische Notify-Action. Für produktive Automationen sollte außerdem berücksichtigt werden, dass ein reiner Standortwechsel ein Event ohne hinzugefügte oder entfernte IDs auslösen kann. Nach einem partiellen Scan wird der nächste vollständige Scan als neue Vergleichsbasis behandelt und sendet ebenfalls noch kein Event.
