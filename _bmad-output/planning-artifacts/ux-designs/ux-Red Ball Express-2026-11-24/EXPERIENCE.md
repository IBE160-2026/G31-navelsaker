---
name: Red Ball Express
status: final
created: 2026-11-24
updated: 2026-11-24
sources:
  - ../../prds/prd-Red Ball Express-2026-11-24/prd.md
  - ../../architecture/architecture-Red Ball Express-2026-11-24/ARCHITECTURE-SPINE.md
  - ../../briefs/brief-Red Ball Express-2026-09-16/brief.md
  - ../../briefs/brief-Red Ball Express-2026-09-16/addendum.md
  - ../../briefs/brief-Red Ball Express-2026-09-16/tilbakemelding-product-brief.md
---

# Red Ball Express — opplevelsesspine

## Foundation

Webapp for PC, laget som én Vite + React-SPA med React Router ([arkitekturen](../../architecture/architecture-Red%20Ball%20Express-2026-11-24/ARCHITECTURE-SPINE.md), AD-11). Det finnes ett grensesnitt, én rolle (demobrukeren) og norsk UI-tekst. Det brukes ikke noe komponentbibliotek. Komponentene lages med egen CSS som bruker tokenene i [DESIGN.md](DESIGN.md) som CSS-variabler. DESIGN.md eier hvordan appen ser ut, og dette dokumentet eier hvordan den fungerer. Begge gjelder foran skissene ved konflikt. Samlet referanse: [mockups/key-screens.html](mockups/key-screens.html).

Begrepene følger PRD §3 (vare, bestillingsforslag, exception-melding, byggenummer, MRP-kjøring). I brukergrensesnittet heter en exception-melding **melding**.

## Information Architecture

| Side | Adresse | Nås fra | Formål | Krav |
| --- | --- | --- | --- | --- |
| Innlogging | `/logg-inn` | Alle sider uten innlogging | Logge inn | FR-1 |
| Startside | `/` | Etter innlogging, klikk på logoen | Rolig mellomledd: fire dører og én nøytral statuslinje. Ingen meldinger | — |
| Bestillingsforslag og meldinger | `/forslag` | Meny, dør | Meldinger og alle bestillingsforslag fra siste kjøring, med endringer | FR-13, FR-14, FR-16, FR-17 |
| MRP-tabell | `/mrp/:vare` (f.eks. `/mrp/PLT-900`) | Meny, dør, lenke på varenavn | MRP-tabellen for én vare, valgt i en vareliste | FR-15, FR-17 |
| BOM-tre | `/bom` | Meny, dør, lenke på varenavn | Produktstrukturen, med redigering av mengde per, ledetid og partiregel | FR-4, FR-18 |
| MPS og lager | `/plan` | Meny, dør | Hovedplan, åpne ordre og lagerbeholdning. Tilbakestilling | FR-3, FR-5–FR-8 |

- Menylinjen med de fire skjermbildene finnes på alle sider etter innlogging. Logoen fører til startsiden.
- **Varenavn er lenker** til varens MRP-tabell overalt der de står: i meldinger, forslag og BOM-treet (panelet har lenken «Vis MRP-tabell»).
- `/mrp` uten vare åpner den første varen i varelisten (RBE-000).
- Ingen modale vinduer oppå hverandre. Den eneste dialogen er bekreftelsen før tilbakestilling.

→ Navigasjonskart og alle sider: [mockups/key-screens.html](mockups/key-screens.html). Tidligere alternativer: [.working/wireframes-1.html](.working/wireframes-1.html).

## Endringer og fargebetydning

Dette avsnittet beskriver hvordan resultatet av en MRP-kjøring sammenlignes med forrige kjøring (FR-17), og hvordan fargene brukes. Det gjelder alle skjermbilder.

**Fargebetydning.** Se `DESIGN.md` → Colors.

