import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { getMe, type UserData } from "../api/auth";

interface AuthCtx {
  user: UserData | null;
  authChecked: boolean;
  modalOpen: boolean;
  modalTab: "login" | "register";
  login: (u: UserData) => void;
  logout: () => void;
  openModal: (tab: "login" | "register") => void;
  closeModal: () => void;
}

const AuthContext = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserData | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalTab, setModalTab] = useState<"login" | "register">("login");

  // 页面加载时从 localStorage token 恢复登录状态
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setAuthChecked(true);
      return;
    }
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem("access_token"))
      .finally(() => setAuthChecked(true));
  }, []);

  // 监听 401 拦截器发出的 token 清除事件
  useEffect(() => {
    const handler = () => setUser(null);
    window.addEventListener("auth:logout", handler);
    return () => window.removeEventListener("auth:logout", handler);
  }, []);

  const login = useCallback((u: UserData) => {
    setUser(u);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setUser(null);
  }, []);

  const openModal = useCallback((tab: "login" | "register") => {
    setModalTab(tab);
    setModalOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setModalOpen(false);
  }, []);

  return (
    <AuthContext.Provider value={{ user, authChecked, modalOpen, modalTab, login, logout, openModal, closeModal }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
