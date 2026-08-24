import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import SimpleMarkdown from "./SimpleMarkdown";

describe("SimpleMarkdown", () => {
  it("renders uploaded images without allowing HTML attribute injection", () => {
    const html = renderToStaticMarkup(
      <SimpleMarkdown content={'![x" onerror="alert(1)](/uploads/a.png)'} />,
    );

    expect(html).toContain('src="/isaac/uploads/a.png"');
    expect(html).not.toContain('onerror="');
  });

  it("does not render javascript image URLs", () => {
    const html = renderToStaticMarkup(
      <SimpleMarkdown content="![unsafe](javascript:alert(1))" />,
    );

    expect(html).not.toContain("javascript:");
  });
});
