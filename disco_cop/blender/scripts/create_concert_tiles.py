#!/usr/bin/env python3
"""Generate Led Zeppelin Concert tileset for Disco Cop Level 03.

Creates tileset_concert.png with 6 tiles in a horizontal strip (192x32):
  1. Stage floor (dark wood planks, grain texture)
  2. Stage floor variant (lighter wood + gaffer tape mark)
  3. Backstage concrete (gray, cracks, scuff marks)
  4. Amp wall (black, speaker grille pattern, gold logo, chrome)
  5. Crowd area (very dark, silhouette hints, phone screen dots)
  6. Stage edge (wood top + metal lip + amber LED strip + dark void below)

Usage:
    python create_concert_tiles.py
"""

import random
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "environment"

TILE = 32
random.seed(404)

# Concert palette
STAGE_DARK = (60, 40, 25)
STAGE_MID = (80, 55, 35)
STAGE_LIGHT = (95, 65, 42)
STAGE_GRAIN = (70, 48, 30)
STAGE_GAP = (35, 22, 12)
STAGE_LIGHT_WOOD = (110, 78, 50)
GAFFER_TAPE = (170, 170, 175)
GAFFER_TAPE_DARK = (140, 140, 145)
CONCRETE_BASE = (100, 100, 98)
CONCRETE_LIGHT = (120, 120, 118)
CONCRETE_DARK = (75, 75, 73)
CONCRETE_CRACK = (55, 55, 53)
AMP_BLACK = (25, 25, 28)
AMP_DARK = (35, 35, 38)
AMP_GRILLE = (50, 50, 55)
AMP_GRILLE_LIGHT = (65, 65, 70)
AMP_GOLD = (200, 170, 50)
AMP_CHROME = (180, 185, 195)
CROWD_DARK = (12, 10, 15)
CROWD_SILHOUETTE = (25, 20, 30)
CROWD_HEAD = (30, 25, 35)
PHONE_GLOW = (180, 200, 255)
PHONE_GLOW2 = (200, 180, 255)
METAL_LIP = (140, 145, 155)
METAL_LIP_LIGHT = (180, 185, 195)
LED_AMBER = (255, 180, 40)
LED_AMBER_DIM = (180, 120, 20)
VOID_BLACK = (8, 5, 10)


def draw_stage_floor(img, x_off, variant=False):
    """Dark wood plank stage floor."""
    d = ImageDraw.Draw(img)
    base = STAGE_LIGHT_WOOD if variant else STAGE_DARK
    mid = STAGE_MID if not variant else (100, 70, 45)

    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=base)

    # Plank gaps (horizontal)
    for y in [7, 15, 23, 31]:
        d.line([x_off, y, x_off + TILE - 1, y], fill=STAGE_GAP)

    # Wood grain
    for y in range(TILE):
        if random.random() < 0.25:
            length = random.randint(6, 22)
            sx = x_off + random.randint(0, TILE - length)
            d.line([sx, y, sx + length, y], fill=STAGE_GRAIN)

    # Plank highlights
    for y_start in [0, 8, 16, 24]:
        for x in range(x_off, x_off + TILE):
            if random.random() < 0.15:
                img.putpixel((x, y_start + 1), (*mid, 255))

    # Variant: gaffer tape mark
    if variant:
        tape_y = random.randint(10, 20)
        d.rectangle([x_off + 4, tape_y, x_off + TILE - 4, tape_y + 2], fill=GAFFER_TAPE)
        d.rectangle([x_off + 5, tape_y, x_off + TILE - 5, tape_y + 1], fill=GAFFER_TAPE_DARK)

    # Scuff marks
    for _ in range(2):
        sx = x_off + random.randint(2, TILE - 4)
        sy = random.randint(2, TILE - 4)
        d.point([sx, sy], fill=STAGE_LIGHT)


def draw_backstage_concrete(img, x_off):
    """Gray backstage concrete with cracks and scuffs."""
    d = ImageDraw.Draw(img)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=CONCRETE_BASE)

    # Subtle texture
    for _ in range(35):
        x = x_off + random.randint(0, TILE - 1)
        y = random.randint(0, TILE - 1)
        c = random.choice([CONCRETE_LIGHT, CONCRETE_DARK, CONCRETE_BASE])
        img.putpixel((x, y), (*c, 255))

    # Expansion joint
    d.line([x_off + 16, 0, x_off + 16, TILE - 1], fill=CONCRETE_CRACK)

    # Random cracks
    for _ in range(2):
        cx = x_off + random.randint(4, 28)
        cy = random.randint(4, 28)
        crack_len = random.randint(4, 8)
        for i in range(crack_len):
            dx = random.randint(-1, 1)
            px = min(max(cx + dx, x_off), x_off + TILE - 1)
            py = min(cy + i, TILE - 1)
            d.point([px, py], fill=CONCRETE_CRACK)

    # Scuff marks (dark streaks)
    for _ in range(3):
        sx = x_off + random.randint(2, TILE - 6)
        sy = random.randint(2, TILE - 2)
        d.line([sx, sy, sx + random.randint(2, 5), sy], fill=CONCRETE_DARK)


