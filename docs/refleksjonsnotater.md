# Refleksjonsnotater

Korte notater med mine egne erfaringer fra hver arbeidsøkt, som råstoff til refleksjonsrapporten (del 2). AI-loggen og sesjonsloggene sier *hva* som ble gjort. Disse notatene sier hva *jeg* tenkte om det.

Claude spør ved slutten av hver økt som endret noe, og fører svaret inn ordrett. Teksten pyntes ikke, og Claude skriver ikke notater på mine vegne. Hopper jeg over, står det «(hoppet over)».

Gode spørsmål å svare på (to–tre setninger holder):

- Hva fungerte godt med KI i dag, og hva fungerte dårlig?
- Hvor rettet, avviste eller presiserte jeg noe KI-en foreslo, og hvorfor?
- Hva lærte jeg, eller hva ville jeg gjort annerledes?

## Mal

```markdown
## YYYY-MM-DD — Hva økten gjaldt (lenke til sesjonslogg)

Mine ord, ordrett.
```

## Notater

## 2026-11-27 — Tilbakeblikk på epic 1 ([sesjonslogg](../.logs/thobias-navelsaker/984-2026-11-27-10-27-10-retro-epic-1.md))

KI rettet innlogginsfeil fra første demoversjon. Her kan du legge til hvordan du rettet det. Deretter la den til vis-passord-funksjon etter mitt ønske

> **Tillegg fra Claude, etter ønske (fakta fra loggene, ikke mine ord):** Feilen var «Fikk ikke kontakt med serveren. Prøv igjen.» da Thobias prøvde innloggingen fra story 1.5. Det var ingen feil i koden. Backend kjørte ikke, fordi `uv run fastapi dev` stoppes av en Windows-sperre på denne maskinen (`os error 5`, tilgang nektet til `fastapi.exe`). KI-en fant årsaken og startet backend med `uv run python -m fastapi dev src/rbe/main.py`, som går utenom sperren. Etter det virket innloggingen. I story 1.7 ble `python -m`-formen hovedkommandoen i README og i arkitekturen (AD-10 og AD-11), og en prøve fra en ny klone bekreftet valget. Se [AI-loggen](ai-log.md) under story 1.6 og 1.7. «Vis passord» ble lagt til på innloggingssiden etter Thobias sitt ønske (AI-loggen, 2026-11-26).

Jeg lot KI-en flette PR #4–#6 uten egen gjennomgang. Det var ikke planlagt som et eksperiment, men i ettertid ser jeg det som et. Hver PR var gått gjennom av tre KI-lag, og testene var grønne. Likevel fant retrospektiven 17 nye funn i grensene mellom stories. Ett av dem, at `get_session` ikke committer, ville gitt tap av data i epic 3. Feilene som faktisk ble synlige for en bruker, fant jeg selv da jeg prøvde appen. Lærdommen er at KI-gjennomgang per story ikke erstatter at et menneske prøver helheten.

*(Avsnittet over er formulert av Claude etter at jeg spurte om påstanden var gyldig, og jeg har godkjent det som mitt.)*

### Om økten

Jeg ble overrasket over hvor mye retrospektiven fant etter at alt var testet og så bra ut. Jeg har lært at jeg må prøve appen selv ofte og se på helheten, ikke bare stole på at KI-gjennomgangen tar alt.

### Læringspunkter fra retrospektiven av epic 1

Stikkordene er mine. Claude har skrevet forklaringene etter at jeg ba om det, og jeg har valgt punktene. Kilde: [retrospektiven av epic 1](../_bmad-output/implementation-artifacts/epic-1-retro-2026-11-27.md).

**Det jeg lærte:**

- **`get_session` lagrer ikke endringer.** Funksjonen gir hver API-rute en forbindelse til databasen. Den åpner forbindelsen, men gjør ingen commit, altså lagrer ikke endringene til slutt. Ennå finnes ingen rute som skriver data, så feilen har ikke merkes. Men den første ruten som gjør det, for eksempel kjøring av MRP eller endring av lager i epic 3 og 4, ville svart «OK» mens endringen forsvant. Hver story var gått gjennom og testet for seg selv. Feilen ligger likevel i grensen mellom story 1.4, som laget funksjonen, og en story som ennå ikke er skrevet. Derfor så ingen av gjennomgangene den. Den rettes før story 3.1. *Lærdom:* noen feil finnes bare når helheten ses under ett.

- **`/docs` var åpen uten innlogging, i strid med AD-8, og rutetesten oppdaget det ikke.** FastAPI lager automatisk sidene `/docs`, `/redoc` og `/openapi.json`, som viser hele API-et. Arkitekturen (AD-8) sier at bare helsesjekken og innloggingen skal være åpne. Vi hadde en test som skulle passe på det, men den så bare på ruter under `/api`. Sidene utenfor `/api` slapp derfor gjennom. Det er nå rettet: sidene er skrudd av, og testen fanger alle ruter utenfor `/api/`. Jeg sjekket at testen faktisk feiler hvis sidene slås på igjen. *Lærdom:* en test som består, beviser bare det den faktisk sjekker. Jeg må spørre hva testen *ikke* dekker.

- **PR #4–#6 ble flettet uten at jeg gikk gjennom dem, så feil gikk videre uten at jeg så dem. Det har jeg lært av.** Jeg stolte på at tre KI-gjennomganger og grønne tester var nok. Retrospektiven fant likevel 17 nye funn i koden fra epic 1. Det viktigste var `get_session`-feilen over. En menneskelig gjennomgang er ingen garanti for at alt blir funnet, men uten den er det ingen som ser helheten med egne øyne, og ingen spor av at jeg vurderte KI-arbeidet kritisk. *Tiltak:* fra epic 2 går jeg gjennom hver PR selv, med `bmad-walkthrough`, og skriver én egen observasjon i PR-en før den flettes.

