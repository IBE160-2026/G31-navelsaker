import { useEffect } from "react";

/** Foreløpig vernet side for alle adresser utenom /logg-inn. Story 1.6 bytter den ut. */
export function SignedInPage() {
  useEffect(() => {
    document.title = "Red Ball Express";
  }, []);

  return (
    <main className="page">
      <h1>Du er logget inn</h1>
      <p>Skjermbildene kommer i neste steg.</p>
    </main>
  );
}
