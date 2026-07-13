import client from "./client";
import type { ApiResponse, PaginatedData } from "../types/api";
import type { Character } from "../types/character";

export async function getCharacters(params: {
  page?: number;
  page_size?: number;
  is_tainted?: boolean;
  search?: string;
}): Promise<ApiResponse<PaginatedData<Character>>> {
  const { data } = await client.get("/characters", { params });
  return data;
}

export async function getCharacterById(id: number): Promise<ApiResponse<Character>> {
  const { data } = await client.get(`/characters/${id}`);
  return data;
}
