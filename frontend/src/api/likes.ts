import client from "./client";
import type { ApiResponse } from "../types/api";

interface LikeData {
  like_count: number;
}

export async function addLike(guideId: number): Promise<ApiResponse<LikeData>> {
  const { data } = await client.post(`/likes?guide_id=${guideId}`);
  return data;
}

export async function removeLike(guideId: number): Promise<ApiResponse<LikeData>> {
  const { data } = await client.delete(`/likes/${guideId}`);
  return data;
}
