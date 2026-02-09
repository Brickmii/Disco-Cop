"""
Generate small pixel-art sprites for projectiles and loot drops.
These are too tiny for Blender — hand-drawn pixel art via Pillow.

Run via: python generate_small_sprites.py

Outputs:
  assets/sprites/weapons/projectile_*.png  (6 projectiles)
  assets/sprites/ui/loot_*.png             (4 loot icons)
"""

import os
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))
WEAPONS_DIR = os.path.join(BASE_DIR, 'assets', 'sprites', 'weapons')
UI_DIR = os.path.join(BASE_DIR, 'assets', 'sprites', 'ui')


def ensure_dirs():
    os.makedirs(WEAPONS_DIR, exist_ok=True)
    os.makedirs(UI_DIR, exist_ok=True)


def save(img, directory, name):
    path = os.path.join(directory, name)
    img.save(path)
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# Projectiles (drawn facing RIGHT along +X)
# ---------------------------------------------------------------------------

def create_projectile_bullet():
    """Default bullet: 10x4, bright yellow-white streak."""
    img = Image.new('RGBA', (10, 4), (0, 0, 0, 0))
    px = img.load()
    # Core bright line (row 1-2, cols 1-8)
    for x in range(1, 9):
        px[x, 1] = (255, 255, 200, 255)
        px[x, 2] = (255, 255, 200, 255)
    # Brighter tip
    px[8, 1] = (255, 255, 255, 255)
    px[8, 2] = (255, 255, 255, 255)
    px[9, 1] = (255, 255, 240, 200)
    px[9, 2] = (255, 255, 240, 200)
    # Dimmer trail
    px[0, 1] = (200, 200, 150, 150)
    px[0, 2] = (200, 200, 150, 150)
    # Top/bottom edge glow
    for x in range(2, 8):
        px[x, 0] = (255, 255, 180, 100)
        px[x, 3] = (255, 255, 180, 100)
    save(img, WEAPONS_DIR, 'projectile_bullet.png')


