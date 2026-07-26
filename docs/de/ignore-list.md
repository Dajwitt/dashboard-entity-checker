# Ausschlüsse

Exakte Entity-IDs, die bewusst nicht als aktive Funde erscheinen sollen, können im Config Flow oder Options Flow ausgewählt oder eingegeben werden.

## Auswahl

Das suchbare Mehrfachauswahlfeld enthält:

- alle Entity-IDs aus Home Assistants aktueller State Machine,
- alle Einträge der Entity Registry, einschließlich registrierter Entities ohne aktuellen State,
- aktuelle und bereits ignorierte Checker-Funde sowie gespeicherte Ignore-IDs.

Nach Domain, Objekt-ID oder einem vollständigen Wert suchen und jeden gewünschten Eintrag auswählen. Existiert eine ID nicht mehr, kann sie vollständig eingegeben und über **Benutzerdefiniertes Element hinzufügen** übernommen werden:

```text
sensor.example_intentionally_missing
```

Beim Speichern muss jeder Wert eine syntaktisch gültige Home-Assistant-Entity-ID sein. Duplikate werden zusammengeführt. Die ID muss nicht existieren; genau dafür bleibt die freie exakte Eingabe verfügbar.

## Exakte Übereinstimmung

Ausschlüsse gelten nur für die komplette ID. Es gibt keine Wildcards, regulären Ausdrücke, Domain-Filter oder Teilstring-Suche.

```text
sensor.example_room
```

ignoriert nicht `sensor.example_room_temperature`.

## Transparenz

| Attribut | Inhalt |
|---|---|
| `missing_entities` | aktive, nicht ignorierte Funde |
| `ignored_entities` | vollständige konfigurierte Liste |
| `ignored_matches` | derzeit tatsächlich gefundene und ausgeschlossene IDs mit Standorten |

Eine konfigurierte ID, die im Scan nicht fehlt, erscheint nur unter `ignored_entities`, nicht unter `ignored_matches`.

## Beispiel

```json
{
  "missing_entities": [
    {"entity": "sensor.example_active_problem", "locations": []}
  ],
  "ignored_entities": ["binary_sensor.example_expected_missing"],
  "ignored_matches": [
    {"entity": "binary_sensor.example_expected_missing", "locations": []}
  ]
}
```

## Liste leeren

Das Feld im Options Flow vollständig leeren und speichern. Die Integration entfernt dann alle Ausschlüsse. Sind Benachrichtigungen aktiv, wird das nächste vollständige Scanergebnis entsprechend aktualisiert.
