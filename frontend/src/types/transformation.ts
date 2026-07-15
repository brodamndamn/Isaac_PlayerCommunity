export interface EnrichedItem {
  id: number | null;
  name_en: string;
  name_cn: string;
  image_url: string | null;
}

export interface Transformation {
  id: number;
  name_en: string;
  name_cn: string;
  items_needed: number;
  required_items: string[];
  effect: string | null;
  item_pools: string[] | null;
  required_items_enriched?: EnrichedItem[];
  first_item_id?: number | null;
}
