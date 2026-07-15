import styles from "./HeartTypes.module.css";

interface HeartType {
  key: string;
  name: string;
  effect: string;
}

const HEART_TYPES: HeartType[] = [
  { key: "red", name: "红心", effect: "装在红心容器中的主要生命值，可以拾取红心补充" },
  { key: "soul", name: "魂心", effect: "蓝色临时生命，不需要容器，受伤时优先于红心扣除" },
  { key: "black", name: "黑心", effect: "类似魂心，耗尽时对全房间敌人造成40点伤害" },
  { key: "eternal", name: "永恒之心", effect: "白色半心，前往下一层转化为一个红心容器" },
  { key: "gold", name: "金心", effect: "围绕在最右边的心上，耗尽时碎裂生成大量金币" },
  { key: "bone", name: "骨心", effect: "骨制容器可填入红心，清空后再受伤永久破碎" },
  { key: "rotten", name: "腐心", effect: "一颗腐心等同半颗心血量，每清完一个房间生成两只蓝苍蝇（多颗腐心可叠加）" },
];

export default function HeartTypes() {
  return (
    <div className={styles.wrapper}>
      <h3 className={styles.title}>生命类型</h3>
      <div className={styles.grid}>
        {HEART_TYPES.map((h) => (
          <div key={h.key} className={styles.card}>
            <span className={styles.iconPlaceholder} data-heart={h.key} />
            <span className={styles.label}>{h.name}：{h.effect}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
