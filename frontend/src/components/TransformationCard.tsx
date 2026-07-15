import { Link } from "react-router-dom";
import type { Transformation } from "../types/transformation";
import styles from "./TransformationCard.module.css";

interface Props {
  transformation: Transformation;
}

export default function TransformationCard({ transformation }: Props) {
  return (
    <Link to={`/transformations/${transformation.id}`} className={styles.card}>
      <div className={styles.topRow}>
        {transformation.first_item_id ? (
          <img
            className={styles.thumb}
            src={`/images/items/${transformation.first_item_id}.png`}
            alt={transformation.name_cn || transformation.name_en}
            data-item-id={transformation.first_item_id}
          />
        ) : (
          <div className={styles.thumbPlaceholder} />
        )}
        <div className={styles.titleCol}>
          <div className={styles.headerRow}>
            <span className={styles.id}>#{transformation.id}</span>
            <span className={styles.category}>套装</span>
          </div>
          <h3 className={styles.name}>{transformation.name_cn || transformation.name_en}</h3>
          <p className={styles.nameEn}>{transformation.name_en}</p>
        </div>
      </div>
      <div className={styles.bottomRow}>
        <p className={styles.needed}>
          需要 {transformation.items_needed} 个道具触发
        </p>
        <p className={styles.desc}>{transformation.effect}</p>
      </div>
    </Link>
  );
}
