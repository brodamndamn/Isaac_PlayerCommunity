export interface Character {
  id: number;
  name_en: string;
  name_cn: string;
  is_tainted: boolean;
  base_character_id: number | null;
  health: string;
  damage: number | null;
  speed: number | null;
  tears: number | null;
  starting_items: number[] | null;
  unlock_method: string | null;
  description: string | null;
  suitable_items: number[] | null;
  image_url: string | null;
}
