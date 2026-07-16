import client from "./client";
import type { ApiResponse } from "../types/api";

export interface UserData {
  id: number;
  username: string;
  email: string;
  role: string;
  avatar: string | null;
  created_at: string;
}

export interface LoginData {
  token: string;
  user: UserData;
}

export async function register(body: {
  username: string;
  email: string;
  password: string;
}): Promise<ApiResponse<UserData>> {
  const { data } = await client.post("/auth/register", body);
  return data;
}

export async function login(body: {
  login: string;
  password: string;
}): Promise<ApiResponse<LoginData>> {
  const { data } = await client.post("/auth/login", body);
  return data;
}

export async function getMe(): Promise<ApiResponse<UserData>> {
  const { data } = await client.get("/auth/me");
  return data;
}
