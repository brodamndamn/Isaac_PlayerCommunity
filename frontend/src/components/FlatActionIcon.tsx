type ActionIconName = "like" | "favorite" | "comment";

interface FlatActionIconProps {
  name: ActionIconName;
  active?: boolean;
  size?: number;
}

/** 扁平线性图标：避免 Emoji 因系统字体不同出现立体效果。 */
export default function FlatActionIcon({ name, active = false, size = 15 }: FlatActionIconProps) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: active ? "currentColor" : "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
  };

  if (name === "like") {
    return <svg {...common}><path d="M20.8 4.9a5.4 5.4 0 0 0-7.6 0L12 6.1l-1.2-1.2a5.4 5.4 0 0 0-7.6 7.6L12 21l8.8-8.5a5.4 5.4 0 0 0 0-7.6Z" /></svg>;
  }

  if (name === "favorite") {
    return <svg {...common}><path d="m12 3 2.78 5.64 6.22.9-4.5 4.39 1.06 6.2L12 17.2l-5.56 2.93 1.06-6.2L3 9.54l6.22-.9L12 3Z" /></svg>;
  }

  return <svg {...common}><path d="M4 4.5h16v11H9l-5 4v-15Z" /><path d="M8 9h8M8 12.5h5" /></svg>;
}
