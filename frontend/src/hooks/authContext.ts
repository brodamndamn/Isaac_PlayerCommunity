import { createContext } from "react";
import type { UserData } from "../api/auth";

export interface AuthCtx {
  user: UserData | null;
  authChecked: boolean;
  modalOpen: boolean;
  modalTab: "login" | "register";
  login: (user: UserData) => void;
  logout: () => void;
  openModal: (tab: "login" | "register") => void;
  closeModal: () => void;
}

export const AuthContext = createContext<AuthCtx | null>(null);
