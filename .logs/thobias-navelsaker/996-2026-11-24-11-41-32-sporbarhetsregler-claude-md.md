# Sporbarhetsregler i CLAUDE.md

## 2026-11-24 kl. 11:41 — Thobias Navelsaker

### Oppgave
Brukeren spurte om logging og sporbarhet skjer automatisk. Svaret var at bare sesjonsloggen (via CLAUDE.md), Co-Authored-By og BMADs .memlog gjør det, mens AI-logg, commits og FR-referanser avhenger av prompten. Brukeren ba om å gjøre disse til faste instrukser i CLAUDE.md.

### Plan
- Legge til tre seksjoner i CLAUDE.md: AI-logg (når og hva, rekkefølge ved avslutning), Commits (avgrensede, norske, imperative; push bare på forespørsel) og Sporbarhet fra krav til kode (FR-nummer i stories, tester, commits og PR-er; beregningstester mot fasitscenarioer; regler for endring av fasiten; avvik føres tilbake).
- Andre forslag (en Stop-hook som håndhever logging, og branch/PR per story i implementasjonen) ble presentert, men ikke valgt nå.

### Resultat
- CLAUDE.md oppdatert, commit `1f44523`. Oppføring i docs/ai-log.md, commit `e6fe098`. Ikke pushet.
- Lukket fra issues.md: «docs/ai-log.md må fylles videre» — dette er nå en fast instruks i CLAUDE.md.

### Åpne punkter
- Branch og pull request per story bør tas i bruk når implementasjonen starter (sensorkriterium 1, arbeidsflyt). Det er ikke lagt inn i CLAUDE.md ennå.
