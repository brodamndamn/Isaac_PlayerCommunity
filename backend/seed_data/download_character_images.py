"""
下载角色立绘到 frontend/public/images/characters/<id>.png

用法：cd backend && python seed_data/download_character_images.py
"""
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# 角色名到 Wiki 页面标题的映射
# Wiki 页面标题就是角色的英文名，但有些需要调整
CHARACTER_WIKI_MAP = {
    1: "Isaac",
    2: "Magdalene",
    3: "Cain",
    4: "Judas",
    5: "???",  # 没有图片
    6: "Eve",
    7: "Samson",
    8: "Azazel",
    9: "Lazarus",
    10: "Eden",
    11: "The Lost",
    12: "Lilith",
    13: "Keeper",
    14: "Apollyon",
    15: "The Forgotten",  # 没有图片
    16: "Bethany",
    17: "Jacob and Esau",  # Wiki 用 "and" 不是 "&"
    18: "Tainted Isaac",
    19: "Tainted Magdalene",
    20: "Tainted Cain",
    21: "Tainted Judas",
    22: "Tainted ???",
    23: "Tainted Eve",
    24: "Tainted Samson",
    25: "Tainted Azazel",
    26: "Tainted Lazarus",  # 没有图片
    27: "Tainted Eden",
    28: "Tainted Lost",
    29: "Tainted Lilith",
    30: "Tainted Keeper",
    31: "Tainted Apollyon",
    32: "Tainted Forgotten",  # 没有图片
    33: "Tainted Bethany",
    34: "Tainted Jacob",
}

# 没有 Wiki 图片的角色 ID
NO_IMAGE_CHARACTERS = {5, 15, 17, 26, 32}

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "characters"
WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"


def fetch_page_html(title: str) -> str | None:
    """从 Wiki API 获取页面 HTML。"""
    import urllib.parse
    encoded_title = urllib.parse.quote(title)
    url = f"{WIKI_API}?action=parse&page={encoded_title}&prop=text&format=json"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        if "parse" in data:
            return data["parse"]["text"]["*"]
    except Exception as e:
        print(f"    Error fetching page: {e}")
    return None


def extract_character_image_url(html: str) -> str | None:
    """从 HTML 中提取角色立绘 URL。"""
    # Pattern 1: alt="Character image" with data-src (lazy loading)
    # data-src contains the real URL, src contains placeholder GIF
    match = re.search(r'alt="Character image"[^>]*?data-src="([^"]+)"', html)
    if match:
        url = match.group(1)
        # Skip placeholder GIFs
        if 'data:image' not in url and 'base64' not in url:
            return url

    # Pattern 2: Character_<Name>_appearance.png
    match = re.search(r'(https?://[^"]+Character_[^"]+_appearance\.png[^"]*)', html)
    if match:
        url = match.group(1)
        if 'data:image' not in url and 'base64' not in url:
            return url

    return None


def download_image(url: str, output_path: Path) -> bool:
    """下载图片并保存。"""
    try:
        # Remove query parameters for cleaner URL
        clean_url = url.split('?')[0]
        req = urllib.request.Request(clean_url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=15)
        data = response.read()

        # Check if it's a valid image
        # Valid formats: PNG (starts with 89 50 4E 47) or WebP (starts with RIFF....WEBP)
        is_png = data[:4] == b'\x89PNG'
        is_webp = data[:4] == b'RIFF' and data[8:12] == b'WEBP'

        if is_png or is_webp:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(data)
            return True
        else:
            print(f"    Invalid image format (first 4 bytes: {data[:4]})")
            return False
    except Exception as e:
        print(f"    Download error: {e}")
        return False


def main():
    # Load characters
    with open('seed_data/characters.json', 'r', encoding='utf-8') as f:
        characters = json.load(f)

    print(f"Downloading character images...")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Characters to download: {len(characters) - len(NO_IMAGE_CHARACTERS)}")
    print()

    success_count = 0
    fail_count = 0

    for char in characters:
        char_id = char['id']
        name_en = char['name_en']

        # Skip characters without images
        if char_id in NO_IMAGE_CHARACTERS:
            print(f"#{char_id:2d} {name_en}: SKIPPED (no Wiki image)")
            continue

        # Check if already downloaded
        output_path = OUTPUT_DIR / f"{char_id}.png"
        if output_path.exists() and output_path.stat().st_size > 500:
            print(f"#{char_id:2d} {name_en}: ALREADY EXISTS ({output_path.stat().st_size} bytes)")
            success_count += 1
            continue

        # Get Wiki page title
        wiki_title = CHARACTER_WIKI_MAP.get(char_id, name_en)
        print(f"#{char_id:2d} {name_en} (Wiki: {wiki_title})...", end=" ", flush=True)

        # Fetch page
        html = fetch_page_html(wiki_title)
        if not html:
            print("FAILED (page not found)")
            fail_count += 1
            time.sleep(0.5)
            continue

        # Extract image URL
        image_url = extract_character_image_url(html)
        if not image_url:
            print("FAILED (no image in page)")
            fail_count += 1
            time.sleep(0.5)
            continue

        # Download image
        if download_image(image_url, output_path):
            print(f"OK ({output_path.stat().st_size} bytes)")
            success_count += 1
        else:
            print("FAILED (download error)")
            fail_count += 1

        time.sleep(0.5)  # Rate limiting

    print()
    print(f"Done: {success_count} success, {fail_count} failed")
    print(f"Total character images: {len(list(OUTPUT_DIR.glob('*.png')))}")


if __name__ == "__main__":
    main()
