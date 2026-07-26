# Aktion `scan_now`

## `dashboard_entity_checker.scan_now`

Die Aktion fordert sofort einen Scan aller konfigurierten Dashboards an. Sie besitzt keine Parameter.

## Entwicklerwerkzeuge

Unter **Entwicklerwerkzeuge → Aktionen**:

```yaml
action: dashboard_entity_checker.scan_now
```

## Script-Beispiel

```yaml
script:
  example_dashboard_check:
    alias: "Beispiel: Dashboard-Prüfung"
    sequence:
      - action: dashboard_entity_checker.scan_now
```

## Automations-Beispiel

```yaml
automation:
  - alias: "Beispiel: Dashboard-Prüfung anfordern"
    triggers:
      - trigger: time
        at: "03:15:00"
    actions:
      - action: dashboard_entity_checker.scan_now
```

Für normale Nutzung ist diese Automation nicht erforderlich, weil die Integration bereits automatisch im eingestellten Intervall scannt.

## Ausführung und Fehler

Ein manueller Aufruf wartet auf einen bereits laufenden Scan; parallele Scans werden verhindert. Können alle ausgewählten Dashboards nicht geladen werden oder tritt ein vollständiger Coordinator-Fehler auf, schlägt der Action-Aufruf mit einem Home-Assistant-Fehler fehl.

Bei einem Teilausfall wird die Action erfolgreich beendet. Details stehen anschließend in `dashboard_errors` und `last_error`.
