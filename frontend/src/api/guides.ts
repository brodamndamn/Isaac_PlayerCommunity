import client from "./client";
import type { ApiResponse, PaginatedData } from "../types/api";
import type { Guide } from "../types/guide";

export async function getGuides(params: {
  page?: number;
  page_size?: number;
  category?: string;
  search?: string;
}): Promise<ApiResponse<PaginatedData<Guide>>> {
  const { data } = await client.get("/guides", { params });
  return data;
}

export async function getGuideById(id: number): Promise<ApiResponse<Guide>> {
  const { data } = await client.get(`/guides/${id}`);
  return data;
}

export async function createGuide(body: {
  title: string;
  content: string;
  category: string;
  cover_image?: string;
  related_item_id?: number;
  related_character_id?: number;
  related_ending_id?: number;
}): Promise<ApiResponse<Guide>> {
  const { data } = await client.post("/guides", body);
  return data;
}

export async function deleteGuide(id: number): Promise<ApiResponse<null>> {
  const { data } = await client.delete(`/guides/${id}`);
  return data;
}
