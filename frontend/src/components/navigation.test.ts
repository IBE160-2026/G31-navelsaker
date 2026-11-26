import { beforeEach, describe, expect, it, vi } from "vitest";

type Navigation = typeof import("./navigation");
let navigation: Navigation;

beforeEach(async () => {
  vi.resetModules();
  navigation = await import("./navigation");
});

describe("UX-DR21: fokus til H1 ved sidebytte", () => {
  it("flytter ikke fokus ved første lasting, heller ikke når effekten kjører to ganger", () => {
    navigation.rememberInitialLocation("default");
    expect(navigation.isInAppNavigation("default")).toBe(false);
    expect(navigation.isInAppNavigation("default")).toBe(false);
  });

  it("flytter fokus ved sidebytte, også tilbake til første adresse", () => {
    navigation.rememberInitialLocation("default");
    navigation.rememberInitialLocation("abc123");
    expect(navigation.isInAppNavigation("abc123")).toBe(true);
    expect(navigation.isInAppNavigation("default")).toBe(true);
  });
});
