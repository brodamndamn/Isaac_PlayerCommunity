import { useRef, useState, type ChangeEvent, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { createGuide } from "../api/guides";
import { uploadImage } from "../api/upload";
import styles from "./CreateGuidePage.module.css";

const CATEGORIES = [
  { value: "general", label: "综合讨论" },
  { value: "item", label: "道具攻略" },
  { value: "character", label: "角色攻略" },
  { value: "ending", label: "结局攻略" },
];

export default function CreateGuidePage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [category, setCategory] = useState("general");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadingImg, setUploadingImg] = useState(false);
  const [coverImage, setCoverImage] = useState("");
  const [uploadingCover, setUploadingCover] = useState(false);
  const [preview, setPreview] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const renderMarkdown = (md: string) => {
    let html = md
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" style="max-width:100%;border-radius:6px;margin:8px 0" />');
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/^### (.+)$/gm, "<h4>$1</h4>");
    html = html.replace(/^## (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^# (.+)$/gm, "<h2>$1</h2>");
    html = html.replace(/\n/g, "<br />");
    return html;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;
    setError("");
    setLoading(true);
    try {
      await createGuide({ title: title.trim(), content: content.trim(), category, cover_image: coverImage || undefined });
      navigate("/guides?toast=published");
    } catch (err: any) {
      setError(err.response?.data?.message || "发布失败");
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingImg(true);
    try {
      const res = await uploadImage(file);
      const url = res.data!.url;
      // 在光标位置插入 Markdown 图片语法
      const ta = textareaRef.current;
      if (ta) {
        const start = ta.selectionStart;
        const end = ta.selectionEnd;
        const imgMarkdown = `![](${url})`;
        const newContent = content.slice(0, start) + imgMarkdown + content.slice(end);
        setContent(newContent);
        // 恢复光标位置到插入文本末尾
        setTimeout(() => {
          ta.focus();
          ta.selectionStart = ta.selectionEnd = start + imgMarkdown.length;
        }, 0);
      } else {
        setContent((prev) => prev + `![](${url})\n`);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "图片上传失败");
    } finally {
      setUploadingImg(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleCoverUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingCover(true);
    try {
      const res = await uploadImage(file);
      setCoverImage(res.data!.url);
    } catch (err: any) {
      setError(err.response?.data?.message || "封面上传失败");
    } finally {
      setUploadingCover(false);
    }
  };

  return (
    <div>
      <button onClick={() => navigate(-1)} className={styles.backBtn}>&larr; 返回</button>
      <h1 className={styles.title}>发布攻略</h1>

      {error && <p className={styles.error}>{error}</p>}

      <form onSubmit={handleSubmit} className={styles.form}>
        <input
          className={styles.input}
          type="text"
          placeholder="标题"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
          autoFocus
        />

        <div className={styles.coverRow}>
          <input
            type="file"
            accept="image/png,image/jpeg,image/gif,image/webp"
            onChange={handleCoverUpload}
            style={{ display: "none" }}
            id="coverInput"
          />
          <button type="button" className={styles.coverBtn} onClick={() => document.getElementById("coverInput")?.click()} disabled={uploadingCover}>
            {uploadingCover ? "上传中..." : coverImage ? "🖼 更换封面" : "🖼 添加封面（可选）"}
          </button>
          {coverImage && (
            <>
              <img src={coverImage} alt="封面预览" className={styles.coverPreview} />
              <button type="button" className={styles.coverRemove} onClick={() => setCoverImage("")}>✕</button>
            </>
          )}
        </div>

        <div className={styles.categories}>
          {CATEGORIES.map((c) => (
            <label key={c.value} className={`${styles.radio} ${category === c.value ? styles.radioActive : ""}`}>
              <input
                type="radio"
                name="category"
                value={c.value}
                checked={category === c.value}
                onChange={(e) => setCategory(e.target.value)}
              />
              {c.label}
            </label>
          ))}
        </div>
        <div className={styles.contentArea}>
          {preview ? (
            <div className={styles.preview} dangerouslySetInnerHTML={{ __html: renderMarkdown(content) || "<span style='color:#b0a090'>暂无内容</span>" }} />
          ) : (
            <textarea
              ref={textareaRef}
              className={styles.textarea}
              placeholder="正文内容（支持 Markdown）"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={15}
            />
          )}
          <div className={styles.contentToolbar}>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/gif,image/webp"
              onChange={handleImageUpload}
              style={{ display: "none" }}
            />
            {!preview && (
              <button
                type="button"
                className={styles.imgBtn}
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadingImg}
              >
                {uploadingImg ? "上传中..." : "📷 插入图片"}
              </button>
            )}
            <button
              type="button"
              className={styles.previewBtn}
              onClick={() => setPreview((v) => !v)}
            >
              {preview ? "✏️ 编辑" : "👁 预览"}
            </button>
            {!preview && <span className={styles.imgHint}>编辑时图片不可见，请切换到预览查看</span>}
          </div>
        </div>
        <button className={styles.submitBtn} type="submit" disabled={loading}>
          {loading ? "发布中..." : "发布"}
        </button>
      </form>
    </div>
  );
}
