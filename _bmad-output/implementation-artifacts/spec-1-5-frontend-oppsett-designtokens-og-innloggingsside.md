---
title: 'Story 1.5: Frontend-oppsett, designtokens og innloggingsside'
type: 'feature'
created: '2026-11-26'
status: 'done'
baseline_commit: '702808aa9831665629661a88887b5eee9fb87bd7'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-Red Ball Express-2026-11-24/DESIGN.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Det finnes ingen frontend ennå. Sensor skal kunne åpne appen i nettleseren, bli sendt til innlogging og logge inn med demobrukeren mot API-et fra story 1.4 (FR-1, NFR-6, AD-11, UX-DR1, UX-DR2, UX-DR5, UX-DR20).

**Approach:** Lag `frontend/` fra Vite-malen `react-ts`, med Biome i stedet for ESLint, en Vite-proxy for `/api`, designtokens som CSS-variabler, Manrope lokalt, favicon og logo. Lag en fetch-klient, innloggingstilstand med ruteverneren og siden `/logg-inn` etter UX-DR5. Alle andre adresser er vernet og viser foreløpig en enkel side som story 1.6 bytter ut.

## Boundaries & Constraints

**Always:**
- Versjoner festes nøyaktig i `package.json` (uten `^`): `vite` 8.3.8, `react` og `react-dom` 19.3.1, `react-router` 8.5.2, `@biomejs/biome` 2.6.8 og `@fontsource/manrope` 5.3.0. `typescript` beholdes som `~7.0.2` fra malen. Løser ikke npm en versjon, stopp og før avviket.
- ESLint-filene og -pakkene fra malen fjernes. `biome.json` ligger i `frontend/`. `npm run check` kjører `biome check`.
- `vite.config.ts` sender `/api` til `http://127.0.0.1:8000`, så nettleseren ser ett opphav. Ingen CORS og ingen absolutte API-adresser i koden.
- `src/styles/tokens.css` har alle `colors`, `typography`, `rounded` og `spacing` fra frontmatter i DESIGN.md som CSS-variabler (`--color-accent`, `--font-size-body`, `--radius-md`, `--space-4` osv.), med kildehenvisning øverst. `src/styles/global.css` gir `body` bakgrunn, tekstfarge og Manrope, og gir alt som kan få fokus en synlig ramme i `--color-accent`. Komponentene bruker bare variablene, aldri hex-verdier.
- Manrope importeres fra `@fontsource/manrope` i vektene 400, 500, 600, 700 og 800, og hentes aldri fra nettet. `index.html` har `lang="no"` og favicon fra `mockups/favicon.svg`. Logoen er en React-komponent med innebygd SVG i to varianter, liggende (fra `logo-3c.svg`) og stablet (fra innloggingskortet i `mockups/key-screens.html`), så teksten får Manrope. Den har `role="img"` og `aria-label="Red Ball Express"`.
- `src/api/client.ts`: en `fetch`-innpakning med `credentials: "same-origin"` og JSON. Den kaster `ApiError` med status og `detail`, eller `NetworkError` når serveren ikke svarer (avvist fetch, eller status 502–504 fra proxyen). Et 401-svar på et annet kall enn login og me sender, når brukeren var innlogget, til `/logg-inn` med meldingen om utløpt sesjon.
- Innloggingstilstanden (`AuthProvider`) kaller `GET /api/auth/me` ved oppstart og viser «Henter …» til svaret kommer. Ruteverneren sender uinnloggede til `/logg-inn` og tar med adressen de ba om i routerens `state` (sti, søk og hash). Etter innlogging sendes brukeren dit, eller til `/` hvis adressen mangler. En innlogget bruker som åpner `/logg-inn`, sendes til `/`.
- Innloggingssiden (UX-DR5):
  - Kortet er sentrert og ca. 320 px bredt, med stablet logo og H1 «Logg inn». Feltene «Brukernavn» og «Passord» har synlig `<label>`, `autocomplete` (`username` og `current-password`) og autofokus på brukernavnet.
  - Primærknappen «Logg inn» går over hele bredden, og hjelpeteksten er «Demobrukeren står i README».
  - Mens den arbeider, viser knappen «Logger inn …» og er deaktivert (`aria-live="polite"`).
  - Dokumenttittelen er «Logg inn – Red Ball Express». Hele innloggingen kan gjøres med Tab og Enter (ett `<form>` med `onSubmit`). Feltene har ikke `required`, så nettleserens egne meldinger aldri vises.
