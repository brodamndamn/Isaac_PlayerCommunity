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
      <h3 className={styles.name}>{ending.name_cn}</h3>
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
