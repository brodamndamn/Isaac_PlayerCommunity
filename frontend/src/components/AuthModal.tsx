import { useState, type FormEvent, type KeyboardEvent } from "react";
import { login, register, type UserData } from "../api/auth";
import styles from "./AuthModal.module.css";

const SAVED_KEY = "saved_credentials";

function loadSaved() {
  try {
    const raw = localStorage.getItem(SAVED_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return null;
}

interface AuthModalProps {
  isOpen: boolean;
  initialTab?: "login" | "register";
  onClose: () => void;
  onLogin: (user: UserData) => void;
}

export default function AuthModal({ isOpen, initialTab = "login", onClose, onLogin }: AuthModalProps) {
  const saved = loadSaved();
  const [tab, setTab] = useState<"login" | "register">(initialTab);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // 登录表单 —— 挂载时从 localStorage 恢复
  const [loginField, setLoginField] = useState(saved?.login || "");
  const [loginPassword, setLoginPassword] = useState(saved?.password || "");
  const [showLoginPw, setShowLoginPw] = useState(false);
  const [rememberMe, setRememberMe] = useState(!!saved);

  // 注册表单
  const [regUsername, setRegUsername] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [showRegPw, setShowRegPw] = useState(false);
  const [regConfirm, setRegConfirm] = useState("");
  const [showConfirmPw, setShowConfirmPw] = useState(false);

  if (!isOpen) return null;

  const reset = () => {
    setError("");
    setLoginField("");
    setLoginPassword("");
    setRegUsername("");
    setRegEmail("");
    setRegPassword("");
    setRegConfirm("");
  };

  const switchTab = (t: "login" | "register") => {
    setTab(t);
    setError("");
  };

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    if (!loginField.trim() || !loginPassword) return;
    setError("");
    setLoading(true);
    try {
      const res = await login({ login: loginField.trim(), password: loginPassword, remember_me: rememberMe });
      localStorage.setItem("access_token", res.data.token);
      // 记住密码：保存账号密码到 localStorage；不勾选则清除
      if (rememberMe) {
        localStorage.setItem(SAVED_KEY, JSON.stringify({ login: loginField.trim(), password: loginPassword }));
      } else {
        localStorage.removeItem(SAVED_KEY);
      }
      onLogin(res.data.user);
      onClose();
      reset();
    } catch (err: any) {
      setError(err.response?.data?.message || "登录失败，请重试");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();
    if (!regUsername.trim() || !regEmail.trim() || !regPassword) return;
    if (regPassword !== regConfirm) {
      setError("两次输入的密码不一致");
      return;
    }
    if (regPassword.length < 6) {
      setError("密码至少 6 位");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await register({
        username: regUsername.trim(),
        email: regEmail.trim(),
        password: regPassword,
      });
      // 注册成功后自动登录
      const loginRes = await login({ login: regUsername.trim(), password: regPassword });
      localStorage.setItem("access_token", loginRes.data.token);
      onLogin(loginRes.data.user);
      onClose();
      reset();
    } catch (err: any) {
      setError(err.response?.data?.message || "注册失败，请重试");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Escape") onClose();
  };

  return (
    <div className={styles.overlay} onKeyDown={handleKeyDown}>
      <div className={styles.modal}>
        <button className={styles.closeBtn} onClick={onClose} aria-label="关闭">
          &times;
        </button>

        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${tab === "login" ? styles.active : ""}`}
            onClick={() => switchTab("login")}
          >
            登录
          </button>
          <button
            className={`${styles.tab} ${tab === "register" ? styles.active : ""}`}
            onClick={() => switchTab("register")}
          >
            注册
          </button>
        </div>

        {error && <p className={styles.error}>{error}</p>}

        {tab === "login" ? (
          <form onSubmit={handleLogin} className={styles.form}>
            <input
              className={styles.input}
              type="text"
              placeholder="用户名或邮箱"
              value={loginField}
              onChange={(e) => setLoginField(e.target.value)}
              autoFocus
            />
            <div className={styles.passwordWrap}>
              <input
                className={styles.input}
                type={showLoginPw ? "text" : "password"}
                placeholder="密码"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
              />
              <button
                type="button"
                className={styles.togglePw}
                onClick={() => setShowLoginPw((v) => !v)}
                tabIndex={-1}
              >
                {showLoginPw ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  ) : (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                      <path d="M1 1l22 22" />
                      <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24" />
                    </svg>
                  )}
              </button>
            </div>
            <label className={styles.remember}>
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              记住密码（7 天内自动登录）
            </label>
            <button className={styles.submitBtn} type="submit" disabled={loading}>
              {loading ? "登录中..." : "登录"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className={styles.form}>
            <input
              className={styles.input}
              type="text"
              placeholder="用户名"
              value={regUsername}
              onChange={(e) => setRegUsername(e.target.value)}
              autoFocus
            />
            <input
              className={styles.input}
              type="email"
              placeholder="邮箱"
              value={regEmail}
              onChange={(e) => setRegEmail(e.target.value)}
            />
            <div className={styles.passwordWrap}>
              <input
                className={styles.input}
                type={showRegPw ? "text" : "password"}
                placeholder="密码（至少 6 位）"
                value={regPassword}
                onChange={(e) => setRegPassword(e.target.value)}
              />
              <button
                type="button"
                className={styles.togglePw}
                onClick={() => setShowRegPw((v) => !v)}
                tabIndex={-1}
              >
                {showRegPw ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  ) : (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                      <path d="M1 1l22 22" />
                      <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24" />
                    </svg>
                  )}
              </button>
            </div>
            <div className={styles.passwordWrap}>
              <input
                className={styles.input}
                type={showConfirmPw ? "text" : "password"}
                placeholder="确认密码"
                value={regConfirm}
                onChange={(e) => setRegConfirm(e.target.value)}
              />
              <button
                type="button"
                className={styles.togglePw}
                onClick={() => setShowConfirmPw((v) => !v)}
                tabIndex={-1}
              >
                {showConfirmPw ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  ) : (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                      <path d="M1 1l22 22" />
                      <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24" />
                    </svg>
                  )}
              </button>
            </div>
            <button className={styles.submitBtn} type="submit" disabled={loading}>
              {loading ? "注册中..." : "注册"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
