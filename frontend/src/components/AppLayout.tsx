import { type MouseEvent, useState } from "react";
import { Outlet } from "react-router";
import { useAuth } from "../auth/AuthProvider";
import { TopNav } from "./TopNav";
import "./AppLayout.css";

const MAIN_ID = "innhold";

/** Felles oppsett for alle vernede sider: «Hopp til innhold», menylinjen og `<main>` (UX-DR21, UX-DR22). */
export function AppLayout() {
  const { user, logout } = useAuth();
  const [loggingOut, setLoggingOut] = useState(false);
  const [logoutFailed, setLogoutFailed] = useState(false);

  async function handleLogout() {
    if (loggingOut) return;
    setLoggingOut(true);
    setLogoutFailed(false);
    try {
      await logout();
    } catch {
      // Cookien lever fortsatt på serveren, så innloggingen beholdes.
      setLogoutFailed(true);
      setLoggingOut(false);
    }
  }

  function skipToContent(event: MouseEvent<HTMLAnchorElement>) {
    // Ikke la nettleseren endre hash: det ville vært et sidebytte for routeren.
    event.preventDefault();
    document.getElementById(MAIN_ID)?.focus();
  }

  return (
    <>
      <a className="skip-link" href={`#${MAIN_ID}`} onClick={skipToContent}>
        Hopp til innhold
      </a>
      <TopNav
        username={user?.username ?? ""}
        onLogout={handleLogout}
        loggingOut={loggingOut}
      />
      <main id={MAIN_ID} className="app-main" tabIndex={-1}>
        <div className="app-main__banner" aria-live="assertive">
          {logoutFailed && (
            <p className="error-banner">
              Fikk ikke kontakt med serveren. Prøv igjen.
            </p>
          )}
        </div>
        <Outlet />
      </main>
    </>
  );
}
