import client from "./client";
import type { ApiResponse } from "../types/api";

export async function uploadImage(file: File): Promise<ApiResponse<{ url: string }>> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await client.post("/upload", form);
  return data;
}
