import { BrowserRouter, Route, Routes } from "react-router-dom";
import CharacterDetailPage from "./pages/CharacterDetailPage";
import CharactersPage from "./pages/CharactersPage";
import EndingDetailPage from "./pages/EndingDetailPage";
import EndingsPage from "./pages/EndingsPage";
import HomePage from "./pages/HomePage";
import ItemDetailPage from "./pages/ItemDetailPage";
import ItemsPage from "./pages/ItemsPage";
import TransformationDetailPage from "./pages/TransformationDetailPage";

export default function App() {
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
            <Route path="/transformations/:id" element={<TransformationDetailPage />} />
          </Routes>
        </main>
        <footer style={{ textAlign: "center", padding: 16, fontSize: 13, color: "#999", borderTop: "1px solid #eee" }}>
          游戏图片版权 &copy; Edmund McMillen / Nicalis
        </footer>
      </div>
    </BrowserRouter>
  );
}
