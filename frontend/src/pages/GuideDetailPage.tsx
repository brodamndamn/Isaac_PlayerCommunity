import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { addFavorite, removeFavorite } from "../api/favorites";
import { deleteGuide, getGuideById } from "../api/guides";
import { addLike, removeLike } from "../api/likes";
import { likeComment, unlikeComment } from "../api/comments";
import { useAuth } from "../hooks/useAuth";
import client from "../api/client";
import type { ApiResponse, PaginatedData } from "../types/api";
import type { Guide } from "../types/guide";
import styles from "./GuideDetailPage.module.css";

const CATEGORY_LABELS: Record<string, string> = {
  general: "综合",
  item: "道具",
  character: "角色",
  ending: "结局",
};

export default function GuideDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [guide, setGuide] = useState<Guide | null>(null);
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [likeCount, setLikeCount] = useState(0);
  const [isLiked, setIsLiked] = useState(false);
  const [favCount, setFavCount] = useState(0);
  const [isFavorited, setIsFavorited] = useState(false);
  const [comments, setComments] = useState<any[]>([]);
  const [commentText, setCommentText] = useState("");
  const [submittingComment, setSubmittingComment] = useState(false);

  const fetchComments = useCallback(async () => {
    try {
      const { data } = await client.get<ApiResponse<PaginatedData<any>>>(`/guides/${id}/comments?page_size=100`);
      setComments(data.data!.items);
    } catch { /* ignore */ }
  }, [id]);

  const fetchGuide = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getGuideById(Number(id));
      const g = res.data!;
      setGuide(g);
      setLikeCount(g.like_count);
      setIsLiked(g.is_liked);
      setFavCount(g.favorite_count);
      setIsFavorited(g.is_favorited);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchGuide();
    fetchComments();
  }, [fetchGuide, fetchComments]);

  const handleDelete = async () => {
    if (!confirm("确定删除这篇攻略吗？")) return;
    setDeleting(true);
    try {
      await deleteGuide(Number(id));
      navigate("/guides");
    } catch (err: any) {
      alert(err.response?.data?.message || "删除失败");
    } finally {
      setDeleting(false);
    }
  };

  const handleLike = async () => {
    if (!user) return;
    try {
      if (isLiked) {
        await removeLike(Number(id));
        setLikeCount((c) => c - 1);
        setIsLiked(false);
      } else {
        await addLike(Number(id));
        setLikeCount((c) => c + 1);
        setIsLiked(true);
      }
    } catch { /* ignore */ }
  };

  const handleFav = async () => {
    if (!user) return;
    try {
      if (isFavorited) {
        await removeFavorite(Number(id));
        setFavCount((c) => c - 1);
        setIsFavorited(false);
      } else {
        await addFavorite(Number(id));
        setFavCount((c) => c + 1);
        setIsFavorited(true);
      }
    } catch { /* ignore */ }
  };

  const handlePostComment = async () => {
    if (!commentText.trim()) return;
    setSubmittingComment(true);
    try {
      await client.post(`/guides/${id}/comments`, { content: commentText.trim() });
      setCommentText("");
      fetchComments();
      // 更新评论计数
      setGuide((prev) => prev ? { ...prev, comment_count: prev.comment_count + 1 } : prev);
    } catch { /* ignore */ }
    finally { setSubmittingComment(false); }
  };

  const isOwner = user && guide && user.id === guide.author_id;
  const isAdmin = user?.role === "admin";
  const canDelete = isOwner || isAdmin;

  if (loading) return <p className={styles.loading}>加载中...</p>;
  if (!guide) return <p className={styles.loading}>攻略不存在</p>;

  const date = new Date(guide.created_at).toLocaleString("zh-CN");

  // 简易 Markdown → HTML
  const renderContent = (md: string) => {
    let html = md
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    // 图片 ![](url)
    html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" style="max-width:100%;border-radius:6px;margin:8px 0" />');
    // 粗体 **text**
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    // 标题 ## text
    html = html.replace(/^### (.+)$/gm, "<h4>$1</h4>");
    html = html.replace(/^## (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^# (.+)$/gm, "<h2>$1</h2>");
    // 换行
    html = html.replace(/\n/g, "<br />");
    return html;
  };

  return (
    <div>
      <button onClick={() => navigate(-1)} className={styles.backBtn}>&larr; 返回</button>

      {canDelete && (
        <button onClick={handleDelete} disabled={deleting} className={styles.deleteBtn}>
          {deleting ? "删除中..." : "删除攻略"}
        </button>
      )}

      <div className={styles.header}>
        <span className={`${styles.category} ${styles[guide.category] || ""}`}>{CATEGORY_LABELS[guide.category] || guide.category}</span>
        <h1 className={styles.title}>{guide.title}</h1>
        <div className={styles.metaRow}>
          <span className={styles.author}>@{guide.author_name}</span>
          <span className={styles.metaSep}>·</span>
          <span className={styles.date}>{date}</span>
          {guide.updated_at !== guide.created_at && " (已编辑)"}
          <div className={styles.metaActions}>
            <button className={`${styles.actionBtn} ${isLiked ? styles.actionActive : ""}`} onClick={handleLike}>
              {isLiked ? "❤️" : "🤍"} {likeCount}
            </button>
            <button className={`${styles.actionBtn} ${isFavorited ? styles.actionActive : ""}`} onClick={handleFav}>
              {isFavorited ? "⭐" : "☆"} {favCount}
            </button>
            <span className={styles.actionBtn} onClick={() => document.getElementById("comments")?.scrollIntoView({ behavior: "smooth" })} style={{ cursor: "pointer" }}>💬 {guide.comment_count}</span>
          </div>
        </div>
      </div>

      <div className={styles.content} dangerouslySetInnerHTML={{ __html: renderContent(guide.content) }} />

      <div className={styles.commentSection} id="comments">
        <h3 className={styles.commentTitle}>评论 ({guide.comment_count})</h3>

        {user ? (
          <div className={styles.commentForm}>
            <textarea
              className={styles.commentInput}
              placeholder="写下你的评论..."
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              rows={3}
            />
            <button
              className={styles.commentSubmit}
              onClick={handlePostComment}
              disabled={submittingComment || !commentText.trim()}
            >
              {submittingComment ? "提交中..." : "发表评论"}
            </button>
          </div>
        ) : (
          <p className={styles.commentLoginHint}>请先登录才能发表评论</p>
        )}

        <div className={styles.commentList}>
          {comments.map((c) => (
            <div key={c.id} className={styles.commentItem}>
              <div className={styles.commentMeta}>
                <span className={styles.commentAuthor}>@{c.author_name}</span>
                <span className={styles.commentDate}>{new Date(c.created_at).toLocaleDateString("zh-CN")}</span>
                <button
                  className={`${styles.commentLikeBtn} ${c.is_liked ? styles.commentLiked : ""}`}
                  onClick={async () => {
                    if (!user) return;
                    try {
                      if (c.is_liked) {
                        await unlikeComment(c.id);
                        c.is_liked = false;
                        c.like_count = Math.max(0, c.like_count - 1);
                      } else {
                        await likeComment(c.id);
                        c.is_liked = true;
                        c.like_count += 1;
                      }
                      setComments([...comments]);
                    } catch { /* ignore */ }
                  }}
                >
                  {c.is_liked ? "❤️" : "🤍"} {c.like_count || 0}
                </button>
                {(user?.id === c.user_id || user?.role === "admin") && (
                  <button
                    className={styles.commentDelBtn}
                    onClick={async () => {
                      if (!confirm("确定删除这条评论吗？")) return;
                      try {
                        await client.delete(`/comments/${c.id}`);
                        fetchComments();
                      } catch { /* ignore */ }
                    }}
                  >
                    ✕
                  </button>
                )}
              </div>
              <p className={styles.commentBody}>{c.content}</p>
            </div>
          ))}
          {comments.length === 0 && <p className={styles.commentEmpty}>暂无评论，来发表第一条吧</p>}
        </div>
      </div>
    </div>
  );
}