- **PR-ene hadde for mange commits.** Regelen vår er 2–5 commits per PR, men PR #1–#7 hadde 8–14. Mye av det var like loggcommits (for eksempel tre med meldingen `Logg: story-1-4-innlogging-i-backend`), som ikke sier noe om hva som ble endret. Sensor leser commit-historikken og ser etter små, avgrensede commits med beskrivende meldinger. Støy gjør det vanskeligere å se de commitene som betyr noe. *Tiltak:* én loggcommit per story, og jeg sprer arbeidet over flere dager i stedet for å gjøre det meste på én dag.

- **Hvorfor det ble for mange commits, og hvordan vi unngår det.** Jeg spurte Claude hvordan vi kan unngå det. Svaret var å se på hvor commitene kom fra. I PR #4, med 11 commits, var bare rundt 3 kode. Resten var dokumentasjon delt opp i mange små commits:
  - Sesjonslogg-skillen committet hver gang loggen ble oppdatert, tre ganger i samme story.
  - AI-loggen ble committet for seg og så oppdatert igjen.
  - Statusen «done» og loggen fra forrige story ble med inn i neste PR som egne commits.

  Verktøyet gjorde det det var laget for, men ingen hadde sett på hva det ga i sum. Nå følger hver story et fast mønster med 4–5 commits: spec, kode med tester, retting etter gjennomgangen, og én samlet commit for dokumentasjonen. Mønsteret står i CLAUDE.md under «Commits», så det gjelder fra story 2.1. Vi valgte bort «squash merge», som slår alt sammen til én commit, fordi da forsvinner sporet av hvordan arbeidet gikk fram. *Lærdom:* når KI-verktøy jobber automatisk, må jeg av og til se på helheten de lager, ikke bare på hvert steg.

**Det som fungerte:**

- **Det jeg prøvde selv, fant det automatikken ikke fant.**
  - Da jeg skulle logge inn, fikk jeg «Fikk ikke kontakt med serveren». Årsaken var at backend ikke startet, fordi Windows sperret programmet (os error 5). Det førte til at README nå bruker kommandoer som virker også med sperren.
  - Jeg savnet en knapp for å vise passordet, og den ble lagt til.
  - Skjermbildene KI-en tok med en usynlig nettleser, viste tekst utenfor boksene. Jeg krevde bilder fra en ekte nettleser, og regelen er nå endret.

  Ingen av disse tingene ble fanget av testene eller KI-gjennomgangene, fordi de bare synes når et menneske faktisk bruker appen. *Lærdom:* KI kan teste koden, men jeg må teste opplevelsen.

## 2026-11-27 — Story 2.1: lavnivåkoder og resultatform ([sesjonslogg](../.logs/thobias-navelsaker/983-2026-11-27-12-12-26-story-2-1-lavnivakoder.md))

Gjennomgangen av specen før godkjenning fant 12 svakheter, som ble rettet før koden ble skrevet. Den alvorligste ville fått alle sammenligningene mot fasiten til å feile i neste story. Det viser verdien av å gjennomgå arbeidet hele veien, ikke bare koden til slutt.

*(Formulert av Claude etter mine stikkord «Gjennomgang av spec fant 12 svakheter som ble rettet (skriv bedre). Viser verdi av konstant gjennomgang», og jeg har godkjent det som mitt.)*

## 2026-11-27 — Story 2.2: bruttobehov, netting, partiregel og ledetidsoffset ([sesjonslogg](../.logs/thobias-navelsaker/982-2026-11-27-12-49-00-story-2-2-bruttobehov-netting.md))

I gjennomgangen av PR #11 fant jeg at det ikke var bestemt hvordan uke gjøres om til arrayindeks, og jeg ba om at story 2.2 tok det opp. Undersøkelsen før specen viste at fasiten ikke skiller åpne ordre i samme uke fra flere FOQ-partier, så en kjerne med feil i disse reglene ville bestått alle fasittestene. Det viser at jeg ikke kan stole blindt på at testene består.

Gjennomgangen av specen fant to feil før koden ble skrevet: en vakt som ikke kunne fått noen test til å feile, og en feilberegning av sikkerhetslageret. Begge ble funnet av KI, men bare fordi jeg ba om gjennomgangen i stedet for å godkjenne direkte. Det gjorde dem enkle å rette. Kodegjennomgangen fant etterpå to tilfeller som manglet test. Bruken av fem subagenter gjorde at arbeidet gikk raskere.

*(Formulert av Claude etter mine stikkord «Skriv bedre og før inn, og si fra dersom noe er feil. Jeg ba om en gjennomgang av uke -> indeks som jeg fant i PR # 11. En feil jeg ikke ville funnet selv. Undersøkelsen viste at fasiten ikke skiller åpne ordrer i samme uke og flere FOQ-partier. Viser viktigheten av at å ikke stole blindt på tester. Gjennomgang fant to feil KI ikke fanget opp: En test som ikke kunne vist feil, og feil beregning av sikkerhetslager. Alle feil ble funnet før koden ble skrevet, og kunne dermed rettes enkelt. Bruk av fem subagenter gjorde at det gikk raskere». Claude rettet tre punkter: jeg fant uke → indeks selv, begge feilene ble funnet av KI, og kodegjennomgangen fant to manglende tester etter at koden var skrevet.)*
