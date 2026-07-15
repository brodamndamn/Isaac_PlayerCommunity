import client from "./client";
import type { Transformation } from "../types/transformation";

interface ListResponse {
  code: number;
  message: string;
  data: {
    items: Transformation[];
    total: number;
  };
}

interface DetailResponse {
  code: number;
  message: string;
  data: Transformation | null;
}

export async function getTransformations(): Promise<ListResponse> {
  const { data } = await client.get("/transformations");
  return data;
}

export async function getTransformationById(id: number): Promise<DetailResponse> {
  const { data } = await client.get(`/transformations/${id}`);
  return data;
}
