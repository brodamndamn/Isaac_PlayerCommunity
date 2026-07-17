import { useEffect, useRef, useState, type ChangeEvent, type WheelEvent, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import client from "../api/client";
import { getMyFavorites } from "../api/favorites";
import { getGuides } from "../api/guides";
import { useAuth } from "../hooks/useAuth";
import type { ApiResponse } from "../types/api";
import styles from "./ProfilePage.module.css";

const CROP_SIZE = 200;

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, login, logout } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [postCount, setPostCount] = useState(0);
  const [favCount, setFavCount] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!user) return;
    getGuides({ author_id: user.id, page_size: 1 }).then(r => setPostCount(r.data?.total || 0)).catch(() => {});
    getMyFavorites({ page_size: 1 }).then(r => setFavCount(r.data?.total || 0)).catch(() => {});
  }, [user]);

  // 裁剪状态
  const [cropSrc, setCropSrc] = useState<string | null>(null);
  const [cropScale, setCropScale] = useState(1);
  const cropX = useRef(0);
  const cropY = useRef(0);
  const imgW = useRef(0);
  const imgH = useRef(0);
  const dragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0, cx: 0, cy: 0 });
  const [, forceRender] = useState(0);

  if (!user) return null;

  const avatarUrl = user.avatar ? `/uploads/${user.avatar}` : null;

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        // 计算初始缩放和位置，使图片尽量填充裁剪框
        const scale = Math.max(CROP_SIZE / img.width, CROP_SIZE / img.height, 0.5);
        imgW.current = img.width;
        imgH.current = img.height;
        setCropScale(scale);
        cropX.current = (CROP_SIZE - img.width * scale) / 2;
        cropY.current = (CROP_SIZE - img.height * scale) / 2;
        setCropSrc(reader.result as string);
        setError("");
      };
      img.src = reader.result as string;
    };
    reader.readAsDataURL(file);
    if (fileRef.current) fileRef.current.value = "";
  };

  // 鼠标按下 → 开始拖拽
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    dragging.current = true;
    dragStart.current = { x: e.clientX, y: e.clientY, cx: cropX.current, cy: cropY.current };
  };

  // 鼠标移动 → 更新图片位置
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!dragging.current) return;
    cropX.current = dragStart.current.cx + (e.clientX - dragStart.current.x);
    cropY.current = dragStart.current.cy + (e.clientY - dragStart.current.y);
    forceRender((n) => n + 1);
  };

  // 鼠标释放
  const handleMouseUp = () => {
    dragging.current = false;
  };

  // 滚轮缩放（以鼠标位置为中心）
  const handleWheel = (e: WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    const newScale = Math.max(0.2, Math.min(3, cropScale + delta));
    // 以鼠标在裁剪框内的位置为缩放中心
    const rect = e.currentTarget.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    cropX.current = mx - (mx - cropX.current) * (newScale / cropScale);
    cropY.current = my - (my - cropY.current) * (newScale / cropScale);
    setCropScale(newScale);
  };

  // Canvas 裁剪 → 上传
  const handleCropAndUpload = useCallback(async () => {
    if (!cropSrc) return;
    setUploading(true);
    setError("");

    try {
      const img = new Image();
      await new Promise<void>((resolve, reject) => {
        img.onload = () => resolve();
        img.onerror = reject;
        img.src = cropSrc;
      });

      const canvas = document.createElement("canvas");
      canvas.width = CROP_SIZE;
      canvas.height = CROP_SIZE;
      const ctx = canvas.getContext("2d")!;

      // 圆形裁剪区域
      ctx.beginPath();
      ctx.arc(CROP_SIZE / 2, CROP_SIZE / 2, CROP_SIZE / 2, 0, Math.PI * 2);
      ctx.clip();

      // 用与预览一致的参数画图
      const sw = img.width * cropScale;
      const sh = img.height * cropScale;
      ctx.drawImage(img, cropX.current, cropY.current, sw, sh);

      const blob = await new Promise<Blob | null>((resolve) =>
        canvas.toBlob(resolve, "image/png")
      );
      if (!blob) throw new Error("裁剪失败");

      const form = new FormData();
      form.append("file", blob, "avatar.png");
      const { data } = await client.post<ApiResponse<{ avatar: string }>>(
        "/auth/avatar",
        form
      );
      login({ ...user, avatar: data.data.avatar });
      setCropSrc(null);
    } catch (err: any) {
      setError(err.response?.data?.message || "上传失败");
    } finally {
      setUploading(false);
    }
  }, [cropSrc, cropScale, user, login]);

  return (
    <div>
      <button onClick={() => navigate(-1)} className={styles.backBtn}>&larr; 返回</button>
      <h1 className={styles.title}>个人资料</h1>

      {/* 裁剪弹窗 */}
      {cropSrc && (
        <div className={styles.cropOverlay}>
          <div className={styles.cropModal}>
            <h3 className={styles.cropTitle}>拖动调整位置 · 滚轮缩放</h3>
            <div
              className={styles.cropArea}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              onWheel={handleWheel}
            >
              <img
                src={cropSrc}
                alt="裁剪"
                className={styles.cropImg}
                draggable={false}
                style={{
                  transform: `translate(${cropX.current}px, ${cropY.current}px) scale(${cropScale})`,
                }}
              />
              <div className={styles.cropCircle} />
            </div>
            <input
              type="range"
              min={0.2}
              max={3}
              step={0.05}
              value={cropScale}
              onChange={(e) => setCropScale(Number(e.target.value))}
              className={styles.cropSlider}
            />
            <div className={styles.cropActions}>
              <button className={styles.cropCancel} onClick={() => setCropSrc(null)}>
                取消
              </button>
              <button
                className={styles.cropConfirm}
                onClick={handleCropAndUpload}
                disabled={uploading}
              >
                {uploading ? "上传中..." : "确认裁剪并上传"}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className={styles.card}>
        <div className={styles.avatarSection}>
          {avatarUrl ? (
            <img src={avatarUrl} alt="头像" className={styles.avatar} />
          ) : (
            <div className={styles.avatarPlaceholder}>{user.username[0].toUpperCase()}</div>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="image/png,image/jpeg,image/jpg,image/gif,image/webp,image/bmp"
            onChange={handleFileSelect}
            style={{ display: "none" }}
          />
          <button
            className={styles.uploadBtn}
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? "上传中..." : "更换头像"}
          </button>
          <p className={styles.hint}>支持 PNG / JPEG / GIF / WebP，最大 2MB</p>
        </div>

        {error && <p className={styles.error}>{error}</p>}

        <div className={styles.info}>
          <div className={styles.row}>
            <span className={styles.label}>用户名</span>
            <span className={styles.value}>{user.username}</span>
          </div>
          <div className={styles.row}>
            <span className={styles.label}>邮箱</span>
            <span className={styles.value}>{user.email}</span>
          </div>
        </div>

        <Link to={`/guides?author_id=${user.id}`} className={styles.linkRow}>
          <span className={styles.label}>我的帖子</span>
          <span className={styles.linkValue}>{postCount} →</span>
        </Link>
        <Link to="/favorites" className={styles.linkRow}>
          <span className={styles.label}>收藏的帖子</span>
          <span className={styles.linkValue}>{favCount} →</span>
        </Link>

        <button
          className={styles.logoutBtn}
          onClick={() => { logout(); navigate("/"); }}
        >
          退出登录
        </button>
      </div>
    </div>
  );
}
