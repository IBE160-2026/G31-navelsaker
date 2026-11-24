# AI-logg

Kuratert logg over vesentlige KI-prompter og beslutninger under utvikling, til bruk for sporbarhet (jf. sensorveiledningens kriterium "Prosess og KI-styring"). Dekker implementasjonsfasen (kode, tester). Planleggingsfasen (brief, PRD, arkitektur, stories) spores i egne BMAD-artefakter under `_bmad-output/` (bl.a. `.memlog.md`-filer per dokument).

## Når og hvordan logge

Legg til én ny oppføring under **Logg** etter en KI-sesjon som endrer kode, tester eller planleggingsdokumenter på en måte som er verdt å spore — ikke for trivielle rettelser (typo, formatering). Commit loggoppføringen sammen med (eller i samme PR som) endringen den beskriver, slik at git-historikken og loggen følger hverandre. Siden commits allerede får en `Co-Authored-By: Claude`-linje, gir git-loggen (`git log`) i tillegg en automatisk oversikt over hvilke commits som hadde KI-involvering.

**Format per oppføring:**

```
## YYYY-MM-DD — Kort tittel på hva som ble gjort

- **Hvorfor**: Hvilket behov, tilbakemelding eller krav som utløste dette.
- **Prompt(er)**: Kort sammendrag av hva som ble spurt om (ikke nødvendigvis ordrett — nok til å forstå hensikten).
- **Verktøy/modell**: Hvilket KI-verktøy og modell (f.eks. Claude Code, Sonnet 5).
- **Endringer**: Hvilke filer/moduler som ble endret.
- **Verifisering**: Hvordan output ble kvalitetssikret (kjørt mot fasit, test, manuell gjennomlesning, code review).
- **Commit**: Kort hash eller melding for commit(ene) endringen hører til (fylles inn etter commit).
```

## Logg

## 2026-11-24 — Avgrenset v1-omfang i product brief

- **Hvorfor**: Faglærers tilbakemelding (`_bmad-output/.../tilbakemelding-product-brief.md`) påpekte at v1 var for stort for ett semester/én person, at suksesskriteriene ikke var testbare, og at Supabase gjorde appen avhengig av ekstern konto.
- **Prompt(er)**: Oppsummer tilbakemeldingen → anbefal neste steg → skriv ny Omfang-seksjon (v1 = flernivå BOM + MRP for ett testfartøy, trinn 2 = sikkerhetslager) → oppdater resten av briefen til å stemme med det nye omfanget → forenkle BOM i v1 til fast struktur uten alternativregler, og rett emnekode IBE130 → IBE160.
- **Verktøy/modell**: Claude Code (Sonnet 5).
- **Endringer**: `_bmad-output/planning-artifacts/briefs/brief-Red Ball Express-2026-09-16/brief.md` (Sammendrag, Løsningen, Hva gjør dette annerledes, Hvem dette tjener, Suksesskriterier, Omfang, Visjon), `addendum.md` (modul-merking v1/trinn 2/utenfor v1, emnekode).
- **Verifisering**: Manuell gjennomlesning for konsistens mot ny Omfang-seksjon og mot faglærers tilbakemelding, punkt for punkt. Ingen automatisert test — dette er et planleggingsdokument, ikke kode.
- **Commit**: `378d919` — Avgrens v1-omfang i product brief til flernivå BOM + MRP

## 2026-11-24 — Testfartøy med håndregnet MRP-fasit

- **Hvorfor**: Suksesskriteriene i briefen (korrekt BOM-eksplosjon, bestillingsforslag og exception-meldinger, synlig forplantning) krever en konkret, håndregnet fasit som MRP-logikken kan testes mot. Dette sto som åpent punkt etter forrige økt.
- **Prompt(er)**: Lag et testfartøy med fast BOM på tre–fire nivåer (inkl. hovedmotor med lang ledetid) og en enkel MPS. Regn ut en komplett MRP-tabell for hånd (nettobehov, bestillingsforslag med ledetidsoffset, minst én exception). Dokumenter som fasit-fil med format og plassering valgt ut fra repoets struktur, og si fra om uklarheter i briefen.
- **Verktøy/modell**: Claude Code (Opus 5.5).
- **Endringer**: `testdata/testfartoy-v1/` (ny: `README.md` med konvensjoner R1–R10, BOM, MPS og beregning steg for steg for scenario A/B/C; `input.json`; `expected.json`). Lenker lagt til i `README.md` og i Omfang-seksjonen i `brief.md`.
- **Verifisering**: Håndregning vist steg for steg i fasiten. `expected.json` kryssjekket mot et uavhengig engangsskript (Node, ikke committet) som beregner MRP fra `input.json`: alle tre scenarier stemmer, og massebalansen går opp per vare. Skriptet ble selv testet ved å legge inn en bevisst feil i fasiten, som det fanget. Tabellene i README er gjengitt fra `expected.json`, slik at de ikke kan sprike fra JSON-en.
- **Commit**: `94a6c10` — Legg til testfartøy med håndregnet MRP-fasit for v1

## 2026-11-24 — PRD for v1, utvidet fasit (scenario D og E)

- **Hvorfor**: Neste BMAD-steg etter brief og fasit. PRD-en skulle avgjøre de åpne spørsmålene fra fasiten og gjøre akseptansekriteriene testbare mot den.
- **Prompt(er)**: Rett motoreksempelet i briefen → lag PRD med `bmad-prd` (rask vei). Brukeren ba om forslag med begrunnelse til ni beslutninger og godtok dem. Brukeren stilte så oppfølgingsspørsmål: når scenario D skal regnes ut (svar: nå), hvordan BOM kan justeres (variant b: mengde per, ledetid og partiregel, FR-18) og om teknologivalget bør utsettes (ja, til arkitekturen). Videre: hvor mange komponenter MRP-en håndterer (førte til en skalatest i NFR-3) og om 2-sekunderskravet var nødvendig (nei, fjernet). Til slutt avslutning med kvalitetssjekk.
- **Verktøy/modell**: Claude Code (Opus 5.5), BMAD-skill `bmad-prd`.
- **Endringer**: `_bmad-output/planning-artifacts/prds/prd-Red Ball Express-2026-11-24/` (`prd.md` med FR-1–FR-18, NFR-1–7, SM-1–4 og SM-C1–2; `addendum.md`; `.memlog.md` med alle beslutninger). `testdata/testfartoy-v1/` (regel R11, scenario D og E). Motoreksempelet i `brief.md` er rettet.
- **Verifisering**: Scenario D og E er regnet ut for hånd og kryssjekket mot det uavhengige kontrollskriptet (alle fem scenarier stemmer). Kontrollskriptet ble utvidet med R11 og BOM-overstyring. PRD-en er sjekket mot BMADs kvalitetsrubrikk. Det avdekket blant annet at FR-17 ikke definerte når et bestillingsforslag er «det samme» uten pegging, og det er rettet. KI-forslag som ble justert av brukeren: en BOM som bare kunne vises, ble til en BOM som kan justeres, og det faste 2-sekunderskravet ble fjernet.
- **Commit**: `7cb8d9a`, `f50d19f`, `ba85817`, pluss avslutnings-commiten som inneholder denne oppføringen.
