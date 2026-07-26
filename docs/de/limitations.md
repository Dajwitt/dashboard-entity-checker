# Bekannte Grenzen

## JavaScript wird nicht ausgeführt

Button-Card-JavaScript wird statisch als Text untersucht. Statische Zugriffe wie `states['sensor.example_humidity']` sind sichtbar. Dynamisch erzeugte IDs können nicht sicher berechnet werden:

```javascript
const entityId = `sensor.${room}_temperature`;
return states[entityId].state;
```

Der Checker führt keinen JavaScript-Code aus und wertet keine Variablen, Funktionen oder Laufzeitbedingungen aus.

## Kommentare werden mitgeprüft

Entity-ähnliche Werte in JavaScript-Kommentaren werden bewusst erfasst. Ein auskommentierter veralteter Verweis kann daher als Fund erscheinen. Entferne ihn aus dem Dashboard oder trage die exakte ID bewusst in die Ignore-Liste ein.

## Custom Cards

Direkte statische Entity-IDs in ihrer Konfiguration können erkannt werden. Eigene Referenzformate, externe Dateien oder IDs, die erst durch den JavaScript-Code einer Custom Card erzeugt werden, sind dagegen nicht allgemein auflösbar.

## Direkter `action`-Schlüssel

Die direkten Scalar-Schlüssel `service` und `perform_action` werden als Dienstnamen übersprungen. Der modernere Schlüssel `action` wird in normalen Dashboard-Objekten derzeit nicht auf dieselbe Weise ausgeschlossen. Ein entityähnlicher Action-Name wie `light.example_turn_on` kann deshalb fälschlich als Entity-Referenz erscheinen. Bis der Parser dies angleicht, muss ein solcher Fund am angegebenen Dashboard-Ort manuell geprüft werden.

## Decluttering Card

- nur vorhandene `decluttering_templates` der geladenen Dashboard-Konfiguration können aufgelöst werden
- unbekannte Variablen werden diagnostiziert, nicht geraten
- zirkuläre Aufrufe werden abgebrochen
- die maximale rekursive Tiefe beträgt 20
- `[[variable]]` wird unterstützt; Button-Card-JavaScript `[[[ ... ]]]` ist ein getrennter Analyseweg

## Existenzprüfung

Eine Entity mit Registry-Eintrag gilt nicht als fehlend, auch wenn sie deaktiviert, `unavailable` oder ohne aktuellen State ist. Die Integration prüft Referenzexistenz, nicht Verfügbarkeit oder Gerätezustand.

## Kein Reparaturwerkzeug

Der Checker schreibt keine Dashboard-Konfiguration und bietet keine automatische Korrektur. Fundort und vollständige ID sollen eine manuelle, kontrollierte Reparatur erleichtern.

## Kein vollständiger Home-Assistant-Audit

Geprüft werden nur ausgewählte Dashboards und die ausdrücklich unterstützten Referenzformen. Automationen, Scripts, Template-Helfer und andere Home-Assistant-Konfigurationen gehören nicht zu diesem Projektumfang.
