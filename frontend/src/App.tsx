import { BrowserRouter, Route, Routes } from "react-router-dom";
import AuthModal from "./components/AuthModal";
import { useAuth } from "./hooks/useAuth";
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
import TransformationDetailPage from "./pages/TransformationDetailPage";

export default function App() {
  const { user, authChecked, modalOpen, modalTab, modalKey, login, logout, openModal, closeModal } = useAuth();

  return (
    <BrowserRouter>
      <div style={{ minHeight: "100vh" }}>
        <header
          style={{
            padding: "0 24px",
            height: 56,
            background: "#1a0a00",
            display: "flex",
            alignItems: "center",
            gap: 24,
            borderBottom: "2px solid #6b3a2a",
          }}
        >
          <a href="/" style={{ color: "#eee", fontWeight: 600, textDecoration: "none", fontSize: 18 }}>
            ISAAC 玩家社区
          </a>
          <a href="/items" style={{ color: "#ccc", textDecoration: "none", fontSize: 14 }}>
            道具
          </a>
          <a href="/characters" style={{ color: "#ccc", textDecoration: "none", fontSize: 14 }}>
            角色
          </a>
          <a href="/endings" style={{ color: "#ccc", textDecoration: "none", fontSize: 14 }}>
            结局
          </a>
          <a href="/guides" style={{ color: "#ccc", textDecoration: "none", fontSize: 14 }}>
            社区
          </a>

          {/* 右侧：登录/注册 或 用户信息 */}
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 12 }}>
            {authChecked ? (
              user ? (
                <>
                  <a href="/favorites" style={{ color: "#ccc", textDecoration: "none", fontSize: 13 }}>
                    我的收藏
                  </a>
                  <span style={{ color: "#ccc", fontSize: 13 }}>{user.username}</span>
                  <button
                    onClick={logout}
                    style={{
                      background: "none",
                      border: "1px solid #6b3a2a",
                      color: "#ccc",
                      padding: "3px 10px",
                      borderRadius: 4,
                      cursor: "pointer",
                      fontSize: 12,
                      fontFamily: "inherit",
                    }}
                  >
                    退出
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => openModal("login")}
                    style={{
                      background: "none",
                      border: "none",
                      color: "#ccc",
                      cursor: "pointer",
                      fontSize: 13,
                      fontFamily: "inherit",
                    }}
                  >
                    登录
                  </button>
                  <span style={{ color: "#555" }}>|</span>
                  <button
                    onClick={() => openModal("register")}
                    style={{
                      background: "none",
                      border: "none",
                      color: "#ccc",
                      cursor: "pointer",
                      fontSize: 13,
                      fontFamily: "inherit",
                    }}
                  >
                    注册
                  </button>
                </>
              )
            ) : null}
          </div>
        </header>

        <main style={{ maxWidth: 960, margin: "0 auto", padding: 24, position: "relative" }}>
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
            <Route path="/transformations/:id" element={<TransformationDetailPage />} />
          </Routes>
        </main>

        <footer style={{ textAlign: "center", padding: 16, fontSize: 13, color: "#999", borderTop: "1px solid #eee" }}>
          游戏图片版权 &copy; Edmund McMillen / Nicalis
        </footer>
      </div>

      <AuthModal
        key={modalKey}
        isOpen={modalOpen}
        initialTab={modalTab}
        onClose={closeModal}
        onLogin={login}
      />
    </BrowserRouter>
  );
}
