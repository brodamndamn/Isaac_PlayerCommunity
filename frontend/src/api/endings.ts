import client from "./client";
import type { ApiResponse, PaginatedData } from "../types/api";
import type { Ending } from "../types/ending";

export async function getEndings(params: {
  page?: number;
  page_size?: number;
  search?: string;
}): Promise<ApiResponse<PaginatedData<Ending>>> {
  const { data } = await client.get("/endings", { params });
  return data;
}

export async function getEndingById(id: number): Promise<ApiResponse<Ending>> {
  const { data } = await client.get(`/endings/${id}`);
  return data;
}
