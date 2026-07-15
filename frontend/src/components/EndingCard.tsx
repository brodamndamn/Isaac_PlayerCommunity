import { Link } from "react-router-dom";
import type { Ending } from "../types/ending";
import styles from "./EndingCard.module.css";

interface EndingCardProps {
  ending: Ending;
}

export default function EndingCard({ ending }: EndingCardProps) {
  return (
    <Link to={`/endings/${ending.id}`} className={styles.card}>
      <span className={styles.number}>#{ending.ending_number}</span>
      <div className={styles.titleRow}>
        <h3 className={styles.name}>{ending.name_cn}</h3>
        {ending.image_url ? (
          <img
            src={`/images/${ending.image_url}`}
            alt={ending.boss_name}
            className={styles.bossImg}
            data-boss={ending.boss_name}
          />
        ) : (
          <div className={styles.bossImg} data-boss={ending.boss_name} />
        )}
      </div>
      <p className={styles.nameEn}>{ending.name_en}</p>
      <div className={styles.boss}>
        <span className={styles.bossLabel}>Boss：</span>
        {ending.boss_name}
      </div>
      <p className={styles.method}>{ending.completion_method}</p>
      {ending.unlocks && ending.unlocks.length > 0 && (
        <p className={styles.unlocks}>
          解锁：{ending.unlocks.join(" / ")}
        </p>
      )}
    </Link>
  );
}
