# Requirements

## Supported versions

| Component | Minimum version |
|---|---|
| Home Assistant | 2026.7.0 |
| HACS for HACS installation | 2.0.0 |

Version 0.3.6 is the current stable release.

The table lists retained minimums, not the newest tested versions; use a current
HACS release. Regular CI uses HA **2026.10.4**, replacing the old 2026.7.2 test pin.
Separate real-Core tests on **2026.11.0b0/b1** each passed 87 existing tests and
7 runtime tests (94 passed, 96.32% coverage). Both November versions remain beta.
No incompatible October HA pytest plugin was forced into those environments.
CI also repeats the 87 existing tests on b0/b1; the additional seven real-Core
harness tests remain a separate local acceptance, not part of that CI count.

Targeted live b0 scans, ignore behavior, notification create/update/dismiss and
options reload passed with unchanged integration code. Browser rendering and
Recorder persistence are not certified. Frontend-generated Strategy dashboards
are not resolved: an empty scan/OK does not certify their generated contents.

HA November beta's built-in Marketplace is separate from HACS. A separate
Dashboard Entity Checker Marketplace installation was not tested; this is not
a claim of Marketplace certification. Read its community-extension risk notice
yourself before using that alternative. No version bump or runtime fix accompanies
this documentation/test-baseline maintenance.

## Technical classification

| Property | Value |
|---|---|
| Integration type | `service` |
| IoT class | `local_polling` |
| Config flow | yes, version 2 |
| Config entries | one per Home Assistant instance |
| Dependencies | `lovelace`, `persistent_notification` |
| Platform | `sensor` |
| Configuration | UI, no YAML required |

## Supported languages

Config flow, options flow, and notification messages are available in German and English. Internal sensor status values such as `Fehler gefunden` currently remain German regardless of UI language.

## Network and cloud

Scanning runs locally in Home Assistant. The integration itself requires no cloud connection for checking and sends no dashboard content to an external service. HACS or a manual browser download naturally requires GitHub access to install files.

## Release history

| Version | Focus |
|---|---|
| 0.3.6 | native options and search across all Home Assistant entities |
| 0.3.5 | complete detection of accidentally appended dot suffixes |
| 0.3.4 | expanded tests, coverage threshold, and Ruff checks |
| 0.3.3 | project and integration icon |
| 0.3.2 | compact grouped German and English notifications |
| 0.3.1 | ignore list can be cleared completely |
| 0.3.0 | multiple dashboards, nested Decluttering resolution, and result-changed event |

## Project status

The repository is public but is not yet in the default HACS catalog. Until then, install it as a HACS custom repository or manually. Any future v1.0 or default-catalog date is not a firm commitment.