- Meldinger på innloggingssiden:
  - 401 gir «Feil brukernavn eller passord.» i rødt under knappen. Meldingen er koblet til begge feltene med `aria-describedby`, feltene får `aria-invalid` og rød kant, og fokus settes på brukernavnet.
  - `NetworkError` og andre feil gir «Fikk ikke kontakt med serveren. Prøv igjen.» i en feillinje med `aria-live="assertive"`.
  - En utløpt sesjon gir den nøytrale linjen «Du er logget ut. Logg inn igjen for å fortsette.» øverst i kortet, uten farge.
  - Det som er skrevet i feltene, beholdes ved alle feil.
- Foreløpig vernet side for alle andre adresser: H1 «Du er logget inn» og teksten «Skjermbildene kommer i neste steg.», med dokumenttittelen «Red Ball Express». Story 1.6 bytter den ut med menylinjen, startsiden og plassholdersidene.
- All UI-tekst er norsk i du-form. Kode og filnavn er engelske, sider i `src/pages/` og komponenter i `src/components/`.

**Never:**
- Ingen komponentbibliotek, CSS-rammeverk, CSS-in-JS, Google Fonts eller CDN.
- Ingen menylinje, utlogging i UI, startside eller skip-lenke (story 1.6).
- Ingen token eller passord i `localStorage` eller `sessionStorage` (AD-8). Innloggingen er bare cookien.
- Ingen endring i `backend/` utover det som trengs for at proxyen virker (det skal ikke trengs noe).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Første besøk | Uinnlogget, åpner `/mrp?vare=MOT-210` | Sendes til `/logg-inn` uten melding. Etter innlogging står brukeren på `/mrp?vare=MOT-210` | – |
| Direkte på innlogging | Uinnlogget, åpner `/logg-inn` | Skjemaet vises. Etter innlogging står brukeren på `/` | – |
| Allerede innlogget | Gyldig cookie, åpner `/logg-inn` | Sendes til `/` | – |
| Feil passord | `demo`/`feil` | «Feil brukernavn eller passord.», `aria-invalid` på begge feltene, fokus på brukernavnet, og verdiene står | – |
| Arbeider | Knappen er trykket, og svaret er ikke kommet | «Logger inn …», knappen er deaktivert, og et nytt Enter gjør ingenting | – |
| Backend er nede | Vite kjører, men backend ikke | «Fikk ikke kontakt med serveren. Prøv igjen.», feltene beholdes, og knappen blir aktiv igjen | `NetworkError` |
| Utløpt sesjon | Innlogget, så et senere API-kall gir 401 | Sendes til `/logg-inn` med «Du er logget ut. Logg inn igjen for å fortsette.» og kommer tilbake etter innlogging | – |
| Oppstart, me nede | Backend svarer ikke på `me` | Innloggingssiden vises med serverfeilen | `NetworkError` |

</frozen-after-approval>

## Code Map

