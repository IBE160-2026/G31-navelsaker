---
title: 'Story 1.6: Menylinje og startside'
type: 'feature'
created: '2026-11-26'
status: 'done'
baseline_commit: '71673fa776ebc030c998782ea397f8e3be980e14'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Etter innlogging kommer man i dag til en foreløpig side uten navigasjon. Planleggeren skal komme til en rolig startside med fire dører og ha menylinjen med utlogging på alle sider, mens de fire skjermbildene står klare som plassholdere (UX-DR3, UX-DR4, UX-DR21, UX-DR22).

**Approach:** Lag et felles oppsett for alle vernede sider: «Hopp til innhold», menylinjen og `<main>`. Lag startsiden etter UX-DR4, plassholdersider for `/forslag`, `/mrp`, `/bom` og `/plan`, og en side for ukjent adresse. Legg `logout` til innloggingstilstanden, og la hver side sette dokumenttittelen og flytte fokus til H1 ved sidebytte.

## Boundaries & Constraints

**Always:**
- **Oppsett (`AppLayout`)** rundt alle vernede ruter:
  - Først kommer lenken «Hopp til innhold» (`skip-link`, usynlig til den får fokus) til `<main id="innhold" tabIndex={-1}>`.
  - Så menylinjen og innholdet. Innholdet er maks `--space-content-max` bredt med `--space-page-gutter` som sidemarg, og fungerer ned til 1024 px.
- **Menylinjen (UX-DR3, `top-nav`):**
  - Liggende logo som lenke til `/` (tilgjengelig navn «Red Ball Express, startside»).
  - Lenkene «Bestillingsforslag og meldinger» (`/forslag`), «MRP-tabell» (`/mrp`), «BOM-tre» (`/bom`) og «MPS og lager» (`/plan`) i en `<nav aria-label="Hovedmeny">`.
  - Til høyre brukernavnet fra innloggingstilstanden, « · » og knappen «Logg ut».
  - Valgt side har `aria-current="page"`, tekstfargen `--color-text` og en 2 px strek under i `--color-accent`. `/mrp/…` regnes som MRP-tabell.
  - Klikkmål er minst 24 × 24 px.
- **Utlogging:** `AuthProvider` får `logout()`, som kaller `POST /api/auth/logout`.
  - Ved 204 eller 401 settes brukeren til `null` uten melding, og man havner på `/logg-inn` uten adresse å komme tilbake til.
  - Ved `NetworkError` beholdes innloggingen, og «Fikk ikke kontakt med serveren. Prøv igjen.» vises som `error-banner` øverst i innholdet med `aria-live="assertive"`.
  - «Logg ut» er deaktivert mens kallet pågår.
- **Startsiden `/` (UX-DR4):**
  - Havfotoet `hav-stavanger-oleksii-topolianskyi.webp` (kopiert til `frontend/src/assets/`) går over hele vinduets bredde. Det er 340 px høyt, med `object-fit: cover` og `alt=""`.
  - Oppå bildet øverst til venstre ligger velkomstflaten (`welcome-overlay`, `--color-background` med 94 % dekning) med H1 «Velkommen» (`welcome-title`) og «Hva vil du gjøre?».
  - Under ligger fire dør-kort i én rad som delvis ligger over bildet. Hvert kort er én `<a>` med H2-tittel, én setning og «Åpne →», i denne rekkefølgen og med disse tekstene:
    1. «Bestillingsforslag og meldinger»: «Hva som bør bestilles eller startes, og hva som krever oppmerksomhet.»
    2. «MRP-tabell»: «Beregningen uke for uke for én vare.»
    3. «BOM-tre»: «Produktstrukturen for testfartøyet, med ledetider og mengder.»
    4. «MPS og lager»: «Hovedplanen, lagerbeholdning og åpne ordre. Her gjør du endringer.»
  - Ved fokus eller hover får kortet kant i aksentfargen og en myk ring. Svak skygge brukes bare her.
  - Under kortene står statuslinjen «Ingen MRP-kjøring ennå.» (`status-line`, uten farge og antall) og krediteringen «Foto: Oleksii Topolianskyi / Unsplash» i liten, dempet tekst.
  - Dokumenttittelen er «Velkommen – Red Ball Express».
- **Plassholdersidene:**
  - H1 og dokumenttittel er «Bestillingsforslag og meldinger», «MRP-tabell», «BOM-tre» og «MPS og lager», med « – Red Ball Express» etter tittelen.
  - Teksten er «Dette skjermbildet er ikke laget ennå.».
  - `/mrp/:vare` viser den samme MRP-plassholderen.
