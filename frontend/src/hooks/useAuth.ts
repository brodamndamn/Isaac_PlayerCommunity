import { useCallback, useEffect, useRef, useState } from "react";
import { getMe, type UserData } from "../api/auth";

export function useAuth() {
  const [user, setUser] = useState<UserData | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalTab, setModalTab] = useState<"login" | "register">("login");
  const modalKeyRef = useRef(0);

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

  const login = useCallback((u: UserData) => {
    setUser(u);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("saved_credentials");
    setUser(null);
  }, []);

  const openModal = useCallback((tab: "login" | "register") => {
    modalKeyRef.current += 1;
    setModalTab(tab);
    setModalOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setModalOpen(false);
  }, []);

  return { user, authChecked, modalOpen, modalTab, modalKey: modalKeyRef.current, login, logout, openModal, closeModal };
}
