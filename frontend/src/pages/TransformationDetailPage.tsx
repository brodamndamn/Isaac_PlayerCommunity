import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getTransformationById } from "../api/transformations";
import type { Transformation } from "../types/transformation";
import styles from "./TransformationDetailPage.module.css";

export default function TransformationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [item, setItem] = useState<Transformation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getTransformationById(Number(id))
      .then((res) => setItem(res.data!))
      .catch(() => setError("套装效果不存在"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p className={styles.status}>加载中...</p>;
  if (error) return <p className={styles.status} style={{ color: "#c0392b" }}>{error}</p>;
  if (!item) return null;

  return (
    <div className={styles.container}>
      <button onClick={() => navigate(-1)} className={styles.back}>&larr; 返回</button>

      <div className={styles.titleRow}>
        {item.first_item_id ? (
          <img
            src={`/images/items/${item.first_item_id}.png`}
            alt={item.name_cn || item.name_en}
            className={styles.thumb}
            data-item-id={item.first_item_id}
          />
        ) : (
          <div className={styles.imagePlaceholder}>
            <span>套装</span>
          </div>
        )}
        <div>
          <h1 className={styles.name}>{item.name_cn || item.name_en}</h1>
          <p className={styles.nameEn}>{item.name_en}</p>
        </div>
      </div>

      <table className={styles.table}>
        <tbody>
          <tr>
            <td className={styles.label}>ID</td>
            <td>{item.id}</td>
          </tr>
          <tr>
            <td className={styles.label}>需要道具数</td>
            <td>{(item.required_items_enriched || []).length > 1
              ? `任意 ${item.items_needed} 个道具即可触发`
              : `需要 ${item.items_needed} 个${item.required_items_enriched?.[0]?.name_cn || ''}`
            }</td>
          </tr>
        </tbody>
      </table>

      <section className={styles.section}>
        <h3>所需道具</h3>
        <div className={styles.itemList}>
          {(item.required_items_enriched || []).map((ei, i) => (
            <span key={i} className={styles.itemTag}>
              {ei.image_url ? (
                <img
                  src={`/images/${ei.image_url}`}
                  alt={ei.name_cn}
                  className={styles.itemIcon}
                  data-item-id={ei.id ?? undefined}
                />
              ) : (
                <span className={styles.itemIconPlaceholder} data-item-id={ei.id ?? undefined} />
              )}
              {ei.name_cn || ei.name_en}
            </span>
          ))}
        </div>
      </section>

      {item.effect && (
        <section className={styles.section}>
          <h3>套装效果</h3>
          <p className={styles.effectText}>{item.effect}</p>
        </section>
      )}
    </div>
  );
}
