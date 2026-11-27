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

## Skjermbilder og video

Sensor bruker skjermbilder og video i repoet som dokumentasjon av design og funksjonalitet, og som reserve hvis appen ikke lar seg kjøre. **Skjermbilder av appen skal vise den i en ekte nettleser i full skjerm**, ikke fra Edge uten vindu (`--headless`), som ikke gir et riktig bilde. Claude henter dem som bilder fra brukerens skjermopptak, eller ber brukeren ta et kort opptak. Nettleserrammen beskjæres bort, cursor fjernes, og bildet komprimeres før commit. Edge uten vindu kan fortsatt brukes til å teste i nettleseren og til skisser i HTML. **Video tar brukeren**, så Claude minner om den. Ved disse tidspunktene:

- **Et skjermbilde eller en brukerflyt virker for første gang**, f.eks. når en story med brukergrensesnitt er ferdig: skjermbilde.
- **UX-skisser eller wireframes er laget**: legg dem i repoet som spor av designarbeid.
- **En kjerneflyt fra PRD-en virker fra start til slutt**, f.eks. UJ-1 (flytt byggenr. 2, kjør MRP, se markerte endringer): kort video.
- **README oppdateres med beskrivelse av appen**: README skal ha minst ett skjermbilde.
- **Før innlevering**: oppdaterte skjermbilder av alle skjermbildene og én demovideo av hele kjerneflyten.

For video: si konkret hva som bør vises, og foreslå filnavn. Lagres i `docs/media/` med navn `YYYY-MM-DD-<hva>.png` eller `.mp4`. Videoer skal være korte (helst under 2 minutter) og komprimerte (helst under 10 MB). Større filer lenkes til i stedet for å committes, fordi sensor trekker for store binærfiler. Skjermbilder skal ikke vise hemmeligheter (demopassordet er greit). Er en påminnelse ikke fulgt opp, nevnes den i sluttoppsummeringen og som åpent punkt i sesjonsloggen.
