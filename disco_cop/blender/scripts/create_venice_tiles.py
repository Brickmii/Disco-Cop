#!/usr/bin/env python3
"""Generate Venice Beach tileset for Disco Cop Level 02.

Creates tileset_venice.png with 6 tiles in a horizontal strip (192x32):
  1. Sand (light golden beach sand)
  2. Sand variant (darker wet sand near water)
  3. Boardwalk wood (sun-bleached planks)
  4. Concrete (Muscle Beach gym floor)
  5. Ocean water (blue-green surface)
  6. Boardwalk edge (wood top, sand bottom)

Usage:
    python create_venice_tiles.py
"""

import random
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "environment"

TILE = 32
random.seed(99)

# Venice Beach Palette
SAND_LIGHT = (235, 210, 165)
SAND_MID = (215, 190, 145)
SAND_DARK = (195, 170, 130)
SAND_WET = (170, 150, 115)
SAND_WET_DARK = (145, 130, 100)
BOARDWALK = (180, 155, 120)
BOARDWALK_LIGHT = (200, 175, 140)
BOARDWALK_DARK = (140, 120, 90)
BOARDWALK_GRAIN = (160, 135, 105)
CONCRETE = (170, 170, 165)
CONCRETE_LIGHT = (190, 190, 185)
CONCRETE_DARK = (140, 140, 135)
CONCRETE_CRACK = (110, 110, 105)
OCEAN_TOP = (30, 120, 160)
OCEAN_MID = (20, 95, 140)
OCEAN_DARK = (15, 75, 120)
OCEAN_FOAM = (200, 220, 235)
OCEAN_HIGHLIGHT = (80, 170, 210)


def draw_sand(img, x_off, wet=False):
    d = ImageDraw.Draw(img)
    base = SAND_WET if wet else SAND_LIGHT
    dark = SAND_WET_DARK if wet else SAND_DARK
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=base)
    # Sand grain texture
    for _ in range(40):
        x = x_off + random.randint(0, TILE - 1)
        y = random.randint(0, TILE - 1)
        c = random.choice([SAND_MID, dark, base])
        img.putpixel((x, y), (*c, 255))
    # Occasional shell/pebble
    if random.random() < 0.5:
        sx = x_off + random.randint(4, TILE - 5)
        sy = random.randint(4, TILE - 5)
        shell_c = random.choice([(240, 230, 220), (220, 200, 180), (200, 190, 170)])
        d.ellipse([sx, sy, sx + 2, sy + 1], fill=shell_c)


def draw_boardwalk(img, x_off):
    d = ImageDraw.Draw(img)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=BOARDWALK)
    # Plank lines (horizontal gaps)
    for y in [7, 15, 23, 31]:
        d.line([x_off, y, x_off + TILE - 1, y], fill=BOARDWALK_DARK)
    # Wood grain
    for y in range(TILE):
        if random.random() < 0.2:
            length = random.randint(8, 24)
            sx = x_off + random.randint(0, TILE - length)
            d.line([sx, y, sx + length, y], fill=BOARDWALK_GRAIN)
    # Highlight on top of each plank
    for y in [1, 9, 17, 25]:
        for x in range(x_off, x_off + TILE):
            if random.random() < 0.3:
                img.putpixel((x, y), (*BOARDWALK_LIGHT, 255))
    # Nail heads
    for ny in [4, 12, 20, 28]:
        for nx_off in [8, 24]:
            nx = x_off + nx_off
            d.point([nx, ny], fill=BOARDWALK_DARK)


def draw_concrete(img, x_off):
    d = ImageDraw.Draw(img)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=CONCRETE)
    # Subtle texture variation
    for _ in range(30):
        x = x_off + random.randint(0, TILE - 1)
        y = random.randint(0, TILE - 1)
        c = random.choice([CONCRETE_LIGHT, CONCRETE_DARK, CONCRETE])
        img.putpixel((x, y), (*c, 255))
    # Expansion joint / crack
    d.line([x_off + 16, 0, x_off + 16, TILE - 1], fill=CONCRETE_CRACK)
    # Optional crack
    if random.random() < 0.4:
        cx = x_off + random.randint(4, 28)
        cy = random.randint(4, 28)
        for i in range(5):
            d.point([cx + random.randint(-1, 1), cy + i], fill=CONCRETE_CRACK)


def draw_ocean(img, x_off):
    d = ImageDraw.Draw(img)
    # Gradient top to bottom (lighter at surface)
    for y in range(TILE):
        t = y / TILE
        r = int(OCEAN_TOP[0] * (1 - t) + OCEAN_DARK[0] * t)
        g = int(OCEAN_TOP[1] * (1 - t) + OCEAN_DARK[1] * t)
        b = int(OCEAN_TOP[2] * (1 - t) + OCEAN_DARK[2] * t)
        d.line([x_off, y, x_off + TILE - 1, y], fill=(r, g, b, 255))
    # Wave highlights
    for wy in [6, 14, 22]:
        wave_x = x_off + random.randint(0, 8)
        d.line([wave_x, wy, wave_x + random.randint(10, 20), wy], fill=OCEAN_HIGHLIGHT)
    # Foam at top
    for x in range(x_off, x_off + TILE):
        if random.random() < 0.3:
            img.putpixel((x, 0), (*OCEAN_FOAM, 255))
        if random.random() < 0.15:
            img.putpixel((x, 1), (*OCEAN_FOAM, 200))


def draw_boardwalk_edge(img, x_off):
    d = ImageDraw.Draw(img)
    # Top half: boardwalk
    d.rectangle([x_off, 0, x_off + TILE - 1, 15], fill=BOARDWALK)
    for y in [7]:
        d.line([x_off, y, x_off + TILE - 1, y], fill=BOARDWALK_DARK)
    for y in range(16):
        if random.random() < 0.15:
            length = random.randint(6, 18)
            sx = x_off + random.randint(0, TILE - length)
            d.line([sx, y, sx + length, y], fill=BOARDWALK_GRAIN)
    # Edge shadow
    d.line([x_off, 15, x_off + TILE - 1, 15], fill=BOARDWALK_DARK)
    d.line([x_off, 16, x_off + TILE - 1, 16], fill=(120, 100, 75, 255))
    # Bottom half: sand
    d.rectangle([x_off, 17, x_off + TILE - 1, TILE - 1], fill=SAND_LIGHT)
    for _ in range(15):
        x = x_off + random.randint(0, TILE - 1)
        y = random.randint(17, TILE - 1)
        c = random.choice([SAND_MID, SAND_DARK])
        img.putpixel((x, y), (*c, 255))


def main():
    num_tiles = 6
    width = num_tiles * TILE
    img = Image.new("RGBA", (width, TILE), (0, 0, 0, 0))

    draw_sand(img, 0 * TILE, wet=False)
    draw_sand(img, 1 * TILE, wet=True)
    draw_boardwalk(img, 2 * TILE)
    draw_concrete(img, 3 * TILE)
    draw_ocean(img, 4 * TILE)
    draw_boardwalk_edge(img, 5 * TILE)

    out = OUTPUT_DIR / "tileset_venice.png"
    img.save(out)
    print(f"  [OK] {out.name} ({width}x{TILE}, {num_tiles} tiles)")


if __name__ == "__main__":
    print("Generating Venice Beach tileset...")
    main()
    print("Done!")
