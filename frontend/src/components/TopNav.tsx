import { Link, NavLink } from "react-router";
import { Logo } from "./Logo";
import "./TopNav.css";

const LINKS = [
  { to: "/forslag", label: "Bestillingsforslag og meldinger" },
  { to: "/mrp", label: "MRP-tabell" },
  { to: "/bom", label: "BOM-tre" },
  { to: "/plan", label: "MPS og lager" },
] as const;

type TopNavProps = {
  username: string;
  onLogout: () => void;
  loggingOut: boolean;
};

/** Menylinjen øverst på alle sider etter innlogging (UX-DR3). */
export function TopNav({ username, onLogout, loggingOut }: TopNavProps) {
  return (
    <header className="top-nav">
      <div className="top-nav__inner">
        <Link
          to="/"
          className="top-nav__home"
          aria-label="Red Ball Express, startside"
        >
          <Logo variant="horizontal" />
        </Link>
        <nav aria-label="Hovedmeny">
          <ul className="top-nav__links">
            {LINKS.map((link) => (
              <li key={link.to}>
                {/* NavLink gir aria-current="page", også på /mrp/… */}
                <NavLink to={link.to} className="top-nav__link">
                  {link.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <p className="top-nav__user">
          <span>{username}</span>
          <span aria-hidden="true">·</span>
          <button
            type="button"
            className="top-nav__logout"
            onClick={onLogout}
            disabled={loggingOut}
          >
            Logg ut
          </button>
        </p>
      </div>
    </header>
  );
}
