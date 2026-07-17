import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent, type ClipboardEvent, type FormEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { createGuide, getGuideById, updateGuide } from "../api/guides";
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
  const [searchParams] = useSearchParams();
  const editId = searchParams.get("edit");
  const isEdit = !!editId;

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [category, setCategory] = useState("general");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadingImg, setUploadingImg] = useState(false);
  const [coverImage, setCoverImage] = useState("");
  const [uploadingCover, setUploadingCover] = useState(false);
  const [preview, setPreview] = useState(false);
  const [warning, setWarning] = useState(false);
  const [warnLeaving, setWarnLeaving] = useState(false);
  const warnTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 编辑模式：加载已有攻略
  useEffect(() => {
    if (!editId) return;
    getGuideById(Number(editId)).then((res) => {
      const g = res.data!;
      setTitle(g.title);
      setContent(g.content);
      setCategory(g.category);
      if (g.cover_image) setCoverImage(g.cover_image);
    }).catch(() => setError("加载攻略失败"));
  }, [editId]);

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

  const dismissWarning = useCallback(() => {
    setWarnLeaving(true);
    setTimeout(() => {
      setWarning(false);
      setWarnLeaving(false);
    }, 250);
  }, []);

  const showWarning = useCallback(() => {
    if (warnTimerRef.current) clearTimeout(warnTimerRef.current);
    setWarning(true);
    setWarnLeaving(false);
    warnTimerRef.current = setTimeout(dismissWarning, 3000);
  }, [dismissWarning]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      showWarning();
      return;
    }
    setError("");
    setLoading(true);
    try {
      if (isEdit) {
        await updateGuide(Number(editId), { title: title.trim(), content: content.trim(), category, cover_image: coverImage || undefined });
        navigate(`/guides/${editId}`);
      } else {
        await createGuide({ title: title.trim(), content: content.trim(), category, cover_image: coverImage || undefined });
        navigate("/guides?toast=published");
      }
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

  // Ctrl+V 粘贴图片
  const handlePaste = async (e: ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    for (const item of Array.from(items)) {
      if (item.type.startsWith("image/")) {
        e.preventDefault();
        const file = item.getAsFile();
        if (!file) continue;
        setUploadingImg(true);
        try {
          const res = await uploadImage(file);
          const url = res.data!.url;
          const ta = textareaRef.current;
          const imgMd = `![](${url})`;
          if (ta) {
            const start = ta.selectionStart;
            const end = ta.selectionEnd;
            setContent((prev) => prev.slice(0, start) + imgMd + prev.slice(end));
            setTimeout(() => {
              ta.focus();
              ta.selectionStart = ta.selectionEnd = start + imgMd.length;
            }, 0);
          } else {
            setContent((prev) => prev + imgMd + "\n");
          }
        } catch {
          setError("图片粘贴失败");
        } finally {
          setUploadingImg(false);
        }
        break;
      }
    }
  };

  // 从正文中提取所有图片 URL
  const contentImages = useMemo(() => {
    const urls: string[] = [];
    const re = /!\[[^\]]*\]\(([^)]+)\)/g;
    let m;
    while ((m = re.exec(content)) !== null) {
      urls.push(m[1]);
    }
    return urls;
  }, [content]);

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
      <h1 className={styles.title}>{isEdit ? "编辑攻略" : "发布攻略"}</h1>

      {error && <p className={styles.error}>{error}</p>}

      {warning && (
        <div className={`${styles.toast} ${warnLeaving ? styles.toastOut : ""}`}>
          <span>⚠️ 标题和正文都不能为空</span>
          <button className={styles.toastClose} onClick={dismissWarning}>&times;</button>
        </div>
      )}

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
            accept="image/png,image/jpeg,image/gif,image/webp,image/bmp"
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
              placeholder="正文内容。Ctrl+V 可直接粘贴图片"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onPaste={handlePaste}
              rows={15}
            />
          )}
          {!preview && contentImages.length > 0 && (
            <div className={styles.imgStrip}>
              {contentImages.map((url, i) => (
                <img key={i} src={url} alt="" className={styles.imgThumb} />
              ))}
            </div>
          )}
          <div className={styles.contentToolbar}>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/gif,image/webp,image/bmp"
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
          {loading ? "保存中..." : isEdit ? "保存修改" : "发布"}
        </button>
      </form>
    </div>
  );
}
