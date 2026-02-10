#!/usr/bin/env python3
"""Generate HUD sprite assets for Disco Cop.

Creates health/shield/boss bar frames and fills, weapon type icons,
ammo icon, and lives icon. All use the disco color palette.

Usage:
    python create_hud_sprites.py

Output goes to disco_cop/assets/sprites/ui/
"""

from pathlib import Path
from PIL import Image, ImageDraw

# ── Paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # disco_cop/blender/scripts -> project root
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "ui"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Disco Palette ──────────────────────────────────────────────────────
MAGENTA = (255, 20, 147)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
HOT_PINK = (255, 105, 180)
DEEP_PINK = (255, 20, 147)
DARK_PURPLE = (26, 10, 46)
MED_PURPLE = (147, 112, 219)
SILVER = (192, 192, 192)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
DARK_RED = (140, 20, 20)
CYAN_DIM = (0, 180, 200)
CYAN_DARK = (0, 100, 120)
GOLD_DIM = (200, 165, 0)
GOLD_DARK = (140, 110, 0)
TRANSPARENT = (0, 0, 0, 0)
FRAME_OUTER = (180, 140, 220)  # Light purple border
FRAME_INNER = (60, 30, 80)     # Dark purple interior
FRAME_HIGHLIGHT = (220, 180, 255)  # Top edge shine


# ── Bar Sprites ────────────────────────────────────────────────────────

def create_bar_frame(width: int, height: int, color_accent: tuple) -> Image.Image:
    """Create a bar frame with outer border, inner dark area, and accent corners."""
    img = Image.new("RGBA", (width, height), TRANSPARENT)
    d = ImageDraw.Draw(img)

    # Outer border
    d.rectangle([0, 0, width - 1, height - 1], outline=FRAME_OUTER)
    # Inner border
    d.rectangle([1, 1, width - 2, height - 2], outline=FRAME_INNER)
    # Dark fill inside
    d.rectangle([2, 2, width - 3, height - 3], fill=DARK_PURPLE)
    # Top highlight line
    d.line([2, 1, width - 3, 1], fill=FRAME_HIGHLIGHT)
    # Accent pixels in corners
    for x, y in [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]:
        img.putpixel((x, y), (*color_accent, 255))

    return img


def create_bar_fill(width: int, height: int, color_top: tuple, color_bot: tuple) -> Image.Image:
    """Create a bar fill with vertical gradient."""
    img = Image.new("RGBA", (width, height), TRANSPARENT)
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(color_top[0] * (1 - t) + color_bot[0] * t)
        g = int(color_top[1] * (1 - t) + color_bot[1] * t)
        b = int(color_top[2] * (1 - t) + color_bot[2] * t)
        for x in range(width):
            img.putpixel((x, y), (r, g, b, 255))
    return img


def generate_bars():
    """Generate health, shield, and boss bar frames and fills."""
    # Health bar: 100x12 frame, 96x8 fill
    health_frame = create_bar_frame(100, 12, RED)
    health_frame.save(OUTPUT_DIR / "hud_health_frame.png")

    health_fill = create_bar_fill(96, 8, RED, DARK_RED)
    health_fill.save(OUTPUT_DIR / "hud_health_fill.png")

    # Shield bar: 100x12 frame, 96x8 fill
    shield_frame = create_bar_frame(100, 12, CYAN)
    shield_frame.save(OUTPUT_DIR / "hud_shield_frame.png")

    shield_fill = create_bar_fill(96, 8, CYAN, CYAN_DARK)
    shield_fill.save(OUTPUT_DIR / "hud_shield_fill.png")

    # Boss bar: 200x16 frame, 196x12 fill
    boss_frame = create_bar_frame(200, 16, GOLD)
    boss_frame.save(OUTPUT_DIR / "hud_boss_frame.png")

    boss_fill = create_bar_fill(196, 12, GOLD, GOLD_DARK)
    boss_fill.save(OUTPUT_DIR / "hud_boss_fill.png")

    print("  [OK] Bar sprites (6 files)")


# ── Weapon Icons (16x16) ──────────────────────────────────────────────

def draw_pistol(d: ImageDraw.Draw):
    """Small handgun silhouette."""
    # Barrel
    d.rectangle([7, 6, 14, 8], fill=SILVER)
    # Body/grip frame
    d.rectangle([4, 5, 8, 9], fill=SILVER)
    # Grip
    d.rectangle([4, 9, 7, 13], fill=GOLD_DIM)
    # Trigger guard
    d.line([5, 10, 8, 10], fill=SILVER)
    # Muzzle highlight
    d.point([14, 7], fill=WHITE)


def draw_smg(d: ImageDraw.Draw):
    """Compact SMG with stock."""
    # Barrel
    d.rectangle([8, 6, 15, 7], fill=SILVER)
    # Body
    d.rectangle([3, 5, 9, 8], fill=SILVER)
    # Magazine
    d.rectangle([5, 8, 7, 12], fill=GOLD_DIM)
    # Stock
    d.rectangle([1, 6, 3, 8], fill=SILVER)
    # Muzzle flash hint
    d.point([15, 6], fill=MAGENTA)


def draw_shotgun(d: ImageDraw.Draw):
    """Wide-barrel shotgun."""
    # Long barrel
    d.rectangle([5, 5, 15, 7], fill=SILVER)
    # Wide muzzle
    d.rectangle([13, 4, 15, 8], fill=SILVER)
    # Stock
    d.rectangle([1, 5, 5, 8], fill=GOLD_DIM)
    # Pump grip
    d.rectangle([8, 8, 11, 9], fill=SILVER)
    # Trigger
    d.point([6, 9], fill=SILVER)