| Signal | Farge | Hvor |
| --- | --- | --- |
| Krever oppmerksomhet | `{colors.danger}` | Forfalt bestilling (E2), forverret melding, valideringsfeil |
| Obs | `{colors.warning}` | Ledetid lengre enn horisont (E1) |
| Forbedring | `{colors.success}` | Forbedret melding, melding som har forsvunnet, «Lagret», «Testdata er lastet inn på nytt» |
| Nøytral endring | Ingen | Nye og fjernede bestillingsforslag, endrede celler, ikke-kjørte endringer |

**Bestillingsforslag.** Identiteten følger PRD FR-17: (vare, antall, mottaksuke, frigivelsesuke). Nye forslag får merkelappen «ny». Forslag som har forsvunnet, ligger bak lenken «Vis N forslag som er borte siden forrige kjøring», og vises da dempet og gjennomstreket med «borte».

**Meldinger: forverret og forbedret.** Meldinger med samme type og vare **pares** og vises som én melding:

- Har en vare flere meldinger av samme type i begge kjøringene, pares de i rekkefølge etter mottaksuke. De som blir til overs, er nye eller borte.
- For E2 avgjør `weeks_past_due` retningen. Høyere tall: «▲ Forverret: 9 → 11 uker» i rødt. Lavere tall: «▼ Forbedret: 11 → 9 uker» i grønt. Samme antall uker, men andre tall (antall eller mottaksuke): «Endret» uten farge, og meldingen beholder sin vanlige røde farge som forfalt.
- For E1 vises endret ledetid som «Endret: ledetid 20 → 22 uker». Meldingen beholder rav.
- En helt ny melding (uten par) vises med sin vanlige farge og merkelappen «ny».
- En melding uten par i ny kjøring (varen har ikke lenger en melding av den typen) vises i grønt under meldingene: «Løst: …». Den vises bare i denne visningen etter kjøringen.

Dette avviker fra PRD FR-17, der en melding med andre tallfelt regnes som ny + fjernet. Avviket er ført tilbake i PRD FR-17 og arkitekturens AD-6.

**Celler i MRP-tabellen.** Identitet (vare, felt, uke), der uke 0 er kolonnen «Før u1» (AD-6). En endret celle vises uthevet med prikket understrek, og verktøytipset viser «Forrige kjøring: 8». En endret celle får ingen farge.

**Første kjøring** etter tilbakestilling, eller uten tidligere kjøring, viser ingen markeringer.

## Voice and Tone

Du-form, kort og saklig, uten utropstegn og uten emoji. Vareteksten er alltid «navn (varenummer)» eller «varenummer navn». Uker skrives «uke 10» i setninger og «u10» i tabeller. Merkevarens stemme står i `DESIGN.md` → Brand & Style.

| Gjør | Ikke gjør |
| --- | --- |
| «Hva vil du gjøre?» | «Velkommen tilbake! Her er dagens oversikt 🚢» |
| «Hovedmotor (MOT-210) skulle vært bestilt for 11 uker siden. Bestilles den nå, kommer den tidligst i uke 21.» | «FEIL: MOT-210 forfalt −10» |
| «Lagerbeholdningen kan ikke være negativ.» | «Ugyldig input!» |
| «Feil brukernavn eller passord.» | «Passordet er feil.» (røper hva som var feil, FR-1) |
| «Ingen MRP-kjøring ennå. Trykk Kjør MRP for å beregne.» | «Ingen data å vise.» |
| «MRP er kjørt kl. 10:42. Se resultatet under Bestillingsforslag og meldinger.» | «Suksess! Beregningen er fullført.» |
| «Du har 1 endring som ikke er tatt med i MRP ennå.» | «Advarsel: utdaterte resultater» |

Meldingsteksten lages i frontend fra `type`, tallfeltene og varenavnet (arkitekturen, konvensjonen for meldingstekst). Valideringsmeldinger kommer fra backend (AD-7).

## Component Patterns

Hvordan komponentene oppfører seg. Utseendet står i `DESIGN.md` → Components.

