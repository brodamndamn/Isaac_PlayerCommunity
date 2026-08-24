import { Fragment, type ReactNode } from "react";
import { normalizeMediaUrl } from "../lib/paths";

interface SimpleMarkdownProps {
  content: string;
  emptyText?: string;
}

function renderInline(text: string, lineIndex: number): ReactNode[] {
  const nodes: ReactNode[] = [];
  const pattern = /!\[([^\]]*)\]\(([^)]+)\)|\*\*(.+?)\*\*/g;
  let cursor = 0;
  let partIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > cursor) {
      nodes.push(text.slice(cursor, match.index));
    }

    if (match[1] !== undefined) {
      const src = normalizeMediaUrl(match[2]);
      if (src) {
        nodes.push(
          <img
            key={`${lineIndex}-image-${partIndex}`}
            src={src}
            alt={match[1]}
            style={{ maxWidth: "100%", borderRadius: 6, margin: "8px 0" }}
          />,
        );
      } else if (match[1]) {
        nodes.push(match[1]);
      }
    } else {
      nodes.push(
        <strong key={`${lineIndex}-strong-${partIndex}`}>{match[3]}</strong>,
      );
    }

    cursor = pattern.lastIndex;
    partIndex += 1;
  }

  if (cursor < text.length) {
    nodes.push(text.slice(cursor));
  }
  return nodes;
}

export default function SimpleMarkdown({ content, emptyText }: SimpleMarkdownProps) {
  if (!content) {
    return emptyText ? <span>{emptyText}</span> : null;
  }

  return content.split("\n").map((line, index) => {
    const heading = /^(#{1,3})\s+(.+)$/.exec(line);
    if (heading?.[1] === "#") {
      return <h2 key={index}>{renderInline(heading[2], index)}</h2>;
    }
    if (heading?.[1] === "##") {
      return <h3 key={index}>{renderInline(heading[2], index)}</h3>;
    }
    if (heading?.[1] === "###") {
      return <h4 key={index}>{renderInline(heading[2], index)}</h4>;
    }
    return (
      <Fragment key={index}>
        {renderInline(line, index)}
        <br />
      </Fragment>
    );
  });
}
