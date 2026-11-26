import { PageTitle } from "../components/PageTitle";

/** Plassholder for skjermbildene som kommer i senere epics. */
export function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="page">
      <PageTitle title={title} />
      <p>Dette skjermbildet er ikke laget ennå.</p>
    </div>
  );
}
