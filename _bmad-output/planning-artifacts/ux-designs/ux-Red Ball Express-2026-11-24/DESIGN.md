---
name: Red Ball Express
description: Rolig, oversiktlig MRP-verktøy for produksjonsplanlegging ved verft. Egen CSS med tokens (CSS-variabler) i en Vite + React-SPA, uten komponentbibliotek.
status: final
created: 2026-11-24
updated: 2026-11-24
colors:
  background: '#FAF8F5'
  surface: '#FFFFFF'
  surface-muted: '#F6F3EE'
  border: '#ECE6DD'
  border-strong: '#8C857A'
  text: '#2B2A28'
  text-muted: '#6E6A63'
  accent: '#3F4A5A'
  accent-foreground: '#FFFFFF'
  accent-subtle: '#EEF0F3'
  brand-red: '#B5402F'
  danger: '#A8392B'
  danger-subtle: '#FBECE9'
  warning: '#8A5300'
  warning-subtle: '#FCF1DF'
  success: '#2E6B3A'
  success-subtle: '#E5F2E8'
typography:
  page-title:
    fontFamily: 'Manrope'
    fontSize: 22px
    fontWeight: '700'
    lineHeight: '1.25'
  welcome-title:
    fontFamily: 'Manrope'
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.25'
  section-title:
    fontFamily: 'Manrope'
    fontSize: 15px
    fontWeight: '700'
    lineHeight: '1.35'
  wordmark:
    fontFamily: 'Manrope'
    fontSize: 16px
    fontWeight: '700'
    lineHeight: '1.2'
  body:
    fontFamily: 'Manrope'
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  body-strong:
    fontFamily: 'Manrope'
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.5'
  small:
    fontFamily: 'Manrope'
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.45'
  label:
    fontFamily: 'Manrope'
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1.3'
  table-numeric:
    fontFamily: 'Manrope'
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 6px
  md: 10px
  lg: 12px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 20px
  '6': 24px
  '8': 32px
  page-gutter: 24px
  content-max: 1280px
components:
  top-nav:
    background: '{colors.background}'
    border-bottom: '{colors.border}'
    item-foreground: '{colors.text-muted}'
    item-active-foreground: '{colors.text}'
    item-active-indicator: '{colors.accent}'
  button-primary:
    background: '{colors.accent}'
    foreground: '{colors.accent-foreground}'
    radius: '{rounded.full}'
    typography: '{typography.body-strong}'
  button-secondary:
    background: 'transparent'
    foreground: '{colors.text}'
    border: '{colors.border-strong}'
    radius: '{rounded.full}'
  button-danger:
    background: '{colors.danger}'
    foreground: '{colors.accent-foreground}'
    radius: '{rounded.full}'
  card:
    background: '{colors.surface}'
    border: '{colors.border}'
    radius: '{rounded.md}'
    padding: '{spacing.3}'
  door-card:
    background: '{colors.surface}'
    border: '{colors.border}'
    border-focus: '{colors.accent}'
    radius: '{rounded.lg}'
    padding: '{spacing.4}'
  message-card-danger:
    background: '{colors.surface}'
    edge: '{colors.danger}'
    tag-background: '{colors.danger-subtle}'
    tag-foreground: '{colors.danger}'
  message-card-warning:
    background: '{colors.surface}'
    edge: '{colors.warning}'
    tag-background: '{colors.warning-subtle}'
    tag-foreground: '{colors.warning}'
  message-card-success:
    background: '{colors.surface}'
    edge: '{colors.success}'
    tag-background: '{colors.success-subtle}'
    tag-foreground: '{colors.success}'
  tag-past-due:
    background: '{colors.danger-subtle}'
    foreground: '{colors.danger}'
    radius: '{rounded.full}'
    typography: '{typography.label}'
  change-label:
    background: 'transparent'
    foreground: '{colors.text}'
    border: '{colors.text}'
    radius: '{rounded.full}'
    typography: '{typography.label}'
  changed-cell:
    foreground: '{colors.text}'
    fontWeight: '800'
    decoration: 'dotted underline'
  removed-row:
    foreground: '{colors.text-muted}'
    decoration: 'line-through'
  data-table:
    background: '{colors.surface}'
    border: '{colors.border}'
    header-foreground: '{colors.text-muted}'
    typography: '{typography.table-numeric}'
    before-week-1-background: '{colors.surface-muted}'
  list-item-selected:
    background: '{colors.accent-subtle}'
    indicator: '{colors.accent}'
  input:
    background: '{colors.surface}'
    border: '{colors.border-strong}'
    radius: '{rounded.sm}'
  input-error:
    border: '{colors.danger}'
    message-foreground: '{colors.danger}'
  pending-line:
    background: '{colors.surface}'
    border: 'dashed {colors.text-muted}'
    radius: '{rounded.md}'
  status-line:
    foreground: '{colors.text-muted}'
    typography: '{typography.small}'
  section-toggle:
    foreground: '{colors.accent}'
    typography: '{typography.small}'
  item-list:
    background: '{colors.surface}'
    border: '{colors.border}'
    radius: '{rounded.md}'
    group-label: '{colors.text-muted}'
  tree-node:
    foreground: '{colors.text}'
    meta-foreground: '{colors.text-muted}'
    indent: '{spacing.6}'
    divider: '{colors.surface-muted}'
  edit-panel:
    background: '{colors.surface}'
    border: '{colors.border}'
    radius: '{rounded.lg}'
    padding: '{spacing.4}'
  editing-row:
    background: '{colors.surface-muted}'
  empty-state:
    background: '{colors.surface}'
    border: '{colors.border}'
    radius: '{rounded.lg}'
    foreground: '{colors.text-muted}'
  error-banner:
    background: '{colors.danger-subtle}'
    foreground: '{colors.danger}'
    edge: '{colors.danger}'
    radius: '{rounded.md}'
  login-card:
    background: '{colors.surface}'
    border: '{colors.border}'
    radius: '{rounded.lg}'
  welcome-overlay:
    background: '{colors.background}'
    opacity: '0.94'
    radius: '{rounded.lg}'
  skip-link:
    background: '{colors.accent}'
    foreground: '{colors.accent-foreground}'
  checkbox:
    border: '{colors.border-strong}'
    checked: '{colors.accent}'
  confirmation-success:
    background: '{colors.success-subtle}'
    foreground: '{colors.success}'
    radius: '{rounded.md}'
  dialog:
    background: '{colors.surface}'
    border: '{colors.border}'
    radius: '{rounded.lg}'
  logo:
    loop: '{colors.accent}'
    ball: '{colors.brand-red}'
