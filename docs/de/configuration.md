# Konfiguration

Die Einrichtung und spätere Änderungen erfolgen über Home Assistants Config Flow und Options Flow. Es ist keine YAML-Konfiguration nötig.

## Ersteinrichtung

Nach Installation und Neustart:

1. **Einstellungen → Geräte & Dienste** öffnen.
2. **Integration hinzufügen** wählen.
3. Nach **Dashboard Entity Checker** suchen.
4. Mindestens ein Dashboard auswählen.
5. Das Scan-Intervall zwischen 1 und 1440 Minuten setzen; Standard sind 5 Minuten.
6. Persistente Benachrichtigungen aktivieren oder deaktivieren.
7. Optional alle Home-Assistant-Entities durchsuchen und exakt zu ignorierende Entity-IDs auswählen oder eingeben.

Die Einrichtung wird abgewiesen, wenn kein Dashboard gewählt wurde, ein ausgewähltes Dashboard nicht geladen werden kann oder eine Ignore-ID syntaktisch ungültig ist.

## Konfigurationsfelder

| Feld | Typ | Standard | Bedeutung |
|---|---|---|---|
| Dashboards | Mehrfachauswahl | `my-ha-dashboard` | Lovelace-Dashboards, die geprüft werden |
| Scan-Intervall | Ganzzahl 1–1440 | 5 Minuten | Abstand zwischen automatischen Scans |
| Benachrichtigungen | Ein/Aus | Ein | Persistente Meldung bei aktiven Funden |
| Ignorierte Entity-IDs | Suchbare Mehrfachauswahl | leer | Alle vorhandenen und registrierten Entities durchsuchen oder exakte IDs frei eingeben |

`my-ha-dashboard` ist nur der technische Standardwert der Integration. In der Auswahl erscheinen die auf der jeweiligen Home-Assistant-Instanz verfügbaren Dashboards.

Die Entity-Auswahl vereinigt die aktuelle State Machine mit der vollständigen Entity Registry. Dadurch werden auch registrierte, deaktivierte, nicht verfügbare oder derzeit zustandslose Entities angeboten. Aktuelle Checker-Funde und bereits gespeicherte Ignore-IDs bleiben ebenfalls sichtbar; vollständig gelöschte IDs können als benutzerdefinierter exakter Wert eingegeben werden.

## Optionen ändern

**Einstellungen → Geräte & Dienste → Dashboard Entity Checker → Konfigurieren** öffnen. Dort können alle Felder geändert werden. Nach dem Speichern wird die Config Entry neu geladen; der nächste Scan verwendet sofort die neuen Werte.

Wird die Benachrichtigungsoption ausgeschaltet, entfernt die Integration ihre bestehende persistente Benachrichtigung. Sensor und Event bleiben aktiv.

## Eine Instanz

Pro Home-Assistant-Instanz ist genau eine Config Entry erlaubt. Diese eine Instanz kann mehrere Dashboards prüfen.

## Migration älterer Konfigurationen

Konfigurationen aus Config-Flow-Version 1 mit einem einzelnen Dashboard werden automatisch in die Mehrfachauswahl der Version 2 überführt. Das zuvor gewählte Dashboard bleibt erhalten.
