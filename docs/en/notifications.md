# Notifications

When enabled, the integration manages one persistent notification with the fixed ID `dashboard_entity_checker_missing_entities`.

## Behavior

- A complete scan with findings creates or updates the notification.
- An identical result causes no unnecessary update.
- A complete clean scan dismisses it.
- Disabling the option also dismisses it.
- A partial scan does not modify the existing notification.
- Title and message are German or English according to Home Assistant's language.

## Grouping

The message groups findings by dashboard and view. Each view shows at most eight entity IDs; additional findings are summarized by a remaining count. The complete unabridged list remains in the `missing_entities` sensor attribute.

```text
Dashboard Entity Checker: 2 missing entities

2 missing entities in 3 views

### `example-main`

**Overview** · 1
- `sensor.example_retired_temperature`

**Security** · 1
- `binary_sensor.example_old_contact`

### `example-tablet`

**Details** · 1
- `sensor.example_retired_temperature`

Complete list: sensor attribute `missing_entities`.
```

The number in the title counts unique active entity IDs. The same ID can appear at multiple locations below it.

## Partial failures

If a selected dashboard cannot be loaded, the result is incomplete. An existing finding notification is therefore neither dismissed nor overwritten with the partial result. The partial failure itself is exposed by the result sensor and diagnostics.

## No duplicate stream

The integration always uses the same notification ID. It does not create a new notification at every interval. Users who need additional push messages can consume the result-changed event in their own automation.
