# Unterstützte Referenzen

Der Checker untersucht String-Werte in der geladenen Dashboard-Konfiguration. Er erkennt direkte Entity-IDs, unterstützte statische Zugriffe in Button-Card-JavaScript und Entity-IDs nach der Auflösung von Decluttering-Card-Templates.

## Unterstützte Domains

```text
alarm_control_panel, automation, binary_sensor, button, calendar,
camera, climate, cover, device_tracker, fan, group, humidifier,
input_boolean, input_button, input_datetime, input_number,
input_select, input_text, light, lock, media_player, number,
person, remote, scene, script, select, sensor, switch,
timer, update, vacuum, weather, zone
```

## Direkte Referenzen

Ein String, der vollständig wie eine unterstützte Entity-ID aussieht, wird unabhängig vom umgebenden YAML-Schlüssel erfasst:

```yaml
type: entities
entities:
  - entity: sensor.example_room_temperature
  - light.example_ceiling
variables:
  - speaker: media_player.example_speaker
```

Werte der Schlüssel `service` und `perform_action`, Kartentypen, Icons, URLs und CSS-Werte werden gefiltert. Die Prüfung ist auf Referenzen ausgerichtet und interpretiert nicht die Semantik jeder Custom Card. Für den modernen direkten Schlüssel `action` gilt derzeit eine [bekannte Grenze](./limitations.md).

## Fehlerhafte zusätzliche Punkt-Suffixe

Seit Version 0.3.5 wird ein vollständig entityähnlicher Scalar mit einem versehentlich angehängten weiteren Punkt-Suffix als kompletter fehlerhafter Wert erfasst:

```yaml
variables:
  - contact: binary_sensor.example_window_contact.example_door_contact
```

Der Checker meldet `binary_sensor.example_window_contact.example_door_contact` als fehlende Referenz. Er verkürzt den Wert nicht auf das möglicherweise existierende Präfix `binary_sensor.example_window_contact`. Dieser Fall kann entstehen, wenn Autovervollständigung mitten in einer Entity-ID verwendet wird.

## Button-Card-JavaScript

Blöcke in der Form `[[[ ... ]]]` werden als Text analysiert, nicht ausgeführt. Unterstützt sind unter anderem:

```javascript
states['sensor.example_humidity']
states["binary_sensor.example_window"]
states.light.example_ceiling
```

Statische Entity-IDs in Strings und Kommentaren innerhalb des JavaScript-Blocks werden ebenfalls erkannt:

```javascript
// Remove obsolete sensor.example_legacy_value
return states['sensor.example_humidity'].state;
```

Kommentare werden bewusst gescannt, weil dort häufig alte Referenzen verbleiben.

## JavaScript-Filter

Nicht als Referenz behandelt werden unter anderem:

- Service- oder Action-Werte wie `service: sensor.example_placeholder`
- URLs wie `https://sensor.example.invalid/path`
- CSS-Selektoren wie `.sensor.example_value`
- Objekt-Properties wie `object.sensor.example_value`
- dynamische Zugriffe über berechnete Variablen wie `states[entityId]`

Explizite `states[...]`- und `states.domain.object`-Zugriffe bleiben auch in Feldern wie `styles`, `url` oder `icon` sichtbar.

## Decluttering-Card-Templates

Der Checker liest `decluttering_templates`, ersetzt `[[variable]]`-Platzhalter und prüft die daraus entstehenden Kartenobjekte. Defaults werden zuerst angewendet und durch Werte der Karteninstanz überschrieben.

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

Beide IDs werden der Ansicht `Security` zugeordnet. Die Auflösung unterstützt vollständige verschachtelte Kartenobjekte und rekursive Decluttering-Aufrufe bis maximal 20 Ebenen.

## Template-Diagnostik

Auflösungsprobleme werden separat unter `template_diagnostics` gemeldet:

| Code | Bedeutung |
|---|---|
| `missing_template` | Template-Name fehlt oder existiert nicht |
| `circular_template` | zirkuläre Template-Kette erkannt |
| `max_template_depth` | maximale Tiefe von 20 erreicht |
| `unknown_variable` | benötigter Platzhalterwert fehlt |
| `invalid_variables` | Defaults oder Variablen besitzen eine ungültige Struktur |

Eine Template-Diagnose ist nicht automatisch eine fehlende Entity. Der restliche Dashboard-Scan läuft weiter.
