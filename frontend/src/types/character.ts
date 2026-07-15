export interface EnrichedStartingItem {
  id: number | null;
  name_en: string;
  name_cn: string;
  image_url: string | null;
}

export interface Character {
  id: number;
  name_en: string;
  name_cn: string;
  is_tainted: boolean;
  base_character_id: number | null;
  health: string;
  damage: string | null;
  speed: string | null;
  tears: string | null;
  starting_items: number[] | null;
  starting_items_enriched?: EnrichedStartingItem[] | null;
  unlock_method: string | null;
  description: string | null;
  suitable_items: number[] | null;
  image_url: string | null;
}