def draw_assault_rifle(d: ImageDraw.Draw):
    """Medium rifle with magazine."""
    # Barrel
    d.rectangle([7, 5, 15, 6], fill=SILVER)
    # Body
    d.rectangle([3, 5, 8, 8], fill=SILVER)
    # Magazine
    d.rectangle([5, 8, 7, 12], fill=GOLD_DIM)
    # Stock
    d.rectangle([1, 6, 3, 8], fill=SILVER)
    # Scope/sight
    d.rectangle([9, 4, 11, 5], fill=CYAN_DIM)


def draw_sniper(d: ImageDraw.Draw):
    """Long barrel with scope."""
    # Long barrel
    d.rectangle([5, 7, 15, 7], fill=SILVER)
    # Body
    d.rectangle([3, 6, 7, 8], fill=SILVER)
    # Scope
    d.rectangle([7, 4, 12, 5], fill=CYAN_DIM)
    d.rectangle([7, 5, 7, 6], fill=CYAN_DIM)  # Scope mount
    # Stock
    d.rectangle([1, 6, 3, 9], fill=GOLD_DIM)
    # Bipod
    d.line([5, 9, 4, 11], fill=SILVER)
    d.line([7, 9, 8, 11], fill=SILVER)


def draw_rocket_launcher(d: ImageDraw.Draw):
    """Wide tube launcher."""
    # Main tube
    d.rectangle([3, 4, 15, 9], fill=SILVER)
    # Bore (dark center)
    d.rectangle([13, 5, 15, 8], fill=DARK_PURPLE)
    # Grip
    d.rectangle([5, 9, 7, 12], fill=GOLD_DIM)
    # Sight
    d.rectangle([8, 3, 10, 4], fill=CYAN_DIM)
    # Exhaust end
    d.rectangle([3, 5, 3, 8], fill=GOLD_DIM)
    # Rocket tip hint
    d.point([14, 6], fill=RED)
    d.point([14, 7], fill=RED)


WEAPON_ICONS = {
    "icon_pistol": draw_pistol,
    "icon_smg": draw_smg,
    "icon_shotgun": draw_shotgun,
    "icon_assault_rifle": draw_assault_rifle,
    "icon_sniper": draw_sniper,
    "icon_rocket_launcher": draw_rocket_launcher,
}


def generate_weapon_icons():
    """Generate 16x16 weapon type icons."""
    for name, draw_fn in WEAPON_ICONS.items():
        img = Image.new("RGBA", (16, 16), TRANSPARENT)
        d = ImageDraw.Draw(img)
        draw_fn(d)
        img.save(OUTPUT_DIR / f"{name}.png")
    print(f"  [OK] Weapon icons ({len(WEAPON_ICONS)} files)")


# ── Small Icons ────────────────────────────────────────────────────────

def generate_ammo_icon():
    """Generate 8x8 ammo bullet icon."""
    img = Image.new("RGBA", (8, 8), TRANSPARENT)
    d = ImageDraw.Draw(img)
    # Bullet casing
    d.rectangle([2, 3, 5, 7], fill=GOLD_DIM)
    # Bullet tip
    d.rectangle([2, 1, 5, 3], fill=SILVER)
    d.point([2, 1], fill=TRANSPARENT)
    d.point([5, 1], fill=TRANSPARENT)
    # Highlight
    d.point([3, 2], fill=WHITE)
    img.save(OUTPUT_DIR / "icon_ammo.png")
    print("  [OK] Ammo icon")


def generate_lives_icon():
    """Generate 12x12 mini player head icon (disco cop with afro + shades)."""
    img = Image.new("RGBA", (12, 12), TRANSPARENT)
    d = ImageDraw.Draw(img)
    # Afro (big round hair)
    d.ellipse([1, 0, 10, 7], fill=(60, 30, 15))  # Dark brown afro
    # Face
    d.rectangle([3, 4, 8, 9], fill=(180, 120, 80))  # Skin
    # Sunglasses
    d.rectangle([3, 5, 5, 6], fill=GOLD_DIM)  # Left lens
    d.rectangle([6, 5, 8, 6], fill=GOLD_DIM)  # Right lens
    d.line([5, 5, 6, 5], fill=GOLD)  # Bridge
    # Mouth
    d.point([5, 8], fill=(140, 80, 50))
    d.point([6, 8], fill=(140, 80, 50))
    # Collar hint
    d.rectangle([3, 9, 8, 11], fill=MAGENTA)  # Disco jacket
    # Gold chain
    d.point([5, 10], fill=GOLD)
    d.point([6, 10], fill=GOLD)
    img.save(OUTPUT_DIR / "icon_life.png")
    print("  [OK] Lives icon")


# ── Main ───────────────────────────────────────────────────────────────

def main():
    print(f"Generating HUD sprites to: {OUTPUT_DIR}")
    generate_bars()
    generate_weapon_icons()
    generate_ammo_icon()
    generate_lives_icon()
    print(f"\nDone! {len(list(OUTPUT_DIR.glob('hud_*'))) + len(list(OUTPUT_DIR.glob('icon_*')))} HUD files generated.")


if __name__ == "__main__":
    main()