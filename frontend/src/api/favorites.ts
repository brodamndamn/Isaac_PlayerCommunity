import client from "./client";
import type { ApiResponse, PaginatedData } from "../types/api";
import type { Favorite } from "../types/favorite";

export async function getMyFavorites(params: {
  page?: number;
  page_size?: number;
}): Promise<ApiResponse<PaginatedData<Favorite>>> {
  const { data } = await client.get("/favorites", { params });
  return data;
}

export async function addFavorite(guideId: number): Promise<ApiResponse<Favorite>> {
  const { data } = await client.post(`/favorites?guide_id=${guideId}`);
  return data;
}

export async function removeFavorite(guideId: number): Promise<ApiResponse<null>> {
  const { data } = await client.delete(`/favorites/${guideId}`);
  return data;
}
