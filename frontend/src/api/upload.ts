import client from "./client";
import { normalizeMediaUrl } from "../lib/paths";
import type { ApiResponse } from "../types/api";

export async function uploadImage(file: File): Promise<ApiResponse<{ url: string }>> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await client.post<ApiResponse<{ url: string }>>("/upload", form);
  if (data.data?.url) {
    data.data.url = normalizeMediaUrl(data.data.url);
  }
  return data;
}
