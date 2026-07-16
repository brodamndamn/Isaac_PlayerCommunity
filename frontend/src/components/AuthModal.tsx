import { useState, type FormEvent, type KeyboardEvent } from "react";
import { login, register, type UserData } from "../api/auth";
import styles from "./AuthModal.module.css";

interface AuthModalProps {
  isOpen: boolean;
  initialTab?: "login" | "register";
  onClose: () => void;
  onLogin: (user: UserData) => void;
}

export default function AuthModal({ isOpen, initialTab = "login", onClose, onLogin }: AuthModalProps) {
  const [tab, setTab] = useState<"login" | "register">(initialTab);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // 登录表单
  const [loginField, setLoginField] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // 注册表单
  const [regUsername, setRegUsername] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regConfirm, setRegConfirm] = useState("");

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
      const res = await login({ login: loginField.trim(), password: loginPassword });
      localStorage.setItem("access_token", res.data.token);
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

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) onClose();
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Escape") onClose();
  };

  return (
    <div className={styles.overlay} onClick={handleOverlayClick} onKeyDown={handleKeyDown}>
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
            <input
              className={styles.input}
              type="password"
              placeholder="密码"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
            />
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
            <input
              className={styles.input}
              type="password"
              placeholder="密码（至少 6 位）"
              value={regPassword}
              onChange={(e) => setRegPassword(e.target.value)}
            />
            <input
              className={styles.input}
              type="password"
              placeholder="确认密码"
              value={regConfirm}
              onChange={(e) => setRegConfirm(e.target.value)}
            />
            <button className={styles.submitBtn} type="submit" disabled={loading}>
              {loading ? "注册中..." : "注册"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
