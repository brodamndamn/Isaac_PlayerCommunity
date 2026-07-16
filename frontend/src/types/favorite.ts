export interface Favorite {
  id: number;
  user_id: number;
  guide_id: number;
  guide_title: string;
  guide_author: string;
  guide_category: string;
  guide_cover: string | null;
  created_at: string;
}
