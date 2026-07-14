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

// 解析道具池文字中的图片占位符 [img:pool/xxx]
function parsePoolEntry(entry: string): { img?: string; label: string } {
  const match = entry.match(/^\[img:(.+?)\]\s*(.*)/);
  if (match) {
    return { img: match[1], label: match[2] || match[1] };
  }
  return { label: entry };
}

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

  // 道具池：解析 [img:pool/xxx] 占位符 + 中文名
  const poolEntries = item.item_pools?.map(parsePoolEntry) ?? [];

  return (
    <div className={styles.container}>
      <button onClick={() => navigate(-1)} className={styles.back}>&larr; 返回</button>
      {/* 标题区域 */}
      <div className={styles.titleRow}>
        {item.image_url ? (
          <img
            src={`/images/${item.image_url}`}
            alt={item.name_cn || item.name_en}
            className={styles.itemImage}
          />
        ) : (
          <div className={styles.imagePlaceholder}>
            <span>图片</span>
          </div>
        )}
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
              <td>{item.recharge_time}</td>
            </tr>
          )}
          <tr>
            <td className={styles.label}>道具池</td>
            <td>
              {poolEntries.length > 0 ? (
                <div className={styles.poolList}>
                  {poolEntries.map((entry, i) => (
                    <span key={i} className={styles.poolItem}>
                      {entry.img ? (
                        <img
                          src={`/images/${entry.img}.png`}
                          alt={entry.label}
                          className={styles.poolIcon}
                        />
                      ) : (
                        <span className={styles.poolIconPlaceholder} />
                      )}
                      {entry.label}
                    </span>
                  ))}
                </div>
              ) : (
                "未知"
              )}
            </td>
          </tr>
          {item.unlock_method && (
            <tr>
              <td className={styles.label}>解锁方式</td>
              <td>{item.unlock_method}</td>
            </tr>
          )}
        </tbody>
      </table>

      {/* 属性变化表格 */}
      {item.stat_changes && item.stat_changes.length > 0 && (
        <section className={styles.section}>
          <h3>属性变化</h3>
          <table className={styles.statTable}>
            <thead>
              <tr>
                <th>属性</th>
                <th>加成 / 削弱</th>
              </tr>
            </thead>
            <tbody>
              {item.stat_changes.map((row, i) => {
                // row[0] = "[img:stat/damage] 伤害", row[1] = "+1.00"
                const attrMatch = row[0].match(/^\[img:(.+?)\]\s*(.*)/);
                const imgPath = attrMatch ? attrMatch[1] : null;
                const attrName = attrMatch ? attrMatch[2] : row[0];
                return (
                  <tr key={i}>
                    <td className={styles.statAttr}>
                      {imgPath ? (
                        <img
                          src={`/images/${imgPath}.png`}
                          alt={attrName}
                          className={styles.statIcon}
                        />
                      ) : (
                        <span className={styles.statIconPlaceholder} />
                      )}
                      {attrName}
                    </td>
                    <td className={styles.statValue}>{row[1]}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </section>
      )}

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
