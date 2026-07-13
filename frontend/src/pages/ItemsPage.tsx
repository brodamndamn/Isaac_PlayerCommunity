import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
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
  pill: "药丸",
};

export default function ItemsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<Item[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const page = Number(searchParams.get("page")) || 1;
  const search = searchParams.get("search") || "";
  const category = searchParams.get("category") || "";

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

  return (
    <div>
      <h1 className={styles.title}>道具图鉴</h1>

      <div className={styles.filters}>
        <input
          type="text"
          placeholder="搜索道具名称或描述..."
          defaultValue={search}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              updateParam("search", (e.target as HTMLInputElement).value);
            }
          }}
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
