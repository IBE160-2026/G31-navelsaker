# Testfartøy v1 — håndregnet MRP-fasit

Fasit for suksesskriteriene i [product brief](../../_bmad-output/planning-artifacts/briefs/brief-Red%20Ball%20Express-2026-09-16/brief.md) (v1: flernivå BOM + MRP). Et fast testfartøy med BOM på fire nivåer (0–3), en enkel MPS og en komplett, håndregnet MRP-tabell per vare og uke, med bestillingsforslag og exception-meldinger. Fem scenarier: basisplan (A), endret MPS (B), endret lagerstatus (C), forfalte produksjonsordrer (D) og endret BOM (E). B, C og E er grunnlaget for kriteriet om «synlig forplantning». Kravene i [PRD-en](../../_bmad-output/planning-artifacts/prds/prd-Red%20Ball%20Express-2026-11-24/prd.md) (FR-10 til FR-14) viser til scenarioene her.

Laget 2026-11-24. Fasiten endres bare bevisst: endres `input.json`, skal `expected.json` og dette dokumentet oppdateres i samme commit, og endringen føres i [docs/ai-log.md](../../docs/ai-log.md).

## Filer

| Fil | Innhold | Brukes til |
|---|---|---|
| [input.json](input.json) | Horisont, varestamme, BOM, MPS, lager, åpne ordre og scenario-overstyringer | Testinput og grunnlag for seed-data i den lokale databasen |
| [expected.json](expected.json) | Forventet resultat per scenario, vare og uke, pluss exception-meldinger | Testorakel (sammenlignes direkte i automatiske tester) |
| README.md | Beregningskonvensjoner og håndregningen steg for steg | Etterprøving og forklaring |

Mappa ligger i rota (`testdata/`) og ikke under `_bmad-output/`, fordi `_bmad-output/` inneholder genererte planleggingsdokumenter, mens dette er data som skal leses av kode — både backend-tester og seed-skript. Backendens mappestruktur er ikke bestemt ennå; tester kan referere hit med relativ sti.

### Bruk i automatiske tester

- Last `input.json`. For scenario B–E: ta utgangspunkt i A og bruk `override` — `mps` erstatter hele MPS-lista, `on_hand` overstyrer lagerbeholdning for de oppgitte varene, og `bom_qty` overstyrer mengde per på de oppgitte BOM-linjene.
- Sammenlign hele ukesarrayene (lengde 16, indeks 0 = uke 1) per vare og felt mot `expected.json`.
- `planned_order_releases` inneholder bare frigivelser innenfor horisonten. `planned_orders` er autoritativ og inneholder også forfalte frigivelser (`release_week < 1`).
- Sammenlign `exceptions` som en usortert mengde, på `type`, `item` og tallfeltene. Meldingsteksten i UI er fri og testes ikke.

## 1. Beregningskonvensjoner

