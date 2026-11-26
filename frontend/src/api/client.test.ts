import { afterEach, describe, expect, it, vi } from "vitest";
import {
  ApiError,
  apiFetch,
  NetworkError,
  setUnauthorizedHandler,
} from "./client";

function stubFetch(response: Response | Error) {
  const fetchMock = vi.fn(async () => {
    if (response instanceof Error) throw response;
    return response;
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function json(status: number, body: unknown) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
  setUnauthorizedHandler(null);
});

describe("apiFetch", () => {
  it.each([502, 504])(
    "AD-11: %i fra proxyen gir NetworkError",
    async (status) => {
      stubFetch(new Response("", { status }));
      await expect(apiFetch("/api/health")).rejects.toBeInstanceOf(
        NetworkError,
      );
    },
  );

  it("AD-11: avvist fetch gir NetworkError", async () => {
    stubFetch(new TypeError("Failed to fetch"));
    await expect(apiFetch("/api/health")).rejects.toBeInstanceOf(NetworkError);
  });

  it.each(["/api/auth/login", "/api/auth/me"])(
    "FR-1: 401 på %s kaller ikke handleren for utløpt sesjon",
    async (path) => {
      const handler = vi.fn();
      setUnauthorizedHandler(handler);
      stubFetch(json(401, { detail: "Feil brukernavn eller passord." }));
      await expect(apiFetch(path)).rejects.toBeInstanceOf(ApiError);
      expect(handler).not.toHaveBeenCalled();
    },
  );

  it("FR-1: 401 på en annen sti kaller handleren og kaster ApiError med detail", async () => {
    const handler = vi.fn();
    setUnauthorizedHandler(handler);
    stubFetch(json(401, { detail: "Du er ikke logget inn." }));
    const error = await apiFetch("/api/auth/logout", { method: "POST" }).catch(
      (caught: unknown) => caught,
    );
    expect(handler).toHaveBeenCalledOnce();
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(401);
    expect((error as ApiError).detail).toBe("Du er ikke logget inn.");
  });

  it("FR-1: liste-detail (422) kommer tilbake som JSON-tekst", async () => {
    const detail = [{ loc: ["body", "username"], msg: "Field required" }];
    stubFetch(json(422, { detail }));
    const error = await apiFetch("/api/auth/login", {
      method: "POST",
      body: {},
    }).catch((caught: unknown) => caught);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(422);
    expect((error as ApiError).detail).toBe(JSON.stringify(detail));
  });

  it("FR-1: 204 med tom kropp gir undefined", async () => {
    stubFetch(new Response(null, { status: 204 }));
    await expect(
      apiFetch("/api/auth/logout", { method: "POST" }),
    ).resolves.toBeUndefined();
  });
});
