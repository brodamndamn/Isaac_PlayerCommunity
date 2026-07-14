import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getItemById } from "../api/items";
import type { Item } from "../types/item";
import styles from "./ItemDetailPage.module.css";

const CATEGORY_LABELS: Record<string, string> = {
  passive: "被动道具",
  active: "主动道具",
  trinket: "饰品",
  card: "卡牌",
  pill: "药丸",
};

const POOL_LABELS: Record<string, string> = {
  treasure: "宝箱房",
  boss: "Boss房",
  shop: "商店",
  devil: "恶魔房",
  angel: "天使房",
  secret_room: "隐藏房",
  library: "图书馆",
  golden_chest: "金宝箱",
  arcade: "街机厅",
  demon_beggar: "恶魔乞丐",
};

export default function ItemDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [item, setItem] = useState<Item | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getItemById(Number(id))
      .then((res) => setItem(res.data!))
      .catch(() => setError("道具不存在"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p className={styles.status}>加载中...</p>;
  if (error) return <p className={styles.status} style={{ color: "#c0392b" }}>{error}</p>;
  if (!item) return null;

  const pools = item.item_pools
    ?.map((p) => POOL_LABELS[p] || p)
    .join("、") || "未知";

  return (
    <div className={styles.container}>
      <button onClick={() => navigate(-1)} className={styles.back}>&larr; 返回</button>
      {/* 标题区域 */}
      <div className={styles.titleRow}>
        <div className={styles.imagePlaceholder}>
          <span>图片</span>
        </div>
        <div>
          <h1 className={styles.name}>{item.name_cn || item.name_en}</h1>
          <p className={styles.nameEn}>{item.name_en}</p>
        </div>
      </div>

      {item.pick_up_text && (
        <blockquote className={styles.quote}>"{item.pick_up_text}"</blockquote>
      )}

      {/* 属性表格 */}
      <table className={styles.table}>
        <tbody>
          <tr>
            <td className={styles.label}>ID</td>
            <td>{item.id}</td>
          </tr>
          <tr>
            <td className={styles.label}>分类</td>
            <td>{CATEGORY_LABELS[item.category] || item.category}</td>
          </tr>
          <tr>
            <td className={styles.label}>品质</td>
            <td className={styles.quality}>
              {item.quality != null
                ? "★".repeat(item.quality) + "☆".repeat(4 - item.quality)
                : "—"}
            </td>
          </tr>
          {item.recharge_time && (
            <tr>
              <td className={styles.label}>充能</td>
              <td>{item.recharge_time} 格</td>
            </tr>
          )}
          <tr>
            <td className={styles.label}>道具池</td>
            <td>{pools}</td>
          </tr>
          {item.unlock_method && (
            <tr>
              <td className={styles.label}>解锁方式</td>
              <td>{item.unlock_method}</td>
            </tr>
          )}
        </tbody>
      </table>

      {/* 效果描述 */}
      <section className={styles.section}>
        <h3>效果</h3>
        <div className={styles.effectRow}>
          <div className={styles.effectText}>
            {/* 中文效果（优先） */}
            {item.effect ? (
              <p className={styles.effectCn}>{item.effect}</p>
            ) : (
              <p>{item.description || "暂无描述"}</p>
            )}
            {/* 英文描述（参考） */}
            {item.effect && item.description && (
              <p className={styles.effectEn}>{item.description}</p>
            )}
          </div>
          <div className={styles.effectImagePlaceholder}>
            <span>效果图</span>
          </div>
        </div>
      </section>

      {/* 适合角色（后续填充数据后展示） */}
      {item.suitable_characters && item.suitable_characters.length > 0 && (
        <section className={styles.section}>
          <h3>适合角色</h3>
          <div className={styles.charRow}>
            {item.suitable_characters.map((cid) => (
              <div key={cid} className={styles.charPlaceholder}>
                <span>角色{cid}</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
