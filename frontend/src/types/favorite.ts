export interface Favorite {
  id: number;
  user_id: number;
  guide_id: number;
  guide_title: string;
  guide_author: string;
  guide_author_avatar: string | null;
  guide_category: string;
  guide_cover: string | null;
  guide_like_count: number;
  guide_fav_count: number;
  guide_is_liked: boolean;
  guide_is_favorited: boolean;
  created_at: string;
}
