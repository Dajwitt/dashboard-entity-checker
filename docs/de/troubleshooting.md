# Fehlerbehebung

## Sensor bleibt bei `Warte auf ersten Scan`

Der erste Scan startet erst nach Home Assistants vollständigem Start. Kurz nach einem Neustart ist der Zustand normal. Dauert er an, `dashboard_entity_checker.scan_now` unter **Entwicklerwerkzeuge → Aktionen** ausführen und die Home-Assistant-Logs prüfen.

## `dashboard_errors` enthält Einträge

1. `last_error` und den einzelnen Fehlertext prüfen.
2. Kontrollieren, ob der Dashboard-URL-Pfad noch existiert.
3. Das Dashboard in Home Assistant öffnen.
4. Die Integrationsoptionen öffnen und eine ungültige Auswahl entfernen oder neu wählen.
5. Erneut scannen.

Bei Teilausfällen bleiben Ergebnisse anderer Dashboards sichtbar. Sie sind aber kein vollständiger Gesamtscan.

## `template_diagnostics` enthält Einträge

| Code | Typische Ursache |
|---|---|
| `missing_template` | Name fehlt oder Template wurde umbenannt |
| `circular_template` | Templates rufen sich gegenseitig auf |
| `max_template_depth` | Kette ist tiefer als 20 Ebenen |
| `unknown_variable` | benötigte Variable oder Default fehlt |
| `invalid_variables` | `default` oder `variables` ist strukturell ungültig |

Die Diagnose enthält Dashboard, Ansicht, Template und soweit möglich Variable oder Detail. Die Quellkonfiguration dort prüfen; der Checker verändert sie nicht.

## Erwartete fehlende ID wird nicht gemeldet

- Die ID besitzt noch einen Entity-Registry-Eintrag.
- Die ID steht unter `ignored_entities`; bei echtem Treffer erscheint sie unter `ignored_matches`.
- Das betroffene Dashboard ist nicht ausgewählt oder konnte nicht geladen werden.
- Die Referenz wird dynamisch erzeugt oder liegt in einem nicht unterstützten Custom-Card-Format.
- Die ID verwendet eine nicht unterstützte Domain.

Siehe [Unterstützte Referenzen](./supported-references.md) und [Bekannte Grenzen](./limitations.md).

## Offensichtlich falscher Wert wird nur teilweise erkannt

Version 0.3.5 oder neuer installieren. Diese Version behandelt versehentlich angehängte Punkt-Suffixe als vollständigen fehlerhaften Scalar. Nach dem Update Home Assistant neu starten und manuell scannen.

## Entityähnlicher Action-Name wird gemeldet

Direkte Werte unter dem modernen Dashboard-Schlüssel `action` werden derzeit nicht wie `service` und `perform_action` ausgeschlossen. Dadurch kann zum Beispiel `light.example_turn_on` als fehlende Entity erscheinen. Den Fundort prüfen; diese bekannte Grenze ist unter [Bekannte Grenzen](./limitations.md) beschrieben.

## Benachrichtigung fehlt oder ist unverändert

- Benachrichtigungsoption prüfen.
- `missing_entities` kontrollieren.
- Bei einem Teilausfall bleibt die vorherige Benachrichtigung absichtlich unverändert.
- Ein identisches vollständiges Ergebnis erzeugt kein unnötiges Update.

## Fehlerbericht erstellen

1. Neueste Version installieren und Home Assistant neu starten.
2. Einen manuellen Scan ausführen.
3. Sensorattribute und Home-Assistant-Logs prüfen.
4. [Diagnostik](./diagnostics.md) herunterladen und redigieren.
5. Ein Issue unter [GitHub Issues](https://github.com/Dajwitt/dashboard-entity-checker/issues) mit klaren Schritten und erwartetem Ergebnis öffnen.

Keine Zugangsdaten, privaten URLs oder echten privaten Entity-IDs öffentlich posten.
