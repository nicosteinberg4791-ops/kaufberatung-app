# Bewertung Codex R2 (codex-nach-20261108-203000.json)

| Befund | Schwere | Einordnung | Begründung / Maßnahme |
|---|---|---|---|
| B1 Kürzung verwirft Treffer | schwer | bestätigt | in R2 geschlossen (Meldetext vollständig, Test mit zehn Treffern). |
| B2 Nicht zugestellte Ereignisse gehen bei Preisänderung verloren | schwer | ungeklärt → Nico | Rest von R1-B2: Versand scheitert, bis zum nächsten Lauf steigt der Preis wieder über den Wunschpreis → die verpasste Meldung wird nicht nachgereicht. Vorschlag Lead (bewusste Entscheidung, Bestätigung durch Nico offen): nur noch gültige Ereignisse melden. Eine veraltete Meldung über einen nicht mehr verfügbaren Preis führt in die Irre; der fehlgeschlagene Versand macht den Lauf rot (GitHub meldet ihn); eine private, dauerhafte Warteschlange im öffentlichen Repo (Cache/Artefakt/Secret) wäre unverhältnismäßig. Anleitung nennt die Grenze ausdrücklich. Bestätigt Nico nicht: Warteschlange als eigenes Paket. |
