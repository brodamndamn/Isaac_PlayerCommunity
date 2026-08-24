import { BrowserRouter, Link, useRoutes } from "react-router-dom";
import AuthModal from "./components/AuthModal";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import { APP_BASE_PATH, staticUrl } from "./lib/paths";
import { APP_ROUTES } from "./routes";
import styles from "./App.module.css";

function AppRoutes() {
  return useRoutes(APP_ROUTES);
}

function AppInner() {
  const { user, authChecked, modalOpen, modalTab, login, logout, openModal, closeModal } = useAuth();

  return (
    <div style={{ minHeight: "100vh" }}>
      <header className={styles.header}>
        <Link to="/" className={styles.brand}>ISAAC 玩家社区</Link>
        <Link to="/items" className={styles.navLink}>道具</Link>
        <Link to="/characters" className={styles.navLink}>角色</Link>
        <Link to="/endings" className={styles.navLink}>结局</Link>
        <Link to="/guides" className={styles.navLink}>社区</Link>

        <div className={styles.navRight}>
          {authChecked ? (
            user ? (
              <>
                <Link to="/profile" style={{ display: "flex", alignItems: "center" }}>
                  {user.avatar ? (
                    <img src={staticUrl(`uploads/${user.avatar}`)} alt="头像" className={styles.avatarImg} />
                  ) : (
                    <span className={styles.avatarFallback}>{user.username[0].toUpperCase()}</span>
                  )}
                </Link>
                <Link to="/profile" style={{ color: "#ccc", fontSize: 13, textDecoration: "none" }}>{user.username}</Link>
                <button onClick={logout} className={styles.logoutBtn}>退出</button>
              </>
            ) : (
              <>
                <button onClick={() => openModal("login")} className={styles.authBtn}>登录</button>
                <span style={{ color: "#555" }}>|</span>
                <button onClick={() => openModal("register")} className={styles.authBtn}>注册</button>
              </>
            )
          ) : null}
        </div>
      </header>

      <main className={styles.main}>
        <AppRoutes />
      </main>

      <footer className={styles.footer}>
        游戏图片版权 &copy; Edmund McMillen / Nicalis
      </footer>

      <AuthModal isOpen={modalOpen} initialTab={modalTab} onClose={closeModal} onLogin={login} />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter basename={APP_BASE_PATH || "/"}>
      <AuthProvider>
        <AppInner />
      </AuthProvider>
    </BrowserRouter>
  );
}
