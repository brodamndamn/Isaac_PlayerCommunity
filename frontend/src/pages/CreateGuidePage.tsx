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
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;
    setError("");
    setLoading(true);
    try {
      const res = await createGuide({ title: title.trim(), content: content.trim(), category });
      navigate(`/guides/${res.data!.id}`);
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
      // 清空 file input，允许重复上传同一文件
      if (fileInputRef.current) fileInputRef.current.value = "";
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
          <textarea
            ref={textareaRef}
            className={styles.textarea}
            placeholder="正文内容（支持 Markdown）"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={15}
          />
          <div className={styles.contentToolbar}>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/gif,image/webp"
              onChange={handleImageUpload}
              style={{ display: "none" }}
            />
            <button
              type="button"
              className={styles.imgBtn}
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadingImg}
            >
              {uploadingImg ? "上传中..." : "📷 插入图片"}
            </button>
            <span className={styles.imgHint}>支持 PNG/JPEG/GIF/WebP，最大 5MB</span>
          </div>
        </div>
        <button className={styles.submitBtn} type="submit" disabled={loading}>
          {loading ? "发布中..." : "发布"}
        </button>
      </form>
    </div>
  );
}
