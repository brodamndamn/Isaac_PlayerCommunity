import { useCallback, useEffect, useState } from "react";
import { getMyFavorites } from "../api/favorites";
import GuideCard from "../components/GuideCard";
import type { Guide } from "../types/guide";
import type { Favorite } from "../types/favorite";
import styles from "./MyFavoritesPage.module.css";

function favToGuide(f: Favorite): Guide {
  return {
    id: f.guide_id,
    title: f.guide_title,
    content: "",
    author_id: f.user_id,
    author_name: f.guide_author,
    author_avatar: f.guide_author_avatar,
    category: f.guide_category,
    cover_image: f.guide_cover,
    like_count: f.guide_like_count,
    favorite_count: f.guide_fav_count,
    comment_count: 0,
    is_liked: f.guide_is_liked,
    is_favorited: true,
    related_item_id: null,
    related_character_id: null,
    related_ending_id: null,
    created_at: f.created_at,
    updated_at: f.created_at,
  };
}

export default function MyFavoritesPage() {
  const [favs, setFavs] = useState<Favorite[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchFavs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getMyFavorites({ page_size: 100 });
      setFavs(res.data!.items);
      setTotal(res.data!.total);
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchFavs(); }, [fetchFavs]);

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
              <div key={f.id}>
                <GuideCard guide={favToGuide(f)} />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
