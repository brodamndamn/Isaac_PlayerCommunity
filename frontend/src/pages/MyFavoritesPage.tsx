import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyFavorites, removeFavorite } from "../api/favorites";
import type { Favorite } from "../types/favorite";
import styles from "./MyFavoritesPage.module.css";

const CATEGORY_LABELS: Record<string, string> = {
  general: "综合", item: "道具", character: "角色", ending: "结局",
};

export default function MyFavoritesPage() {
  const [favs, setFavs] = useState<Favorite[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [removing, setRemoving] = useState<number | null>(null);

  const fetchFavs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getMyFavorites({ page_size: 100 });
      setFavs(res.data!.items);
      setTotal(res.data!.total);
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchFavs(); }, [fetchFavs]);

  const handleRemove = async (guideId: number) => {
    setRemoving(guideId);
    try {
      await removeFavorite(guideId);
      setFavs((prev) => prev.filter((f) => f.guide_id !== guideId));
      setTotal((t) => t - 1);
    } catch { /* ignore */ }
    finally { setRemoving(null); }
  };

  return (
    <div>
      <a href="/" className={styles.homeBtn}>返回首页</a>
      <h1 className={styles.title}>收藏的帖子</h1>

      {loading ? (
        <p className={styles.loading}>加载中...</p>
      ) : total === 0 ? (
        <p className={styles.empty}>还没有收藏任何帖子</p>
      ) : (
        <>
          <p className={styles.count}>共 {total} 篇</p>
          <div className={styles.grid}>
            {favs.map((f) => (
              <div key={f.id} className={styles.card}>
                <Link to={`/guides/${f.guide_id}`} className={styles.cardInner}>
                  {f.guide_cover && <div className={styles.coverWrap}><img src={f.guide_cover} alt="" className={styles.cover} /></div>}
                  <div className={styles.cardHeader}>
                    <span className={`${styles.cat} ${styles[f.guide_category] || ""}`}>{CATEGORY_LABELS[f.guide_category] || f.guide_category}</span>
                    <span className={styles.date}>{new Date(f.created_at).toLocaleDateString("zh-CN")}</span>
                  </div>
                  <h3 className={styles.cardTitle}>{f.guide_title}</h3>
                  <p className={styles.cardAuthor}>@{f.guide_author}</p>
                </Link>
                <button
                  className={styles.removeBtn}
                  onClick={() => handleRemove(f.guide_id)}
                  disabled={removing === f.guide_id}
                >
                  {removing === f.guide_id ? "..." : "取消收藏"}
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
