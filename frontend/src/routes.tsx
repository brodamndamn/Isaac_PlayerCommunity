import type { RouteObject } from "react-router-dom";
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

export const APP_ROUTES: RouteObject[] = [
  { path: "/", element: <HomePage /> },
  { path: "/items", element: <ItemsPage /> },
  { path: "/items/:id", element: <ItemDetailPage /> },
  { path: "/characters", element: <CharactersPage /> },
  { path: "/characters/:id", element: <CharacterDetailPage /> },
  { path: "/endings", element: <EndingsPage /> },
  { path: "/endings/:id", element: <EndingDetailPage /> },
  { path: "/guides", element: <GuidesPage /> },
  { path: "/guides/new", element: <CreateGuidePage /> },
  { path: "/guides/:id", element: <GuideDetailPage /> },
  { path: "/favorites", element: <MyFavoritesPage /> },
  { path: "/profile", element: <ProfilePage /> },
  { path: "/transformations/:id", element: <TransformationDetailPage /> },
];
