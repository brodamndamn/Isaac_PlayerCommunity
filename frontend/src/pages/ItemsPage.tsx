import { useCallback, useEffect, useRef, useState, type KeyboardEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { getItems } from "../api/items";
import { getTransformations } from "../api/transformations";
import ItemCard from "../components/ItemCard";
import TransformationCard from "../components/TransformationCard";
import type { Item } from "../types/item";
import type { Transformation } from "../types/transformation";
import styles from "./ItemsPage.module.css";

const CATEGORIES = ["", "passive", "active", "trinket", "card", "pill", "transformation"];
const CATEGORY_LABELS: Record<string, string> = {
  "": "全部",
  passive: "被动",
  active: "主动",
  trinket: "饰品",
  card: "卡牌",
  pill: "胶囊",
  transformation: "套装",
};

export default function ItemsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<Item[]>([]);
  const [transformations, setTransformations] = useState<Transformation[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const page = Number(searchParams.get("page")) || 1;
  const search = searchParams.get("search") || "";
  const category = searchParams.get("category") || "";
  const isTransformation = category === "transformation";

  const [searchInput, setSearchInput] = useState(search);
  const [pageInput, setPageInput] = useState("");

  const fetchItems = useCallback(async () => {
    setLoading(true);
    try {
      if (isTransformation) {
        const res = await getTransformations();
        setTransformations(res.data.items);
        setTotal(res.data.total);
      } else {
        const res = await getItems({
          page,
          page_size: 20,
          search: search || undefined,
          category: category || undefined,
        });
        setItems(res.data!.items);
        setTotal(res.data!.total);
      }
    } finally {
      setLoading(false);
    }
  }, [page, search, category, isTransformation]);

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

  // 套装搜索过滤
  const filteredTransformations = transformations.filter((t) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return t.name_cn.includes(s) || t.name_en.toLowerCase().includes(s);
  });

  return (
    <div>
      <a href="/" className={styles.homeBtn}>返回首页</a>
      <h1 className={styles.title}>道具图鉴</h1>

      <div className={styles.filters}>
        <div className={styles.searchRow}>
          <input
            type="text"
            placeholder={isTransformation ? "搜索套装名称..." : "搜索道具名称或描述..."}
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
      ) : isTransformation ? (
        <>
          <p className={styles.count}>共 {filteredTransformations.length} 个</p>
          <div className={styles.grid}>
            {filteredTransformations.map((t) => (
              <TransformationCard key={t.id} transformation={t} />
            ))}
          </div>
        </>
      ) : (
        <>
          <p className={styles.count}>共 {total} 个</p>
          <div className={styles.grid}>
            {items.map((item) => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
          {totalPages > 1 && (
            <div className={styles.pagination}>
              <button disabled={page <= 1} onClick={() => updateParam("page", String(page - 1))}>
                上一页
              </button>
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
              <button disabled={page >= totalPages} onClick={() => updateParam("page", String(page + 1))}>
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
