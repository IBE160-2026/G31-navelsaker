# Addendum: Red Ball Express

Utfyllende materiale som støtter briefen, men som er for detaljert til å stå i selve brief-dokumentet. Dette er kildegrunnlag for senere PRD- og arkitekturarbeid.

## Designprinsipp: eksplisitt synlig dataflyt og beslutningslogikk

Siden prosjektet vurderes uten formell rubrikk, bør UI/dokumentasjon gjøre dataflyt og beslutningslogikk eksplisitt synlig — dette er et bevisst designvalg, ikke en funksjon for sluttbrukeren.

## Fullstendig modulspesifikasjon (fra oppgaveteksten, IBE130)

Seks moduler, hver med data inn / data ut / beslutningspunkter, slik faget definerer dem:

### 1. Demand Management (prognoser)
- **Data inn**: Historiske salgstall, sesong-/trendsignaler, kampanjer/markedsdata, kundebestillinger og salgsprognoser.
- **Data ut**: Etterspørselsprognoser per periode/produkt, scenarioer (optimistisk/pessimistisk/normal).
- **Beslutningspunkter**: Prognosemetoder, sikkerhetsmargin, håndtering av outliers.

### 2. Sales & Operations Planning (S&OP — månedlig)
- **Data inn**: Etterspørselsprognoser, kapasitet, lagerstatus, økonomiske begrensninger.
- **Data ut**: Aggregert produksjonsplan, kapasitetsbehov, scenarioer for servicegrad/kost.
- **Beslutningspunkter**: Produksjon vs. lager, intern produksjon vs. outsourcing.

### 3. Master Production Scheduling (MPS — ukentlig)
- **Data inn**: S&OP, kundebestillinger, lagerstatus ferdigvarer.
- **Data ut**: Hovedproduksjonsplan per uke/produkt, leveringsdatoer, prioriteringslister.
- **Beslutningspunkter**: Mix og volum, prioritering ved kapasitetsmangel.

### 4. Bill of Materials (BOM — produktstruktur)
- **Data inn**: Produktdata fra engineering, versjoner, komponentinformasjon.
- **Data ut**: Multinivå BOM med mengdekrav og alternativregler.
- **Beslutningspunkter**: Standardisering vs. tilpasning, alternative materialer.

### 5. Material Requirements Planning (MRP — ukentlig komponentplan)
- **Data inn**: MPS, BOM, lagerstatus, innkjøpstid, sikkerhetslager.
- **Data ut**: Nettobehov per uke, bestillingsforslag, exception-meldinger.
- **Beslutningspunkter**: Bestillingstidspunkt, partistørrelse, leverandørvalg.

### 6. Operations Planning (Scheduling — detaljplan)
- **Data inn**: Planlagte ordre, maskinkapasitet, operasjonstider, routing.
- **Data ut**: Produksjonskjøreplan, forventede ferdigdatoer, varsler om forsinkelser.
- **Beslutningspunkter**: Jobbrekkefølge, batch-størrelse, håndtering av hasteordre.

Vanskelighetsgrad (fagets egen merking): 🔴 Vanskelig.

## Markedsgrunnlag (research, innhentet under brief-arbeidet)

**Sammenlignbare systemer** — begrenset offentlig dokumentert AI-integrasjon i planleggingskjernen for verft; alle er generalist-ERP eller maritime MRO-verktøy tilpasset engineer-to-order (ETO):
- SAP S/4HANA PP — multinivå BOM-diffing, standard MRP-eksplosjonslogikk, ETO via salgsordre-drevet produksjon.
- IFS Cloud — bygget for prosjektbasert, anleggsintensiv ETO-produksjon; god passform for nordiske/vesteuropeiske verft.
- Infor CloudSuite Industrial (SyteLine) — fleksibel ETO-arkitektur for private verft/reparasjonsverft/komponentleverandører. Maritimt tilknyttede verktøy: ABS Nautical Systems, SpecTec AMOS (MRO-tungt), AVEVA (engineering-siden).

**AI/ML i produksjonsplanlegging (2025–2026), reelt vs. hype:**
- ML-basert etterspørselsprognose er moden praksis integrert med ERP/MES/IoT for kontinuerlig re-planlegging (McKinsey rapporterer 20–50 % redusert prognosefeil, opptil 65 % færre stockouts — leverandørrapportert, bør tolkes med forbehold).
- "Agentic AI" multi-agent planlegging markedsføres som 2025–2026-trend, men er i stor grad leverandørnarrativ med uklar modenhet for ETO/lavvolum-domener som skipsbygging.
- Sikkerhetslager/Monte Carlo er en etablert kvantitativ teknikk, ikke ny: probabilistisk sikkerhetslager-formel (SS = Z·√(LT·σ²_demand + demand²·σ²_LT)), Monte Carlo simulerer etterspørsels- og ledetidsusikkerhet samlet.
- Direkte akademisk presedens for prioritet 1 (BOM+MRP/ledetid): Springer (2025/2026) — "Process-Aware Procurement Lead Time Prediction for Shipyard Delay Mitigation" — ML-basert ledetidsprediksjon spesifikt for verft. Nærmeste faglige analog for prosjektet.
- ML på BOM-siden er hovedsakelig PLM-feildeteksjon/validering, ikke MRP-eksplosjon-spesifikk.

**Verftsspesifikke utfordringer:**
- ETO-strukturer: prosjektomfang og BOM endres midt i byggeprosessen; endringer må forplante seg gjennom innkjøp/produksjon uten å bryte MRP.
- Ledetidsusikkerhet ved innkjøp er den anerkjente kjerneutfordringen i ETO/skipsbygging; én forsinket kritisk komponent (f.eks. hovedmotor) kaskaderer gjennom hele byggesekvensen pga. sekvensielle avhengigheter mellom skrog og utrustning.
- Væravhengighet: utendørs skrog-/blokkarbeid begrenses av "weather windows" (bølgehøyde/vindgrenser) — en usikkerhetsakse som ikke finnes i innendørs diskret produksjon.
- Koordinerings-/planleggingsfeil trekkes fram som en større feilkilde i verftsindustrien enn ren kapasitetsmangel.

## Kilder
- IFS 2026 Buyer's Guide (shipbuilding/ship repair)
- SAP Help — multinivå BOM/MRP-eksplosjon
- erpresearch.com, danaos-projects.com — verfts-ERP-oversikter
- softtype.com, startup-house.com, leewayhertz.com — AI i produksjonsplanlegging 2025–2026
- UNIS, Lumivero, arXiv (Monte Carlo for forsyningskjeder)
- Springer — "Process-Aware Procurement Lead Time Prediction for Shipyard Delay Mitigation"
- Springer — ETO-litteraturgjennomgang; weather window-prediksjon
- Epicflow — prosjektporteføljestyring i skipsbygging
