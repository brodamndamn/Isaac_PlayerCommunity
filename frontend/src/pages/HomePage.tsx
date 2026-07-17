import { Link } from "react-router-dom";
import styles from "./HomePage.module.css";

const SECTIONS = [
  { path: "/items", image: "/images/items/114.png", title: "道具图鉴", desc: "700+ 道具的详细效果、解锁方式与搭配推荐", count: "1000+" },
  { path: "/characters", image: "/images/characters/1.png", title: "角色资料", desc: "34 个表里角色的属性、初始道具与解锁条件", count: "34" },
  { path: "/endings", image: "/images/moms-heart.png", title: "结局一览", desc: "全部结局的达成方式、Boss 信息与解锁奖励", count: "20+" },
];

export default function HomePage() {
  return (
    <div className={styles.root}>
      {/* 主视觉区 */}
      <section className={styles.hero}>
        <div className={styles.heroOverlay}>
          <h1 className={styles.title}>ISAAC 玩家社区</h1>
          <p className={styles.subtitle}>
            以撒的结合 · 中文攻略资料库
          </p>
          <p className={styles.heroDesc}>
            从地下室到天堂，从羔羊到 Mega Satan——这里有你需要的每一件道具、每一个角色、每一种结局。
          </p>
        </div>
      </section>

      {/* 入口卡片 */}
      <section className={styles.cards}>
        {SECTIONS.map((s) => (
          <Link to={s.path} key={s.path} className={styles.card}>
            <img src={s.image} alt={s.title} className={styles.cardImage} />
            <span className={styles.badge}>{s.count}</span>
            <h3 className={styles.cardTitle}>{s.title}</h3>
            <p className={styles.cardDesc}>{s.desc}</p>
          </Link>
        ))}
        {/* 社区入口 — 全宽卡片 */}
        <Link to="/guides" className={`${styles.card} ${styles.communityCard}`}>
          <div className={styles.communityImages}>
            <img src="/images/community-discuss/1.gif" alt="攻略" className={styles.communityImage} />
            <img src="/images/community-discuss/2.gif" alt="讨论" className={styles.communityImage} />
            <img src="/images/community-discuss/3.png" alt="收藏" className={styles.communityImage} />
          </div>
          <span className={styles.badge}>NEW</span>
          <h3 className={styles.cardTitle}>玩家社区</h3>
          <p className={styles.cardDesc}>分享攻略、交流心得、收藏你喜欢的帖子</p>
        </Link>
      </section>

      {/* 底部信息 */}
      <footer className={styles.bottom}>
        <p>游戏版权 &copy; Edmund McMillen / Nicalis</p>
        <p>本站为玩家社区项目，仅供学习交流</p>
      </footer>
    </div>
  );
}
