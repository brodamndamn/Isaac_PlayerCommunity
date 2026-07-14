export interface Item {
  id: number;
  name_en: string;
  name_cn: string;
  category: string;
  quality: number | null;
  description: string;
  effect: string | null;
  unlock_method: string | null;
  pick_up_text: string | null;
  recharge_time: string | null;
  image_url: string | null;
  item_pools: string[] | null;
  stat_changes: string[][] | null;
  suitable_characters: number[] | null;
}