- `backend/src/rbe/api/auth.py` -- kontrakten: `POST /api/auth/login` tar `{username, password}` og gir `{username}` eller 401 med `detail` «Feil brukernavn eller passord.». `GET /api/auth/me` gir `{username}` eller 401 med «Du er ikke logget inn.». `POST /api/auth/logout` gir 204. Skal ikke endres.
- `backend/src/rbe/main.py` -- cookien `rbe_session` (httpOnly, SameSite=Lax, ikke Secure), så den virker over http via proxyen. Backend startes med `uv run python -m fastapi dev src/rbe/main.py` (port 8000) i `backend/`.
- `_bmad-output/planning-artifacts/ux-designs/ux-Red Ball Express-2026-11-24/DESIGN.md` -- frontmatter med tokens. Komponentene `login-card`, `button-primary`, `input`, `input-error` og `error-banner`.
- `…/ux-Red Ball Express-2026-11-24/EXPERIENCE.md` -- linje 124 (Logger inn), 128–129 (serverfeil, utløpt sesjon) og 143–157 (Accessibility Floor).
- `…/mockups/logo-3c.svg`, `favicon.svg` og `key-screens.html` linje 84–88 -- logoene. Det stablede SVG-et i innloggingskortet er kilden til den stablede varianten.
- `.gitignore` -- `node_modules/` og `dist/` er allerede ignorert.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/` -- lag fra `npm create vite@latest frontend -- --template react-ts`, fest versjonene, fjern ESLint og malens demoinnhold (`App.css`, `assets/react.svg`, `public/vite.svg`), og legg til `biome.json` og skriptet `check`
- [x] `frontend/vite.config.ts` -- proxyen for `/api`
- [x] `frontend/index.html`, `frontend/public/favicon.svg` -- `lang="no"`, favicon og tittelen «Red Ball Express»
- [x] `frontend/src/styles/tokens.css`, `global.css` og `src/main.tsx` -- tokens, grunnstil, Manrope-importene og routeren
- [x] `frontend/src/components/Logo.tsx` -- liggende og stablet variant
- [x] `frontend/src/api/client.ts` og `src/auth/AuthProvider.tsx` -- klienten, innloggingstilstanden, ruteverneren og håndteringen av utløpt sesjon
- [x] `frontend/src/pages/LoginPage.tsx` og `src/pages/SignedInPage.tsx` -- innloggingssiden og den foreløpige siden, og rutene i `src/App.tsx`
- [x] `docs/media/2026-11-26-innlogging.png` -- skjermbilde av `/logg-inn` med Edge uten vindu (1280 × 800), beskåret til innholdet og komprimert, mens backend og frontend kjører
- [x] `docs/ai-log.md` -- oppføring for story 1.5

**Commit-plan:** (1) Vite-oppsett med Biome, proxy, tokens, font, favicon og logo (UX-DR1, UX-DR2, AD-11), (2) klient, innloggingstilstand og innloggingsside (FR-1, UX-DR5, UX-DR20), (3) skjermbilde og AI-logg.

**Acceptance Criteria:**
- Given `frontend/`, when `npm run build` og `npx biome check` kjøres, then gir begge 0 feil.
- Given at backend og `npm run dev` kjører, when `curl -i http://localhost:5173/api/health` kjøres, then er svaret 200 med `{"status":"ok"}` gjennom proxyen.
- Given at backend og frontend kjører, when hver rad i I/O-matrisen prøves i nettleseren, then oppfører appen seg som beskrevet. Stegene og utfallene føres i Implementation Notes og i PR-beskrivelsen (manuell gjennomgang, som epics.md krever).

## Design Notes

Hvorfor adressen ligger i routerens `state` og ikke i et søkeparameter: `state` kan ikke brukes til å sende brukeren til et annet nettsted (åpen omdirigering), og det trengs ingen validering. Ulempen er at adressen glemmes hvis `/logg-inn` lastes inn på nytt. Da kommer brukeren til `/`, og det er akseptabelt.

Utløpt sesjon kontra første besøk: bare et 401-svar etter at `me` har bekreftet innloggingen, gir meldingen. Uinnlogget ved oppstart gir ingen melding.

## Verification

**Commands:**
- `npm run build` (i `frontend/`) -- expected: typesjekk og bygg uten feil
- `npx biome check` (i `frontend/`) -- expected: 0 feil
- `uv run python -m pytest` (i `backend/`) -- expected: fortsatt 107 tester som består

**Manual checks:**
- Radene i I/O-matrisen i nettleseren. Tastaturet: Tab mellom feltene og knappen, Enter sender skjemaet, og fokusrammen er synlig.

## Implementation Notes