- **Ukjent adresse:** H1 «Fant ikke siden», en lenke «Til startsiden» og dokumenttittelen «Fant ikke siden – Red Ball Express».
- **Fokus og tittel (UX-DR21):** en felles komponent eller hook setter dokumenttittelen. Ved hvert sidebytte i appen flyttes fokus til sidens H1 (`tabIndex={-1}`). Det skjer ikke ved første lasting av dokumentet, så «Hopp til innhold» blir første Tab-stopp. Fokusrammen fra `global.css` gjelder.
- `SignedInPage.tsx` fjernes. `/logg-inn` og ruteverneren fra story 1.5 beholdes uendret.
- Alt bruker tokenene. UI-tekst er norsk i du-form, og det er ingen nye avhengigheter.

**Never:**
- Ingen meldinger, antall, farger eller data om kjøringer på startsiden (statuslinjen får ekte data i story 3.2).
- Ingen innhold i skjermbildene utover H1 og plassholderteksten. Ingen «Kjør MRP».
- Ingen endring i `backend/`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Startside | Innlogget, åpner `/` | Foto, velkomstflate, fire dører i fast rekkefølge, statuslinje og kreditering. Tittel «Velkommen – Red Ball Express» | – |
| Første Tab | Siden er nettopp lastet | Første fokus er «Hopp til innhold». Enter flytter fokus til `<main>` | – |
| Sidebytte | Klikk på «BOM-tre» i menyen eller på døren | `/bom`, H1 «BOM-tre» har fokus, tittelen er «BOM-tre – Red Ball Express», og menypunktet er markert | – |
| MRP med vare | Åpner `/mrp/PLT-900` | MRP-plassholderen, og «MRP-tabell» er markert | – |
| Ukjent adresse | Åpner `/finnes-ikke` | «Fant ikke siden» i oppsettet med menylinjen | – |
| Logg ut | Trykker «Logg ut» | På `/logg-inn` uten melding. `GET /api/auth/me` gir 401. Etter ny innlogging står man på `/` | – |
| Logg ut uten server | Backend er stoppet, trykker «Logg ut» | Fortsatt innlogget, og feillinjen vises øverst i innholdet | `NetworkError` |
| Innlogging på nytt (fra 1.5) | Uinnlogget, åpner `/plan?x=1#a` | Etter innlogging er man på `/plan?x=1#a` med menylinjen. En utløpt sesjon gir fortsatt meldingen fra 1.5 | – |

</frozen-after-approval>

## Code Map

