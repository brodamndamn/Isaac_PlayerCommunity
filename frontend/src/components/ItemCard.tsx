import { Link } from "react-router-dom";
import type { Item } from "../types/item";
import styles from "./ItemCard.module.css";

interface ItemCardProps {
  item: Item;
}

const CATEGORY_LABELS: Record<string, string> = {
  passive: "被动",
  active: "主动",
  trinket: "饰品",
  card: "卡牌",
  pill: "药丸",
};

// CSS 类名映射 — 避免 .card 容器同名冲突
const TAG_CLASS: Record<string, string> = {
  passive: "passive",
  active: "active",
  trinket: "trinket",
  card: "catCard",
  pill: "pill",
};
const BORDER_CLASS: Record<string, string> = {
  passive: "bPassive",
  active: "bActive",
  trinket: "bTrinket",
  card: "bCard",
  pill: "bPill",
};

export default function ItemCard({ item }: ItemCardProps) {
  return (
    <Link to={`/items/${item.id}`} className={`${styles.card} ${styles[BORDER_CLASS[item.category]] || ""}`}>
      <div className={styles.header}>
        <span className={styles.id}>#{item.id}</span>
        <span className={`${styles.category} ${styles[TAG_CLASS[item.category]] || ""}`}>
          {CATEGORY_LABELS[item.category] || item.category}
        </span>
      </div>
      <h3 className={styles.name}>{item.name_cn || item.name_en}</h3>
      {item.pick_up_text && (
        <p className={styles.quote}>"{item.pick_up_text}"</p>
      )}
      <p className={styles.desc}>{item.effect || item.description}</p>
      {item.quality != null && (
        <div className={styles.quality}>
          {"★".repeat(item.quality)}{"☆".repeat(4 - item.quality)}
        </div>
      )}
    </Link>
  );
}
