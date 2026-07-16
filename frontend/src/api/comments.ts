import client from "./client";

export async function likeComment(commentId: number): Promise<any> {
  const { data } = await client.post(`/comments/${commentId}/like`);
  return data;
}

export async function unlikeComment(commentId: number): Promise<any> {
  const { data } = await client.delete(`/comments/${commentId}/like`);
  return data;
}
