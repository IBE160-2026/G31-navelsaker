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