- `frontend/src/App.tsx` -- rutene. `<RequireAuth>` står rundt `*` → `SignedInPage`. Bytt til `RequireAuth` → `AppLayout` med barnerutene `/`, `/forslag`, `/mrp`, `/mrp/:vare`, `/bom`, `/plan` og `*`.
- `frontend/src/auth/AuthProvider.tsx` -- `AuthContextValue` (`user`, `notice`, `login`). `logout` legges til her. `setUnauthorizedHandler` setter `expired` bare når brukeren var innlogget. Utlogging må ikke gi den meldingen: 401 på logout kaller handleren, så `logout` setter brukeren til `null` selv og tar hånd om 401.
- `frontend/src/api/client.ts` -- `apiFetch`, `ApiError` og `NetworkError`. Gjenbrukes uendret.
- `frontend/src/components/Logo.tsx` -- `variant="horizontal"`. Brukes i menylinjen.
- `frontend/src/styles/global.css` -- `.page`, `.button-primary`, `.error-banner` og `:focus-visible`. Felles stil (skip-link, top-nav) kan legges her eller i komponentenes egne CSS-filer, som `Logo.css`.
- `frontend/src/pages/LoginPage.tsx` -- mønsteret for `document.title`. Skal ikke endres.
- `_bmad-output/planning-artifacts/ux-designs/ux-Red Ball Express-2026-11-24/imports/hav-stavanger-oleksii-topolianskyi.webp` -- fotoet (270 KB). `mockups/key-screens.html` linje 35–38 og 65–68 har stilene for `.heroimg`, `.overlay`, `.lift`, `.door` og `.credit`.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/auth/AuthProvider.tsx` -- `logout()` som beskrevet
- [x] `frontend/src/components/AppLayout.tsx`, `TopNav.tsx` og stilene -- skip-lenken, menylinjen og `<main>` med feillinjen
- [x] `frontend/src/components/PageTitle.tsx` (eller en hook) -- tittel og fokus til H1 ved sidebytte
- [x] `frontend/src/pages/HomePage.tsx` og `.css`, `frontend/src/assets/hav-stavanger-oleksii-topolianskyi.webp` -- startsiden
- [x] `frontend/src/pages/PlaceholderPage.tsx` og `NotFoundPage.tsx` -- plassholdersidene og siden for ukjent adresse, og rutene i `App.tsx`. Fjern `SignedInPage.tsx`
- [x] `docs/media/2026-11-26-startside.png` -- skjermbilde av `/` innlogget, med Edge uten vindu (1280 × 800), beskåret og komprimert
- [x] `docs/ai-log.md` -- oppføring for story 1.6

**Commit-plan:** (1) utlogging, oppsett, menylinje og tittel/fokus (UX-DR3, UX-DR21, UX-DR22), (2) startside, plassholdersider og ukjent adresse (UX-DR4), (3) skjermbilde og AI-logg.

**Acceptance Criteria:**
- Given `frontend/`, when `npm run build`, `npx biome check` og `npm run test` kjøres, then gir alle 0 feil.
- Given at backend og frontend kjører, when hver rad i I/O-matrisen prøves i nettleseren med tastatur der det gjelder, then oppfører appen seg som beskrevet. Stegene og utfallene føres i Implementation Notes (manuell gjennomgang, som epics.md krever).

## Design Notes

Hvorfor utlogging uten server beholder innloggingen: cookien lever fortsatt på serveren. Hvis frontend bare glemte brukeren, ville en ny lasting av siden logge inn igjen uten at brukeren ba om det. Feillinjen er samme mønster som serverfeil ellers i appen (EXPERIENCE.md, «Serverfeil eller ingen kontakt»).

Fokus til H1 hoppes over ved første lasting, så skjermlesere og tastatur starter øverst med «Hopp til innhold». Når man havner på en side etter innlogging, er det et sidebytte i appen, og da flyttes fokus.

## Verification

**Commands:**
- `npm run build`, `npx biome check` og `npm run test` (i `frontend/`) -- expected: 0 feil
- `uv run python -m pytest` (i `backend/`) -- expected: 107 tester som består

**Manual checks:**
- Radene i I/O-matrisen i nettleseren ved 1280 og 1024 px bredde. Tab-rekkefølge: skip-lenken, logoen, de fire menylenkene, «Logg ut» og så innholdet.

## Implementation Notes

**Commits:** `593e95c` (utlogging, oppsett, menylinje, tittel/fokus), `ac5af66` (startside, plassholdere, ukjent adresse), `a27ce44` (skjermbilde og AI-logg). Commit 1 bygger alene: der står `SignedInPage` midlertidig bak `AppLayout`.

**Løsninger:**
- `logout()` setter en ref mens kallet pågår, så handleren for 401 ikke gir `expired`. Ved 204/401 settes notice `signed-out` og brukeren `null`. Andre feil kastes videre, og `AppLayout` viser feillinjen for alle feil (spesifisert bare for `NetworkError`; en 500 gir samme tekst).
- **Avvik:** `RequireAuth` sender til `/logg-inn` uten `state` når notice er `signed-out`. Grunn: React Router pakker navigasjon inn i `startTransition`, så `setUser(null)` blir tegnet før en navigasjon fra «Logg ut», og ruteverneren ville da lagt siden man logget ut fra i `state`. Uinnlogget tilgang og utløpt sesjon oppfører seg som i 1.5. `login` nullstiller notice.
- Første lasting skilles fra sidebytter med `navigation.ts`: `App` husker første `location.key`, og `PageTitle` flytter fokus bare når nøkkelen er en annen, eller når det allerede har vært et sidebytte. Tåler StrictModes doble effekter (enhetstest i `navigation.test.ts`).
- «Hopp til innhold» flytter fokus med `preventDefault`, så hashen ikke endres (det ville vært et sidebytte for routeren og flyttet fokus til H1).
- Skygge og 94 % dekning er laget med `color-mix()` på tokenene, ikke med nye fargeverdier.

**Manuell gjennomgang** (Edge uten vindu over DevTools-protokollen, backend på 8000, Vite på 5174, ekte Tab/Enter/museklikk; 32/32 sjekker OK):
- Rad 1: `/` har foto 1280 × 340 (`cover`, `alt=""`), velkomstflaten, dørene `/forslag,/mrp,/bom,/plan` i én rad med «Åpne →», statuslinjen og krediteringen, tittelen «Velkommen – Red Ball Express», og ingen horisontal rulling. OK.
- Rad 2: etter lasting har ingen element fokus. Første Tab gir «Hopp til innhold» (synlig), og Enter gir fokus på `#innhold`. OK.
- Tab-rekkefølge: skip-lenken, «Red Ball Express, startside», de fire menylenkene, «Logg ut», første dør. OK. Klikkmålene er minst 24 × 24 (minst er «Logg ut», 55 × 27).
- Rad 3: klikk på «BOM-tre» i menyen og på døren gir `/bom`, fokus på H1 «BOM-tre», riktig tittel og `aria-current` bare på BOM-tre, med 2 px strek i aksent og tekstfarge. Logoen gir `/` med fokus på H1. De andre plassholderne er også prøvd. OK.
- Rad 4: `/mrp/PLT-900` viser MRP-plassholderen med «MRP-tabell» markert. OK.
- Rad 5: `/finnes-ikke` viser «Fant ikke siden» med menylinjen, lenken «Til startsiden» og riktig tittel. OK.
- Rad 6: «Logg ut» gir `/logg-inn` uten melding, `GET /api/auth/me` gir 401, og ny innlogging går til `/`. Også prøvd med sesjonen allerede utlogget i backend (401 på logout): ingen «Du er logget ut». OK.
- Rad 7: logout-kallet avvist i nettleseren (`Fetch.failRequest`, samme `NetworkError` som stoppet backend): «Logg ut» er deaktivert mens kallet venter, deretter står man på `/bom`, innlogget, med feillinjen øverst i `<main>` i et område med `aria-live="assertive"`. OK. Backend ble ikke stoppet, fordi den som kjørte på 8000 ikke var startet av økten.
- Rad 8: uinnlogget `/plan?x=1#a` gir `/logg-inn`, og etter innlogging `/plan?x=1#a` med menylinjen og fokus på H1. OK. Meldingen om utløpt sesjon er ikke prøvd på nytt i nettleseren: ingen side gjør ennå data-kall som kan gi 401, og koden for den er uendret bortsett fra vakten under utlogging.
- 1024 px: ingen horisontal rulling, dørene i én rad, menylinjen på én linje (56 px høy). OK.
- Etter gjennomgangen (38/38 sjekker OK): utlogging fra `/bom` gir `/`, ikke `/bom`, etter ny innlogging. OK.
- Etter gjennomgangen: logger man ut og åpner `/plan?x=1` i samme fane, havner man på `/logg-inn`, og innloggingen går til `/plan?x=1`. Det samme gjelder tilbake-knappen etter utlogging (`/plan?x=1` → `/bom` → «Logg ut» → tilbake). Feillinjen fra rad 7 forsvinner ved sidebytte. OK.

