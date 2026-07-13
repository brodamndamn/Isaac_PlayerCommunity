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
  image_url: string | null;
}
