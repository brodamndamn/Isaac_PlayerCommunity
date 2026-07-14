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
  // 判定是否为药丸（category === 'pill'），用对应的 _shared sprite
  // 或者其他 image_url（如 _shared/xxx 或 items/xxx）
  const pillSprite = item.category === "pill";
  const imgSrc = item.image_url
    ? `/images/${item.image_url}`
    : null;

  return (
    <Link to={`/items/${item.id}`} className={`${styles.card} ${styles[BORDER_CLASS[item.category]] || ""}`}>
      {/* 上半：图左 + 标题右 */}
      <div className={styles.topRow}>
        {imgSrc ? (
          <img
            src={imgSrc}
            alt={item.name_cn || item.name_en}
            className={pillSprite ? styles.pillThumb : styles.thumb}
            loading="lazy"
          />
        ) : (
          <div className={styles.thumbPlaceholder} />
        )}
        <div className={styles.titleCol}>
          <div className={styles.headerRow}>
            <span className={styles.id}>#{item.id}</span>
            <span className={`${styles.category} ${styles[TAG_CLASS[item.category]] || ""}`}>
              {CATEGORY_LABELS[item.category] || item.category}
            </span>
          </div>
          <h3 className={styles.name}>{item.name_cn || item.name_en}</h3>
          <p className={styles.nameEn}>{item.name_en}</p>
        </div>
      </div>
      {/* 下半：描述 + 星级 */}
      <div className={styles.bottomRow}>
        {item.pick_up_text && (
          <p className={styles.quote}>"{item.pick_up_text}"</p>
        )}
        <p className={styles.desc}>{item.effect || item.description}</p>
        {item.quality != null && (
          <div className={styles.quality}>
            {"★".repeat(item.quality)}{"☆".repeat(4 - item.quality)}
          </div>
        )}
      </div>
    </Link>
  );
}