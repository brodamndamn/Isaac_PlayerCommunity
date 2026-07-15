import { useCallback, useEffect, useRef, useState, type KeyboardEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { getItems } from "../api/items";
import ItemCard from "../components/ItemCard";
import type { Item } from "../types/item";
import styles from "./ItemsPage.module.css";

const CATEGORIES = ["", "passive", "active", "trinket", "card", "pill"];
const CATEGORY_LABELS: Record<string, string> = {
  "": "全部",
  passive: "被动",
  active: "主动",
  trinket: "饰品",
  card: "卡牌",
  pill: "胶囊",
};

export default function ItemsPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<Item[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const page = Number(searchParams.get("page")) || 1;
  const search = searchParams.get("search") || "";
  const category = searchParams.get("category") || "";

  // 本地搜索输入（实时更新），初始值从 URL 读取
  const [searchInput, setSearchInput] = useState(search);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getItems({ page, page_size: 20, search: search || undefined, category: category || undefined });
      setItems(res.data!.items);
      setTotal(res.data!.total);
    } finally {
      setLoading(false);
    }
  }, [page, search, category]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

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

  // 实时搜索：每次输入变化，本地立即更新 + 300ms 防抖更新 URL
  const handleSearchChange = (value: string) => {
    setSearchInput(value);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      updateParam("search", value);
    }, 300);
  };

  const handlePageJump = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key !== "Enter") return;
    const n = parseInt((e.target as HTMLInputElement).value, 10);
    if (n >= 1 && n <= totalPages) {
      updateParam("page", String(n));
      (e.target as HTMLInputElement).value = "";
    }
  };

  return (
    <div>
      <a href="/" className={styles.homeBtn}>返回首页</a>
      <h1 className={styles.title}>道具图鉴</h1>

      <div className={styles.filters}>
        <input
          type="text"
          placeholder="实时搜索道具名称或描述..."
          value={searchInput}
          onChange={(e) => handleSearchChange(e.target.value)}
          className={styles.search}
        />
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
          <p className={styles.count}>共 {total} 个道具</p>
          <div className={styles.grid}>
            {items.map((item) => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
          {totalPages > 1 && (
            <div className={styles.pagination}>
              <button
                disabled={page <= 1}
                onClick={() => updateParam("page", String(page - 1))}
              >
                上一页
              </button>
              <span>{page} / {totalPages}</span>
              <input
                type="number"
                min={1}
                max={totalPages}
                placeholder="跳转"
                onKeyDown={handlePageJump}
                className={styles.pageJump}
              />
              <button
                disabled={page >= totalPages}
                onClick={() => updateParam("page", String(page + 1))}
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
