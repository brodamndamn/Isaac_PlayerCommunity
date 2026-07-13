import styles from "./HealthHearts.module.css";

interface Props {
  health: string;
}

/**
 * 把 "3❤" / "3❤ + 3💙" / "随机" 这类 health 字符串渲染成 N 颗心形图标。
 * - 整数 N → 重复心形 N 次
 * - 半心（N.5）→ 加一颗半心（CSS scaleX）
 * - 复合（X❤ + Y💙）→ 按 + 拆开分组渲染
 * - 无法解析（"随机"、"?"）→ 原样输出
 */
export default function HealthHearts({ health }: Props) {
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
        <span key={i}>
          {renderGroup(part)}
          {i < parts.length - 1 && <span className={styles.plus}>+</span>}
        </span>
      ))}
    </span>
  );
}

function renderGroup(part: string) {
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

  return (
    <>
      {heart.repeat(full)}
      {hasHalf && <span className={styles.half}>{heart}</span>}
    </>
  );
}
