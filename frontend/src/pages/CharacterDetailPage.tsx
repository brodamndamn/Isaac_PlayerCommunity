import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getCharacterById } from "../api/characters";
import type { Character } from "../types/character";
import HealthHearts from "../components/HealthHearts";
import styles from "./CharacterDetailPage.module.css";

export default function CharacterDetailPage() {
  const { id } = useParams<{ id: string }>();
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
      <Link to="/characters" className={styles.back}>&larr; 返回角色列表</Link>

      <div className={styles.titleRow}>
        <div className={styles.imagePlaceholder}><span>立绘</span></div>
        <div>
          <h1 className={styles.name}>
            {char.name_cn}
            {char.is_tainted && <span className={styles.taintedBadge}>里</span>}
          </h1>
          <p className={styles.nameEn}>{char.name_en}</p>
        </div>
      </div>

      {/* 属性表格 */}
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
            <td><HealthHearts health={char.health} /></td>
          </tr>
          {char.damage != null && (
            <tr>
              <td className={styles.label}>初始攻击</td>
              <td>{char.damage}</td>
            </tr>
          )}
          {char.speed != null && (
            <tr>
              <td className={styles.label}>初始速度</td>
              <td>{char.speed}</td>
            </tr>
          )}
          {char.tears != null && (
            <tr>
              <td className={styles.label}>初始射速</td>
              <td>{char.tears}</td>
            </tr>
          )}
          {char.starting_items && char.starting_items.length > 0 && (
            <tr>
              <td className={styles.label}>初始道具</td>
              <td>ID: {char.starting_items.join(", ")}</td>
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
