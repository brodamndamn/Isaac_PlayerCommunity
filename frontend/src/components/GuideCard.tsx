import { Link } from "react-router-dom";
import type { Guide } from "../types/guide";
import styles from "./GuideCard.module.css";

const CATEGORY_LABELS: Record<string, string> = {
  general: "综合",
  item: "道具",
  character: "角色",
  ending: "结局",
};

interface GuideCardProps {
  guide: Guide;
}

export default function GuideCard({ guide }: GuideCardProps) {
  const date = new Date(guide.created_at).toLocaleDateString("zh-CN");
  const coverUrl = guide.cover_image || null;

  return (
    <Link to={`/guides/${guide.id}`} className={styles.card}>
      {coverUrl && (
        <div className={styles.coverWrap}>
          <img src={coverUrl} alt="" className={styles.cover} />
        </div>
      )}
      <div className={styles.header}>
        <span className={`${styles.category} ${styles[guide.category] || ""}`}>{CATEGORY_LABELS[guide.category] || guide.category}</span>
        <span className={styles.date}>{date}</span>
      </div>
      <h3 className={styles.title}>{guide.title}</h3>
      <p className={styles.author}>@{guide.author_name}</p>
    </Link>
  );
}
