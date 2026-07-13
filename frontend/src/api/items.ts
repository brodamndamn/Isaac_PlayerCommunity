import client from "./client";
import type { ApiResponse, PaginatedData } from "../types/api";
import type { Item } from "../types/item";

export async function getItems(params: {
  page?: number;
  page_size?: number;
  category?: string;
  search?: string;
}): Promise<ApiResponse<PaginatedData<Item>>> {
  const { data } = await client.get("/items", { params });
  return data;
}

export async function getItemById(id: number): Promise<ApiResponse<Item>> {
  const { data } = await client.get(`/items/${id}`);
  return data;
}
