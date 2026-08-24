import { describe, expect, it } from "vitest";
import { matchRoutes } from "react-router-dom";
import { APP_BASE_PATH } from "./lib/paths";
import { APP_ROUTES } from "./routes";

describe("ISAAC routes", () => {
  it.each([
    "/isaac/items/1",
    "/isaac/characters/1",
    "/isaac/endings/1",
    "/isaac/guides/1",
    "/isaac/transformations/1",
  ])("matches a deep application route: %s", (pathname) => {
    const appPath = pathname.slice(APP_BASE_PATH.length) || "/";
    expect(matchRoutes(APP_ROUTES, appPath)).not.toBeNull();
  });
});
