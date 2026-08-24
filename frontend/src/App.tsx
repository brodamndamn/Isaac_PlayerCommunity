import { BrowserRouter, Link, NavLink, useRoutes } from "react-router-dom";
import AuthModal from "./components/AuthModal";
import { AuthProvider } from "./hooks/useAuth";
import { useAuth } from "./hooks/useAuthHook";
import { APP_BASE_PATH, staticUrl, uploadUrl } from "./lib/paths";
import { APP_ROUTES } from "./routes";
import styles from "./App.module.css";

const NAV_ITEMS = [
  { to: "/items", label: "道具" },
  { to: "/characters", label: "角色" },
  { to: "/endings", label: "结局" },
  { to: "/guides", label: "社区" },
];

function AppRoutes() { return useRoutes(APP_ROUTES); }

function AppInner() {
  const { user, authChecked, modalOpen, modalTab, login, logout, openModal, closeModal } = useAuth();

  return (
    <div className={styles.appShell}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <Link to="/" className={styles.brand} aria-label="返回 ISAAC 玩家社区首页">
            <img src={staticUrl("favicon.ico")} alt="" className={styles.brandSigil} />
            <span className={styles.brandCopy}><strong>ISAAC</strong><small>地下室档案</small></span>
          </Link>
          <nav className={styles.nav} aria-label="主要导航">
            {NAV_ITEMS.map((item) => (
              <NavLink key={item.to} to={item.to} className={({ isActive }) => `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`}>
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className={styles.navRight}>
            {authChecked ? user ? (
              <>
                <Link to="/profile" className={styles.userLink}>
                  {user.avatar ? (
                    <img
                      src={uploadUrl(user.avatar)}
                      alt="头像"
                      className={styles.avatarImg}
                      onError={(event) => { event.currentTarget.src = staticUrl("favicon.ico"); }}
                    />
                  ) : <span className={styles.avatarFallback}>{user.username[0].toUpperCase()}</span>}
                  <span>{user.username}</span>
                </Link>
                <button onClick={logout} className={styles.logoutBtn}>退出</button>
              </>
            ) : (
              <>
                <button onClick={() => openModal("login")} className={styles.authBtn}>登录</button>
                <span className={styles.authDivider}>/</span>
                <button onClick={() => openModal("register")} className={styles.authBtn}>注册</button>
              </>
            ) : null}
          </div>
        </div>
      </header>
      <main className={styles.main}><AppRoutes /></main>
      <footer className={styles.footer}>
        <span>ISAAC 玩家社区 · 非官方中文资料站</span>
        <span>游戏图片版权 © Edmund McMillen / Nicalis</span>
      </footer>
      <AuthModal isOpen={modalOpen} initialTab={modalTab} onClose={closeModal} onLogin={login} />
    </div>
  );
}

export default function App() {
  return <BrowserRouter basename={APP_BASE_PATH || "/"}><AuthProvider><AppInner /></AuthProvider></BrowserRouter>;
}