| Komponent | Brukes på | Regler for oppførsel |
| --- | --- | --- |
| Menylinje | Alle sider etter innlogging | Fire lenker og «Logg ut». Valgt side er markert. Logoen fører til startsiden |
| Dør-kort | Startside | Hele kortet er én lenke til skjermbildet. Rekkefølge: forslag, MRP-tabell, BOM-tre, MPS og lager |
| Statuslinje | Startside, under sidetittel | Nøytral tekst om siste kjøring, uten antall og uten farge. Uten kjøring: «Ingen MRP-kjøring ennå.» |
| «Kjør MRP» | Bestillingsforslag og meldinger, MRP-tabell, MPS og lager, linjen om ikke-kjørte endringer | Vises bare der det er relevant (ikke i menyen, ikke på startsiden eller i BOM-treet utenom linjen). Ved trykk: «Kjører …» og deaktivert. Etterpå blir Ingrid værende på siden, innholdet oppdateres, og en nøytral bekreftelseslinje vises. **Hopper aldri automatisk til meldingene** |
| Meldingsseksjon | Bestillingsforslag og meldinger | Overskrift «Meldinger (N)» med «Skjul/Vis». **Åpen når siden åpnes.** Rekkefølge: røde, rav, grønne. Varenavn er lenker |
| Meldingskort | Meldingsseksjonen | Én melding per kort. Merkelapp etter signal (se Endringer og fargebetydning) |
| Forslagstabell | Bestillingsforslag og meldinger | Sortert på frigivelsesuke (forfalte først), deretter varenummer. Kolonner: endring, vare, type, antall, frigivelse, mottak. Forfalte forslag har den røde merkelappen «u−10 forfalt». Fjernede forslag ligger bak en lenke |
| Vareliste | MRP-tabell | Varer gruppert etter nivå (lavnivåkode), sortert på varenummer, med søkefelt øverst som filtrerer på nummer og navn. Valgt vare er markert, og adressen endres. Piltast opp/ned flytter valget når listen har fokus |
| MRP-tabell | MRP-tabell | Overskrift med vare, type, ledetid, partiregel og lavnivåkode. Rader: bruttobehov, åpne ordre, beregnet lager, nettobehov, planlagt mottak, planlagt frigivelse. Kolonner: «Før u1» og uke 1–16. Nuller vises som tom celle, unntatt i «beregnet lager». Forfalte frigivelser summeres i «Før u1». Endrede celler markeres. Avkrysningsboksen «Vis verdier fra forrige kjøring» over tabellen viser «24 ← 0» i endrede celler, så forrige verdi også kan nås uten mus. Tabellen ligger i et rulleområde som kan nås med tastatur |
| BOM-tre | BOM-tre | Alle 12 linjer. Varer med flere foreldre vises under hver forelder. Noder kan foldes inn og ut, og alt er utfoldet når siden åpnes. Hver node viser varenummer, navn, «× mengde per», type, ledetid og LLC (FR-4). Klikk eller Enter på en node åpner redigeringspanelet |
| Redigeringspanel | BOM-tre | Viser valgt vare og hvilken forelder den ble valgt under. Felt: mengde per (bare for denne BOM-linjen), ledetid, partiregel (L4L/FOQ) og kvantum (bare ved FOQ). Teksten «gjelder alle N steder varen brukes» står ved varedataene. «Lagre» og «Avbryt». Esc avbryter. Lenke «Vis MRP-tabell» |
| Radredigering | MPS og lager (alle tre tabeller) | «Endre» gjør raden om til felt med «Lagre» og «Avbryt». Én rad om gangen. Enter lagrer, Esc avbryter. «Slett» sletter etter en innebygd bekreftelse i raden («Slette byggenr. 2? Ja / Nei»). «+ Legg til …» legger til en tom rad i redigeringsmodus |
| Felt med validering | Panel, radredigering, innlogging | Validering i backend (AD-7). Feilmeldingen står under feltet, og feltet får rød kant. Ingenting lagres ved feil (FR-8). Fokus flyttes til første felt med feil |
| Linje om ikke-kjørte endringer | BOM-tre, MPS og lager | Vises etter en lagret endring som ikke er kjørt ennå: «Du har N endringer som ikke er tatt med i MRP ennå.» med en liten «Kjør MRP». Forsvinner etter kjøring. Ingen farge |
| Bekreftelseslinje | Etter lagring, kjøring og tilbakestilling | «✓ Lagret.» (grønn) og «✓ Testdata er lastet inn på nytt.» (grønn) forsvinner etter 5 sekunder. «MRP er kjørt kl. …» (nøytral) blir stående til neste handling. Leses opp av skjermleser |
| Bekreftelsesdialog | MPS og lager → «Tilbakestill til testdata …» | Forklarer hva som går tapt. «Avbryt» har fokus som standard. «Tilbakestill» er rød. Esc avbryter (FR-3) |

