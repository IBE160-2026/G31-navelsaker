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
