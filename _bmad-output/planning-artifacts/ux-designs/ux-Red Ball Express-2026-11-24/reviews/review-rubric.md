# Spine Pair Review — Red Ball Express (rubrikk)

2026-11-24. Kjørt sekvensielt i økta, ikke som uavhengig subagent. Funnene er rettet før status `final`.

## Overall verdict
Paret er brukbart som kontrakt. Flytene, fargebetydningen, tilstandene og koblingen til PRD-en er sterke. Den største svakheten var at flere komponenter i EXPERIENCE.md manglet visuell spesifikasjon i DESIGN.md.

## 1. Flow coverage — strong
UJ-1 og UJ-2 fra PRD-en finnes med navn ordrett, nummererte steg, høydepunkt og feilsti.

## 2. Token completeness — adequate
Alle `{…}`-referanser i prosa og komponenter finnes i frontmatter. Alle fargetokener har hex-verdi, og kontrasten er oppgitt for de viktige parene.
### Findings
- **medium** Tabulære tall og overlay-dekning (94 %) står bare i prosa (Typography, Colors). *Fix:* akseptert. DESIGN.md-spesifikasjonen har ikke felt for fontFeature, og prosaen er tydelig.

## 3. Component coverage — thin → rettet
### Findings
- **high** Mangler i DESIGN.md.Components, men brukt i EXPERIENCE.md: statuslinje, meldingsseksjon (skjul/vis), vareliste med søk, BOM-node, redigeringspanel, rad under redigering, tom tilstand, feillinje for serverfeil, innloggingskort og velkomstflate på startsiden. *Fix:* lagt til.
- **low** Navnet «Bekreftelse» (DESIGN.md) og «Bekreftelseslinje» (EXPERIENCE.md) var ulikt. *Fix:* «Bekreftelseslinje» brukes begge steder.

## 4. State coverage — adequate → rettet
### Findings
- **medium** Ingen tilstand for en kjøring uten bestillingsforslag, for eksempel med tom hovedplan. *Fix:* «Ingen bestillingsforslag fra siste kjøring.» er lagt til.
- **low** Innlogging manglet ventetilstand. *Fix:* «Logger inn …» er lagt til.
- **low** Det var ikke beskrevet at «Kjør MRP» blir aktiv igjen etter en feil ved kjøring. *Fix:* lagt til.

## 5. Visual reference coverage — strong
`mockups/key-screens.html`, `mockups/logo-3c.svg`, `mockups/favicon.svg`, `imports/…webp` og `imports/KILDER.md` er lenket der de hører hjemme. Alle filer i `.working/` er lenket under Inspiration. At spinene gjelder ved konflikt, står i begge. Det står også at `.working/startside-hav-2.html` viser til et fjernet bilde.

## 6. Bloat & overspecification — adequate
«Endringer og fargebetydning» gjentar fargetabellen kort, men beskriver oppførsel som DESIGN.md ikke eier. Det er akseptert.

## 7. Inheritance discipline — strong
`sources` finnes, UJ-navnene er ordrett like, og forholdet mellom «exception-melding» i PRD-en og «melding» i UI-et er forklart. Avviket fra FR-17 er merket og skal føres tilbake.

## 8. Shape fit — strong
DESIGN.md har alle åtte seksjoner i riktig rekkefølge. EXPERIENCE.md har alle standardseksjonene, pluss Responsive, Inspiration og den egendefinerte «Endringer og fargebetydning», som er begrunnet.

## Mechanical notes
Ingen brutte kryssreferanser.
