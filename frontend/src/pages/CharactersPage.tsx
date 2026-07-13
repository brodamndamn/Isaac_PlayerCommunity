import { useCallback, useEffect, useState } from "react";
import { getCharacters } from "../api/characters";
import CharacterCard from "../components/CharacterCard";
import type { Character } from "../types/character";
import styles from "./CharactersPage.module.css";

export default function CharactersPage() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<"all" | "normal" | "tainted">("all");

  const fetchCharacters = useCallback(async () => {
    setLoading(true);
    try {
      const isTainted = filter === "tainted" ? true : filter === "normal" ? false : undefined;
      const res = await getCharacters({ page_size: 34, is_tainted: isTainted });
      setCharacters(res.data!.items);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchCharacters();
  }, [fetchCharacters]);

  const normal = characters.filter((c) => !c.is_tainted);
  const tainted = characters.filter((c) => c.is_tainted);

  return (
    <div>
      <h1 className={styles.title}>角色资料</h1>

      <div className={styles.filters}>
        {(["all", "normal", "tainted"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`${styles.fBtn} ${filter === f ? styles.active : ""}`}
          >
            {f === "all" ? `全部 (${characters.length})` : f === "normal" ? `表角色 (${normal.length})` : `里角色 (${tainted.length})`}
          </button>
        ))}
      </div>

      {loading ? (
        <p className={styles.loading}>加载中...</p>
      ) : (
        <>
          {/* 表角色 */}
          {filter !== "tainted" && (
            <section>
              <h2 className={styles.sectionTitle}>表角色</h2>
              <div className={styles.grid}>
                {(filter === "normal" ? characters : normal).map((c) => (
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
                {(filter === "tainted" ? characters : tainted).map((c) => (
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
