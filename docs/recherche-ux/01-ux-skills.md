# Recherche 01: UX-/UI-Skills für Claude Code

Stand: 24.11.2026 (alle Angaben am 24.11.2026 per Web abgerufen). Nur gelesen, nichts installiert oder ausgeführt. Webinhalte als Daten behandelt. Die Seitenzusammenfassungen kamen aus WebFetch (Kurzmodell, kein Rohtext Zeile für Zeile); Commit-Daten waren auf den GitHub-Seiten nicht lesbar und sind daher "nicht geprüft".

Schon vorhanden: Impeccable 4.10, Anthropic frontend-design, Apple-HIG-Review, Emil-Kowalski-Design-Engineering, Animations-Skills, Dataviz.

## Tabelle der Kandidaten

| Kandidat | Repo | Lizenz | Sterne | Inhalt (belegt) | Skripte/Netz | Urteil |
|---|---|---|---|---|---|---|
| ux-heuristics (wondelai) | https://github.com/wondelai/skills | MIT | 2,8k | Krug (Trunk-Test, 3 Gesetze), Nielsen 10, Schweregrad 0-4, Score; kein Usability-Test-Leitfaden im SKILL.md | keine Skripte; Amazon-Affiliate-Links im Text | Empfehlung 1 |
| cognitive-walkthrough (mastepanoski) | https://github.com/mastepanoski/claude-skills | MIT | 74 | Aufgabenzerlegung, 4 Fragen je Schritt, Pflichteingabe Persona (Novize bis Experte), Hinweis "Expertenprüfung, kein empirischer Test" | nur Markdown; Repo hat scripts/validate.js (Zweck nicht geprüft) | Empfehlung 2 |
| nielsen-heuristics-audit (mastepanoski) | gleiches Repo | MIT | 74 | 4 Schritte, Nielsen 10, Schweregrad 0-4, Berichtsvorlage, Injection-Schutzhinweis | keine Skripte, keine URLs | Alternative zu ux-heuristics |
| ux-audit (EliaAlberti) | https://github.com/EliaAlberti/ux-audit-skill | MIT (Repo); im SKILL.md keine Lizenzangabe | 35 | Audit aus Screenshots: Zielvorgabe, 16 Frameworks, Befunde mit IDs, annotierte Bilder | scripts/annotate.py (Pillow, Quelltext nicht gelesen), pip nötig | Empfehlung 3 (nur bei Screenshot-Audit), erst Skript lesen |
| ui-ux-pro-max (nextlevelbuilder) | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill | MIT | 153,4k | Suche in CSV-Datenbank (Stile, Paletten, Fonts, UX-Regeln), Checkliste Barrierefreiheit/Touch/Formulare/Navigation; keine Nielsen/Baymard/Laws-of-UX ausdrücklich | scripts/search.py (laut Text ohne Netz), npm-CLI-Installer, CI-Workflow mit Google-Fonts-API nur im Repo | nicht empfohlen: Überlappung mit Impeccable/HIG, Installer und Skript-Zusatz |
| web-design-guidelines (Vercel) | https://github.com/vercel-labs/agent-skills | MIT | 34,8k | über 100 Regeln: A11y, Fokus, Formulare, Touch, Dark Mode, i18n; Ausgabe file:line; Regeln lokal ("Do not fetch rules from the network") | Update-Abschnitt mit gh/curl nur für manuelle Pflege | Option, deckt sich weitgehend mit Impeccable/HIG |
| refactoring-ui (wondelai) | https://github.com/wondelai/skills | MIT | 2,8k | Hierarchie, Abstand, Farbe, Graustufen-zuerst | keine Skripte; Affiliate-Links | Überlappung mit Impeccable, nicht nötig |
| rolemodel-skills | https://github.com/rolemodel/rolemodel-skills | MIT | 7 | laws-of-ux laut README entfernt (ersetzt durch ux-review) | ein Skill installiert einen PreToolUse-Hook | nicht empfohlen |
| Laws-of-UX-Einzelskills, Hydrogen-Ecommerce-UX (Baymard/NN/g-Bezug nur laut Eigenangabe), nexscope ecommerce-checkout | nur über Verzeichnisseiten (skills.sh, claudemarketplaces) gesehen | nexscope MIT laut Snippet | nexscope 493 laut Snippet | nicht geprüft | nicht geprüft | nicht geprüft; Hydrogen ist Shopify-spezifisch, Checkout passt nicht zu einer Beratungs-App |
| anthropics/skills, awesome-claude-skills-Listen | https://github.com/anthropics/skills | - | - | nicht gesondert geprüft (frontend-design schon vorhanden) | - | nicht geprüft |