---

# Red Ball Express — designspine

## Brand & Style

Red Ball Express er et arbeidsverktøy for en produksjonsplanlegger ved et verft. Det skal føles rolig, rent og profesjonelt. Det skal være svært enkelt å finne fram, og ingen elementer skal kjempe om oppmerksomheten. Det viktigste prinsippet er å **unngå overstimulering**: planleggeren skal møte lite informasjon om gangen og selv velge når hun ser varsler.

**Synlig dataflyt** er et designprinsipp fra [brief-addendumet](../../briefs/brief-Red%20Ball%20Express-2026-09-16/addendum.md): det skal være tydelig hvordan en endring forplanter seg gjennom strukturen. Prinsippet oppfylles med endringsmarkering etter hver kjøring, lenker fra hvert varenavn til varens MRP-tabell, BOM-treet med lavnivåkoder og MRP-tabellen med alle rader. Det balanseres mot prinsippet om å unngå overstimulering: dataflyten er alltid tilgjengelig ett klikk unna, men den presses aldri på planleggeren.

**Farger har fast betydning.** Rødt betyr at noe krever oppmerksomhet, rav betyr obs, og grønt betyr forbedring. Det som er nøytralt, har ingen farge. Resten av flaten er varm off-white, hvitt og én dempet skiferfarge.

Navnet viser til konvoisystemet med lastebiler i Frankrike i 1944, der røde baller merket prioritert gods og en enveis rute. **Logoen** (variant 3c, «rund bane») er en kort, rund sløyfe i `{colors.accent}` med en rød ball (`{colors.brand-red}`) øverst til høyre, ved siden av ordmerket «Red Ball Express» i `{typography.wordmark}`. Logoen bruker enkle former og ingen militære emblemer. Den finnes liggende (menylinjen) og stablet (innlogging). → [logo-3c.svg](mockups/logo-3c.svg), [favicon.svg](mockups/favicon.svg).

Startsiden har et ekte fotografi av havet ved Stavanger (Oleksii Topolianskyi, Unsplash-lisens). → [imports/hav-stavanger-oleksii-topolianskyi.webp](imports/hav-stavanger-oleksii-topolianskyi.webp), kilde i [imports/KILDER.md](imports/KILDER.md).

