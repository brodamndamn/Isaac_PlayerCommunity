import { useEffect, useState } from "react";
import { getEndings } from "../api/endings";
import EndingCard from "../components/EndingCard";
import type { Ending } from "../types/ending";
import styles from "./EndingsPage.module.css";

export default function EndingsPage() {
  const [endings, setEndings] = useState<Ending[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getEndings({ page_size: 22 })
      .then((res) => setEndings(res.data!.items))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className={styles.title}>结局一览</h1>

      {loading ? (
        <p className={styles.loading}>加载中...</p>
      ) : (
        <div className={styles.grid}>
          {endings.map((e) => (
            <EndingCard key={e.id} ending={e} />
          ))}
        </div>
      )}
    </div>
  );
}