## State Patterns

| Tilstand | Side | Visning |
| --- | --- | --- |
| Ingen MRP-kjøring ennå | Forslag, MRP-tabell | Rolig tom tilstand: «Ingen MRP-kjøring ennå. Trykk Kjør MRP for å beregne.» med knappen. Startsidens statuslinje: «Ingen MRP-kjøring ennå.» |
| Første kjøring | Forslag, MRP-tabell | Resultatet vises uten markeringer |
| Kjøring pågår | Der «Kjør MRP» står | «Kjører …», deaktivert knapp, innholdet beholdes til resultatet er klart |
| Kjøring ferdig | Samme side | Innholdet oppdateres, og bekreftelseslinjen vises. Ikke-kjørt-linjen forsvinner |
| Ikke-kjørte endringer | BOM-tre, MPS og lager | Linjen om ikke-kjørte endringer. Resultatsidene viser fortsatt siste kjøring, med statuslinjen «Inndata er endret etter siste kjøring.» |
| Lagret | Panel, rad | Grønn «✓ Lagret.» og raden går tilbake til visning |
| Valideringsfeil | Panel, rad, innlogging | Rød kant og melding under feltet. Ingenting lagres |
| Ingen varer etter søk | Vareliste | «Ingen varer passer søket.» |
| Tom hovedplan | MPS og lager | «Ingen byggenummer i planen. MRP gir da ingen behov.» og «+ Legg til byggenummer» |
| Ingen åpne ordre | MPS og lager | «Ingen åpne ordre.» og «+ Legg til åpen ordre» |
| Ingen meldinger | Forslag | Seksjonen viser «Ingen meldinger fra siste kjøring.» (nøytral) |
| Ingen bestillingsforslag | Forslag | «Ingen bestillingsforslag fra siste kjøring.» (nøytral), for eksempel når hovedplanen er tom |
| Logger inn | Innlogging | Knappen viser «Logger inn …» og er deaktivert |
| Kjøring feilet | Der «Kjør MRP» står | Feillinjen vises, knappen blir aktiv igjen, og forrige resultat beholdes |
| Tilbakestilt | MPS og lager | Grønn bekreftelse. Kjøringene er slettet, så resultatsidene viser «Ingen MRP-kjøring ennå» |
| Lasting av side | Alle | Overskriften vises med en gang, og tabellene viser «Henter …» i dempet tekst. Ingen skjelettanimasjon |
| Serverfeil eller ingen kontakt | Alle | Rød linje øverst i innholdet: «Fikk ikke kontakt med serveren. Prøv igjen.» med «Prøv igjen». Det som ble skrevet i et skjema, beholdes |
| Utløpt sesjon (401) | Alle | Videresending til innlogging med nøytral tekst: «Du er logget ut. Logg inn igjen for å fortsette.» Etter innlogging kommer man tilbake til siden man var på |
| Ukjent vare i adressen | MRP-tabell | «Fant ikke varen XYZ.» og varelisten vises |

## Interaction Primitives

