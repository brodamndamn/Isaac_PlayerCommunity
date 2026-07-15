"""
下载缺失角色图片到 frontend/public/images/characters/<id>.png
优先尝试 Fandom Wiki，失败则尝试中文 wiki (灰机 wiki)

用法：cd backend && PYTHONPATH=. python seed_data/download_missing_character_images.py
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# 缺失角色 ID 和 Wiki 页面标题映射
MISSING_CHARACTERS = {
    5: {"en": "???", "wiki_fandom": "???", "wiki_cn": "???"},
    15: {"en": "The Forgotten", "wiki_fandom": "The Forgotten", "wiki_cn": "被遗忘者"},
    17: {"en": "Jacob & Esau", "wiki_fandom": "Jacob and Esau", "wiki_cn": "雅各与以扫"},
    26: {"en": "Tainted Lazarus", "wiki_fandom": "Tainted Lazarus", "wiki_cn": "里拉撒路"},
    32: {"en": "Tainted Forgotten", "wiki_fandom": "Tainted Forgotten", "wiki_cn": "里遗骸"},
}

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "characters"
FANDOM_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HUIJI_API = "https://isaac.huijiwiki.com/api.php"


def fetch_fandom_image(title: str) -> str | None:
    """从 Fandom Wiki 获取角色立绘 URL。"""
    encoded_title = urllib.parse.quote(title)
    url = f"{FANDOM_API}?action=parse&page={encoded_title}&prop=text&format=json"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        if "parse" not in data:
            return None
        html = data["parse"]["text"]["*"]

        # Pattern 1: alt="Character image" with data-src (lazy loading)
        match = re.search(r'alt="Character image"[^>]*?data-src="([^"]+)"', html)
        if match:
            url = match.group(1)
            if 'data:image' not in url and 'base64' not in url:
                return url

        # Pattern 2: Character_<Name>_appearance.png
        match = re.search(r'(https?://[^"]+Character_[^"]+_appearance\.png[^"]*)', html)
        if match:
            url = match.group(1)
            if 'data:image' not in url and 'base64' not in url:
                return url

    except Exception as e:
        print(f"    Fandom error: {e}")
    return None


def fetch_cn_image(title: str) -> str | None:
    """从灰机 wiki 获取角色立绘 URL。"""
    encoded_title = urllib.parse.quote(title)
    url = f"{HUIJI_API}?action=parse&page={encoded_title}&prop=text&format=json"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        if "parse" not in data:
            return None
        html = data["parse"]["text"]["*"]

        # 查找角色立绘图片 (通常在 infobox 中)
        # Pattern: data-src with character appearance image
        match = re.search(r'data-src="([^"]*(?:appearance|Character)[^"]*\.png[^"]*)"', html, re.IGNORECASE)
        if match:
            url = match.group(1)
            if 'data:image' not in url and 'base64' not in url:
                return url

        # Pattern: src with character image
        match = re.search(r'src="([^"]*(?:appearance|Character)[^"]*\.png[^"]*)"', html, re.IGNORECASE)
        if match:
            url = match.group(1)
            if 'data:image' not in url and 'base64' not in url:
                return url

        # Pattern: 任何 .png 图片 (排除小图标)
        matches = re.findall(r'(?:data-src|src)="([^"]+\.png[^"]*)"', html)
        for url in matches:
            if 'data:image' in url or 'base64' in url:
                continue
            # 排除小图标和 UI 元素
            if any(x in url.lower() for x in ['icon', 'logo', 'ui', 'button', 'frame']):
                continue
            return url

    except Exception as e:
        print(f"    Huiji error: {e}")
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
        is_png = data[:4] == b'\x89PNG'
        is_webp = data[:4] == b'RIFF' and data[8:12] == b'WEBP'
        is_jpeg = data[:2] == b'\xff\xd8'

        if is_png or is_webp or is_jpeg:
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
    print("Downloading missing character images...")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Missing characters: {len(MISSING_CHARACTERS)}")
    print()

    success_count = 0
    fail_count = 0

    for char_id, info in MISSING_CHARACTERS.items():
        output_path = OUTPUT_DIR / f"{char_id}.png"
        print(f"#{char_id:2d} {info['en']}...")

        # Try Fandom Wiki first
        print(f"  Trying Fandom Wiki ({info['wiki_fandom']})...", end=" ", flush=True)
        image_url = fetch_fandom_image(info['wiki_fandom'])
        if image_url:
            print(f"Found URL")
            if download_image(image_url, output_path):
                print(f"  -> OK ({output_path.stat().st_size} bytes)")
                success_count += 1
                time.sleep(0.5)
                continue
            else:
                print(f"  -> Download failed")
        else:
            print("No image found")

        # Try Chinese wiki
        print(f"  Trying Huiji Wiki ({info['wiki_cn']})...", end=" ", flush=True)
        image_url = fetch_cn_image(info['wiki_cn'])
        if image_url:
            print(f"Found URL")
            if download_image(image_url, output_path):
                print(f"  -> OK ({output_path.stat().st_size} bytes)")
                success_count += 1
                time.sleep(0.5)
                continue
            else:
                print(f"  -> Download failed")
        else:
            print("No image found")

        print(f"  -> FAILED (no image available)")
        fail_count += 1
        time.sleep(0.5)

    print()
    print(f"Done: {success_count} success, {fail_count} failed")
    print(f"Total character images: {len(list(OUTPUT_DIR.glob('*.png')))}")


if __name__ == "__main__":
    main()
