import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { deleteGuide, getGuideById } from "../api/guides";
import { useAuth } from "../hooks/useAuth";
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

  const fetchGuide = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getGuideById(Number(id));
      setGuide(res.data!);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchGuide();
  }, [fetchGuide]);

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
        <p className={styles.meta}>
          @{guide.author_name} · {date}
          {guide.updated_at !== guide.created_at && " (已编辑)"}
        </p>
      </div>

      <div className={styles.content} dangerouslySetInnerHTML={{ __html: renderContent(guide.content) }} />
    </div>
  );
}
