import styles from "./HealthHearts.module.css";

interface Props {
  health: string;
  /** 图片尺寸 px，默认 16 */
  size?: number;
}

/**
 * 把 "3❤" / "3❤ + 3🖤" / "随机" 这类 health 字符串渲染成 N 张心形图片。
 * 心形 emoji → 图片映射：❤→red  💙→soul  🖤→black  💛→gold  🤍→eternal  🦴→bone  💚→rotten
 * 无法解析（"随机"、"?"）→ 原样输出文字
 */
const EMOJI_TO_KEY: Record<string, string> = {
  "❤": "red",
  "💙": "soul",
  "🖤": "black",
  "💛": "gold",
  "🤍": "eternal",
  "🦴": "bone",
  "💚": "rotten",
  "💰": "coin",
};

export default function HealthHearts({ health, size = 16 }: Props) {
  if (!health || !health.trim()) {
    return <span className={styles.hearts}>—</span>;
  }

  const parts = health.split("+").map((p) => p.trim()).filter(Boolean);
  if (parts.length === 0) {
    return <span className={styles.hearts}>—</span>;
  }

  return (
    <span className={styles.hearts}>
      {parts.map((part, i) => (
        <span key={i} className={styles.group}>
          {renderGroup(part, size)}
          {i < parts.length - 1 && <span className={styles.plus}>+</span>}
        </span>
      ))}
    </span>
  );
}

function renderGroup(part: string, size: number) {
  const m = /^(\d+(?:\.\d+)?)?(.*)$/.exec(part);
  if (!m) return <>{part}</>;

  const numStr = m[1];
  const heart = m[2];

  // 没有数字部分（"随机" / "?" 等），原样展示
  if (!numStr) {
    return <>{part}</>;
  }

  const count = parseFloat(numStr);
  if (!Number.isFinite(count) || count <= 0) {
    return <>—</>;
  }

  const full = Math.floor(count);
  const hasHalf = count - full === 0.5;
  const key = EMOJI_TO_KEY[heart];

  // 有对应图片就渲染图片，否则回退到 emoji
  if (key) {
    return (
      <>
        {Array.from({ length: full }, (_, i) => (
          <img
            key={i}
            src={`/images/heart/${key}.png`}
            alt={key}
            className={styles.heartImg}
            style={{ width: size, height: size }}
          />
        ))}
        {hasHalf && (
          <span className={styles.halfWrap} style={{ width: size, height: size }}>
            <img
              src={`/images/heart/${key}.png`}
              alt={key}
              className={styles.heartImg}
              style={{ width: size, height: size }}
            />
          </span>
        )}
      </>
    );
  }

  // 回退：用 emoji 文字
  return (
    <>
      {heart.repeat(full)}
      {hasHalf && <span className={styles.half}>{heart}</span>}
    </>
  );
}