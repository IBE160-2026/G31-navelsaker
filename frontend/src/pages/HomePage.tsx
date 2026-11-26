import { Link } from "react-router";
import seaPhoto from "../assets/hav-stavanger-oleksii-topolianskyi.webp";
import { PageTitle } from "../components/PageTitle";
import "./HomePage.css";

const DOORS = [
  {
    to: "/forslag",
    title: "Bestillingsforslag og meldinger",
    text: "Hva som bør bestilles eller startes, og hva som krever oppmerksomhet.",
  },
  {
    to: "/mrp",
    title: "MRP-tabell",
    text: "Beregningen uke for uke for én vare.",
  },
  {
    to: "/bom",
    title: "BOM-tre",
    text: "Produktstrukturen for testfartøyet, med ledetider og mengder.",
  },
  {
    to: "/plan",
    title: "MPS og lager",
    text: "Hovedplanen, lagerbeholdning og åpne ordre. Her gjør du endringer.",
  },
] as const;

/** Startsiden `/` med fire dører (UX-DR4). Viser aldri meldinger. */
export function HomePage() {
  return (
    <div className="home">
      <div className="home-hero">
        <img className="home-hero__photo" src={seaPhoto} alt="" />
        <div className="home-hero__inner">
          <div className="welcome-overlay">
            <PageTitle className="welcome-title" title="Velkommen" />
            <p className="welcome-overlay__lead">Hva vil du gjøre?</p>
          </div>
        </div>
      </div>

      <div className="home-body">
        <ul className="doors">
          {DOORS.map((door) => (
            <li key={door.to}>
              <Link className="door" to={door.to}>
                <h2 className="door__title">{door.title}</h2>
                <p className="door__text">{door.text}</p>
                <span className="door__go">Åpne →</span>
              </Link>
            </li>
          ))}
        </ul>

        {/* Statuslinjen får ekte data i story 3.2. Aldri farge eller antall. */}
        <p className="status-line">Ingen MRP-kjøring ennå.</p>
        <p className="home-credit">Foto: Oleksii Topolianskyi / Unsplash</p>
      </div>
    </div>
  );
}
