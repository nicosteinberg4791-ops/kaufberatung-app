# Offene Punkte – Kaufberatung-App

| ID | Datum | Frage | Auswirkung, wenn offen | entscheidet | Ergebnis |
|---|---|---|---|---|---|
| O1 | 08.11.2026 | Tägliche Preisabfrage für die App | – | Nico | entschieden 08.11.2026 (über Lead-Sitzung): GitHub Actions (`schedule` täglich morgens + `workflow_dispatch`), committet preise.json nur bei Änderung; lokale geplante Aufgabe entfällt, Runde 6 liest preise.json statt eigener heise-Abfrage. Umsetzung offen |
| O2 | 08.11.2026 | Hosting und Push | – | Nico | entschieden 08.11.2026: öffentliches Repo („Einfach, öffentlich“), Push über ntfy.sh mit langem Zufalls-Topic nur als Secret `NTFY_TOPIC`. Offen: Wunschpreise für den Workflow (z. B. wunschpreise.json), heise von GitHub-Runnern erreichbar?, Nutzungsbedingungen heise ungeklärt (robots.txt erlaubt Produktseiten), Ende 01.12.2026, 60-Tage-Abschaltung von Zeitplänen |
| O3 | 08.11.2026 | Anlegen des öffentlichen Repos wurde von der Freigabesperre der Sitzung blockiert (Freigabe kam nur weitergeleitet) | App nicht online | Nico | erledigt 08.11.2026: Nico „Ja, veröffentlichen“, Repo und Pages angelegt |
