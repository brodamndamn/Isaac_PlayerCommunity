export interface Guide {
  id: number;
  title: string;
  content: string;
  author_id: number;
  author_name: string;
  author_avatar: string | null;
  category: string;
  cover_image: string | null;
  like_count: number;
  favorite_count: number;
  comment_count: number;
  is_liked: boolean;
  is_favorited: boolean;
  related_item_id: number | null;
  related_character_id: number | null;
  related_ending_id: number | null;
  created_at: string;
  updated_at: string;
}
