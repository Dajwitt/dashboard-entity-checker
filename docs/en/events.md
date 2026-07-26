# Events

## `dashboard_entity_checker_result_changed`

After a complete baseline scan, the integration fires this event when the complete active result changes.

## When is it fired?

| Situation | Event |
|---|---|
| active result changes after baseline | yes |
| result remains identical | no |
| first complete scan establishes baseline | no |
| at least one dashboard could not be loaded | no |
| only `ignored_matches` changes while active list stays equal | no |

A location change counts because `missing_entities`, including locations, is compared. In that case, `added_entities` and `removed_entities` can both be empty.

## Event data

| Field | Type | Meaning |
|---|---|---|
| `dashboards` | list | configured dashboard URL paths |
| `previous_count` | number | previous count of active IDs |
| `current_count` | number | current count of active IDs |
| `added_entities` | list | newly missing IDs, sorted |
| `removed_entities` | list | IDs no longer missing, sorted |
| `missing_entities` | list | complete current result with locations |
| `scan_time` | string | ISO timestamp of the scan |

## Automation example

```yaml
automation:
  - alias: "Example: dashboard findings changed"
    triggers:
      - trigger: event
        event_type: dashboard_entity_checker_result_changed
    conditions:
      - condition: template
        value_template: "{{ trigger.event.data.added_entities | count > 0 }}"
    actions:
      - action: persistent_notification.create
        data:
          title: "New dashboard references"
          message: >
            {{ trigger.event.data.added_entities | join(', ') }}
```

The example deliberately avoids a device-specific notify action. Production automations should also account for location-only changes that fire an event without added or removed IDs. After a partial scan, the next complete scan is treated as a new comparison baseline and also does not fire an event yet.
