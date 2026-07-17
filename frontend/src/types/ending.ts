export interface EnrichedUnlock {
  text: string;
  unlock_type: string;
  item_id: number | null;
  character_id: number | null;
  image_url: string | null;
  label_cn: string | null;
}

export interface Ending {
  id: number;
  name_en: string;
  name_cn: string;
  ending_number: number;
  completion_method: string;
  unlock_method: string | null;
  required_character: string | null;
  boss_name: string;
  unlocks: string[] | null;
  unlocks_enriched?: EnrichedUnlock[] | null;
  image_url: string | null;
}
