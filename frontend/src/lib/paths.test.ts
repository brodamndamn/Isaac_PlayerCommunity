import { describe, expect, it } from "vitest";
import { APP_BASE_PATH, normalizeMediaUrl, staticUrl } from "./paths";

describe("ISAAC public paths", () => {
  it("uses /isaac as the application base path", () => {
    expect(APP_BASE_PATH).toBe("/isaac");
  });

  it("prefixes public images with the application base path", () => {
    expect(staticUrl("images/items/1.png")).toBe("/isaac/images/items/1.png");
    expect(staticUrl("/images/items/1.png")).toBe("/isaac/images/items/1.png");
  });

  it("does not add the application prefix twice", () => {
    expect(staticUrl("/isaac/images/items/1.png")).toBe("/isaac/images/items/1.png");
    expect(normalizeMediaUrl("/isaac/uploads/guides/cover.png")).toBe(
      "/isaac/uploads/guides/cover.png",
    );
  });

  it("normalizes legacy image and upload paths", () => {
    expect(normalizeMediaUrl("/images/characters/1.png")).toBe(
      "/isaac/images/characters/1.png",
    );
    expect(normalizeMediaUrl("/uploads/guides/cover.png")).toBe(
      "/isaac/uploads/guides/cover.png",
    );
  });

  it("keeps external HTTP and HTTPS media URLs unchanged", () => {
    expect(normalizeMediaUrl("http://example.com/a.png")).toBe(
      "http://example.com/a.png",
    );
    expect(normalizeMediaUrl("https://example.com/a.png")).toBe(
      "https://example.com/a.png",
    );
  });
  it("normalizes local media paths without a leading slash", () => {
    expect(normalizeMediaUrl("images/items/1.png")).toBe(
      "/isaac/images/items/1.png",
    );
    expect(normalizeMediaUrl("uploads/guides/cover.png")).toBe(
      "/isaac/uploads/guides/cover.png",
    );
  });

  it("rejects unsafe media protocols", () => {
    expect(normalizeMediaUrl("javascript:alert(1)")).toBe("");
    expect(normalizeMediaUrl("data:text/html,unsafe")).toBe("");
  });
});