Spinene (dette dokumentet og [EXPERIENCE.md](EXPERIENCE.md)) gjelder foran alle skisser ved konflikt. Samlet referanse: [mockups/key-screens.html](mockups/key-screens.html).

## Colors

| Token | Hex | Brukes til | Brukes ikke til |
| --- | --- | --- | --- |
| `background` | `#FAF8F5` | Sidebakgrunn, menylinje | Kort og tabeller |
| `surface` | `#FFFFFF` | Kort, tabeller, panel, dialog, felt | — |
| `surface-muted` | `#F6F3EE` | Kolonnen «Før u1» i MRP-tabellen, rad under redigering | Markering av endringer |
| `border` / `border-strong` | `#ECE6DD` / `#8C857A` | Linjer mellom rader og rundt kort / kant på felt, sekundærknapper og avkrysningsbokser (minst 3:1, WCAG 1.4.11) | `border` på felt (for svak) |
| `text` / `text-muted` | `#2B2A28` / `#6E6A63` | Tekst / hjelpetekst, kolonneoverskrifter, fjernede rader | — |
| `accent` | `#3F4A5A` | Primærknapp, valgt menypunkt, valgt rad/node, fokusramme, lenker, sløyfen i logoen | Status eller varsler. Aksenten betyr ingenting |
| `accent-subtle` | `#EEF0F3` | Bakgrunn på valgt vare i varelisten og valgt node i BOM-treet | — |
| `brand-red` | `#B5402F` | Bare ballen i logoen | Tekst, knapper, varsler |
| `danger` / `danger-subtle` | `#A8392B` / `#FBECE9` | **Krever oppmerksomhet:** forfalt bestilling (E2), forverret melding, valideringsfeil, knappen «Tilbakestill» i bekreftelsesdialogen | Pynt, nøytrale endringer |
| `warning` / `warning-subtle` | `#8A5300` / `#FCF1DF` | **Obs:** ledetid lengre enn horisont (E1) | Endringsmarkering |
| `success` / `success-subtle` | `#2E6B3A` / `#E5F2E8` | **Forbedring:** forbedret eller forsvunnet melding, «Lagret», «Testdata er lastet inn på nytt» | Knapper, navigasjon |

Nøytrale endringer (nye og fjernede bestillingsforslag, endrede tall i MRP-tabellen, «ikke kjørt ennå») har **ingen farge**. De vises med tekst og form i `{colors.text}` eller `{colors.text-muted}`.

Kontrast (WCAG 2.x, normal tekst ≥ 4,5:1), beregnet 2026-11-24: `text`, `text-muted` og `accent` mot `surface` og `background`, og `danger`, `warning` og `success` mot både `surface` og sin egen `*-subtle`-tone, er alle minst 4,5:1. `accent-foreground` på `accent` er minst 4,5:1. Kanter på grensesnittelementer (`border-strong`, fokusramme i `accent`) har minst 3:1 mot både `surface` og `background`. Fotografiet bærer aldri tekst direkte. Tekst over bildet står på en flate (`{colors.background}` med 94 % dekning).

Ingen mørk modus i v1.

## Typography

Én familie, **Manrope**, til alt: logo, overskrifter, brødtekst og tabeller. Den lastes ned som npm-pakke (`@fontsource/manrope`) og serveres lokalt, så appen ikke trenger nett ved kjøring (NFR-1). Vektene 400, 500, 600, 700 og 800 brukes.

| Rolle | Token | Brukes til |
| --- | --- | --- |
| Sidetittel | `{typography.page-title}` | H1 på hvert skjermbilde |
| Velkomst | `{typography.welcome-title}` | «Velkommen» på startsiden |
| Seksjon | `{typography.section-title}` | H3: «Meldinger», «Bestillingsforslag», tabelloverskrifter, kort-titler |
| Ordmerke | `{typography.wordmark}` | «Red Ball Express» i menylinjen |
| Brødtekst | `{typography.body}` / `{typography.body-strong}` | Tekst, tabellceller / varenummer, knapper, valgt meny |
| Liten | `{typography.small}` | Statuslinjer, hjelpetekst, varelisten |
| Merkelapp | `{typography.label}` | «ny», «borte», «Forfalt», «▲ Forverret …» |
| Tall i tabeller | `{typography.table-numeric}` | Alle tall i tabeller. **Alltid tabulære tall** (`font-variant-numeric: tabular-nums`), høyrejustert |