## Spec Change Log

## Review Triage Log

Runde 1 (2026-11-26, lagene blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG)). Rute: patch (P), defer (D) eller avvist (A).

| # | Lag | Funn | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | BH, ECH | `notice = "signed-out"` nullstilles aldri, så en dyp lenke etter utlogging mister adressen | medium | Det er reelt: logger man ut og limer inn `/plan?x=1`, går innloggingen til `/`. Rettet med `clearSignedOut()` fra innloggingssiden | P |
| 2 | BH, ECH | Feillinjen etter mislykket utlogging følger med til andre sider | low | `AppLayout` står montert ved sidebytte. Nullstilles direkte på `location.key` | P |
| 3 | BH | Testnavnet viser bare til UX-DR21 | low | CLAUDE.md vil ha kravnummer. NFR-6 er lagt til | P |
| 4 | BH | AI-loggen mangler «Brukerens styring» og hashen for skjermbildet | low | Rettes ved avslutningen | P (orkestrator) |
| 5 | VG, BH | Utlogging, `RequireAuth` etter utlogging, fokus i `PageTitle` og rutene har ingen automatisk test | medium | Det krever et testmiljø for komponenter (jsdom), som repoet ikke har. Specen valgte manuell gjennomgang | D |
| 6 | BH, ECH, VG | `loggingOutRef` demper alle 401-svar mens utloggingen pågår | low | Det finnes ingen parallelle datakall ennå. Å begrense det krever et nytt valg i `apiFetch` | A |
| 7 | ECH | En annen feil enn 401 ved utlogging (f.eks. 500) gir «Fikk ikke kontakt med serveren.» | low | Samme valg som for innlogging i 1.5 (specen: «NetworkError og andre feil») | A |
| 8 | BH | `rememberInitialLocation` kalles i render med tilstand på modulnivå | low | Kallet setter verdien bare én gang og tåler StrictMode. Det er testet med enhetstest og i nettleseren | A |
| 9 | BH | Navnene på skjermbildene står tre steder (meny, dører, ruter) | low | Det ville krevd en felles rutetabell. Navnene er låst i specen og prøvd manuelt | A |
| 10 | BH | Specen og sprintstatusen er ikke committet | false | De committes ved avslutningen, med avviket i Implementation Notes | A |
| 11 | BH | `NotFoundPage` og MRP-plassholderen viser ikke adressen eller varen | false | Specen fastsetter innholdet. Varen kommer i story 3.4 | A |
