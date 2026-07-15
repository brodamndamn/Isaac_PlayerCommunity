import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getCharacterById } from "../api/characters";
import type { Character } from "../types/character";
import styles from "./CharacterDetailPage.module.css";

const HEART_ICONS: Record<string, string> = {
  "❤": "red", "💙": "soul", "🖤": "black",
  "💛": "gold", "🤍": "eternal", "🦴": "bone", "💚": "rotten",
};

export default function CharacterDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [char, setChar] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getCharacterById(Number(id))
      .then((res) => setChar(res.data!))
      .catch(() => setError("角色不存在"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p className={styles.status}>加载中...</p>;
  if (error) return <p className={styles.status} style={{ color: "#c0392b" }}>{error}</p>;
  if (!char) return null;

  return (
    <div className={styles.container}>
      <button onClick={() => navigate(-1)} className={styles.back}>&larr; 返回</button>
      <div className={styles.titleRow}>
        {char.image_url ? (
          <img
            src={`/images/${char.image_url}`}
            alt={char.name_en}
            className={styles.characterImage}
            data-item-id={char.id}
          />
        ) : (
          <div className={styles.imagePlaceholder} data-item-id={char.id}><span>立绘</span></div>
        )}
        <div>
          <h1 className={styles.name}>
            {char.name_cn}
            {char.is_tainted && <span className={styles.taintedBadge}>里</span>}
          </h1>
          <p className={styles.nameEn}>{char.name_en}</p>
        </div>
      </div>

      {/* 基本信息 */}
      <table className={styles.table}>
        <tbody>
          <tr>
            <td className={styles.label}>类型</td>
            <td>{char.is_tainted ? "里角色" : "表角色"}</td>
          </tr>
          {char.base_character_id && (
            <tr>
              <td className={styles.label}>对应表角色</td>
              <td>ID: {char.base_character_id}</td>
            </tr>
          )}
          <tr>
            <td className={styles.label}>生命值</td>
            <td>
              {char.health.split(" ").map((part, i) => {
                const match = part.match(/^(\d*)([❤💙🖤💛🤍🦴💚])$/);
                if (match) {
                  const key = HEART_ICONS[match[2]] || "health";
                  return (
                    <span key={i} className={styles.heartItem}>
                      <span className={styles.statIcon} data-heart={key} />
                      {part}
                    </span>
                  );
                }
                return <span key={i}>{part}</span>;
              })}
            </td>
          </tr>
          {char.starting_items_enriched && char.starting_items_enriched.length > 0 && (
            <tr>
              <td className={styles.label}>初始道具</td>
              <td>
                <div className={styles.itemRow}>
                  {char.starting_items_enriched.map((ei) => (
                    <span key={ei.id} className={styles.itemTag}>
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
              </td>
            </tr>
          )}
          {char.unlock_method && (
            <tr>
              <td className={styles.label}>解锁方式</td>
              <td>{char.unlock_method}</td>
            </tr>
          )}
        </tbody>
      </table>

      {/* 初始属性表格 */}
      {(char.damage != null || char.speed != null || char.tears != null) && (
        <section className={styles.section}>
          <h3>初始属性</h3>
          <table className={styles.statTable}>
            <thead>
              <tr>
                <th>属性</th>
                <th>数值</th>
              </tr>
            </thead>
            <tbody>
              {char.damage != null && (
                <tr>
                  <td className={styles.statAttr}>
                    <img src="/images/stat/damage.png" alt="" className={styles.statIcon} />
                    攻击
                  </td>
                  <td className={styles.statValue}>{char.damage}</td>
                </tr>
              )}
              {char.speed != null && (
                <tr>
                  <td className={styles.statAttr}>
                    <img src="/images/stat/speed.png" alt="" className={styles.statIcon} />
                    速度
                  </td>
                  <td className={styles.statValue}>{char.speed}</td>
                </tr>
              )}
              {char.tears != null && (
                <tr>
                  <td className={styles.statAttr}>
                    <img src="/images/stat/tears.png" alt="" className={styles.statIcon} />
                    射速
                  </td>
                  <td className={styles.statValue}>{char.tears}</td>
                </tr>
              )}
            </tbody>
          </table>
        </section>
      )}

      {char.description && (
        <section className={styles.section}>
          <h3>角色特性</h3>
          <p>{char.description}</p>
        </section>
      )}

      {char.suitable_items && char.suitable_items.length > 0 && (
        <section className={styles.section}>
          <h3>适合道具</h3>
          <div className={styles.itemRow}>
            {char.suitable_items.map((iid) => (
              <div key={iid} className={styles.itemPlaceholder}>
                <span>道具{iid}</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
