/**
 * Tynn innpakning rundt fetch for API-et under /api (AD-11).
 *
 * Adressene er relative, så Vite-proxyen gir ett opphav og det trengs ingen CORS.
 * Innloggingen er bare sesjonscookien (AD-8), som sendes med `credentials: "same-origin"`.
 */

/** Serveren svarte, men med en feilstatus. `detail` er FastAPIs feiltekst. */
export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor(status: number, detail: string) {
    super(detail || `HTTP ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

/** Serveren svarte ikke: fetch ble avvist, eller proxyen ga 502–504. */
export class NetworkError extends Error {
  constructor(message = "Fikk ikke kontakt med serveren.") {
    super(message);
    this.name = "NetworkError";
  }
}

/** Kall som selv avgjør innloggingen, og som derfor ikke regnes som utløpt sesjon ved 401. */
const AUTH_PATHS = new Set(["/api/auth/login", "/api/auth/me"]);

let onUnauthorized: (() => void) | null = null;

/**
 * Registrerer hva som skjer når et annet kall enn login og me får 401.
 * Innloggingstilstanden bruker dette til å sende brukeren til /logg-inn.
 */
export function setUnauthorizedHandler(handler: (() => void) | null): void {
  onUnauthorized = handler;
}

type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
};

export async function apiFetch<T>(
  path: string,
  { method = "GET", body }: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  let response: Response;
  try {
    response = await fetch(path, {
      method,
      headers,
      credentials: "same-origin",
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new NetworkError();
  }

  if (response.status >= 502 && response.status <= 504) {
    throw new NetworkError();
  }

  const payload = await readJson(response);

  if (!response.ok) {
    if (response.status === 401 && !AUTH_PATHS.has(path)) {
      onUnauthorized?.();
    }
    throw new ApiError(response.status, detailOf(payload));
  }

  return payload as T;
}

async function readJson(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) {
    return undefined;
  }
  try {
    return JSON.parse(text);
  } catch {
    return undefined;
  }
}

/** FastAPI gir `detail` som tekst, eller som en liste ved valideringsfeil. */
function detailOf(payload: unknown): string {
  if (payload && typeof payload === "object" && "detail" in payload) {
    const { detail } = payload as { detail: unknown };
    if (typeof detail === "string") {
      return detail;
    }
    if (detail !== undefined) {
      return JSON.stringify(detail);
    }
  }
  return "";
}