- **Eksplisitt framfor automatisk.** MRP kjøres bare når Ingrid trykker «Kjør MRP». Ingenting beregnes, oppdateres eller navigerer av seg selv.
- **Ingen tvang til å se meldinger.** Startsiden viser aldri innholdet i eller antallet meldinger, og ingen handling sender Ingrid til meldingene uten at hun selv klikker.
- **Lenker på varenavn** er den raske veien til en vares MRP-tabell.
- **Tastatur:** «Hopp til innhold» er første element med fokus. Tab følger leserekkefølgen. Enter aktiverer lenker og knapper og lagrer en rad eller et panel. Esc lukker panel, rad og dialog. Piltastene flytter i varelisten og BOM-treet.
- **Fokus ved navigasjon:** ved sidebytte settes dokumenttittelen (f.eks. «MRP-tabell: PLT-900 – Red Ball Express»), og fokus flyttes til H1.
- **Fokus ved redigering:** «Endre» og et klikk på en BOM-node flytter fokus til første felt. «Lagre» eller «Avbryt» gir fokus tilbake til utløseren (knappen «Endre» eller noden). Bekreftelsen i raden ved «Slett» har fokus på «Nei».
- **Mus:** klikk. Ingen dra-og-slipp og ingen funksjoner som bare finnes ved hover.
- **Ikke tillatt:** automatisk omberegning, automatisk navigasjon til meldinger, modaler oppå modaler, uendelig rulling, faner i MPS og lager.

## Accessibility Floor

Krav til oppførsel. Kontrast står i `DESIGN.md` → Colors (alle tekstpar minst 4,5:1).

- WCAG 2.2 AA som mål for hele appen (NFR-6).
- **Ingen betydning formidles bare med farge.** Rødt, rav og grønt har alltid tekst («Forfalt», «Obs», «▲ Forverret», «▼ Forbedret», «Løst»). Nøytrale endringer bruker tekst og form.
- Alle felt har synlig etikett knyttet til feltet. Feilmeldinger er koblet til feltet med `aria-describedby`, og feltet får `aria-invalid`.
- Synlig fokusramme i `{colors.accent}` på alle elementer som kan få fokus.
- Bekreftelseslinjer og «Kjører …» meldes med `aria-live="polite"`. Serverfeil meldes med `aria-live="assertive"`.
- Dialogen holder fokus inne i seg og gir fokus tilbake til knappen som åpnet den.
- BOM-treet bruker tre-semantikk (`role="tree"`/`treeitem`, `aria-expanded`). MRP-tabellen er en ekte `<table>` med rad- og kolonneoverskrifter (`<th scope>`).
- Endrede celler har skjult tekst for skjermleser, for eksempel «24, endret fra 0».
- Fotografiet er dekorativt (`alt=""`).
- «Hopp til innhold»-lenke (WCAG 2.4.1), unik dokumenttittel per side (2.4.2) og fokus til H1 ved sidebytte.
- Forrige verdi i endrede celler kan nås uten hover, via avkrysningsboksen «Vis verdier fra forrige kjøring» (1.4.13, 2.1.1).
- Rulleområdet rundt MRP-tabellen har `tabindex="0"`, `role="region"` og en etikett, så det kan rulles med tastatur.
- Klikkbare mål er minst 24 × 24 px (2.5.8). Kanter på felt og knapper har minst 3:1 kontrast (1.4.11).
- `lang="no"` på dokumentet.

## Responsive & Platform

| Bredde | Oppførsel |
| --- | --- |
| ≥ 1280 px | Målbredde. Alt vises som i skissene |
| 1024–1279 px | Samme layout. Varelisten og redigeringspanelet beholder bredden, og MRP-tabellen ruller sideveis inne i seg selv |
| < 1024 px | Ikke et mål (NFR-6). Siden kan brukes med rulling, men det er ikke optimalisert |

Bare PC-nettleser. Ingen mobilapp og ingen mørk modus i v1.

## Inspiration & Anti-patterns

