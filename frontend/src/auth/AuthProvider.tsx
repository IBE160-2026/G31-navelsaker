import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Navigate, Outlet, useLocation } from "react-router";
import { ApiError, apiFetch, setUnauthorizedHandler } from "../api/client";

export type User = { username: string };

/**
 * Melding innloggingssiden skal vise uten at brukeren har gjort noe:
 * `expired` når et kall ga 401 etter at innloggingen var bekreftet,
 * `server-error` når `me` ikke fikk svar ved oppstart,
 * `signed-out` når brukeren selv logget ut (ingen melding, og ingen adresse å komme tilbake til).
 */
export type AuthNotice = "expired" | "server-error" | "signed-out" | null;

/** Adressen brukeren ba om, lagt i routerens `state` av ruteverneren. */
export type LoginLocationState = {
  from?: { pathname: string; search: string; hash: string };
};

type AuthContextValue = {
  /** `undefined` til `me` har svart, deretter brukeren eller `null`. */
  user: User | null | undefined;
  notice: AuthNotice;
  login: (username: string, password: string) => Promise<void>;
  /**
   * Logger ut med `POST /api/auth/logout`. 204 og 401 gir utlogget uten melding.
   * `NetworkError` (og andre feil) kastes videre, og brukeren er da fortsatt innlogget.
   */
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null | undefined>(undefined);
  const [notice, setNotice] = useState<AuthNotice>(null);
  const userRef = useRef(user);
  userRef.current = user;
  const loggingOutRef = useRef(false);

  useEffect(() => {
    let cancelled = false;
    apiFetch<User>("/api/auth/me")
      .then((me) => {
        if (!cancelled) setUser(me);
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        setUser(null);
        if (!(error instanceof ApiError && error.status === 401)) {
          setNotice("server-error");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      // Bare en bekreftet innlogging kan utløpe. Uinnlogget gir ingen melding.
      // 401 på utlogging er ikke en utløpt sesjon: `logout` tar hånd om den selv.
      if (userRef.current && !loggingOutRef.current) {
        setUser(null);
        setNotice("expired");
      }
    });
    return () => setUnauthorizedHandler(null);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const me = await apiFetch<User>("/api/auth/login", {
      method: "POST",
      body: { username, password },
    });
    setNotice(null);
    setUser(me);
  }, []);

  const logout = useCallback(async () => {
    loggingOutRef.current = true;
    try {
      await apiFetch<void>("/api/auth/logout", { method: "POST" });
    } catch (error: unknown) {
      // 401: sesjonen var allerede borte på serveren, og brukeren er like fullt logget ut.
      if (!(error instanceof ApiError && error.status === 401)) throw error;
    } finally {
      loggingOutRef.current = false;
    }
    setNotice("signed-out");
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, notice, login, logout }),
    [user, notice, login, logout],
  );

  return (
    <AuthContext value={value}>
      {user === undefined ? <AuthLoading /> : children}
    </AuthContext>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth må brukes inne i AuthProvider.");
  }
  return context;
}

/** Viser «Henter …» til `me` har svart. */
export function AuthLoading() {
  return (
    <main className="page">
      <p className="muted" aria-live="polite">
        Henter …
      </p>
    </main>
  );
}

/**
 * Ruteverneren: uinnloggede sendes til /logg-inn med adressen de ba om.
 * Etter egen utlogging huskes ingen adresse, så neste innlogging går til `/`.
 */
export function RequireAuth() {
  const { user, notice } = useAuth();
  const location = useLocation();

  if (!user && notice === "signed-out") {
    return <Navigate to="/logg-inn" replace />;
  }
  if (!user) {
    const state: LoginLocationState = {
      from: {
        pathname: location.pathname,
        search: location.search,
        hash: location.hash,
      },
    };
    return <Navigate to="/logg-inn" replace state={state} />;
  }
  return <Outlet />;
}