def create_projectile_fire():
    """Fire projectile: 10x4, orange-red gradient."""
    img = Image.new('RGBA', (10, 4), (0, 0, 0, 0))
    px = img.load()
    # Core — orange to red
    colors = [
        (180, 60, 20, 180),   # trail
        (220, 80, 10, 220),
        (255, 120, 10, 255),
        (255, 150, 20, 255),
        (255, 170, 30, 255),
        (255, 180, 40, 255),
        (255, 160, 20, 255),
        (255, 130, 10, 255),
        (255, 100, 0, 255),   # tip bright
        (255, 80, 0, 200),
    ]
    for x in range(10):
        px[x, 1] = colors[x]
        px[x, 2] = colors[x]
    # Flickering edges
    for x in range(1, 9):
        r, g, b, a = colors[x]
        px[x, 0] = (r, g + 20, b, a // 2)
        px[x, 3] = (r, g + 20, b, a // 2)
    save(img, WEAPONS_DIR, 'projectile_fire.png')


def create_projectile_ice():
    """Ice projectile: 10x4, cyan-blue crystal."""
    img = Image.new('RGBA', (10, 4), (0, 0, 0, 0))
    px = img.load()
    # Core — light blue to white
    for x in range(1, 9):
        t = x / 9.0
        r = int(150 + 105 * t)
        g = int(200 + 55 * t)
        b = 255
        px[x, 1] = (r, g, b, 255)
        px[x, 2] = (r, g, b, 255)
    # Bright tip
    px[8, 1] = (240, 250, 255, 255)
    px[8, 2] = (240, 250, 255, 255)
    px[9, 1] = (220, 240, 255, 200)
    px[9, 2] = (220, 240, 255, 200)
    # Trail
    px[0, 1] = (120, 180, 255, 150)
    px[0, 2] = (120, 180, 255, 150)
    # Edges — frosty glow
    for x in range(2, 8):
        px[x, 0] = (180, 220, 255, 80)
        px[x, 3] = (180, 220, 255, 80)
    save(img, WEAPONS_DIR, 'projectile_ice.png')


def create_projectile_electric():
    """Electric projectile: 10x4, bright yellow with jagged shape."""
    img = Image.new('RGBA', (10, 4), (0, 0, 0, 0))
    px = img.load()
    # Jagged bolt pattern — zigzag between rows
    # Row pattern: top-mid-bot-mid alternating
    bolt = [(1, 1), (2, 0), (3, 1), (4, 2), (5, 3), (6, 2), (7, 1), (8, 0), (9, 1)]
    for x, y in bolt:
        px[x, y] = (255, 255, 50, 255)
        # Thicken: fill adjacent row too
        if y > 0:
            px[x, y - 1] = (255, 255, 100, 200)
        if y < 3:
            px[x, y + 1] = (255, 255, 100, 200)
    # Core center glow
    for x in range(2, 9):
        px[x, 1] = (255, 255, 80, 255)
        px[x, 2] = (255, 255, 80, 255)
    # Trail
    px[0, 1] = (200, 200, 50, 150)
    px[0, 2] = (200, 200, 50, 150)
    save(img, WEAPONS_DIR, 'projectile_electric.png')


def create_projectile_explosive():
    """Explosive projectile: 12x6, dark red round shell."""
    img = Image.new('RGBA', (12, 6), (0, 0, 0, 0))
    px = img.load()
    # Oval body — dark red
    body = (160, 30, 20, 255)
    highlight = (200, 60, 40, 255)
    dark = (100, 20, 10, 255)
    # Fill oval shape
    #   Row 0:       ..XXXX....
    #   Row 1:     .XXXXXXXX.
    #   Row 2-3:   XXXXXXXXXX
    #   Row 4:     .XXXXXXXX.
    #   Row 5:       ..XXXX....
    rows = {
        0: range(3, 9),
        1: range(2, 10),
        2: range(1, 11),
        3: range(1, 11),
        4: range(2, 10),
        5: range(3, 9),
    }
    for y, xs in rows.items():
        for x in xs:
            px[x, y] = body
    # Highlight on top-right
    for x in range(5, 8):
        px[x, 1] = highlight
    px[6, 0] = highlight
    # Dark shadow on bottom-left
    for x in range(3, 6):
        px[x, 4] = dark
    # Nose tip (right side)
    px[10, 2] = (180, 40, 20, 255)
    px[10, 3] = (180, 40, 20, 255)
    px[11, 2] = (140, 30, 15, 200)
    px[11, 3] = (140, 30, 15, 200)
    # Tail fin (left side)
    px[1, 1] = (80, 80, 80, 255)
    px[1, 4] = (80, 80, 80, 255)
    px[0, 0] = (80, 80, 80, 200)
    px[0, 5] = (80, 80, 80, 200)
    save(img, WEAPONS_DIR, 'projectile_explosive.png')


def create_projectile_enemy():
    """Enemy bullet: 8x4, magenta-purple streak."""
    img = Image.new('RGBA', (8, 4), (0, 0, 0, 0))
    px = img.load()
    # Core — magenta
    for x in range(1, 7):
        px[x, 1] = (220, 50, 180, 255)
        px[x, 2] = (220, 50, 180, 255)
    # Bright tip
    px[6, 1] = (255, 100, 220, 255)
    px[6, 2] = (255, 100, 220, 255)
    px[7, 1] = (255, 120, 230, 180)
    px[7, 2] = (255, 120, 230, 180)
    # Trail
    px[0, 1] = (160, 30, 130, 140)
    px[0, 2] = (160, 30, 130, 140)
    # Edge glow
    for x in range(2, 6):
        px[x, 0] = (200, 40, 160, 80)
        px[x, 3] = (200, 40, 160, 80)
    save(img, WEAPONS_DIR, 'projectile_enemy.png')


# ---------------------------------------------------------------------------
# Loot Drops (16x16, white/neutral base — rarity color applied via modulate)
# ---------------------------------------------------------------------------

def draw_rect(px, x1, y1, x2, y2, color):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            px[x, y] = color


def create_loot_weapon():
    """Weapon icon: 16x16, pistol silhouette in white/light grey."""
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = img.load()
    white = (240, 240, 240, 255)
    grey = (200, 200, 200, 255)
    dark = (160, 160, 160, 255)
    # Barrel (horizontal, rows 5-7, cols 6-14)
    draw_rect(px, 6, 5, 14, 7, white)
    # Barrel tip
    px[15, 5] = grey
    px[15, 6] = grey
    px[15, 7] = grey
    # Body (rows 7-9, cols 4-10)
    draw_rect(px, 4, 7, 10, 9, white)
    # Trigger guard (rows 9-11, cols 6-8)
    px[6, 10] = grey
    px[8, 10] = grey
    px[6, 11] = grey
    px[7, 11] = grey
    px[8, 11] = grey
    # Grip (rows 9-13, cols 4-6)
    draw_rect(px, 4, 9, 6, 13, grey)
    draw_rect(px, 4, 9, 5, 13, dark)
    # Muzzle flash hint (small)
    px[14, 4] = (255, 255, 255, 120)
    px[14, 8] = (255, 255, 255, 120)
    save(img, UI_DIR, 'loot_weapon.png')


def create_loot_shield():
    """Shield icon: 16x16, shield shape in white/light grey."""
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = img.load()
    white = (240, 240, 240, 255)
    grey = (200, 200, 200, 255)
    bright = (255, 255, 255, 255)
    # Shield outline — pointed bottom
    # Top edge
    draw_rect(px, 3, 2, 12, 3, white)
    # Sides
    for y in range(4, 10):
        px[2, y] = white
        px[3, y] = grey
        px[12, y] = grey
        px[13, y] = white
    # Fill interior
    draw_rect(px, 4, 4, 11, 9, grey)
    # Taper to point
    draw_rect(px, 4, 10, 11, 10, grey)
    draw_rect(px, 5, 11, 10, 11, grey)
    draw_rect(px, 6, 12, 9, 12, grey)
    draw_rect(px, 7, 13, 8, 13, white)
    # Center cross/emblem
    draw_rect(px, 7, 4, 8, 9, bright)
    draw_rect(px, 5, 6, 10, 7, bright)
    save(img, UI_DIR, 'loot_shield.png')


def create_loot_health():
    """Health icon: 16x16, cross/heart in white."""
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = img.load()
    white = (240, 240, 240, 255)
    bright = (255, 255, 255, 255)
    # Plus/cross shape
    # Vertical bar
    draw_rect(px, 6, 2, 9, 13, white)
    # Horizontal bar
    draw_rect(px, 2, 6, 13, 9, white)
    # Bright center
    draw_rect(px, 6, 6, 9, 9, bright)
    save(img, UI_DIR, 'loot_health.png')


def create_loot_ammo():
    """Ammo icon: 16x16, bullet/cartridge shape in white."""
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = img.load()
    white = (240, 240, 240, 255)
    grey = (200, 200, 200, 255)
    dark = (170, 170, 170, 255)
    # Bullet tip (rounded, rows 2-4)
    draw_rect(px, 6, 2, 9, 2, grey)
    draw_rect(px, 5, 3, 10, 4, white)
    # Casing body (rows 5-12)
    draw_rect(px, 5, 5, 10, 12, grey)
    # Highlight stripe
    draw_rect(px, 7, 5, 8, 12, white)
    # Base rim (rows 13-14)
    draw_rect(px, 4, 13, 11, 14, dark)
    # Primer circle
    px[7, 13] = grey
    px[8, 13] = grey
    save(img, UI_DIR, 'loot_ammo.png')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ensure_dirs()

    print("=== Generating Projectile Sprites ===")
    create_projectile_bullet()
    create_projectile_fire()
    create_projectile_ice()
    create_projectile_electric()
    create_projectile_explosive()
    create_projectile_enemy()

    print("\n=== Generating Loot Drop Sprites ===")
    create_loot_weapon()
    create_loot_shield()
    create_loot_health()
    create_loot_ammo()

    print("\nDone! 10 sprites generated.")


if __name__ == '__main__':
    main()
