export interface Guide {
  id: number;
  title: string;
  content: string;
  author_id: number;
  author_name: string;
  category: string;
  related_item_id: number | null;
  related_character_id: number | null;
  related_ending_id: number | null;
  created_at: string;
  updated_at: string;
}
