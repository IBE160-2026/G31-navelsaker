import { type FormEvent, useEffect, useRef, useState } from "react";
import { Navigate, useLocation } from "react-router";
import { ApiError } from "../api/client";
import { type LoginLocationState, useAuth } from "../auth/AuthProvider";
import { Logo } from "../components/Logo";
import "./LoginPage.css";

type LoginError = "credentials" | "server" | null;

const ERROR_ID = "login-error";
const PASSWORD_ID = "login-password";

/** Innloggingssiden `/logg-inn` (FR-1, UX-DR5). */
export function LoginPage() {
  const { user, notice, login, clearSignedOut } = useAuth();
  const location = useLocation();
  const from = (location.state as LoginLocationState | null)?.from;

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<LoginError>(
    notice === "server-error" ? "server" : null,
  );
  const usernameRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    document.title = "Logg inn – Red Ball Express";
  }, []);

  useEffect(() => {
    if (notice === "signed-out") clearSignedOut();
  }, [notice, clearSignedOut]);

  if (user) {
    const target = from ? `${from.pathname}${from.search}${from.hash}` : "/";
    return <Navigate to={target} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    // Skjul passordet igjen før det sendes, så nettleseren ikke lagrer feltet som vanlig tekst.
    setShowPassword(false);
    setPending(true);
    setError(null);
    try {
      await login(username, password);
    } catch (caught: unknown) {
      if (caught instanceof ApiError && caught.status === 401) {
        setError("credentials");
        usernameRef.current?.focus();
      } else {
        setError("server");
      }
    } finally {
      setPending(false);
    }
  }

  const invalid = error === "credentials";

  return (
    <main className="login">
      <div className="login-card">
        {notice === "expired" && (
          <p className="login-card__notice">
            Du er logget ut. Logg inn igjen for å fortsette.
          </p>
        )}
        <Logo variant="stacked" className="login-card__logo" />
        <h1 className="login-card__title">Logg inn</h1>

        <div className="login-card__banner-slot" aria-live="assertive">
          {error === "server" && (
            <p className="error-banner">
              Fikk ikke kontakt med serveren. Prøv igjen.
            </p>
          )}
        </div>

        <form className="login-card__form" onSubmit={handleSubmit} noValidate>
          <label className="field">
            <span className="field__label">Brukernavn</span>
            <input
              ref={usernameRef}
              className="field__input"
              name="username"
              type="text"
              autoComplete="username"
              // biome-ignore lint/a11y/noAutofocus: UX-DR5 krever autofokus på brukernavnet.
              autoFocus
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              aria-invalid={invalid || undefined}
              aria-describedby={invalid ? ERROR_ID : undefined}
            />
          </label>
          <div className="field">
            <div className="field__label-row">
              <label className="field__label" htmlFor={PASSWORD_ID}>
                Passord
              </label>
              <button
                className="field__toggle"
                type="button"
                aria-controls={PASSWORD_ID}
                onClick={() => setShowPassword((shown) => !shown)}
              >
                {showPassword ? "Skjul passord" : "Vis passord"}
              </button>
            </div>
            <input
              id={PASSWORD_ID}
              className="field__input"
              name="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              aria-invalid={invalid || undefined}
              aria-describedby={invalid ? ERROR_ID : undefined}
            />
          </div>

          <button
            className="button-primary login-card__submit"
            type="submit"
            disabled={pending}
            aria-live="polite"
          >
            {pending ? "Logger inn …" : "Logg inn"}
          </button>

          {invalid && (
            <p id={ERROR_ID} className="login-card__error">
              Feil brukernavn eller passord.
            </p>
          )}
        </form>

        <p className="login-card__hint">Demobrukeren står i README</p>
      </div>
    </main>
  );
}
