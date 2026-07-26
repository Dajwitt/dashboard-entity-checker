# Anforderungen

## Unterstützte Versionen

| Komponente | Mindestversion |
|---|---|
| Home Assistant | 2026.7.0 |
| HACS für HACS-Installation | 2.0.0 |

Version 0.3.6 ist der aktuelle stabile Release.

## Technische Einordnung

| Eigenschaft | Wert |
|---|---|
| Integrationstyp | `service` |
| IoT-Klasse | `local_polling` |
| Config Flow | ja, Version 2 |
| Config Entries | eine pro Home-Assistant-Instanz |
| Abhängigkeiten | `lovelace`, `persistent_notification` |
| Plattform | `sensor` |
| Konfiguration | UI, kein YAML erforderlich |

## Unterstützte Sprachen

Config Flow, Options Flow und Benachrichtigungstexte sind auf Deutsch und Englisch vorhanden. Interne Sensorstatuswerte wie `Fehler gefunden` stammen derzeit deutsch aus der Integration.

## Netzwerk und Cloud

Der Scan läuft lokal in Home Assistant. Die Integration selbst benötigt für die Prüfung keine Cloud-Verbindung und sendet keine Dashboard-Inhalte an einen externen Dienst. HACS oder ein manueller Browser-Download benötigen selbstverständlich Zugriff auf GitHub, um die Dateien zu installieren.

## Veröffentlichungsstand

| Version | Schwerpunkt |
|---|---|
| 0.3.6 | native Optionen und Suche über alle Home-Assistant-Entities |
| 0.3.5 | vollständige Erkennung versehentlich angehängter Punkt-Suffixe |
| 0.3.4 | erweiterte Tests, Coverage-Grenze und Ruff-Prüfung |
| 0.3.3 | Projekt- und Integrationssymbol |
| 0.3.2 | kompakte deutsch/englisch gruppierte Benachrichtigungen |
| 0.3.1 | Ignore-Liste kann vollständig geleert werden |
| 0.3.0 | mehrere Dashboards, verschachtelte Decluttering-Auflösung und Result-Changed-Event |

## Projektstatus

Das Repository ist öffentlich, aber noch nicht im Standard-HACS-Katalog. Bis dahin erfolgt die Installation als HACS-Custom-Repository oder manuell. Informationen zu einem zukünftigen v1.0- oder Standard-HACS-Termin sind keine feste Zusage.
