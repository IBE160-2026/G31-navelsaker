## Sesjonslogg

Når en oppgave eller økt avsluttes, før sluttoppsummeringen, bruk `sesjonslogg`-skillen: dokumenter Oppgave + Plan + Resultat + åpne punkter i `.logs/<bruker>/`, og før åpne punkter i `.logs/<bruker>/issues.md`. Skillen committer loggfila lokalt; push gjør du selv. Gruppens egne regler for commit og språk gjelder foran dette. På en story-branch committes sesjonsloggen bare én gang, i dokumentasjonscommiten (se «Commits»), ikke hver gang den oppdateres.

## AI-logg

Etter hver økt som endrer kode, tester eller planleggingsdokumenter, legg til en oppføring i [docs/ai-log.md](docs/ai-log.md) etter formatet som står der: hvorfor, prompter, verktøy/modell, endringer, verifisering og commit. Ta med konkrete eksempler der brukeren presiserte, avviste eller rettet KI-forslag. Hopp over trivielle rettelser (skrivefeil, formatering). Rekkefølge ved avslutning: commit av arbeidet → AI-logg og sesjonslogg → sluttoppsummering. På en story-branch er AI-logg og sesjonslogg samlet i dokumentasjonscommiten (se «Commits»).

## Refleksjonsnotater

- På slutten av hver økt som endret noe, ber Claude i sluttoppsummeringen brukeren om to–tre setninger om egne erfaringer: hva som fungerte og ikke fungerte med KI, hvor brukeren rettet eller avviste noe, og hva brukeren lærte.
- Svaret føres **ordrett** i [docs/refleksjonsnotater.md](docs/refleksjonsnotater.md) under datoen for økten det gjelder, med lenke til sesjonsloggen. Det committes sammen med dokumentasjonscommiten hvis den ikke er laget ennå, og ellers for seg. Svarer brukeren i neste økt, føres det inn da.
- Claude skriver aldri notater på vegne av brukeren og pynter ikke teksten. Hopper brukeren over, står det «(hoppet over)».

## Retrospektiv etter hver epic

- Når siste story i en epic er flettet og satt til `done`, kjøres `bmad-retrospective` for epicen før neste epic starter. Si fra til brukeren og foreslå det, ikke hopp over det i stillhet.
- Dokumentet lagres som `_bmad-output/implementation-artifacts/epic-<n>-retro-<dato>.md`. Tiltakene føres inn i `sprint-status.yaml` med skriptet til skillen, ikke for hånd.
- Ved start av en epic leses åpne tiltak fra forrige retrospektiv (`action_items` i sprintstatus). Tiltak som gjelder epicen, tas inn i specen for storyen de hører til. Retrospektiven for neste epic sjekker om de ble gjort.
- Retrospektiven får en oppføring i AI-loggen og en sesjonslogg, som annet arbeid.

## Commits

- Commit avgrensede endringer underveis, ikke alt i én stor commit til slutt. Hver commit skal gjelde én sak.
- Commit-meldinger skrives på norsk, i imperativ og beskrivende (f.eks. «Legg til netting og partiregel i MRP-kjernen»).
- Push bare når brukeren ber om det.
- **Fast mønster per story-PR, 4–5 commits** (innført etter retrospektiven av epic 1, der PR-ene hadde 8–14 commits, mest av like loggcommits):
  1. **Spec:** specen, sprintstatus `in-progress` for storyen og `done` for forrige story, hvis den ikke er satt ennå. For eksempel «Legg til spec for story 2.1».
  2. **Kode med tester,** 1–2 commits som viser til FR-nummeret, for eksempel «FR-5: beregn lavnivåkoder».
  3. **Retting etter gjennomgangen:** alle funn som rettes, i én commit, for eksempel «Rett funn fra gjennomgangen av story 2.1».
  4. **Dokumentasjon samlet:** AI-logg, sesjonslogg, triageloggen i specen, sprintstatus `review` og eventuelt refleksjonsnotat i én commit, for eksempel «Dokumenter story 2.1 i AI-logg og sesjonslogg».
- **All gjennomgang er ferdig før dokumentasjonscommiten,** også Thobias sin egen (innført etter Thobias sin observasjon i PR #13, der gjennomgangen etter dokumentasjonscommiten ga to commits til). Rekkefølgen: kode, kodegjennomgang og retting, så pusher Claude branchen og oppretter PR-en, så går Thobias gjennom den (`bmad-walkthrough`) og skriver observasjonen i PR-en. Rettinger fra Thobias sin gjennomgang går inn i rettingscommiten eller en commit rett etter. Dokumentasjonscommiten kommer til slutt, med AI-logg og sesjonslogg for hele storyen, også gjennomgangen.
- Status `done` etter flettingen blir ikke en egen commit på `main`. Den tas med i spec-commiten til neste story.
- Ikke slå sammen PR-er med «squash merge». Merge-commit beholder sporet fra spec via kode til retting.
- Endringer utenfor en story, som tiltak fra en retrospektiv, følger samme tanke: én commit per sak, og dokumentasjonen samlet i én commit til slutt.

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
