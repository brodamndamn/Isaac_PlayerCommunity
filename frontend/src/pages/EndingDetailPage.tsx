import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getEndingById } from "../api/endings";
import type { Ending } from "../types/ending";
import styles from "./EndingDetailPage.module.css";

export default function EndingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [ending, setEnding] = useState<Ending | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getEndingById(Number(id))
      .then((res) => setEnding(res.data!))
      .catch(() => setError("结局不存在"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p className={styles.status}>加载中...</p>;
  if (error) return <p className={styles.status} style={{ color: "#c0392b" }}>{error}</p>;
  if (!ending) return null;

  return (
    <div className={styles.container}>
      <button onClick={() => navigate(-1)} className={styles.back}>&larr; 返回</button>
      <div className={styles.titleRow}>
        <h1 className={styles.title}>
          {ending.name_cn}
          <span className={styles.num}> #{ending.ending_number}</span>
        </h1>
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

      <table className={styles.table}>
        <tbody>
          <tr>
            <td className={styles.label}>Boss</td>
            <td>{ending.boss_name}</td>
          </tr>
          <tr>
            <td className={styles.label}>完成方式</td>
            <td>{ending.completion_method}</td>
          </tr>
          {ending.unlock_method && (
            <tr>
              <td className={styles.label}>解锁条件</td>
              <td>{ending.unlock_method}</td>
            </tr>
          )}
          {ending.required_character && (
            <tr>
              <td className={styles.label}>指定角色</td>
              <td>{ending.required_character}</td>
            </tr>
          )}
          {ending.unlocks_enriched && ending.unlocks_enriched.length > 0 && (
            <tr>
              <td className={styles.label}>完成后解锁</td>
              <td>
                <div className={styles.unlockList}>
                  {ending.unlocks_enriched.map((u, i) => {
                    const id = u.item_id ?? u.character_id ?? undefined;
                    const isHeading = u.unlock_type === "system" && !u.image_url;
                    return (
                      <div key={i} className={`${styles.unlockRow} ${isHeading ? styles.unlockHeading : ""}`}>
                        {u.label_cn && (
                          <span className={`${styles.typeBadge} ${styles["badge_" + u.unlock_type] || styles.badge_unknown}`}>
                            {u.label_cn}
                          </span>
                        )}
                        {u.image_url ? (
                          <img src={`/images/${u.image_url}`} alt={u.text} className={styles.unlockIcon} data-item-id={id} />
                        ) : id ? (
                          <span className={styles.unlockIconPlaceholder} data-item-id={id} />
                        ) : null}
                        <span className={isHeading ? styles.headingText : styles.unlockText}>{u.text}</span>
                      </div>
                    );
                  })}
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
