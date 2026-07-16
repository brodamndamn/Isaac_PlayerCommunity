import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyFavorites, removeFavorite } from "../api/favorites";
import type { Favorite } from "../types/favorite";
import styles from "./MyFavoritesPage.module.css";

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
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFavs();
  }, [fetchFavs]);

  const handleRemove = async (guideId: number) => {
    setRemoving(guideId);
    try {
      await removeFavorite(guideId);
      setFavs((prev) => prev.filter((f) => f.guide_id !== guideId));
      setTotal((t) => t - 1);
    } catch (err: any) {
      alert(err.response?.data?.message || "操作失败");
    } finally {
      setRemoving(null);
    }
  };

  return (
    <div>
      <a href="/" className={styles.homeBtn}>返回首页</a>
      <h1 className={styles.title}>我的收藏</h1>

      {loading ? (
        <p className={styles.loading}>加载中...</p>
      ) : total === 0 ? (
        <p className={styles.empty}>还没有收藏任何攻略</p>
      ) : (
        <>
          <p className={styles.count}>共 {total} 篇</p>
          <div className={styles.list}>
            {favs.map((f) => (
              <div key={f.id} className={styles.item}>
                <div className={styles.info}>
                  <Link to={`/guides/${f.guide_id}`} className={styles.link}>
                    {f.guide_title}
                  </Link>
                  <span className={styles.author}>@{f.guide_author}</span>
                  <span className={styles.date}>
                    {new Date(f.created_at).toLocaleDateString("zh-CN")}
                  </span>
                </div>
                <button
                  onClick={() => handleRemove(f.guide_id)}
                  disabled={removing === f.guide_id}
                  className={styles.removeBtn}
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
