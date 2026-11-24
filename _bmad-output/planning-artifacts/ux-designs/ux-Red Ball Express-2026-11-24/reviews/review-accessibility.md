# Tilgjengelighetsgjennomgang — Red Ball Express (NFR-6, WCAG 2.2 AA)

2026-11-24. Kjørt sekvensielt i økta. Funnene er rettet før status `final`.

## Verdict
God grunnmur: ingen betydning formidles bare med farge, all tekstkontrast er minst 4,5:1, og tastatur, etiketter og tre-semantikk er beskrevet. Fem funn kan stoppe AA-samsvar, og de er rettet.

## Findings
- **high · 1.4.11 kontrast for grensesnittelementer.** `border-strong` (#C9C2B6) mot hvitt er 1,77:1. Det gjelder kanten på felt og sekundærknapper, som skal ha minst 3:1. *Fix:* `border-strong` er endret til #8C857A (3,65:1 mot hvitt, 3,44:1 mot bakgrunnen).
- **high · 2.1.1 / 1.4.13 innhold bare ved hover.** Forrige verdi for endrede celler fantes bare som verktøytips (`title`), så tastaturbrukere fikk ikke tilgang til den. *Fix:* en avkrysningsboks over tabellen, «Vis verdier fra forrige kjøring», viser «24 ← 0» i cellene. Verktøytipset og den skjulte skjermlesertekst beholdes.
- **medium · 2.4.1 hoppe over gjentatte blokker.** Det fantes ingen «Hopp til innhold»-lenke. *Fix:* den er lagt til som første element med fokus.
- **medium · 2.4.2 sidetittel og fokus ved navigasjon.** Det var ikke beskrevet. *Fix:* hver adresse setter dokumenttittel (f.eks. «MRP-tabell: PLT-900 – Red Ball Express»), og fokus flyttes til H1 ved sidebytte.
- **medium · Fokushåndtering ved redigering.** Det var ikke beskrevet hvor fokus går ved «Endre», «Lagre», panel og bekreftelse i raden. *Fix:* fokus går til første felt ved åpning og tilbake til utløseren ved lagring eller avbryt. Ved «Slett» har «Nei» fokus som standard.
- **medium · 2.1.1 rullbar tabell.** En MRP-tabell som ruller sideveis, må kunne rulles med tastatur. *Fix:* rulleområdet har `tabindex="0"`, `role="region"` og en etikett.
- **low · 2.5.8 målstørrelse.** Små knapper («Lagre» i rad) kan bli under 24 px høye. *Fix:* minst 24 × 24 px er lagt inn som regel.
- **low · 2.2.1 tidsbegrensning.** Grønne bekreftelseslinjer forsvinner etter 5 sekunder. De er statusmeldinger som også meldes med `aria-live`, så det er akseptert.