- **Forkastet: dashbord med tall og varsler rett etter innlogging.** Det er overstimulerende. Startsiden er i stedet et rolig mellomledd.
- **Forkastet: farge på nøytrale endringer.** Farge er forbeholdt betydning.
- **Forkastet: automatisk hopp til meldinger etter «Kjør MRP».** Ingrid velger selv når hun ser varsler.
- **Forkastet: sidemeny (retning A) og tett regnearkstil (retning B).** C var mest oversiktlig.
- **Forkastet: serif-overskrifter.** Manrope gjennomgående gir et renere uttrykk.
- **Forkastet: faner i MPS og lager.** Tabellene er små, og faner kan skjule endringer før kjøring.
- **Forkastet: grønn aksentfarge.** Grønt betyr forbedring og kan ikke samtidig være pynt.
- Skisser fra prosessen: [.working/directions-3.html](.working/directions-3.html), [.working/logo-concepts-1.html](.working/logo-concepts-1.html), [.working/logo-concepts-2.html](.working/logo-concepts-2.html), [.working/font-pairs-1.html](.working/font-pairs-1.html), [.working/color-themes-1.html](.working/color-themes-1.html), [.working/color-themes-2.html](.working/color-themes-2.html), [.working/startside-hav-1.html](.working/startside-hav-1.html), [.working/startside-hav-2.html](.working/startside-hav-2.html). Det forkastede Lindesnes-bildet i den siste er fjernet fra repoet.

## Key Flows

### Flyt 1 — UJ-1. Ingrid framskynder byggenr. 2 og ser hva det koster

Ingrid Solheim, produksjonsplanlegger ved verftet. Salg har ringt: kunden vil ha byggenr. 2 i uke 14 i stedet for uke 16.

1. Ingrid logger inn og kommer til startsiden: havet, «Velkommen» og fire dører. Statuslinjen sier bare når siste kjøring var.
2. Hun velger døren **MPS og lager**.
3. I hovedplanen trykker hun «Endre» på byggenr. 2, endrer leveringsuke fra 16 til 14 og trykker Enter. «✓ Lagret.» vises, og linjen «Du har 1 endring som ikke er tatt med i MRP ennå» dukker opp.
4. Hun trykker «Kjør MRP». Knappen viser «Kjører …», og så: «MRP er kjørt kl. 10:42. Se resultatet under Bestillingsforslag og meldinger.» Hun blir værende på siden.
5. Når hun er klar, følger hun lenken til **Bestillingsforslag og meldinger**. Meldingene er åpne.
6. **Høydepunkt:** Øverst står hovedmotoren i rødt: «▲ Forverret: 9 → 11 uker». Under ligger forslagene. Forslagene for byggenr. 2 har «ny», for eksempel giret med frigivelse i uke 2 i stedet for uke 4. Forslagene for byggenr. 1 er umerket. Hun klikker på **PLT-900** og ser i MRP-tabellen at behovet fra seksjonene og styrehuset nå havner i samme uke, med uthevede celler. Nå vet hun hva hun skal si til motorleverandøren.

Feil: Hun skriver uke 18 ved et uhell. Feltet får rød kant og teksten «Uke må være mellom 1 og 16.», og ingenting lagres.

### Flyt 2 — UJ-2. Sensor prøver appen etter README

En sensor som ikke kjenner prosjektet, har startet appen etter README.

1. Sensor logger inn med demobrukeren. Et feil passord gir «Feil brukernavn eller passord.»
2. Startsiden viser fire dører. Sensor åpner **BOM-tre** og ser fire nivåer, med PLT-900 under tre foreldre.
3. Sensor går til **MPS og lager** og setter lagerbeholdningen for GIR-220 til 0. Etter «Lagret» trykker sensor «Kjør MRP».
4. I **Bestillingsforslag og meldinger** står en ny rød melding: giret skulle vært bestilt for 1 uke siden, med merkelappen «ny». Ingen andre varer har endringer.
5. Sensor prøver å sette lagerbeholdningen til −1 og får «Lagerbeholdningen kan ikke være negativ.» Ingenting lagres.
6. Sensor flytter byggenr. 1 til uke 4 og kjører MRP. Flere røde meldinger om forfalte produksjonsordrer dukker opp, og appen krasjer ikke.
7. **Høydepunkt:** Sensor trykker «Tilbakestill til testdata …», leser dialogen og bekrefter. «✓ Testdata er lastet inn på nytt.» Resultatsidene viser «Ingen MRP-kjøring ennå», og en ny kjøring gir tallene fra fasiten for scenario A, uten markeringer.

Feil: Serveren er stoppet. Rød linje: «Fikk ikke kontakt med serveren. Prøv igjen.» Det som ble skrevet, er beholdt.
