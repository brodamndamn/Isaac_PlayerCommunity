import { useEffect, useState } from "react";
import { getCharacters } from "../api/characters";
import CharacterCard from "../components/CharacterCard";
import HeartTypes from "../components/HeartTypes";
import type { Character } from "../types/character";
import styles from "./CharactersPage.module.css";

export default function CharactersPage() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<"all" | "normal" | "tainted">("all");

  // 一次性拉全部；tab 切换只控制显示，不重 fetch，避免 count 跟着变动
  useEffect(() => {
    setLoading(true);
    getCharacters({ page_size: 34 })
      .then((res) => setCharacters(res.data!.items))
      .finally(() => setLoading(false));
  }, []);

  const normal = characters.filter((c) => !c.is_tainted);
  const tainted = characters.filter((c) => c.is_tainted);
  const totalCount = characters.length;
  const normalCount = normal.length;
  const taintedCount = tainted.length;

  return (
    <div>
      <a href="/" className={styles.homeBtn}>返回首页</a>
      <h1 className={styles.title}>角色资料</h1>

      <div className={styles.filters}>
        {(["all", "normal", "tainted"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`${styles.fBtn} ${filter === f ? styles.active : ""}`}
          >
            {f === "all" ? `全部 (${totalCount})` : f === "normal" ? `表角色 (${normalCount})` : `里角色 (${taintedCount})`}
          </button>
        ))}
      </div>

      <HeartTypes />

      {loading ? (
        <p className={styles.loading}>加载中...</p>
      ) : (
        <>
          {/* 表角色 */}
          {filter !== "tainted" && (
            <section>
              <h2 className={styles.sectionTitle}>表角色</h2>
              <div className={styles.grid}>
                {normal.map((c) => (
                  <CharacterCard key={c.id} character={c} />
                ))}
              </div>
            </section>
          )}

          {/* 里角色 */}
          {filter !== "normal" && (
            <section>
              <h2 className={styles.sectionTitle}>里角色</h2>
              <div className={styles.grid}>
                {tainted.map((c) => (
                  <CharacterCard key={c.id} character={c} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
