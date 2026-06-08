import { describe, expect, it } from "vitest";

import { createAdminTokenProvider } from "./adminTokenProvider";

describe("createAdminTokenProvider", () => {
  it("fails closed until an admin session boundary supplies a token", () => {
    const provider = createAdminTokenProvider();

    expect(provider.getAuthToken()).toBe("");
  });

  it("does not read Vite environment token names", () => {
    const providerSource = createAdminTokenProvider.toString();

    const forbiddenViteTokenEnv = "VITE_ADMIN" + "_API_TOKEN";

    expect(providerSource).not.toContain(forbiddenViteTokenEnv);
    expect(providerSource).not.toContain("import.meta.env");
  });

  it("does not persist admin bearer tokens in browser storage", () => {
    const providerSource = createAdminTokenProvider.toString();

    expect(providerSource).not.toContain("localStorage");
    expect(providerSource).not.toContain("sessionStorage");
  });
});
