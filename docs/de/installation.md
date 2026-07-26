# Installation

Dashboard Entity Checker ist eine Custom-Integration. Version 0.3.6 ist der aktuelle stabile Pre-1.0-Release und noch nicht im Standard-HACS-Katalog enthalten.

## Voraussetzungen

- Home Assistant 2026.7.0 oder neuer
- HACS 2.0.0 oder neuer für die HACS-Installation
- ein Lovelace-Dashboard im Storage-Modus oder ein anderes Dashboard, das Home Assistant über seine Lovelace-Schnittstellen laden kann

## Installation über HACS

HACS muss bereits installiert und funktionsfähig sein.

[Custom-Repository in Home Assistant öffnen](https://my.home-assistant.io/redirect/hacs_repository/?owner=Dajwitt&repository=dashboard-entity-checker&category=integration)

Falls der Link nicht funktioniert:

1. HACS in Home Assistant öffnen.
2. Das Dreipunkt-Menü oben rechts öffnen.
3. **Custom repositories** wählen.
4. Diese Repository-URL eingeben:

```text
https://github.com/Dajwitt/dashboard-entity-checker
```

5. Kategorie **Integration** wählen und das Repository hinzufügen.
6. **Dashboard Entity Checker** in HACS öffnen und **Download** wählen.
7. Home Assistant neu starten.
8. Mit der [Konfiguration](./configuration.md) fortfahren.

Es ist kein Eintrag in `configuration.yaml` erforderlich.

## Manuelle Installation

1. Das neueste GitHub-Release herunterladen.
2. Sicherstellen, dass der Zielpfad genau so aussieht:

```text
/config/custom_components/dashboard_entity_checker/manifest.json
```

3. Den Ordner `custom_components/dashboard_entity_checker` nach `/config/custom_components/` kopieren.
4. Home Assistant neu starten.
5. Mit der [Konfiguration](./configuration.md) fortfahren.

## Aktualisieren

Bei HACS-Installationen das Update über HACS herunterladen und Home Assistant anschließend neu starten. Bei manuellen Installationen den Integrationsordner vollständig durch den Ordner aus dem neuen Release ersetzen und ebenfalls neu starten.

Vor einem Update empfiehlt sich ein Home-Assistant-Backup. Die bestehende Config Entry wird beim Update weiterverwendet.

## Deinstallation

1. Die Integration unter **Einstellungen → Geräte & Dienste** entfernen.
2. Bei HACS-Installation das Repository über HACS entfernen; bei manueller Installation den Ordner `dashboard_entity_checker` löschen.
3. Home Assistant neu starten.

Das Entfernen der Integration verändert keine Dashboards.