**Avvik fra planen:**
- `create-vite` 9.4.0 lager ikke lenger ESLint i `react-ts`-malen, men oxlint (`.oxlintrc.json`, pakken `oxlint`, skriptet `lint`). Dette er fjernet i stedet, siden hensikten er Biome som eneste linter. Malens demoinnhold var også `src/index.css`, `src/assets/{hero.png,vite.svg}`, `public/icons.svg` og malens `README.md`, og alt dette er fjernet.
- Malen hadde `vite` `^8.4.0`. Den er festet til 8.3.8 etter specen. `@vitejs/plugin-react` 6.3.0 godtar `vite ^8.0.0`. Resten av utviklingspakkene er også festet nøyaktig (`@types/node` 26.6.11, `@types/react` 19.3.3, `@types/react-dom` 19.3.0, `@vitejs/plugin-react` 6.3.0). `typescript` står som `~7.0.2`.
- `biome.json` utelater `public/`, fordi `favicon.svg` er en uendret kopi fra mockups og Biome ellers krever `<title>` i SVG-en.
- «Henter …» vises av `AuthProvider` selv til `me` svarer, så verken skjemaet eller den vernede siden blinker forbi.
- Når backend er nede, svarer Vite-proxyen 502 (sjekket med curl), så det er denne grenen i `NetworkError` som slår til i praksis.

**Manuell gjennomgang (2026-11-26):** kjørt i Edge uten vindu, styrt over DevTools-protokollen med et skript i scratchpad, mot `fastapi dev` og `npm run dev`. Tastene er ekte tastetrykk (Tab, Enter) og tekst skrevet inn i feltet med fokus.

| Rad | Steg | Utfall |
|---|---|---|
| Første besøk | Uten cookie, åpne `/mrp?vare=MOT-210`, skriv demo, Tab, demo, Enter | Sendt til `/logg-inn` uten melding, autofokus på brukernavn, tittel «Logg inn – Red Ball Express». Etterpå på `/mrp?vare=MOT-210` med H1 «Du er logget inn» og tittel «Red Ball Express» |
| Direkte på innlogging | Uten cookie, åpne `/logg-inn` og logg inn | Står på `/` |
| Allerede innlogget | Innlogget, åpne `/logg-inn` | Sendt til `/` |
| Feil passord | `demo`/`feil` | Meldingen vises i rødt (`#A8392B`), begge feltene har `aria-invalid="true"`, `aria-describedby="login-error"` og rød kant, fokus på brukernavn, verdiene står, ingen `required` |
| Arbeider | Innloggingskallet holdes igjen med `Fetch.requestPaused`, så Enter i passordfeltet en gang til | «Logger inn …», deaktivert, `aria-live="polite"`, fortsatt bare ett kall. Innlogget når kallet slippes |
| Utløpt sesjon | Innlogget på `/bom?x=1#node`, logg ut i backend bak frontends rygg, så et kall gjennom `apiFetch` | 401, sendt til `/logg-inn` med «Du er logget ut. …» øverst i kortet i tekstfarge, tilbake på `/bom?x=1#node` etter innlogging, meldingen borte |
| Oppstart, me nede | Backend stoppet, åpne `/plan` | Sendt til `/logg-inn` med «Fikk ikke kontakt med serveren. Prøv igjen.» |
| Backend er nede | Backend stoppet, logg inn | Serverfeilen i feillinjen (`aria-live="assertive"`), feltene beholdt, knappen aktiv igjen |
| Tastatur | Tab fra brukernavn | Passord, så knappen, med fokusramme 2 px `#3F4A5A`. Ingenting i `localStorage`/`sessionStorage` |

Merk: i raden «Backend er nede» står serverfeilen allerede fra oppstarten (me feilet). Skjemaet tømmer feilen ved innsending og setter den på nytt, men skriptet kan ikke skille de to. Grenen der `fetch` selv avvises (ikke 502), er ikke prøvd i nettleseren.

**Etter gjennomgangen (`7d659c7`):** `vitest` 5.1.1 er lagt til med skriptet `npm run test`, og `src/api/client.test.ts` har 8 tester for grenene i `apiFetch` (502–504, avvist fetch, 401 på og utenfor `AUTH_PATHS`, liste-`detail`, tom 204). Testen for 504 feiler når sjekken smalnes til `<= 503`, og det er prøvd. Flyten for innlogging er utsatt til story 1.6 og testplanen (`deferred-work.md`).

## Spec Change Log

## Review Triage Log

Runde 1 (2026-11-26, lagene blind-hunter (BH), edge-case-hunter (ECH) og verification-gap (VG)). Rute: patch (P), defer (D) eller avvist (A).

