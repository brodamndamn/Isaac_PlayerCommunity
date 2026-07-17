import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { addFavorite, removeFavorite } from "../api/favorites";
import { addLike, removeLike } from "../api/likes";
import { useAuth } from "../hooks/useAuth";
import UserAvatar from "./UserAvatar";
import type { Guide } from "../types/guide";
import styles from "./GuideCard.module.css";

const CATEGORY_LABELS: Record<string, string> = {
  general: "综合",
  item: "道具",
  character: "角色",
  ending: "结局",
};

interface GuideCardProps {
  guide: Guide;
  onUpdate?: (id: number, data: Partial<Guide>) => void;
}

export default function GuideCard({ guide }: GuideCardProps) {
  const navigate = useNavigate();
  const { user, openModal } = useAuth();
  const [likeCount, setLikeCount] = useState(guide.like_count);
  const [isLiked, setIsLiked] = useState(guide.is_liked);
  const [favCount, setFavCount] = useState(guide.favorite_count);
  const [isFavorited, setIsFavorited] = useState(guide.is_favorited);
  const date = new Date(guide.created_at).toLocaleDateString("zh-CN");
  const coverUrl = guide.cover_image || null;

  const goDetail = () => navigate(`/guides/${guide.id}`);

  const handleLike = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!user) { openModal("login"); return; }
    try {
      if (isLiked) {
        await removeLike(guide.id);
        setLikeCount((c) => c - 1);
        setIsLiked(false);
      } else {
        await addLike(guide.id);
        setLikeCount((c) => c + 1);
        setIsLiked(true);
      }
    } catch { /* ignore */ }
  };

  const handleFav = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!user) { openModal("login"); return; }
    try {
      if (isFavorited) {
        await removeFavorite(guide.id);
        setFavCount((c) => c - 1);
        setIsFavorited(false);
      } else {
        await addFavorite(guide.id);
        setFavCount((c) => c + 1);
        setIsFavorited(true);
      }
    } catch { /* ignore */ }
  };

  return (
    <div className={styles.card} onClick={goDetail} style={{ cursor: "pointer" }}>
      {coverUrl && (
        <div className={styles.coverWrap}>
          <img src={coverUrl} alt="" className={styles.cover} />
        </div>
      )}
      <div className={styles.header}>
        <span className={`${styles.category} ${styles[guide.category] || ""}`}>{CATEGORY_LABELS[guide.category] || guide.category}</span>
        <span className={styles.date}>{date}</span>
      </div>
      <h3 className={styles.title}>{guide.title}</h3>
      <div className={styles.bottomRow}>
        <span className={styles.author}>
          <UserAvatar avatar={guide.author_avatar} username={guide.author_name} size={16} /> {guide.author_name}
        </span>
        <div className={styles.actions}>
          <button className={`${styles.actionBtn} ${isLiked ? styles.active : ""}`} onClick={handleLike}>
            {isLiked ? "❤️" : "🤍"} {likeCount}
          </button>
          <button className={`${styles.actionBtn} ${isFavorited ? styles.active : ""}`} onClick={handleFav}>
            {isFavorited ? "⭐" : "☆"} {favCount}
          </button>
        </div>
      </div>
    </div>
  );
}
