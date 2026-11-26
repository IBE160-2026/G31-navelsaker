# Utsatt arbeid

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-backend-oppsett-med-helsesjekk-og-konfigurasjon.md`
  summary: Story 1.3 må opprette `backend/data/` før databasen åpnes, og gi en tydelig feil ved oppstart hvis `fixture_path` ikke finnes.
  evidence: `database_url` peker på `backend/data/rbe.db`, men mappa er gitignorert og blir ikke opprettet, så SQLite feiler på en ren klone. `fixture_path` valideres ikke før seed leser den (gjennomgang av story 1.1, punkt 11–12).

- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-database-og-seed-ved-tom-database.md`
  summary: Når skjemaet endres (første gang i story 4.6 med `input_revision`), bør oppstarten oppdage en gammel databasefil og gi en tydelig melding om å slette den, i stedet for en uklar feil ved første spørring.
  evidence: `create_all` legger ikke til nye kolonner i tabeller som allerede finnes. AD-5 sier at fila slettes ved skjemaendring, men ingenting forteller utvikleren det (gjennomgang av story 1.3, funn 7).
