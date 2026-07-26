# Supported references

The checker inspects string values in loaded dashboard configuration. It detects direct entity IDs, supported static accesses in Button-Card JavaScript, and entity IDs produced by Decluttering Card template resolution.

## Supported domains

```text
alarm_control_panel, automation, binary_sensor, button, calendar,
camera, climate, cover, device_tracker, fan, group, humidifier,
input_boolean, input_button, input_datetime, input_number,
input_select, input_text, light, lock, media_player, number,
person, remote, scene, script, select, sensor, switch,
timer, update, vacuum, weather, zone
```

## Direct references

A string that entirely resembles a supported entity ID is collected regardless of the surrounding YAML key:

```yaml
type: entities
entities:
  - entity: sensor.example_room_temperature
  - light.example_ceiling
variables:
  - speaker: media_player.example_speaker
```

Values of the `service` and `perform_action` keys, card types, icons, URLs, and CSS values are filtered. The checker focuses on references and does not interpret every custom card's semantics. The modern direct `action` key currently has a [known limitation](./limitations.md).

## Malformed extra dot suffixes

Since version 0.3.5, an otherwise entity-like scalar with an accidentally appended dot-separated suffix is collected as the complete malformed value:

```yaml
variables:
  - contact: binary_sensor.example_window_contact.example_door_contact
```

The checker reports `binary_sensor.example_window_contact.example_door_contact` as a missing reference. It does not shorten it to the potentially existing prefix `binary_sensor.example_window_contact`. This can happen when autocomplete is used in the middle of an entity ID.

## Button-Card JavaScript

Blocks using `[[[ ... ]]]` are analyzed as text and are not executed. Supported forms include:

```javascript
states['sensor.example_humidity']
states["binary_sensor.example_window"]
states.light.example_ceiling
```

Static entity IDs in strings and comments inside the JavaScript block are also detected:

```javascript
// Remove obsolete sensor.example_legacy_value
return states['sensor.example_humidity'].state;
```

Comments are deliberately scanned because stale references often remain there.

## JavaScript filtering

The following are not treated as references, among other cases:

- service or action values such as `service: sensor.example_placeholder`
- URLs such as `https://sensor.example.invalid/path`
- CSS selectors such as `.sensor.example_value`
- object properties such as `object.sensor.example_value`
- dynamic access through computed variables such as `states[entityId]`

Explicit `states[...]` and `states.domain.object` access remains visible even in fields such as `styles`, `url`, or `icon`.

## Decluttering Card templates

The checker reads `decluttering_templates`, substitutes `[[variable]]` placeholders, and scans the resulting card objects. Defaults are applied first and are overridden by values supplied by the card instance.

```yaml
decluttering_templates:
  example_security_row:
    default:
      - secondary: binary_sensor.example_secondary_contact
    card:
      type: entities
      entities:
        - '[[primary]]'
        - '[[secondary]]'

views:
  - title: Security
    cards:
      - type: custom:decluttering-card
        template: example_security_row
        variables:
          - primary: binary_sensor.example_primary_contact
```

Both IDs are assigned to the `Security` view. Resolution supports complete nested card objects and recursive Decluttering calls up to 20 levels.

## Template diagnostics

Resolution problems are reported separately under `template_diagnostics`:

| Code | Meaning |
|---|---|
| `missing_template` | template name is absent or does not exist |
| `circular_template` | circular template chain detected |
| `max_template_depth` | maximum depth of 20 reached |
| `unknown_variable` | required placeholder value is missing |
| `invalid_variables` | defaults or variables have an invalid structure |

A template diagnostic is not automatically a missing entity. The rest of the dashboard scan continues.
