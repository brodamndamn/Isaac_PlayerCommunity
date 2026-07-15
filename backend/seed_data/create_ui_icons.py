"""
创建生命类型和角色属性的 UI 图标图片

生命类型图标: frontend/public/images/heart/<type>.png
- red (红心), soul (魂心), black (黑心), eternal (永恒之心)
- gold (金心), bone (骨心), rotten (腐心)

角色属性图标: frontend/public/images/stat/<key>.png
- damage (伤害), tears (射速), speed (移速), range (射程)
- shot_speed (弹速), luck (幸运)

用法: cd backend && PYTHONPATH=. python seed_data/create_ui_icons.py
"""
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("PIL not available, using fallback method")

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images"

# Heart type definitions: (key, color, symbol)
HEART_TYPES = [
    ("red", (220, 20, 20), "♥"),
    ("soul", (50, 100, 220), "♥"),
    ("black", (40, 40, 40), "♥"),
    ("eternal", (255, 255, 255), "♥"),
    ("gold", (255, 215, 0), "♥"),
    ("bone", (200, 200, 180), "♥"),
    ("rotten", (100, 180, 50), "♥"),
]

# Stat definitions: (key, color, label)
STAT_TYPES = [
    ("damage", (220, 50, 50), "ATK"),
    ("tears", (50, 150, 220), "T"),
    ("speed", (50, 200, 100), "SPD"),
    ("range", (180, 100, 50), "RNG"),
    ("shot_speed", (150, 50, 180), "SS"),
    ("luck", (220, 180, 50), "LCK"),
]


def create_heart_icon_pil(color, size=22):
    """Create a heart icon using PIL."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw heart shape using two circles and a triangle
    margin = size // 6
    circle_r = (size - 2 * margin) // 3

    # Top-left circle
    draw.ellipse([margin, margin, margin + circle_r * 2, margin + circle_r * 2], fill=color)
    # Top-right circle
    draw.ellipse([size - margin - circle_r * 2, margin, size - margin, margin + circle_r * 2], fill=color)
    # Bottom triangle
    draw.polygon([
        (margin, size // 2),
        (size - margin, size // 2),
        (size // 2, size - margin)
    ], fill=color)

    return img


def create_stat_icon_pil(color, label, size=20):
    """Create a stat icon using PIL."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw circle background
    draw.ellipse([0, 0, size - 1, size - 1], fill=color)

    # Draw simple text (if available)
    try:
        from PIL import ImageFont
        font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size - text_w) // 2
        y = (size - text_h) // 2
        draw.text((x, y), label, fill=(255, 255, 255), font=font)
    except:
        pass

    return img


def create_heart_svg(color_hex, size=22):
    """Create a heart icon as SVG string."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 22 22">
  <path d="M11 18.5C11 18.5 2 12.5 2 7C2 4 4.5 2 7 2C8.5 2 10 3 11 4.5C12 3 13.5 2 15 2C17.5 2 20 4 20 7C20 12.5 11 18.5 11 18.5Z" fill="{color_hex}"/>
</svg>'''


def create_stat_svg(color_hex, label, size=20):
    """Create a stat icon as SVG string."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 20 20">
  <circle cx="10" cy="10" r="9" fill="{color_hex}"/>
  <text x="10" y="14" text-anchor="middle" fill="white" font-size="8" font-family="Arial">{label}</text>
</svg>'''


def color_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def main():
    # Create directories
    heart_dir = OUTPUT_DIR / "heart"
    stat_dir = OUTPUT_DIR / "stat"
    heart_dir.mkdir(parents=True, exist_ok=True)
    stat_dir.mkdir(parents=True, exist_ok=True)

    print("Creating heart type icons...")
    for key, color, symbol in HEART_TYPES:
        output_path = heart_dir / f"{key}.png"
        if HAS_PIL:
            img = create_heart_icon_pil(color)
            img.save(output_path)
        else:
            # Save SVG as .png (fallback - will need browser to render)
            svg_content = create_heart_svg(color_to_hex(color))
            svg_path = heart_dir / f"{key}.svg"
            with open(svg_path, 'w') as f:
                f.write(svg_content)
            print(f"  Created SVG: {svg_path.name}")
            continue
        print(f"  Created: {output_path.name}")

    print("\\nCreating stat icons...")
    for key, color, label in STAT_TYPES:
        output_path = stat_dir / f"{key}.png"
        if HAS_PIL:
            img = create_stat_icon_pil(color, label)
            img.save(output_path)
        else:
            svg_content = create_stat_svg(color_to_hex(color), label)
            svg_path = stat_dir / f"{key}.svg"
            with open(svg_path, 'w') as f:
                f.write(svg_content)
            print(f"  Created SVG: {svg_path.name}")
            continue
        print(f"  Created: {output_path.name}")

    print(f"\\nDone! Created {len(HEART_TYPES)} heart icons and {len(STAT_TYPES)} stat icons")


if __name__ == "__main__":
    main()