def draw_amp_wall(img, x_off):
    """Amp wall: black cabinet, speaker grille, gold logo, chrome."""
    d = ImageDraw.Draw(img)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=AMP_BLACK)

    # Cabinet border
    d.rectangle([x_off + 1, 1, x_off + TILE - 2, TILE - 2], outline=AMP_DARK)

    # Gold logo strip at top
    d.rectangle([x_off + 4, 2, x_off + TILE - 4, 5], fill=AMP_DARK)
    for lx in range(x_off + 6, x_off + TILE - 6, 2):
        d.point([lx, 3], fill=AMP_GOLD)
        d.point([lx, 4], fill=AMP_GOLD)

    # Speaker grille (dot pattern)
    for gy in range(8, TILE - 4, 2):
        for gx in range(x_off + 3, x_off + TILE - 3, 2):
            c = AMP_GRILLE if (gx + gy) % 4 == 0 else AMP_GRILLE_LIGHT
            d.point([gx, gy], fill=c)

    # Speaker cone hints (2 circles)
    for cy in [14, 24]:
        cx = x_off + TILE // 2
        r = 5
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=AMP_GRILLE_LIGHT)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=AMP_BLACK)

    # Chrome corner protectors
    for corner_x, corner_y in [(x_off + 1, 1), (x_off + TILE - 3, 1),
                                (x_off + 1, TILE - 3), (x_off + TILE - 3, TILE - 3)]:
        d.rectangle([corner_x, corner_y, corner_x + 1, corner_y + 1], fill=AMP_CHROME)


def draw_crowd_area(img, x_off):
    """Very dark crowd area with silhouette hints and phone screen dots."""
    d = ImageDraw.Draw(img)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=CROWD_DARK)

    # Head silhouettes (rounded bumps along top)
    for hx in range(x_off + 3, x_off + TILE - 3, 6):
        hy = random.randint(2, 8)
        d.ellipse([hx - 2, hy, hx + 2, hy + 4], fill=CROWD_SILHOUETTE)
        # Shoulder hints
        d.rectangle([hx - 3, hy + 4, hx + 3, hy + 8], fill=CROWD_HEAD)

    # Raised arm silhouettes
    for _ in range(2):
        ax = x_off + random.randint(4, TILE - 4)
        ay = random.randint(0, 6)
        d.line([ax, ay + 6, ax, ay], fill=CROWD_SILHOUETTE, width=1)

    # Phone screen glow dots (small bright rectangles)
    for _ in range(3):
        px = x_off + random.randint(2, TILE - 4)
        py = random.randint(4, 16)
        glow = random.choice([PHONE_GLOW, PHONE_GLOW2])
        d.rectangle([px, py, px + 1, py + 2], fill=glow)

    # Dark gradient toward bottom
    for y in range(TILE // 2, TILE):
        for x in range(x_off, x_off + TILE):
            r0, g0, b0, a0 = img.getpixel((x, y))
            if a0 > 0:
                darken = (y - TILE // 2) / (TILE // 2) * 0.5
                nr = max(int(r0 * (1 - darken)), 0)
                ng = max(int(g0 * (1 - darken)), 0)
                nb = max(int(b0 * (1 - darken)), 0)
                img.putpixel((x, y), (nr, ng, nb, 255))


def draw_stage_edge(img, x_off):
    """Stage edge: wood top + metal lip + amber LED strip + dark void below."""
    d = ImageDraw.Draw(img)

    # Top half: stage wood floor
    d.rectangle([x_off, 0, x_off + TILE - 1, 13], fill=STAGE_DARK)
    # Plank gaps
    for y in [6]:
        d.line([x_off, y, x_off + TILE - 1, y], fill=STAGE_GAP)
    # Wood grain
    for y in range(14):
        if random.random() < 0.2:
            length = random.randint(5, 16)
            sx = x_off + random.randint(0, TILE - length)
            d.line([sx, y, sx + length, y], fill=STAGE_GRAIN)

    # Metal lip (2px strip)
    d.rectangle([x_off, 14, x_off + TILE - 1, 15], fill=METAL_LIP)
    # Metal highlight
    for x in range(x_off, x_off + TILE):
        if random.random() < 0.3:
            img.putpixel((x, 14), (*METAL_LIP_LIGHT, 255))

    # Amber LED strip (3px tall)
    for x in range(x_off, x_off + TILE):
        if (x - x_off) % 4 < 2:
            d.point([x, 16], fill=LED_AMBER)
            d.point([x, 17], fill=LED_AMBER)
            d.point([x, 18], fill=LED_AMBER_DIM)
        else:
            d.point([x, 16], fill=LED_AMBER_DIM)
            d.point([x, 17], fill=AMP_BLACK)
            d.point([x, 18], fill=AMP_BLACK)

    # Dark void below
    d.rectangle([x_off, 19, x_off + TILE - 1, TILE - 1], fill=VOID_BLACK)
    # Subtle structure hint in void
    for y in range(20, TILE):
        if random.random() < 0.1:
            x = x_off + random.randint(0, TILE - 1)
            d.point([x, y], fill=(15, 12, 18))


def main():
    num_tiles = 6
    width = num_tiles * TILE
    img = Image.new("RGBA", (width, TILE), (0, 0, 0, 0))

    draw_stage_floor(img, 0 * TILE, variant=False)
    draw_stage_floor(img, 1 * TILE, variant=True)
    draw_backstage_concrete(img, 2 * TILE)
    draw_amp_wall(img, 3 * TILE)
    draw_crowd_area(img, 4 * TILE)
    draw_stage_edge(img, 5 * TILE)

    out = OUTPUT_DIR / "tileset_concert.png"
    img.save(out)
    print(f"  [OK] {out.name} ({width}x{TILE}, {num_tiles} tiles)")


if __name__ == "__main__":
    print("Generating Led Zeppelin Concert tileset...")
    main()
    print("Done!")
