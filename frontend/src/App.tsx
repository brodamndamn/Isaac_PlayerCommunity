import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import AuthModal from "./components/AuthModal";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import CharacterDetailPage from "./pages/CharacterDetailPage";
import CharactersPage from "./pages/CharactersPage";
import CreateGuidePage from "./pages/CreateGuidePage";
import EndingDetailPage from "./pages/EndingDetailPage";
import EndingsPage from "./pages/EndingsPage";
import GuideDetailPage from "./pages/GuideDetailPage";
import GuidesPage from "./pages/GuidesPage";
import HomePage from "./pages/HomePage";
import ItemDetailPage from "./pages/ItemDetailPage";
import ItemsPage from "./pages/ItemsPage";
import MyFavoritesPage from "./pages/MyFavoritesPage";
import ProfilePage from "./pages/ProfilePage";
import TransformationDetailPage from "./pages/TransformationDetailPage";
import styles from "./App.module.css";

function AppInner() {
  const { user, authChecked, modalOpen, modalTab, login, logout, openModal, closeModal } = useAuth();

  return (
    <div style={{ minHeight: "100vh" }}>
      <header className={styles.header}>
        <a href="/" className={styles.brand}>ISAAC 玩家社区</a>
        <a href="/items" className={styles.navLink}>道具</a>
        <a href="/characters" className={styles.navLink}>角色</a>
        <a href="/endings" className={styles.navLink}>结局</a>
        <a href="/guides" className={styles.navLink}>社区</a>

        <div className={styles.navRight}>
          {authChecked ? (
            user ? (
              <>
                <Link to="/profile" style={{ display: "flex", alignItems: "center" }}>
                  {user.avatar ? (
                    <img src={`/uploads/${user.avatar}`} alt="头像" className={styles.avatarImg} />
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
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/items" element={<ItemsPage />} />
          <Route path="/items/:id" element={<ItemDetailPage />} />
          <Route path="/characters" element={<CharactersPage />} />
          <Route path="/characters/:id" element={<CharacterDetailPage />} />
          <Route path="/endings" element={<EndingsPage />} />
          <Route path="/endings/:id" element={<EndingDetailPage />} />
          <Route path="/guides" element={<GuidesPage />} />
          <Route path="/guides/new" element={<CreateGuidePage />} />
          <Route path="/guides/:id" element={<GuideDetailPage />} />
          <Route path="/favorites" element={<MyFavoritesPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/transformations/:id" element={<TransformationDetailPage />} />
        </Routes>
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
    <BrowserRouter>
      <AuthProvider>
        <AppInner />
      </AuthProvider>
    </BrowserRouter>
  );
}