Ingen kursiv for betydning, ingen store bokstaver i overskrifter, ingen utropstegn.

## Layout & Spacing

Spacing-skala på 4 px: `{spacing.1}`–`{spacing.8}`. Sidemarg `{spacing.page-gutter}`. Innholdet er maks `{spacing.content-max}` bredt.

- **Menylinje øverst** (retning C): logo til venstre, de fire skjermbildene som tekstlenker, «demo · Logg ut» til høyre. Ingen sidemeny.
- **Ett hovedinnhold per side.** Tittel og eventuell «Kjør MRP» på samme linje øverst, med statuslinje under tittelen.
- **Luft framfor linjer.** Seksjoner skilles med avstand (`{spacing.6}`) og overskrift, ikke med tunge streker.
- **Startsiden:** fotografiet over hele bredden (340 px høyt), velkomstflaten oppå til venstre, og fire dør-kort i én rad som delvis ligger over bildet.
- **MRP-tabell:** vareliste (ca. 210 px) til venstre og tabellen til høyre.
- **BOM-tre:** treet til venstre og redigeringspanelet (ca. 320 px) til høyre.
- **MPS og lager:** én kolonne (maks ca. 820 px) med hovedplan, åpne ordre og lagerbeholdning under hverandre.
- **Bare PC.** Layouten er laget for en bredde på minst 1280 px og fungerer ned til 1024 px. Er det for smalt, ruller MRP-tabellen sideveis inne i seg selv. Mobil er ikke et mål (NFR-6).

## Elevation & Depth

Flatt. Dybde lages med `{colors.surface}` mot `{colors.background}` og tynne `{colors.border}`-linjer. Skygge brukes bare på dør-kortene på startsiden (svak, for å løfte dem over fotografiet) og på bekreftelsesdialogen.

## Shapes

`{rounded.sm}` (6 px) på felt. `{rounded.md}` (10 px) på kort, tabeller og linjer. `{rounded.lg}` (12 px) på dør-kort, panel og dialog. `{rounded.full}` på knapper og merkelapper. Runde, myke former samsvarer med den runde sløyfen i logoen.

## Components

