# Benachrichtigungen

Wenn die Option aktiviert ist, verwaltet die Integration eine einzige persistente Benachrichtigung mit der festen ID `dashboard_entity_checker_missing_entities`.

## Verhalten

- Ein vollständiger Scan mit Funden erstellt oder aktualisiert die Meldung.
- Ein identisches Ergebnis erzeugt kein unnötiges Update.
- Ein vollständiger sauberer Scan entfernt die Meldung.
- Das Deaktivieren der Option entfernt sie ebenfalls.
- Ein partieller Scan verändert die bestehende Meldung nicht.
- Titel und Meldungstext sind abhängig von Home Assistants Sprache deutsch oder englisch.

## Gruppierung

Die Meldung gruppiert nach Dashboard und Ansicht. Pro Ansicht werden höchstens acht Entity-IDs gezeigt; weitere Funde erscheinen als Restzähler. Die vollständige, ungekürzte Liste bleibt im Sensorattribut `missing_entities`.

```text
Dashboard Entity Checker: 2 fehlende Entities

2 fehlende Entities in 3 Ansichten

### `example-main`

**Overview** · 1
- `sensor.example_retired_temperature`

**Security** · 1
- `binary_sensor.example_old_contact`

### `example-tablet`

**Details** · 1
- `sensor.example_retired_temperature`

Vollständige Liste: Sensorattribut `missing_entities`.
```

Die Zahl im Titel zählt eindeutige aktive Entity-IDs. Dieselbe ID kann darunter an mehreren Standorten erscheinen.

## Teilausfälle

Kann ein ausgewähltes Dashboard nicht geladen werden, ist das Ergebnis unvollständig. Eine vorhandene Fundmeldung wird deshalb weder entfernt noch mit dem Teilergebnis überschrieben. Der Teilausfall selbst steht im Result-Sensor und in der Diagnostik.

## Keine zusätzlichen Duplikate

Die Integration verwendet immer dieselbe Notification-ID. Sie erstellt nicht bei jedem Intervall eine neue Meldung. Wer zusätzliche Push-Nachrichten benötigt, kann das Result-Changed-Event in einer eigenen Automation verwenden.
