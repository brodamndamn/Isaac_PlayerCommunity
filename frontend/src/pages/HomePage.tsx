import { Link } from "react-router-dom";
import { staticUrl } from "../lib/paths";
import styles from "./HomePage.module.css";

const ARCHIVES = [
  { path: "/items", image: staticUrl("images/items/114.png"), kicker: "物品房档案", title: "道具图鉴", desc: "查看道具效果、品质、充能与解锁方式", count: "1000+", tone: "blood" },
  { path: "/characters", image: staticUrl("images/characters/1.png"), kicker: "地下室住客", title: "角色资料", desc: "整理角色属性、初始道具与解锁条件", count: "34", tone: "soul" },
  { path: "/endings", image: staticUrl("images/moms-heart.png"), kicker: "逃离记录", title: "结局档案", desc: "追踪达成路线、Boss 与对应解锁奖励", count: "20+", tone: "coin" },
];

export default function HomePage() {
  return (
    <div className={styles.root}>
      <section className={styles.hero}>
        <div className={styles.heroCopy}>
          <p className={styles.eyebrow}>BASEMENT ARCHIVE · B1</p>
          <h1 className={styles.title}>每一次通关，<br /><span>都值得记录。</span></h1>
          <p className={styles.heroDesc}>从地下室到天堂，从羔羊到 Mega Satan。这里整理每件道具、每位角色和每条逃离路线。</p>
          <div className={styles.heroActions}>
            <Link to="/items" className={styles.primaryAction}>翻开道具档案 <span>→</span></Link>
            <Link to="/guides" className={styles.secondaryAction}>前往玩家公告板</Link>
          </div>
        </div>

        <div className={styles.specimen} aria-label="D6 道具档案插图">
          <div className={styles.pin} />
          <span className={styles.specimenLabel}>SPECIMEN / 105</span>
          <img src={staticUrl("images/items/105.png")} alt="D6" />
          <p>“命运不好？那就再掷一次。”</p>
        </div>
      </section>

      <div className={styles.archiveHeading}>
        <div><p>地下室资料柜</p><h2>选择要翻阅的档案</h2></div>
        <span>所有图片均来自现有游戏资料库</span>
      </div>

      <section className={styles.cards}>
        {ARCHIVES.map((archive, index) => (
          <Link to={archive.path} key={archive.path} className={`${styles.card} ${styles[archive.tone]}`}>
            <div className={styles.cardTop}>
              <span className={styles.cardIndex}>0{index + 1}</span>
              <span className={styles.cardCount}>{archive.count}</span>
            </div>
            <div className={styles.spriteStage}><img src={archive.image} alt={archive.title} /></div>
            <p className={styles.cardKicker}>{archive.kicker}</p>
            <h3>{archive.title}</h3>
            <p className={styles.cardDesc}>{archive.desc}</p>
            <span className={styles.cardLink}>打开档案 <b>↗</b></span>
          </Link>
        ))}
      </section>

      <section className={styles.community}>
        <div className={styles.communityCopy}>
          <p className={styles.eyebrow}>COMMUNITY NOTICE BOARD</p>
          <h2>玩家留下的求生笔记</h2>
          <p>分享攻略、讨论搭配，收藏下一次下潜可能用到的线索。</p>
          <Link to="/guides" className={styles.primaryAction}>查看玩家攻略 <span>→</span></Link>
        </div>
        <div className={styles.communityImages}>
          <figure><img src={staticUrl("images/community-discuss/1.gif")} alt="玩家攻略" /><figcaption>攻略</figcaption></figure>
          <figure><img src={staticUrl("images/community-discuss/2.gif")} alt="玩家讨论" /><figcaption>讨论</figcaption></figure>
          <figure><img src={staticUrl("images/community-discuss/3.png")} alt="玩家收藏" /><figcaption>收藏</figcaption></figure>
        </div>
      </section>
    </div>
  );
}
