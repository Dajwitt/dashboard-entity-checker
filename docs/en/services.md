# `scan_now` action

## `dashboard_entity_checker.scan_now`

This action immediately requests a scan of every configured dashboard. It has no parameters.

## Developer Tools

Under **Developer Tools → Actions**:

```yaml
action: dashboard_entity_checker.scan_now
```

## Script example

```yaml
script:
  example_dashboard_check:
    alias: "Example: dashboard check"
    sequence:
      - action: dashboard_entity_checker.scan_now
```

## Automation example

```yaml
automation:
  - alias: "Example: request dashboard check"
    triggers:
      - trigger: time
        at: "03:15:00"
    actions:
      - action: dashboard_entity_checker.scan_now
```

This automation is unnecessary for normal use because the integration already scans automatically at the configured interval.

## Execution and errors

A manual request waits for an already running scan; parallel scans are prevented. If none of the selected dashboards can be loaded or the coordinator update fails completely, the action call fails with a Home Assistant error.

During a partial failure, the action completes successfully. Details then appear in `dashboard_errors` and `last_error`.
