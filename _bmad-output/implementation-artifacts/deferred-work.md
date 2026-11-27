# Utsatt arbeid

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-backend-oppsett-med-helsesjekk-og-konfigurasjon.md`
  summary: Story 1.3 må opprette `backend/data/` før databasen åpnes, og gi en tydelig feil ved oppstart hvis `fixture_path` ikke finnes.
  evidence: `database_url` peker på `backend/data/rbe.db`, men mappa er gitignorert og blir ikke opprettet, så SQLite feiler på en ren klone. `fixture_path` valideres ikke før seed leser den (gjennomgang av story 1.1, punkt 11–12).

- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-database-og-seed-ved-tom-database.md`
  summary: Når skjemaet endres (første gang i story 4.6 med `input_revision`), bør oppstarten oppdage en gammel databasefil og gi en tydelig melding om å slette den, i stedet for en uklar feil ved første spørring.
  evidence: `create_all` legger ikke til nye kolonner i tabeller som allerede finnes. AD-5 sier at fila slettes ved skjemaendring, men ingenting forteller utvikleren det (gjennomgang av story 1.3, funn 7).

- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-frontend-oppsett-designtokens-og-innloggingsside.md`
  summary: Flyten for innlogging i frontend (adressen brukeren ba om ligger i routerens `state`, meldingen om utløpt sesjon vises bare etter bekreftet innlogging) bør prøves på nytt når story 1.6 bygger om rutene i `App.tsx`, og føres i testplanen i story 3.2.
  evidence: Flyten er bare prøvd manuelt i story 1.5. Et tapt `search`/`hash` i `RequireAuth` eller en fjernet vakt rundt `userRef.current` passerer build, Biome og backendtestene (gjennomgang av story 1.5, funn 2).

- source_spec: `_bmad-output/implementation-artifacts/spec-1-6-menylinje-og-startside.md`
  summary: Frontend mangler et testmiljø for komponenter (jsdom og testing-library), så utloggingen i `AuthProvider` (204/401/nettverksfeil og vakten mot meldingen om utløpt sesjon), `RequireAuth` etter egen utlogging, fokus til H1 i `PageTitle` og rutene for menyen og dørene er bare prøvd manuelt.
  evidence: Å fjerne vakten `loggingOutRef`, snu betingelsen i `PageTitle` eller endre en rutesti passerer build, Biome og Vitest (gjennomgang av story 1.6, VG-funn 1–4). Vurder testmiljøet når skjermbildene i epic 3 og 4 kommer, eller før stegene i testplanen i 3.2.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-lavnivakoder-og-resultatform.md`
  summary: Tiltak 4 fra retrospektiven av epic 1 (tester for egen RBE_DEMO_USERNAME og egen RBE_FIXTURE_PATH gjennom seed og innlogging, R2 og R3) tas inn i specen for story 3.1.
  evidence: Retrospektiven la tiltaket til «neste backend-story». Thobias valgte 2026-11-27 å flytte det fra 2.1, som bare gjelder den rene kjernen, til 3.1, som uansett endrer deps.py og legger til API-tester.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-lavnivakoder-og-resultatform.md`
  summary: Story 2.2 må bestemme hvordan uke gjøres om til arrayindeks. `Horizon.first_week` brukes ikke i dag, mens `ItemResult` sier at indeks 0 er uke 1. *Løst i story 2.2 (2026-11-27):* Thobias valgte at kjernen krever første uke 1 og gir `MrpInputError` ellers. Indeks = uke − 1 (AD-2).
  evidence: Thobias sin gjennomgang av PR #11, risikopunkt 2 (`backend/src/rbe/mrp/types.py`, docstringen til `ItemResult`). Fasiten har `first_week` 1, så en kode som antar uke 1 består fasittestene uansett.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-lavnivakoder-og-resultatform.md`
  summary: Verdiene i inndataene (negativ `qty_per` eller ledetid, MPS-uker utenfor horisonten, horisont ≤ 0) sjekkes ikke av kjernen. Avklar i specen for 4.1 at API-et avviser dem (AD-7, FR-8), og vurder om kjernen skal gi `MrpInputError` i tillegg. *Oppdatert i story 2.2:* kjernen avviser nå første uke ≠ 1, MPS-linjer og åpne ordre utenfor horisonten, negativ ledetid, ukjent partiregel og FOQ uten kvantum. Mengde per < 1 og negative mengder sjekkes fortsatt bare av API-et i 4.1. Horisont ≤ 0 sjekkes ikke, fordi horisonten ikke kan redigeres.
  evidence: Thobias sin gjennomgang av PR #11, risikopunkt 3. `_check_input` i `backend/src/rbe/mrp/llc.py` sjekker bare duplikater og referanser. Horisont ≤ 0 ble avvist i triage nr. 7, fordi tilstanden ikke kan nås før epic 4.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-lavnivakoder-og-resultatform.md`
  summary: Story 2.4 må gjøre sorteringsnøkkelen for meldinger eksplisitt per type, i stedet for `getattr(e, "receipt_week", 0)`, så en ny meldingstype ikke kan sorteres feil uten at noe sier fra. *Løst i story 2.4 (2026-11-27):* `_exception_key` i `run.py` har en gren per type med `match`, og en ukjent type gir `TypeError` (`test_ad3_unknown_exception_type_is_rejected`).
  evidence: Thobias sin gjennomgang av PR #11, risikopunkt 4 (`_ordered` i `backend/src/rbe/mrp/run.py`). I dag finnes bare E1 og E2, og testen for `_ordered` dekker begge.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-lavnivakoder-og-resultatform.md`
  summary: Story 2.4 trenger en egen fasittest for `exceptions`, sammenlignet som usortert mengde per scenario, fordi `pytest_generate_tests` i `tests/conftest.py` bare lager tilfeller for felt per vare. *Løst i story 2.4 (2026-11-27):* `test_fasit_exceptions` i `tests/mrp/test_fixture_scenarios.py` sammenligner meldingene som multimengde per scenario og type, med id-er fra `A-FR-13-meldinger` til `E-FR-14-meldinger`, og feiler på ukjent type.
  evidence: Thobias sin gjennomgang av PR #11, risikopunkt 5. `fasit_cases` leser bare `result["items"]`.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-lavnivakoder-og-resultatform.md`
  summary: Vakten for FR-10 i fasittesten hviler på én vare. PLT-900 er den eneste der lengste og korteste vei gir ulik LLC, så skalatesten i 2.5 må ha flere varer med flere veier av ulik lengde og sjekke LLC mot en uavhengig beregning.
  evidence: Thobias sin gjennomgang av PR #11: korteste vei gir 6 feil av 112, alle på PLT-900 og rekkefølgetesten. Endres BOM-en i fasiten, kan vakten forsvinne uten at noe feiler.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-2-bruttobehov-netting-partiregel-og-ledetidsoffset.md`
  summary: Story 2.3 må legge til egenskapen «ingen behov går tapt» (sum av barnets bruttobehov = sum av foreldrenes `planned_orders` × mengde per, for A–E), fjerne `fasit_marks` og `R11_SKIP` i `tests/mrp/test_fixture_scenarios.py`, og gi D-tilfellene FR-12 i test-id-en. *Løst i story 2.3 (2026-11-27):* R11 er på plass, skip-regelen og `fasit_marks` er fjernet, D-tilfellene for feltene fra 2.2 har FR-12 i id-en, og `test_fr12_no_requirements_are_lost` sjekker egenskapen per vare for A–E (AC 3 i epics er skrevet om fra per BOM-linje til per vare).
  evidence: Thobias sin gjennomgang av PR #12. Ingenting feiler hvis skip-regelen blir stående etter at R11 er på plass: de 77 tilfellene forblir skipped og alt er grønt. Uten R11 er summen av bruttobehov for PLT-900 i D 30, mens fasiten har 66. Behovet forsvinner mellom forelder og barn, så bare egenskapen over fanger det. Massebalansen per vare går opp i D også uten R11, og D er derfor tatt med i den testen.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-3-komponentbehov-fra-forfalte-produksjonsordrer-r11.md`
  summary: Story 4.1 må avgjøre om API-et skal avvise en kjøpt vare (`source` = `purchase`) med BOM-linjer under seg, sammen med CHECK-begrensningene fra tiltak 6 i retrospektiven av epic 1 (R7).
  evidence: Thobias sin gjennomgang av PR #13. Kjernen bruker R11 på alle foreldre, også kjøpte, så ingen behov går tapt, og det beholdes (vedtak 2026-11-27). Fasiten har ingen kjøpte foreldre, og `test_fr12_r11_purchased_parent_past_due` i `tests/mrp/test_plan.py` er eneste test. Om en slik vare er en feil i inndataene, er et spørsmål for valideringen i 4.1, ikke for kjernen.
