import { Link } from "react-router";
import { PageTitle } from "../components/PageTitle";

/** Ukjent adresse innenfor appen. */
export function NotFoundPage() {
  return (
    <div className="page">
      <PageTitle title="Fant ikke siden" />
      <p>
        <Link to="/">Til startsiden</Link>
      </p>
    </div>
  );
}