| # | Lag | Funn | Vurdering | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | VG, BH | Grenene i `apiFetch` (502–504, avvist fetch, `AUTH_PATHS`, `detail`) har ingen automatisk test | medium | En smalere statussjekk eller en fjernet `catch` passerer build og Biome. Det er ren logikk, og arkitekturen tillater Vitest for slikt | P |
| 2 | VG | Flyten for innlogging (adressen i `state` og meldingen om utløpt sesjon) er bare prøvd manuelt | medium | Story 1.6 bygger om rutene. Arkitekturen holder komponent- og e2e-tester utenfor v1 og bruker den manuelle testplanen | D |
| 3 | BH | AI-loggen mangler hashen `f8c2c4b` og viser til en spec som ikke er committet | low | Rettes direkte ved avslutningen, og specen committes da | P (orkestrator) |
| 4 | ECH | 2xx med tom eller ugyldig kropp fra `me` eller login gir `user` lik `undefined` og «Henter …» for alltid | low | Backend gir alltid JSON på disse rutene, og proxyen dekker hele `/api`. Å vokte mot det krever nye grener | A |
| 5 | ECH | `response.text()` som feiler, gir `TypeError` og ikke `NetworkError` | false | Begge kallerne behandler alt som ikke er 401, som serverfeil, så utfallet er det samme | A |
| 6 | ECH | En adresse som begynner med `//`, gir en protokollrelativ `Navigate` etter innlogging | low | Krever at brukeren åpner en slik adresse. `replaceState` på tvers av opphav kaster, og sender ingen videre | A |
| 7 | ECH | `state.from` uten tekstfelt gir en ødelagt adresse | false | Bare `RequireAuth` skriver `state`, alltid med alle tre feltene | A |
| 8 | ECH | To innsendinger før `pending` er satt gir to kall | false | React 19 fullfører oppdateringene fra diskrete hendelser før neste hendelse. Den manuelle testen viste bare ett kall | A |
| 9 | ECH, BH | `AUTH_PATHS` sammenligner hele stien med søk | low | Ingen kaller bruker søk eller skråstrek til slutt på disse rutene | A |
| 10 | ECH | Feilen fra oppstarten vises ikke hvis `notice` endres etter at siden er montert | false | `notice` settes til `server-error` bare før siden monteres (`AuthLoading` vises til da) | A |
| 11 | ECH | `typescript` er `~7.0.2` og ikke nøyaktig festet | false | Specen sier at verdien fra malen beholdes. `package-lock.json` er committet | A |
| 12 | BH | Svar som 422 eller 500 gir «Fikk ikke kontakt med serveren.» | false | Specen fastsetter at `NetworkError` og andre feil gir denne meldingen. Login sender alltid tekst, så 422 oppstår ikke | A |
| 13 | BH | README nevner ikke demobrukeren eller oppstarten av frontend | low | README v1 er story 1.7, som har demopassordet og oppstarten (NFR-2) | A |
| 14 | BH | `vite preview` har ingen proxy | false | AD-11: ingen produksjonsbygg i sensorflyten | A |
| 15 | BH | Backendadressen i proxyen er hardkodet | false | AD-11 fastsetter lokal kjøring på denne adressen | A |
| 16 | BH | Logoen har hardkodet `fontSize` og ikke tokenet for ordmerket | low | Verdiene er SVG-enheter i `viewBox` fra skissen og skaleres med logoen. Tokenet gjelder tekst i menylinjen | A |
| 17 | BH | Manrope 500 og 800 lastes uten å brukes | false | DESIGN.md bruker vektene 400–800 (`changed-cell` er 800), og specen krever dem | A |
| 18 | BH | Kortet har fast bredde og flyter over på mobil | false | Mobil er ikke et mål (NFR-6, UX-DR22) | A |
| 19 | BH | `aria-live` på knappen er uvanlig, og meldingen om utløpt sesjon er ikke en live-region | low | Specen krever `aria-live="polite"` på knappen. Meldingen står allerede på siden når den lastes | A |
| 20 | BH | Ingen `engines` eller `.nvmrc` for Node 26 | low | Forutsetningen står i AD-11 og kommer i README i story 1.7 | A |
| 21 | BH | Auth-konteksten har ikke `logout` | false | Utlogging i brukergrensesnittet er story 1.6 (specens Never-liste) | A |
