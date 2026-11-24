# Regel om skjermbilder og video

## 2026-11-24 kl. 11:57 — Thobias Navelsaker

### Oppgave
Brukeren ønsket en regel som minner om å ta skjermbilder og videoer til riktig tid, med henvisning til sensorveiledningen. Først spurte brukeren generelt hvordan regler som gjelder for hver økt redigeres (svar: `CLAUDE.md` i rota, eventuelt i undermapper, `~/.claude/CLAUDE.md` for personlige regler og hooks for håndheving).

### Plan
- Finne hva sensorveiledningen sier om skjermbilder og video: README med skjermbilde (kriterium 6), spor av designarbeid (kriterium 4), skjermbilder og video som reserve hvis appen ikke kjører (kapittel 3), og ingen store binærfiler (kriterium 7).
- Legge til seksjonen «Skjermbilder og video» i `CLAUDE.md` med fem konkrete tidspunkter, lagring i `docs/media/`, størrelsesgrenser og oppfølging som åpent punkt.
- Committe bare egne filer, siden arkitekturøkten jobbet parallelt i samme arbeidskopi.

### Resultat
- `CLAUDE.md` og `docs/ai-log.md` oppdatert, commits `d2c83cd` og en følgecommit med commit-referansen i AI-loggen. Ikke pushet.
- Sjekket før commit at arkitekturøkten ikke hadde ukommitterte endringer i de samme filene.

### Åpne punkter
- Ingen.