Briefen angir ikke disse reglene. De er valgt her (standard lærebok-MRP), bekreftet i PRD-en, og må holde også i implementasjonen. Se også [Avklaringer](#12-avklaringer-og-forutsetninger).

| # | Regel |
|---|---|
| R1 | **Tidsbøtter**: hele uker, uke 1–16 (horisont H = 16). Uke 1 er første planuke (MRP kjøres ved starten av uke 1), ikke kalenderuke. |
| R2 | **Startlager og åpne ordre**: lagerbeholdning gjelder ved start av uke 1. Åpne ordre (allerede bestilt) kommer inn ved starten av sin uke og kan dekke behov samme uke. |
| R3 | **Bruttobehov**: nivå 0 får bruttobehov fra MPS. For øvrige varer: Σ over foreldre av (foreldrenes planlagte frigivelser i uke *t* × mengde per). Komponentene må være tilgjengelige den uka foreldreordren frigis (startes). |
| R4 | **Lavnivåkode (LLC)**: en vare planlegges én gang, etter alle foreldrene sine. LLC er det dypeste nivået varen forekommer på. PLT-900 forekommer både på nivå 2 og 3, og får LLC 3. |
| R5 | **Nettobehov**: NB<sub>t</sub> = max(0, BB<sub>t</sub> + SS − (BL<sub>t−1</sub> + ÅO<sub>t</sub>)), der SS (sikkerhetslager) = 0 i v1. |
| R6 | **Partistørrelse**: L4L (lot-for-lot): PM = NB. FOQ med kvantum Q: PM = minste multiplum av Q som er ≥ NB. Bare PLT-900 bruker FOQ (Q = 25). |
| R7 | **Beregnet lager** (slutten av uka): BL<sub>t</sub> = BL<sub>t−1</sub> + ÅO<sub>t</sub> + PM<sub>t</sub> − BB<sub>t</sub>. |
| R8 | **Ledetidsoffset**: frigivelsesuke = mottaksuke − ledetid (hele uker, ingen kalender eller ferie). |
| R9 | **Forfalt frigivelse**: gir R8 en frigivelsesuke < 1, beholdes ordren med beregnet (fortidig) frigivelsesuke i `planned_orders`. Den kommer ikke med i PF-raden innenfor horisonten, og den gir exception E2. MRP flytter ikke mottaksuka. |
| R11 | **Barn av forfalte produksjonsordrer** (PRD FR-12): får en produksjonsvare et bestillingsforslag med frigivelsesuke < 1, legges barnas bruttobehov fra det forslaget (antall × mengde per) i uke 1. Regelen gjelder i alle ledd nedover. Testes i scenario D. |
| R10 | **Åpne ordre flyttes ikke** av MRP. Det gis ingen meldinger om å framskynde, utsette eller kansellere i v1. |

**Exception-typer:**

| Kode | Navn | Utløses når | Felter |
|---|---|---|---|
| E1 `LEAD_TIME_EXCEEDS_HORIZON` | Ledetid lengre enn horisont | Varen har bruttobehov i horisonten og ledetid > H. Én melding per vare. | `lead_time_weeks`, `horizon_weeks` |
| E2 `PAST_DUE_RELEASE` | Forfalt frigivelse | En planlagt ordre har frigivelsesuke < 1 | `weeks_past_due` = 1 − frigivelsesuke; `earliest_receipt_week` = 1 + ledetid (tidligste mottak hvis ordren legges i uke 1). Forsinkelse mot behovsuka = `earliest_receipt_week` − `receipt_week` = `weeks_past_due`. |

**Forkortelser i MRP-tabellene:**

| Rad | Betydning | JSON-felt |
|---|---|---|
| BB | Bruttobehov | `gross_requirements` |
| ÅO | Åpne ordre (planlagt mottak på allerede bestilte ordre) | `scheduled_receipts` |
| BL | Beregnet lager ved slutten av uka | `projected_on_hand` |
| NB | Nettobehov | `net_requirements` |
| PM | Planlagt ordremottak (bestillingsforslagets mottak) | `planned_order_receipts` |
| PF | Planlagt ordrefrigivelse (når forslaget må bestilles/startes) | `planned_order_releases` |

Kolonnen **Før u1** viser lagerbeholdning ved horisontstart (rad BL) og forfalte frigivelser som *antall (u beregnet uke)* (rad PF). Tomme celler betyr 0.

## 2. Varestamme

| Vare | Navn | Type | Ledetid (uker) | Lager før u1 | Partiregel | Åpne ordre | LLC |
|---|---|---|---:|---:|---|---|---:|
| RBE-000 | Testfartøy RBE Service 15 (komplett fartøy) | Produksjon | 2 | 0 | L4L | – | 0 |
| SKR-100 | Skrog, sammenstilt | Produksjon | 3 | 0 | L4L | – | 1 |
| MAS-200 | Maskinpakke, installert | Produksjon | 2 | 0 | L4L | – | 1 |
| DEK-300 | Dekk og overbygg | Produksjon | 2 | 0 | L4L | – | 1 |
| SEK-110 | Skrogseksjon (blokk) | Produksjon | 2 | 1 | L4L | – | 2 |
| MOT-210 | Hovedmotor (import) | Innkjøp | **20** | 0 | L4L | 1 stk uke 7 (byggenr. 1) | 2 |
| GIR-220 | Gir og propellanlegg | Innkjøp | 8 | 1 | L4L | – | 2 |
| STY-310 | Styrehus | Produksjon | 2 | 0 | L4L | – | 2 |
| PLT-900 | Stålplate 8 mm, 2000×6000 | Innkjøp | 3 | 20 | FOQ 25 | – | 3 |
| PRF-910 | Profil/spant, 6 m | Innkjøp | 2 | 15 | L4L | 20 stk uke 4 | 3 |
| VIN-920 | Vinduspakke styrehus | Innkjøp | 6 | 0 | L4L | – | 3 |

Sikkerhetslager er 0 for alle varer (sikkerhetslager kommer i trinn 2). Feltet `safety_stock` finnes likevel i `input.json`, slik at datamodellen er klar for det.

## 3. BOM (fast struktur, fire nivåer)

```
Nivå 0      Nivå 1                 Nivå 2                          Nivå 3
RBE-000 Testfartøy
├─ 1 × SKR-100 Skrog
│      └─ 4 × SEK-110 Skrogseksjon
│                 ├─ 6 × PLT-900 Stålplate
│                 └─ 10 × PRF-910 Profil
├─ 1 × MAS-200 Maskinpakke
│      ├─ 1 × MOT-210 Hovedmotor (import, LT 20)
│      └─ 1 × GIR-220 Gir og propellanlegg
└─ 1 × DEK-300 Dekk og overbygg
       ├─ 1 × STY-310 Styrehus
       │          ├─ 4 × PLT-900 Stålplate
       │          └─ 1 × VIN-920 Vinduspakke
       └─ 8 × PLT-900 Stålplate          ← samme vare på nivå 2 og 3 (tester LLC)
```

Det strukturen tester:

- **Felles komponent på flere nivåer**: PLT-900 får behov fra tre foreldre (SEK-110, STY-310 og DEK-300) på to nivåer. Behovene må summeres per uke, og PLT-900 kan først planlegges når alle tre er planlagt (R4).
- **Mengde per > 1**: 4 seksjoner per skrog, og 6/10/4/8 deler per forelder.
- **Lager på mellomnivå**: én ferdig skrogseksjon på lager reduserer behovet for plater og profiler.
- **Kumulativ ledetid**: RBE-000 → MAS-200 → MOT-210 = 2 + 2 + 20 = **24 uker** (kritisk vei). Til sammenligning: via SKR-100 → SEK-110 → PLT-900 = 2 + 3 + 2 + 3 = 10 uker, og via DEK-300 → STY-310 → VIN-920 = 2 + 2 + 2 + 6 = 12 uker.

**Totalbehov per fartøy** (BOM-eksplosjon uten tid og lager): SKR, MAS, DEK, MOT, GIR, STY, VIN 1 stk hver; SEK-110 4; PLT-900 4·6 + 4 + 8 = 36; PRF-910 4·10 = 40.

## 4. MPS (hovedproduksjonsplan)

To søsterfartøy av samme type (samme BOM):

| Byggenr. | Vare | Ferdig uke (A) | Ferdig uke (B) | Antall |
|---|---|---:|---:|---:|
| 1 | RBE-000 | 12 | 12 | 1 |
| 2 | RBE-000 | 16 | **14** | 1 |

## 5. MRP-beregning — scenario A (basisplan)

Varene beregnes i LLC-rekkefølge (0 → 3). Hver tabell følges av utregningen for ukene der noe skjer.

### LLC 0

| **RBE-000** Testfartøy RBE Service 15 (komplett fartøy) · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |
| PM |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |
| PF |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |

- BB fra MPS: uke 12 og 16, 1 stk hver. Startlager 0 → NB = BB → PM = NB (L4L).
- PF = 12 − 2 = **uke 10** og 16 − 2 = **uke 14**.

### LLC 1

| **SKR-100** Skrog, sammenstilt · LT 3 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |
| PM |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |
| PF |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |  |

| **MAS-200** Maskinpakke, installert · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |
| PM |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |
| PF |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |

| **DEK-300** Dekk og overbygg · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |
| PM |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |
| PF |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |

- BB for alle tre = PF(RBE-000) × 1 = uke 10 og 14. Lager 0 → NB = PM = BB.
- SKR-100 (LT 3): PF = 10 − 3 = **7** og 14 − 3 = **11**.
- MAS-200 og DEK-300 (LT 2): PF = **8** og **12**.

### LLC 2

| **SEK-110** Skrogseksjon (blokk) · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  | 4 |  |  |  | 4 |  |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  | 3 |  |  |  | 4 |  |  |  |  |  |
| PM |  |  |  |  |  |  |  | 3 |  |  |  | 4 |  |  |  |  |  |
| PF |  |  |  |  |  | 3 |  |  |  | 4 |  |  |  |  |  |  |  |

- BB = PF(SKR-100) × 4 = uke 7: 4, uke 11: 4.
- Uke 7: tilgjengelig = 1 (lager) + 0 = 1 → NB = 4 − 1 = **3** → PM 3 → BL = 1 + 3 − 4 = 0.
- Uke 11: tilgjengelig 0 → NB = **4**.
- PF = 7 − 2 = **uke 5 (3 stk)** og 11 − 2 = **uke 9 (4 stk)**.

| **MOT-210** Hovedmotor (import) · LT 20 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |
| PM |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |
| PF | **1 (u-8)** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

- BB = PF(MAS-200) × 1 = uke 8: 1, uke 12: 1.
- Uke 7: åpen ordre 1 → BL = 0 + 1 − 0 = 1.
- Uke 8: tilgjengelig 1, BB 1 → NB 0 → BL 0. Byggenr. 1 er dekket av den åpne ordren.
- Uke 12: tilgjengelig 0 → NB **1** → PM 1 → frigivelse 12 − 20 = **uke −8**. Den er forfalt med 1 − (−8) = 9 uker (**E2**). I tillegg er ledetiden 20 > H = 16 (**E1**).

| **GIR-220** Gir og propellanlegg · LT 8 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |
| PM |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |
| PF |  |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |

- BB = PF(MAS-200) × 1 = uke 8 og 12. Lager 1 dekker uke 8 → BL 0.
- Uke 12: NB **1** → PF = 12 − 8 = **uke 4**.

| **STY-310** Styrehus · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |
| PM |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |
| PF |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |  |  |

- BB = PF(DEK-300) × 1 = uke 8 og 12. Lager 0 → PF = **6** og **10**.

### LLC 3

**PLT-900 — sammensetning av bruttobehov** (tre foreldre på to nivåer):

| Forelder | Mengde per | Foreldrenes PF | Bidrag til BB |
|---|---:|---|---|
| SEK-110 (nivå 2) | 6 | u5: 3, u9: 4 | u5: 18, u9: 24 |
| STY-310 (nivå 2) | 4 | u6: 1, u10: 1 | u6: 4, u10: 4 |
| DEK-300 (nivå 1) | 8 | u8: 1, u12: 1 | u8: 8, u12: 8 |
| **Sum BB** | | | u5: 18, u6: 4, u8: 8, u9: 24, u10: 4, u12: 8 (totalt 66) |

| **PLT-900** Stålplate 8 mm, 2000x6000 · LT 3 · FOQ 25 | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  | 18 | 4 |  | 8 | 24 | 4 |  | 8 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 20 | 20 | 20 | 20 | 20 | 2 | 23 | 23 | 15 | 16 | 12 | 12 | 4 | 4 | 4 | 4 | 4 |
| NB |  |  |  |  |  |  | 2 |  |  | 9 |  |  |  |  |  |  |  |
| PM |  |  |  |  |  |  | 25 |  |  | 25 |  |  |  |  |  |  |  |
| PF |  |  |  | 25 |  |  | 25 |  |  |  |  |  |  |  |  |  |  |

- Uke 1–4: BL 20.
- Uke 5: tilgjengelig 20, BB 18 → NB 0 → BL 2.
- Uke 6: tilgjengelig 2, BB 4 → NB **2** → PM = 25 (FOQ) → BL = 2 + 25 − 4 = 23. PF = 6 − 3 = **uke 3**.
- Uke 8: BL = 23 − 8 = 15.
- Uke 9: tilgjengelig 15, BB 24 → NB **9** → PM = 25 → BL = 15 + 25 − 24 = 16. PF = 9 − 3 = **uke 6**.
- Uke 10: 16 − 4 = 12. Uke 12: 12 − 8 = 4. Varen ender med 4 i overskudd på grunn av FOQ.

| **PRF-910** Profil/spant, 6 m · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  | 30 |  |  |  | 40 |  |  |  |  |  |  |  |
| ÅO |  |  |  |  | 20 |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 15 | 15 | 15 | 15 | 35 | 5 | 5 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  | 35 |  |  |  |  |  |  |  |
| PM |  |  |  |  |  |  |  |  |  | 35 |  |  |  |  |  |  |  |
| PF |  |  |  |  |  |  |  | 35 |  |  |  |  |  |  |  |  |  |

- BB = PF(SEK-110) × 10 = uke 5: 30, uke 9: 40.
- Uke 4: åpen ordre 20 → BL = 15 + 20 = 35. Uke 5: 35 − 30 = 5.
- Uke 9: tilgjengelig 5, BB 40 → NB **35** → PM 35 → BL 0. PF = 9 − 2 = **uke 7**.

| **VIN-920** Vinduspakke styrehus · LT 6 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |  |  |
| PM |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |  |  |
| PF | **1 (u0)** |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |

- BB = PF(STY-310) × 1 = uke 6 og 10. Lager 0.
- Uke 6: NB 1 → frigivelse 6 − 6 = **uke 0** → forfalt 1 uke (**E2**).
- Uke 10: NB 1 → PF = **uke 4**.

### Kontrollsummer, scenario A

- **Massebalanse** per vare: lager før u1 + ΣÅO + ΣPM − ΣBB = BL uke 16. Eksempler: PLT-900 20 + 0 + 50 − 66 = 4. PRF-910 15 + 20 + 35 − 70 = 0. SEK-110 1 + 0 + 7 − 8 = 0. MOT-210 0 + 1 + 1 − 2 = 0.
- **Mot BOM-eksplosjonen**: to fartøy gir 72 plater og 80 profiler. Seksjonen på lager trekker fra 6 plater og 10 profiler, som gir 66 plater og 70 profiler. Det stemmer med ΣBB i tabellene.

## 6. Bestillingsforslag — scenario A

Sortert på frigivelsesuke. «Innkjøp» = innkjøpsordre, «Produksjon» = produksjonsordre.

| Vare | Type | Antall | Frigis uke | Mottak uke | Merknad |
|---|---|---:|---:|---:|---|
| MOT-210 | Innkjøp | 1 | **−8** | 12 | Forfalt 9 uker (E2), byggenr. 2 |
| VIN-920 | Innkjøp | 1 | **0** | 6 | Forfalt 1 uke (E2), byggenr. 1 |
| PLT-900 | Innkjøp | 25 | 3 | 6 | FOQ (nettobehov 2) |
| GIR-220 | Innkjøp | 1 | 4 | 12 | Byggenr. 2 |
| VIN-920 | Innkjøp | 1 | 4 | 10 | Byggenr. 2 |
| SEK-110 | Produksjon | 3 | 5 | 7 | Byggenr. 1 (1 seksjon fra lager) |
| PLT-900 | Innkjøp | 25 | 6 | 9 | FOQ (nettobehov 9) |
| STY-310 | Produksjon | 1 | 6 | 8 | Byggenr. 1 |
| SKR-100 | Produksjon | 1 | 7 | 10 | Byggenr. 1 |
| PRF-910 | Innkjøp | 35 | 7 | 9 | |
| MAS-200 | Produksjon | 1 | 8 | 10 | Byggenr. 1 |
| DEK-300 | Produksjon | 1 | 8 | 10 | Byggenr. 1 |
| SEK-110 | Produksjon | 4 | 9 | 11 | Byggenr. 2 |
| RBE-000 | Produksjon | 1 | 10 | 12 | Byggenr. 1, sluttmontasje |
| STY-310 | Produksjon | 1 | 10 | 12 | Byggenr. 2 |
| SKR-100 | Produksjon | 1 | 11 | 14 | Byggenr. 2 |
| MAS-200 | Produksjon | 1 | 12 | 14 | Byggenr. 2 |
| DEK-300 | Produksjon | 1 | 12 | 14 | Byggenr. 2 |
| RBE-000 | Produksjon | 1 | 14 | 16 | Byggenr. 2, sluttmontasje |

Totalt 19 planlagte ordre. Kolonnen «Merknad» om byggenummer er bare forklaring. Fasiten har ikke pegging (sporing av behov til byggenummer), og systemet trenger ikke vise det i v1.

## 7. Exception-meldinger — scenario A

| # | Kode | Vare | Fakta (testes) | Forslag til meldingstekst (testes ikke) |
|---|---|---|---|---|
| 1 | E1 | MOT-210 | ledetid 20, horisont 16 | «Hovedmotor (MOT-210) har ledetid 20 uker, lengre enn planleggingshorisonten på 16 uker. Nye behov innenfor horisonten kan ikke dekkes med normal ledetid.» |
| 2 | E2 | MOT-210 | 1 stk, mottak u12, frigivelse u−8, 9 uker forfalt, tidligst mottak u21 | «Hovedmotor for mottak uke 12 skulle vært bestilt i uke −8 (9 uker for sent). Bestilt nå kommer den tidligst i uke 21. Maskinpakken for byggenr. 2 kan ikke starte i uke 12 uten kortere ledetid eller endret MPS.» |
| 3 | E2 | VIN-920 | 1 stk, mottak u6, frigivelse u0, 1 uke forfalt, tidligst mottak u7 | «Vinduspakke for mottak uke 6 skulle vært bestilt i uke 0 (1 uke for sent). Tidligst mottak uke 7, så styrehuset for byggenr. 1 forsinkes 1 uke.» |

MRP-en melder om problemet, men flytter verken ordre eller MPS. Det er planleggerens beslutning, slik briefen beskriver («ikke ved å ta beslutningen for planleggeren»).

## 8. Scenario B — MPS-endring (forplantning gjennom BOM)

**Endring:** byggenr. 2 framskyndes fra uke 16 til uke 14. Alt annet er som i A.

**Hva som forplanter seg:** alle ordre for byggenr. 1 er uendret. Alle ordre for byggenr. 2 flyttes 2 uker fram på hvert nivå. MOT-210 blir 2 uker mer forfalt. På PLT-900 havner behovet fra to foreldre i samme uke, og overskuddet fra den første plateordren (FOQ) gjør at nettobehovet for den andre ordren blir 1 i stedet for 9 (ordren er fortsatt 25).

| Vare | A: frigivelse → mottak (antall) | B: frigivelse → mottak (antall) |
|---|---|---|
| RBE-000 (2. ordre) | u14 → u16 (1) | u12 → u14 (1) |
| SKR-100 (2. ordre) | u11 → u14 (1) | u9 → u12 (1) |
| MAS-200 (2. ordre) | u12 → u14 (1) | u10 → u12 (1) |
| DEK-300 (2. ordre) | u12 → u14 (1) | u10 → u12 (1) |
| SEK-110 (2. ordre) | u9 → u11 (4) | u7 → u9 (4) |
| MOT-210 | **u−8** → u12 (1), forfalt 9 uker | **u−10** → u10 (1), forfalt 11 uker |
| GIR-220 | u4 → u12 (1) | u2 → u10 (1) |
| STY-310 (2. ordre) | u10 → u12 (1) | u8 → u10 (1) |
| PLT-900 (2. ordre) | u6 → u9 (25), NB 9 | u4 → u7 (25), NB 1 |
| PRF-910 | u7 → u9 (35) | u5 → u7 (35) |
| VIN-920 (2. ordre) | u4 → u10 (1) | u2 → u8 (1) |

**PLT-900 i B — sammensetning av bruttobehov:**

| Forelder | Mengde per | Foreldrenes PF | Bidrag til BB |
|---|---:|---|---|
| SEK-110 | 6 | u5: 3, u7: 4 | u5: 18, u7: 24 |
| STY-310 | 4 | u6: 1, u8: 1 | u6: 4, u8: 4 |
| DEK-300 | 8 | u8: 1, u10: 1 | u8: 8, u10: 8 |
| **Sum BB** | | | u5: 18, u6: 4, u7: 24, **u8: 12** (4 + 8 fra to foreldre), u10: 8 (totalt 66) |

- Uke 5: 20 − 18 = 2. Uke 6: tilgjengelig 2, BB 4 → NB 2 → PM 25 → BL 23, PF u3.
- Uke 7: tilgjengelig 23, BB 24 → NB **1** → PM 25 → BL = 23 + 25 − 24 = 24, PF = 7 − 3 = **u4**.
- Uke 8: 24 − 12 = 12. Uke 10: 12 − 8 = 4.

**MOT-210 i B:** BB uke 8 og 10. Uke 8 er dekket av den åpne ordren. Uke 10: NB 1 → frigivelse 10 − 20 = **u−10**, forfalt 11 uker, tidligst mottak u21.

### Fullstendige MRP-tabeller, scenario B

| **RBE-000** Testfartøy RBE Service 15 (komplett fartøy) · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |
| PM |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |
| PF |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |

| **SKR-100** Skrog, sammenstilt · LT 3 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |
| PM |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |
| PF |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |  |

| **MAS-200** Maskinpakke, installert · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |
| PM |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |
| PF |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |

| **DEK-300** Dekk og overbygg · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |
| PM |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |
| PF |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |

| **SEK-110** Skrogseksjon (blokk) · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  | 4 |  | 4 |  |  |  |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  | 3 |  | 4 |  |  |  |  |  |  |  |
| PM |  |  |  |  |  |  |  | 3 |  | 4 |  |  |  |  |  |  |  |
| PF |  |  |  |  |  | 3 |  | 4 |  |  |  |  |  |  |  |  |  |

| **MOT-210** Hovedmotor (import) · LT 20 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |
| ÅO |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |
| PM |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |
| PF | **1 (u-10)** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

| **GIR-220** Gir og propellanlegg · LT 8 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |
| PM |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |
| PF |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

| **STY-310** Styrehus · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |
| PM |  |  |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |
| PF |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |  |  |

| **PLT-900** Stålplate 8 mm, 2000x6000 · LT 3 · FOQ 25 | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  | 18 | 4 | 24 | 12 |  | 8 |  |  |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 20 | 20 | 20 | 20 | 20 | 2 | 23 | 24 | 12 | 12 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| NB |  |  |  |  |  |  | 2 | 1 |  |  |  |  |  |  |  |  |  |
| PM |  |  |  |  |  |  | 25 | 25 |  |  |  |  |  |  |  |  |  |
| PF |  |  |  | 25 | 25 |  |  |  |  |  |  |  |  |  |  |  |  |

| **PRF-910** Profil/spant, 6 m · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  | 30 |  | 40 |  |  |  |  |  |  |  |  |  |
| ÅO |  |  |  |  | 20 |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 15 | 15 | 15 | 15 | 35 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  | 35 |  |  |  |  |  |  |  |  |  |
| PM |  |  |  |  |  |  |  | 35 |  |  |  |  |  |  |  |  |  |
| PF |  |  |  |  |  | 35 |  |  |  |  |  |  |  |  |  |  |  |

| **VIN-920** Vinduspakke styrehus · LT 6 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |  |  |
| PM |  |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  |  |  |  |
| PF | **1 (u0)** |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |


### Exception-meldinger, scenario B

| # | Kode | Vare | Fakta |
|---|---|---|---|
| 1 | E1 | MOT-210 | ledetid 20, horisont 16 |
| 2 | E2 | MOT-210 | 1 stk, mottak u10, frigivelse u−10, 11 uker forfalt, tidligst mottak u21 |
| 3 | E2 | VIN-920 | 1 stk, mottak u6, frigivelse u0, 1 uke forfalt, tidligst mottak u7 (uendret fra A) |

## 9. Scenario C — endret lagerstatus

**Endring:** giret på lager (GIR-220) viser seg å være skadet, og beholdningen settes fra 1 til 0. Alt annet er som i A.

**Forplantning:** GIR-220 er en kjøpt vare uten barn, så bare GIR-220 endres. Alle andre varer har samme resultat som i A (se `expected.json`). Endringen gir en ny exception-melding.

| **GIR-220** Gir og propellanlegg · LT 8 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |
| PM |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  |  |
| PF | **1 (u0)** |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |

- Uke 8: tilgjengelig 0, BB 1 → NB **1** → PM 1 → frigivelse 8 − 8 = **u0** → forfalt 1 uke (**E2**), tidligst mottak u9. Maskinpakken for byggenr. 1 (planlagt start u8) forsinkes 1 uke.
- Uke 12: som i A, PF u4.

**Exception-meldinger, scenario C:** de tre fra A, pluss **E2 GIR-220**: 1 stk, mottak u8, frigivelse u0, 1 uke forfalt, tidligst mottak u9.

## 10. Scenario D — forfalte produksjonsordrer (regel R11)

**Endring:** byggenr. 1 framskyndes fra uke 12 til uke 4. Byggenr. 2 er fortsatt i uke 16. Alt annet er som i A.

Scenarioet tester hva som skjer når sensor eller planleggeren legger inn en plan som ikke rekker. Produksjonsordrer får frigivelse før uke 1, og barnas behov må legges i uke 1 (R11), i alle ledd nedover.

**Gangen i beregningen (byggenr. 1):**

| Vare | Behov (uke) | Frigivelse | Følge |
|---|---|---|---|
| RBE-000 | u4 | u4 − 2 = **u2** | I horisonten, ingen melding |
| SKR-100 | u2 | u2 − 3 = **u−1** | E2, 2 uker forfalt. Barna får behov i u1 (R11). |
| MAS-200, DEK-300 | u2 | u2 − 2 = **u0** | E2, 1 uke forfalt. Barna får behov i u1. |
| SEK-110 | u1: 4 (fra SKR) − 1 på lager = 3 | u1 − 2 = **u−1** | E2, 2 uker forfalt. Barna får behov i u1. |
| STY-310 | u1 (fra DEK) | u1 − 2 = **u−1** | E2, 2 uker forfalt. Barna får behov i u1. |
| MOT-210 | u1 (fra MAS) | u1 − 20 = **u−19** | E2, 20 uker forfalt, tidligst mottak u21 |
| GIR-220 | u1 (fra MAS) | – | Dekket av lager (1) |
| PLT-900 | u1: 18 (SEK) + 4 (STY) + 8 (DEK) = 30 | u1 − 3 = **u−2** | 30 − 20 på lager = NB 10 → FOQ 25. E2, 3 uker forfalt. |
| PRF-910 | u1: 30 (SEK) | u1 − 2 = **u−1** | 30 − 15 på lager = NB 15. E2, 2 uker forfalt. |
| VIN-920 | u1 (fra STY) | u1 − 6 = **u−5** | E2, 6 uker forfalt |

Ordrene for byggenr. 2 er stort sett de samme som i A. Unntakene er PRF-910 og MOT-210. For PRF-910 dekker den åpne ordren i uke 4 nå mer av behovet, så ordren blir 20 i stedet for 35. MOT-210 er forklart under.

**Merk hovedmotoren:** den åpne ordren i uke 7 var bestilt til byggenr. 1, men kommer for sent. MRP flytter ikke åpne ordre (R10) og har ingen pegging. Derfor dekker motoren i uke 7 behovet for byggenr. 2 i uke 12, mens byggenr. 1 får et nytt, forfalt bestillingsforslag.

**Kontroll av R11:** ingen bruttobehov går tapt. PLT-900 har fortsatt 66 i bruttobehov totalt, og PRF-910 har 70, akkurat som i A.

### MRP-tabeller, scenario D

| **RBE-000** Testfartøy RBE Service 15 (komplett fartøy) · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |
| PM |  |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |
| PF |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |

| **SKR-100** Skrog, sammenstilt · LT 3 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |
| PM |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |
| PF | **1 (u-1)** |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  |

| **MAS-200** Maskinpakke, installert · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |
| PM |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |
| PF | **1 (u0)** |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |

| **DEK-300** Dekk og overbygg · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |
| PM |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |
| PF | **1 (u0)** |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |

| **SEK-110** Skrogseksjon (blokk) · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  | 4 |  |  |  |  |  |  |  |  |  | 4 |  |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  | 3 |  |  |  |  |  |  |  |  |  | 4 |  |  |  |  |  |
| PM |  | 3 |  |  |  |  |  |  |  |  |  | 4 |  |  |  |  |  |
| PF | **3 (u-1)** |  |  |  |  |  |  |  |  | 4 |  |  |  |  |  |  |  |

| **MOT-210** Hovedmotor (import) · LT 20 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  | 1 |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| NB |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| PM |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| PF | **1 (u-19)** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

| **GIR-220** Gir og propellanlegg · LT 8 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  | 1 |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |
| PM |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |
| PF |  |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |

| **STY-310** Styrehus · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  | 1 |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  | 1 |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |
| PM |  | 1 |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |
| PF | **1 (u-1)** |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |

| **PLT-900** Stålplate 8 mm, 2000x6000 · LT 3 · FOQ 25 | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  | 30 |  |  |  |  |  |  |  | 24 | 4 |  | 8 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 20 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 16 | 12 | 12 | 4 | 4 | 4 | 4 | 4 |
| NB |  | 10 |  |  |  |  |  |  |  | 9 |  |  |  |  |  |  |  |
| PM |  | 25 |  |  |  |  |  |  |  | 25 |  |  |  |  |  |  |  |
| PF | **25 (u-2)** |  |  |  |  |  | 25 |  |  |  |  |  |  |  |  |  |  |

| **PRF-910** Profil/spant, 6 m · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  | 30 |  |  |  |  |  |  |  | 40 |  |  |  |  |  |  |  |
| ÅO |  |  |  |  | 20 |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 15 | 0 | 0 | 0 | 20 | 20 | 20 | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  | 15 |  |  |  |  |  |  |  | 20 |  |  |  |  |  |  |  |
| PM |  | 15 |  |  |  |  |  |  |  | 20 |  |  |  |  |  |  |  |
| PF | **15 (u-1)** |  |  |  |  |  |  | 20 |  |  |  |  |  |  |  |  |  |

| **VIN-920** Vinduspakke styrehus · LT 6 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  | 1 |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  | 1 |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |
| PM |  | 1 |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |
| PF | **1 (u-5)** |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |


### Exception-meldinger, scenario D

| # | Kode | Vare | Antall | Mottak | Frigivelse | Uker forfalt | Tidligst mottak |
|---|---|---|---:|---:|---:|---:|---:|
| 1 | E1 | MOT-210 | – | – | – | – | – (ledetid 20 > horisont 16) |
| 2 | E2 | SKR-100 | 1 | u2 | u−1 | 2 | u4 |
| 3 | E2 | MAS-200 | 1 | u2 | u0 | 1 | u3 |
| 4 | E2 | DEK-300 | 1 | u2 | u0 | 1 | u3 |
| 5 | E2 | SEK-110 | 3 | u1 | u−1 | 2 | u3 |
| 6 | E2 | MOT-210 | 1 | u1 | u−19 | 20 | u21 |
| 7 | E2 | STY-310 | 1 | u1 | u−1 | 2 | u3 |
| 8 | E2 | PLT-900 | 25 | u1 | u−2 | 3 | u4 |
| 9 | E2 | PRF-910 | 15 | u1 | u−1 | 2 | u3 |
| 10 | E2 | VIN-920 | 1 | u1 | u−5 | 6 | u7 |

## 11. Scenario E — endret BOM

**Endring:** mengde per på BOM-linjen SKR-100 → SEK-110 endres fra 4 til 5 (fem seksjoner per skrog). Alt annet er som i A.

**Forplantning:** SKR-100 og nivåene over er uendret, fordi endringen bare påvirker behovet *under* skroget. SEK-110 får større bruttobehov, og det forplanter seg til plater og profiler. Alle andre varer har samme resultat som i A. Exception-meldingene er de samme som i A.

**SEK-110:** BB = PF(SKR-100) × 5 = u7: 5, u11: 5. Uke 7: 5 − 1 på lager = NB **4**, PF u5. Uke 11: NB **5**, PF u9.

| **SEK-110** Skrogseksjon (blokk) · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  |  |  | 5 |  |  |  | 5 |  |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  |  |  | 4 |  |  |  | 5 |  |  |  |  |  |
| PM |  |  |  |  |  |  |  | 4 |  |  |  | 5 |  |  |  |  |  |
| PF |  |  |  |  |  | 4 |  |  |  | 5 |  |  |  |  |  |  |  |

**PLT-900:** BB = SEK × 6 (u5: 24, u9: 30) + STY × 4 (u6: 4, u10: 4) + DEK × 8 (u8: 8, u12: 8) = 78 totalt.
- Uke 5: tilgjengelig 20, BB 24 → NB **4** → PM 25 → BL 21, PF u2.
- Uke 6: 21 − 4 = 17. Uke 8: 17 − 8 = 9.
- Uke 9: tilgjengelig 9, BB 30 → NB **21** → PM 25 → BL 4, PF u6.
- Uke 10: 4 − 4 = 0.
- Uke 12: tilgjengelig 0, BB 8 → NB **8** → PM 25 → BL 17, PF u9. Den tredje plateordren kommer bare fordi BOM-en ble endret.

| **PLT-900** Stålplate 8 mm, 2000x6000 · LT 3 · FOQ 25 | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  | 24 | 4 |  | 8 | 30 | 4 |  | 8 |  |  |  |  |
| ÅO |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 20 | 20 | 20 | 20 | 20 | 21 | 17 | 17 | 9 | 4 | 0 | 0 | 17 | 17 | 17 | 17 | 17 |
| NB |  |  |  |  |  | 4 |  |  |  | 21 |  |  | 8 |  |  |  |  |
| PM |  |  |  |  |  | 25 |  |  |  | 25 |  |  | 25 |  |  |  |  |
| PF |  |  | 25 |  |  |  | 25 |  |  | 25 |  |  |  |  |  |  |  |

**PRF-910:** BB = SEK × 10 = u5: 40, u9: 50. Uke 4: 15 + 20 (åpen ordre) = 35. Uke 5: NB 40 − 35 = **5**, PF u3. Uke 9: NB **50**, PF u7.

| **PRF-910** Profil/spant, 6 m · LT 2 · L4L | Før u1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BB |  |  |  |  |  | 40 |  |  |  | 50 |  |  |  |  |  |  |  |
| ÅO |  |  |  |  | 20 |  |  |  |  |  |  |  |  |  |  |  |  |
| BL | 15 | 15 | 15 | 15 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NB |  |  |  |  |  | 5 |  |  |  | 50 |  |  |  |  |  |  |  |
| PM |  |  |  |  |  | 5 |  |  |  | 50 |  |  |  |  |  |  |  |
| PF |  |  |  | 5 |  |  |  | 50 |  |  |  |  |  |  |  |  |  |


## 12. Avklaringer og forutsetninger

Briefen var uklar eller underspesifisert på disse punktene. Valgene ble bekreftet i PRD-en (2026-11-24) der ikke annet står.

1. **Eksempelet «hovedmotoren må bestilles i uke 3 fordi ledetiden er lengre enn planleggingshorisonten»** (brief.md, Løsningen pkt. 4) henger ikke logisk sammen. Er ledetiden lengre enn horisonten og behovet ligger innenfor horisonten, havner frigivelsen alltid *før* uke 1. En frigivelse i uke 3 med LT 20 gir mottak i uke 23, utenfor horisonten, der MRP-en ikke beregner noe. Fasiten bruker derfor «forfalt frigivelse» (E2) sammen med «ledetid > horisont» (E1). Eksempelet i briefen er rettet.
2. **«Ett testfartøy»** er tolket som én fartøystype (én BOM) med to byggenumre i MPS. Med bare ett fartøy blir netting mot lager og åpne ordre, FOQ-overskudd og forplantning mellom byggenumre nesten ikke testet.
3. **Partiregel**: briefen nevner partistørrelse som beslutningspunkt, men angir ingen regel. Fasiten bruker L4L som standard og FOQ på én vare.
4. **Horisontlengde** (16 uker) og **tidsbøttekonvensjonene** (R1–R3, R7–R8) er ikke angitt i briefen.
5. **Exception-typer**: briefen gir bare ett eksempel. v1 har to (E1, E2). Meldinger for åpne ordre (framskynd/utsett/kanseller) er flyttet til trinn 2. Scenario D viser hvorfor de er nyttige: den åpne motorordren i uke 7 kommer for sent til byggenr. 1, men MRP foreslår ikke å framskynde den.
6. **Barn av forfalte produksjonsordrer**: avgjort i PRD-en som regel R11 (behovet legges i uke 1, med E2 på forelderen). Testes i scenario D.
7. **Leverandørvalg** (beslutningspunkt i addendum, MRP) og **pegging** (sporing til byggenummer) er ikke med i v1-fasiten.
8. **Sikkerhetslager** = 0 i v1 (trinn 2). Når det innføres, trengs en egen fasit, fordi R5 da endrer nettobehovet.

## Verifisering

- Hele beregningen er gjort for hånd og vist over (konvensjoner → BOM → MPS → nivå for nivå).
- `expected.json` er kryssjekket mot et uavhengig engangsskript som beregner MRP fra `input.json` etter reglene R1–R10. Alle fem scenarier stemmer, og massebalansen går opp for hver vare. Skriptet ble i tillegg testet med en bevisst feil i fasiten, som det fanget. Skriptet er ikke committet, slik at fasiten ikke blir forvekslet med selve MRP-implementasjonen.
- Tabellene i dette dokumentet er gjengitt direkte fra `expected.json`, så tabeller og JSON ikke kan sprike.
