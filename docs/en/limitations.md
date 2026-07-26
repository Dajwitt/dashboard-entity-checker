# Known limitations

## JavaScript is not executed

Button-Card JavaScript is inspected statically as text. Static access such as `states['sensor.example_humidity']` is visible. Dynamically created IDs cannot be calculated safely:

```javascript
const entityId = `sensor.${room}_temperature`;
return states[entityId].state;
```

The checker does not execute JavaScript or evaluate variables, functions, or runtime conditions.

## Comments are scanned

Entity-like values in JavaScript comments are deliberately collected. A commented-out obsolete reference can therefore appear as a finding. Remove it from the dashboard or deliberately place the exact ID on the ignore list.

## Custom cards

Direct static entity IDs in custom-card configuration can be detected. Proprietary reference formats, external files, or IDs created only by a custom card's JavaScript cannot be resolved generically.

## Direct `action` key

The direct scalar keys `service` and `perform_action` are skipped as service names. The newer `action` key is not currently excluded in the same way in ordinary dashboard objects. An entity-like action name such as `light.example_turn_on` can therefore be reported incorrectly as an entity reference. Until the parser treats these keys consistently, inspect such a finding manually at its reported dashboard location.

## Decluttering Card

- only `decluttering_templates` present in the loaded dashboard configuration can be resolved
- unknown variables are diagnosed rather than guessed
- circular calls are stopped
- maximum recursive depth is 20
- `[[variable]]` is supported; Button-Card JavaScript `[[[ ... ]]]` uses a separate analysis path

## Existence check

An entity with a registry entry does not count as missing, even when disabled, `unavailable`, or lacking a current state. The integration checks reference existence, not availability or device health.

## No repair function

The checker does not write dashboard configuration or offer automatic corrections. The location and complete ID are intended to support a manual, controlled repair.

## Not a complete Home Assistant audit

Only selected dashboards and explicitly supported reference forms are checked. Automations, scripts, template helpers, and other Home Assistant configuration are outside this project's scope.
