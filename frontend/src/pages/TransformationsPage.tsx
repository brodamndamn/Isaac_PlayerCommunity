import { useEffect, useState } from "react";
import { getTransformations } from "../api/transformations";
import TransformationCard from "../components/TransformationCard";
import type { Transformation } from "../types/transformation";
import styles from "./TransformationsPage.module.css";

export default function TransformationsPage() {
  const [items, setItems] = useState<Transformation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTransformations()
      .then((res) => setItems(res.data.items))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <a href="/" className={styles.homeBtn}>返回首页</a>
      <h1 className={styles.title}>套装效果</h1>

      {loading ? (
        <p className={styles.loading}>加载中...</p>
      ) : (
        <>
          <p className={styles.count}>共 {items.length} 种套装效果</p>
          <div className={styles.grid}>
            {items.map((item) => (
              <TransformationCard key={item.id} transformation={item} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