Nicht gefunden: ein Skill für "guided selling"/Entscheidungshilfen, Vergleichstabellen oder Persona-/Usability-Test-Simulation im engeren Sinn. Nächster Treffer ist der Cognitive Walkthrough mit Persona-Eingabe. Weitere Treffer nur über Verzeichnisseiten (z. B. https://claudeskills.page/skills/design/ux-heuristics-review/), nicht im Repo geprüft.

## Empfehlung (höchstens 3)

1. **ux-heuristics (wondelai)**: Usability-Prüfung nach Krug (Trunk-Test) und Nielsen mit Schweregrad und Score. Das ist Bewertung statt Gestaltung/Feinschliff und ergänzt Impeccable, HIG und Emil. Reiner Text, daher unabhängig von React/Vanilla-JS.
   - Installation (Besitzer gibt frei): nur den Ordner `ux-heuristics` aus https://github.com/wondelai/skills nach `.claude/skills/ux-heuristics/` kopieren (bevorzugt). Laut README alternativ `npx skills add wondelai/skills/ux-heuristics` oder `/plugin marketplace add wondelai/skills` mit `/plugin install ux-design@wondelai-skills` (Bündel, daher nicht bevorzugt).
2. **cognitive-walkthrough (mastepanoski)**: Simuliert Aufgaben (z. B. "Fernseher im Finder auswählen") Schritt für Schritt für eine vorgegebene Persona (Novize, 65+). Nächstliegender Ersatz für Persona-/Usability-Test-Simulation; ausdrücklich Expertenprüfung, kein echter Test.
   - Installation laut README: `npx skills add mastepanoski/claude-skills --skill cognitive-walkthrough`, sicherer manuell nur `skills/cognitive-walkthrough/` kopieren.
3. **ux-audit (EliaAlberti)**: nur falls Screenshot-Audits mit annotierten Bildern gewünscht sind, sonst weglassen.
   - Installation laut README: Repo klonen, SKILL.md und scripts nach `.claude/skills/ux-audit/` kopieren, `pip3 install --user pillow`. Vorher `scripts/annotate.py` selbst lesen.

## Sicherheitsbefund je Empfehlung

- **ux-heuristics:** SKILL.md ohne Skripte und Code, keine Datenübertragung, keine Rechteerweiterung, keine verdächtigen Anweisungen. Auffällig nur Amazon-Affiliate-Links (harmlos). `references/`-Dateien nicht gelesen: vor Installation prüfen. `scripts/generate-plugins.sh` auf Repo-Ebene nicht gelesen; wird beim Ordnerkopieren nicht mitinstalliert.
- **cognitive-walkthrough:** nur Markdown, keine URLs, kein Netz; Sicherheitshinweis behandelt Fremdinhalte als unvertrauenswürdig (defensiv). Kein `allowed-tools`-Feld. `references/`-Dateien und `scripts/validate.js` nicht gelesen. `npx skills add` lädt ein npm-Paket und führt es aus: nur mit Besitzerfreigabe, manuelles Kopieren ist sicherer.
- **ux-audit:** SKILL.md ohne Netzzugriff und Datenversand, schreibt lokal in `./ux-audit-<Datum>-<slug>/`. `annotate.py` und pip-Installation von Pillow sind echte Ausführung; Quelltext nicht gelesen, Status "nicht geprüft".
- Hooks: bei den drei Empfehlungen nicht festgestellt (Seiten zeigen keinen Hooks-Ordner; nicht vollständig belegt). Telemetrie auf den gelesenen Seiten nirgends erwähnt, aber nicht ausgeschlossen.

## Nicht prüfbar / offen

- Letzte Commit-Daten und Pflegezustand aller Repos (GitHub-Seiten lieferten nur Commit-Anzahl).
- Rohinhalt der `references/`-Dateien und der Skripte (validate.js, annotate.py, search.py, generate-plugins.sh).
- Verzeichnis-Sterne (nexscope 493) nicht am Repo bestätigt.
- Inhaltsqualität im Vergleich zu Impeccable nur auf Beschreibungsebene bewertet, nicht praktisch getestet.

## Quellen

- https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- https://github.com/vercel-labs/agent-skills
- https://github.com/mastepanoski/claude-skills
- https://github.com/EliaAlberti/ux-audit-skill
- https://github.com/wondelai/skills
- https://github.com/rolemodel/rolemodel-skills
- https://claudeskills.page/skills/design/ux-heuristics-review/
- https://www.skills.sh/hmtkyn/hydrogen-ecommerce-ux/hydrogen-ecommerce-ux
- https://claudemarketplaces.com/skills/nexscope-ai/ecommerce-skills/ecommerce-checkout-optimization
