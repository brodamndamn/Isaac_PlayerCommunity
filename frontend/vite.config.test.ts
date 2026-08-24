import { describe, expect, it } from "vitest";
import type { ProxyOptions, UserConfig } from "vite";
import config from "./vite.config";

const userConfig = config as UserConfig;

describe("Vite subpath configuration", () => {
  it("builds ISAAC under /isaac/", () => {
    expect(userConfig.base).toBe("/isaac/");
  });

  it("rewrites the namespaced API and upload proxies for the backend", () => {
    const proxy = userConfig.server?.proxy as Record<string, ProxyOptions>;

    expect(proxy["/isaac/api/"].rewrite?.("/isaac/api/v1/health")).toBe(
      "/api/v1/health",
    );
    expect(proxy["/isaac/uploads/"].rewrite?.("/isaac/uploads/a.png")).toBe(
      "/uploads/a.png",
    );
    expect(proxy["/isaac/api/"].rewrite?.("/isaac/apiary")).toBe(
      "/isaac/apiary",
    );
  });
});
