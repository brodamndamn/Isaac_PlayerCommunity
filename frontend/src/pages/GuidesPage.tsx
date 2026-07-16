import { useCallback, useEffect, useRef, useState, type KeyboardEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { getGuides } from "../api/guides";
import GuideCard from "../components/GuideCard";
import type { Guide } from "../types/guide";
import styles from "./GuidesPage.module.css";

const TOAST_DURATION = 3500;

const CATEGORIES = ["", "general", "item", "character", "ending"];
const CATEGORY_LABELS: Record<string, string> = {
  "": "全部",
  general: "综合",
  item: "道具",
  character: "角色",
  ending: "结局",
};

export default function GuidesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [guides, setGuides] = useState<Guide[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const page = Number(searchParams.get("page")) || 1;
  const search = searchParams.get("search") || "";
  const category = searchParams.get("category") || "";
  const authorId = searchParams.get("author_id") || "";

  const [searchInput, setSearchInput] = useState(search);
  const [pageInput, setPageInput] = useState("");

  // Toast 提示
  const toast = searchParams.get("toast");
  const [toastLeaving, setToastLeaving] = useState(false);

  const removeToast = () => {
    const params = new URLSearchParams(searchParams);
    params.delete("toast");
    setSearchParams(params, { replace: true });
  };

  const dismissToast = () => {
    setToastLeaving(true);
    setTimeout(removeToast, 250); // 等退出动画播完
  };

  useEffect(() => {
    if (toast === "published") {
      setToastLeaving(false);
      const timer = setTimeout(dismissToast, TOAST_DURATION);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const fetchGuides = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getGuides({
        page,
        page_size: 20,
        search: search || undefined,
        category: category || undefined,
        author_id: authorId ? Number(authorId) : undefined,
      });
      setGuides(res.data!.items);
      setTotal(res.data!.total);
    } finally {
      setLoading(false);
    }
  }, [page, search, category, authorId]);

  useEffect(() => {
    fetchGuides();
  }, [fetchGuides]);

  const totalPages = Math.ceil(total / 20);

  const updateParam = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    if (key !== "page") params.set("page", "1");
    setSearchParams(params);
  };

  const handleSearchChange = (value: string) => {
    setSearchInput(value);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      updateParam("search", value);
    }, 300);
  };

  const doSearch = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    updateParam("search", searchInput);
  };

  const handleSearchKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") doSearch();
  };

  const doPageJump = () => {
    const n = parseInt(pageInput, 10);
    if (n >= 1 && n <= totalPages) {
      updateParam("page", String(n));
      setPageInput("");
    }
  };

  const handlePageJumpKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") doPageJump();
  };

  return (
    <div>
      <a href="/" className={styles.homeBtn}>返回首页</a>
      {toast === "published" && (
        <div className={`${styles.toast} ${toastLeaving ? styles.toastOut : ""}`}>
          <span>✅ 帖子已成功发布！</span>
          <button className={styles.toastClose} onClick={dismissToast}>&times;</button>
        </div>
      )}

      <div className={styles.topRow}>
        <h1 className={styles.title}>玩家社区</h1>
        <Link to="/guides/new" className={styles.createBtn}>发布攻略</Link>
      </div>

      <div className={styles.filters}>
        <div className={styles.searchRow}>
          <input
            type="text"
            placeholder="搜索攻略标题或正文..."
            value={searchInput}
            onChange={(e) => handleSearchChange(e.target.value)}
            onKeyDown={handleSearchKeyDown}
            className={styles.search}
          />
          <button onClick={doSearch} className={styles.searchBtn}>搜索</button>
        </div>
        <div className={styles.categories}>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => updateParam("category", cat)}
              className={`${styles.catBtn} ${category === cat ? styles.active : ""}`}
            >
              {CATEGORY_LABELS[cat]}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <p className={styles.loading}>加载中...</p>
      ) : (
        <>
          <p className={styles.count}>共 {total} 篇</p>
          <div className={styles.grid}>
            {guides.map((g) => (
              <GuideCard key={g.id} guide={g} />
            ))}
          </div>
          {totalPages > 1 && (
            <div className={styles.pagination}>
              <button disabled={page <= 1} onClick={() => updateParam("page", String(page - 1))}>上一页</button>
              <span>{page} / {totalPages}</span>
              <input
                type="number"
                min={1}
                max={totalPages}
                placeholder="跳转"
                value={pageInput}
                onChange={(e) => setPageInput(e.target.value)}
                onKeyDown={handlePageJumpKeyDown}
                className={styles.pageJump}
              />
              <button onClick={doPageJump} className={styles.goBtn}>Go</button>
              <button disabled={page >= totalPages} onClick={() => updateParam("page", String(page + 1))}>下一页</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
