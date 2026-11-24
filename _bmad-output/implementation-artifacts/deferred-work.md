# Utsatt arbeid

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-backend-oppsett-med-helsesjekk-og-konfigurasjon.md`
  summary: Story 1.3 må opprette `backend/data/` før databasen åpnes, og gi en tydelig feil ved oppstart hvis `fixture_path` ikke finnes.
  evidence: `database_url` peker på `backend/data/rbe.db`, men mappa er gitignorert og blir ikke opprettet, så SQLite feiler på en ren klone. `fixture_path` valideres ikke før seed leser den (gjennomgang av story 1.1, punkt 11–12).
