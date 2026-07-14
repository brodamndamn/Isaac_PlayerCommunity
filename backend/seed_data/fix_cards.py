"""
Fix card/trinket overlap:
1. Remove 'Ace of Spades' from trinkets (duplicate - it's already a card at ID 833)
2. Re-number trinkets to fill the gap
3. Re-verify all category counts

Usage: cd backend && python seed_data/fix_cards.py
"""
import json
from pathlib import Path

SEED_DIR = Path(__file__).parent


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    items = load_json("items.json")

    # 1. Remove 'Ace of Spades' trinket (already exists as card ID 833)
    ace_trinket_idx = None
    for idx, item in enumerate(items):
        if item["category"] == "trinket" and item["name_en"] == "Ace of Spades":
            ace_trinket_idx = idx
            break

    if ace_trinket_idx is not None:
        removed = items.pop(ace_trinket_idx)
        print(f"Removed trinket: {removed['name_en']} (was ID {removed['id']})")
        print(f"  Already exists as card ID 833")
    else:
        print("Ace of Spades trinket not found - may already be fixed")

    # ID gap is OK — seed_data.py uses merge() which handles gaps fine

    # 3. Re-count
    passive = sum(1 for i in items if i["category"] == "passive" and i["id"] <= 732)
    active = sum(1 for i in items if i["category"] == "active" and i["id"] <= 732)
    trinket = sum(1 for i in items if i["category"] == "trinket")
    card = sum(1 for i in items if i["category"] == "card")
    pill = sum(1 for i in items if i["category"] == "pill")

    # Check items in ID range 1-732 not passive/active
    leftover = [i for i in items if i["id"] <= 732 and i["category"] not in ("passive", "active")]
    if leftover:
        print(f"\n[WARN] {len(leftover)} items in 1-732 not passive/active:")
        for i in leftover:
            print(f"  ID {i['id']}: {i['name_en']} ({i['category']})")

    # Check for any trinket names that overlap with card names
    card_names = {i["name_en"] for i in items if i["category"] == "card"}
    trinket_overlap = [i for i in items if i["category"] == "trinket" and i["name_en"] in card_names]
    if trinket_overlap:
        print(f"\n[WARN] {len(trinket_overlap)} trinkets still share names with cards:")
        for i in trinket_overlap:
            print(f"  ID {i['id']}: {i['name_en']}")

    # Save
    save_json("items.json", items)

    # Final report
    no_cn = sum(1 for i in items if not i.get("name_cn"))
    print(f"\nFinal counts:")
    print(f"  Passive (1-732): {passive}  (target: 548)")
    print(f"  Active  (1-732): {active}   (target: 171)")
    print(f"  Trinkets:         {trinket}  (was: 188)")
    print(f"  Cards:            {card}   (target: 98, currently 97)")
    print(f"  Pills:            {pill}")
    print(f"  Total items:      {len(items)}")
    print(f"  Without CN name:  {no_cn}")

    if card < 98:
        print(f"\n  Still need to add {98 - card} card(s).")

    print(f"\nNext: python seed_data.py")


if __name__ == "__main__":
    main()
