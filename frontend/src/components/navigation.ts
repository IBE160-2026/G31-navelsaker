/**
 * Skiller første lasting av dokumentet fra sidebytter i appen (UX-DR21).
 *
 * `App` melder fra om første adresse den ser. Så lenge brukeren står på den,
 * flyttes ikke fokus, så «Hopp til innhold» blir første Tab-stopp.
 * Etter første sidebytte flyttes fokus ved hvert sidebytte, også tilbake hit.
 */
let initialKey: string | null = null;
let hasNavigated = false;

export function rememberInitialLocation(key: string): void {
  if (initialKey === null) initialKey = key;
}

/** Sann når denne adressen er et sidebytte i appen, ikke første lasting. */
export function isInAppNavigation(key: string): boolean {
  if (!hasNavigated && key === initialKey) return false;
  hasNavigated = true;
  return true;
}
