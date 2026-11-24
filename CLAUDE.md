## Sesjonslogg

Når en oppgave eller økt avsluttes, før sluttoppsummeringen, bruk `sesjonslogg`-skillen: dokumenter Oppgave + Plan + Resultat + åpne punkter i `.logs/<bruker>/`, og før åpne punkter i `.logs/<bruker>/issues.md`. Skillen committer loggfila lokalt; push gjør du selv. Gruppens egne regler for commit og språk gjelder foran dette.

## AI-logg

Etter hver økt som endrer kode, tester eller planleggingsdokumenter, legg til en oppføring i [docs/ai-log.md](docs/ai-log.md) etter formatet som står der: hvorfor, prompter, verktøy/modell, endringer, verifisering og commit. Ta med konkrete eksempler der brukeren presiserte, avviste eller rettet KI-forslag. Hopp over trivielle rettelser (skrivefeil, formatering). Rekkefølge ved avslutning: AI-logg → commit av arbeidet → sesjonslogg → sluttoppsummering.

## Commits

- Commit avgrensede endringer underveis, ikke alt i én stor commit til slutt. Hver commit skal gjelde én sak.
- Commit-meldinger skrives på norsk, i imperativ og beskrivende (f.eks. «Legg til netting og partiregel i MRP-kjernen»).
- Push bare når brukeren ber om det.

## Sporbarhet fra krav til kode

- Krav har faste nummer i PRD-en (`_bmad-output/planning-artifacts/prds/`): FR-n, NFR-n, SM-n. Bruk dem.
- Stories, tester, commit-meldinger og PR-beskrivelser viser til FR-nummeret de realiserer (f.eks. «FR-11: netting og partiregel»).
- Beregningstester leser fasiten i `testdata/testfartoy-v1/` direkte og oppgir hvilket scenario (A–E) de tester. Fasiten endres bare bevisst: `input.json`, `expected.json` og `README.md` oppdateres i samme commit, og endringen føres i AI-loggen.
- Avvik fra PRD eller arkitektur forklares der de oppstår (i commit eller PR) og føres tilbake i planleggingsdokumentet.
