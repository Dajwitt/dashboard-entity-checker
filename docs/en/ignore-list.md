# Exclusions

Exact entity IDs that intentionally should not appear as active findings can be selected or entered in the config flow or options flow.

## Selection

The searchable multiple-selection field contains:

- every entity ID from Home Assistant's current state machine,
- every entity-registry entry, including registered entities without a current state,
- current and previously ignored checker findings plus saved ignore IDs.

Search by domain, object ID, or a complete value and select each required entry. If an ID no longer exists, enter it completely and choose **Add custom item**:

```text
sensor.example_intentionally_missing
```

Every saved value must be a syntactically valid Home Assistant entity ID. Duplicates are removed. The ID does not need to exist; that is why free exact entry remains available.

## Exact matching

Exclusions apply only to the complete ID. Wildcards, regular expressions, domain filters, and substring matching are not supported.

```text
sensor.example_room
```

does not ignore `sensor.example_room_temperature`.

## Transparency

| Attribute | Content |
|---|---|
| `missing_entities` | active, non-ignored findings |
| `ignored_entities` | complete configured list |
| `ignored_matches` | IDs currently found and excluded, with locations |

A configured ID that is not missing appears only under `ignored_entities`, not under `ignored_matches`.

## Example

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

## Clearing the list

Clear the options-flow field completely and save. The integration then removes every exclusion. If notifications are enabled, the next complete scan updates the result accordingly.