- **Menylinje (`top-nav`).** Menypunkter i `{colors.text-muted}`. Valgt punkt i `{colors.text}`, med 2 px strek under i `{colors.accent}`.
- **Primærknapp (`button-primary`).** Fylt `{colors.accent}`, hvit tekst, pilleform. Brukes til «Kjør MRP», «Lagre» og «Logg inn». Høyst én per synlig område. Mens den arbeider: teksten «Kjører …» og deaktivert.
- **Sekundærknapp (`button-secondary`).** Gjennomsiktig med `{colors.border-strong}`-kant. Brukes til «Avbryt» og «Tilbakestill til testdata …».
- **Fareknapp (`button-danger`).** Fylt `{colors.danger}`. Bare i bekreftelsesdialogen for tilbakestilling.
- **Dør-kort (`door-card`).** Hvitt kort med tittel, én setning og «Åpne →» nederst til høyre. Hele kortet er klikkbart. Ved fokus eller hover: kant i `{colors.accent}` og en myk ring.
- **Meldingskort (`message-card-*`).** Hvitt kort med 4 px kant til venstre og en merkelapp i fargen til meldingens betydning: rød (forfalt, forverret), rav (obs) eller grønn (forbedret). Varenavnet er en lenke.
- **Merkelapper.** `tag-past-due`: rød pille med «u−10 forfalt». `change-label`: «ny» i tekstfarge med tynn kant og uten fyll.
- **Endret celle (`changed-cell`).** Tallet i vekt 800 med prikket understrek. Verdien fra forrige kjøring vises som verktøytips.
- **Fjernet rad (`removed-row`).** Dempet tekst, gjennomstreket, med merkelappen «borte».
- **Datatabell (`data-table`).** Hvit, med tynne radlinjer, dempede kolonneoverskrifter og tabulære tall. Kolonnen «Før u1» har `{colors.surface-muted}`.
- **Valgt rad eller node (`list-item-selected`).** `{colors.accent-subtle}` og 3 px strek til venstre i `{colors.accent}`.
- **Felt (`input`, `input-error`).** Etikett over feltet. Ved feil: 2 px kant i `{colors.danger}` og meldingen rett under i rødt.
- **Linje om ikke-kjørte endringer (`pending-line`).** Hvit med stiplet kant i `{colors.text-muted}` og en liten primærknapp «Kjør MRP». Ingen farge, fordi det ikke er et varsel.
- **Bekreftelseslinje (`confirmation-success`).** Grønn flate med «✓ …». Nøytrale bekreftelser, som «MRP er kjørt kl. 10:42», bruker et vanlig `card` uten farge.
- **Statuslinje (`status-line`).** Liten, dempet tekst under sidetittelen og på startsiden. Aldri farge.
- **Skjul/vis (`section-toggle`).** «Skjul» eller «Vis» i liten tekst i aksentfarge etter seksjonsoverskriften «Meldinger (N)».
- **Vareliste (`item-list`).** Hvitt kort med søkefelt (`input`) øverst. Gruppeoverskrifter «Nivå 0–3» i liten, dempet tekst med store bokstaver og litt sperring. Valgt vare bruker `list-item-selected`.
- **BOM-node (`tree-node`).** Én linje per node med innrykk `{spacing.6}` per nivå, en foldepil (▾/▸), varenummer i `{typography.body-strong}`, navn og «× mengde per», og metadata (type · LT · LLC) til høyre i dempet tekst. Tynn skillelinje i `{colors.surface-muted}`. Valgt node bruker `list-item-selected`.
- **Redigeringspanel (`edit-panel`).** Hvitt panel til høyre for treet. Tittel med varenummer og navn, og undertittel «Valgt under …». Feltene er gruppert i to `fieldset`: «Denne BOM-linjen» og «Varedata». Knappene «Lagre» og «Avbryt» nederst.
- **Rad under redigering (`editing-row`).** Raden får `{colors.surface-muted}`. Feltene er smale `input`-er med «Lagre» (liten primær) og «Avbryt» (liten sekundær) til høyre.
- **Tom tilstand (`empty-state`).** Hvitt kort med sentrert tekst: overskrift i `{typography.section-title}`, én setning i dempet tekst og eventuelt én primærknapp.
- **Feillinje (`error-banner`).** Rød flate med kant til venstre, øverst i innholdet. Tekst og knappen «Prøv igjen» (sekundær).
- **Innloggingskort (`login-card`).** Sentrert hvitt kort (ca. 320 px) med stablet logo, to felt, en primærknapp over hele bredden og hjelpeteksten «Demobrukeren står i README». Til høyre for etiketten «Passord» står tekstknappen «Vis passord» / «Skjul passord» i aksentfargen, så brukeren kan se det som er skrevet. Passordet skjules igjen når skjemaet sendes (lagt til etter ønske fra brukeren 2026-11-26).
- **Velkomstflate (`welcome-overlay`).** Lys flate oppå fotografiet, øverst til venstre, med «Velkommen» (`{typography.welcome-title}`) og «Hva vil du gjøre?».
- **Hopp til innhold (`skip-link`).** Usynlig til den får fokus. Vises da øverst til venstre i aksentfarge.
- **Avkrysningsboks (`checkbox`).** Native avkrysningsboks med kant i `{colors.border-strong}` og avkrysning i `{colors.accent}`. Brukes til «Vis verdier fra forrige kjøring» over MRP-tabellen. Påslått vises endrede celler som «24 ← 0», der forrige verdi står i dempet tekst.
- **Dialog (`dialog`).** Hvit, `{rounded.lg}`, skygge. Tittel, forklaring og knapper til høyre: «Avbryt» og så handlingen.
- **Logo (`logo`).** Se Brand & Style. På mørk eller fotografisk bakgrunn brukes den ikke. Logoen står bare i menylinjen og på innloggingssiden.

## Do's and Don'ts

| Gjør | Ikke gjør |
| --- | --- |
| Bruk rød, rav og grønn bare med sin faste betydning | Bruk farge som pynt eller for å skille nøytrale ting |
| Vis nøytrale endringer med tekst og form («ny», uthevet tall, gjennomstreking) | Farg nye forslag eller endrede celler |
| La aksenten (skifer) være den eneste fargen uten betydning | Innfør nye aksentfarger, eller bruk `brand-red` utenfor logoen |
| Hold én primærknapp per område | Stable flere fylte knapper ved siden av hverandre |
| Gjør alle klikkbare mål minst 24 × 24 px | Små knapper og lenker tett i tett |
| Bruk tabulære, høyrejusterte tall i alle tabeller | Proporsjonale tall i kolonner |
| Sett tekst over fotografiet på en lys flate | Legg tekst rett på bildet |
| Manrope til alt | Bland inn serif eller flere familier |
