#!/usr/bin/env python3
"""Generate CBGB Punk Alley tileset for Disco Cop Level 04.

Creates tileset_punk_alley.png with 6 tiles in a horizontal strip (192x32):
  1. Dirty brick wall (red-brown brick pattern, mortar lines, grime)
  2. Cracked asphalt (dark gray, cracks, oil stains, pebble texture)
  3. Graffiti wall (brick base with colorful paint splotches/tags)
  4. Dumpster/trash (dark green dumpster metal, rust, trash lid, garbage)
  5. Puddle (dark asphalt with reflective water puddle, ripple dots)
  6. Alley edge (top half: brick wall base, bottom half: cracked sidewalk)

Usage:
    python create_punk_tiles.py
"""

import random
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "environment"

TILE = 32
random.seed(809)

# Punk alley palette
BRICK_BASE = (120, 55, 40)
BRICK_DARK = (90, 40, 28)
BRICK_LIGHT = (140, 68, 50)
BRICK_HIGHLIGHT = (155, 80, 60)
MORTAR = (75, 72, 65)
MORTAR_DARK = (60, 58, 52)
GRIME_DARK = (50, 42, 35)
GRIME_STAIN = (65, 55, 45)
ASPHALT_BASE = (55, 55, 52)
ASPHALT_DARK = (40, 40, 38)
ASPHALT_LIGHT = (70, 70, 66)
ASPHALT_CRACK = (30, 28, 26)
OIL_STAIN = (35, 30, 40)
OIL_SHEEN = (50, 45, 60)
PEBBLE = (80, 78, 72)
GRAFFITI_PINK = (210, 80, 130)
GRAFFITI_GREEN = (60, 200, 90)
GRAFFITI_YELLOW = (240, 220, 50)
GRAFFITI_BLUE = (70, 120, 220)
DUMPSTER_BASE = (40, 75, 45)
DUMPSTER_DARK = (28, 55, 32)
DUMPSTER_LIGHT = (55, 95, 60)
RUST_DARK = (110, 55, 25)
RUST_LIGHT = (140, 70, 30)
LID_METAL = (65, 65, 60)
LID_HIGHLIGHT = (90, 90, 85)
TRASH_BROWN = (95, 70, 40)
TRASH_WHITE = (180, 175, 165)
PUDDLE_WATER = (50, 65, 80)
PUDDLE_LIGHT = (70, 90, 110)
PUDDLE_RIPPLE = (85, 105, 130)
PUDDLE_REFLECT = (100, 120, 150)
SIDEWALK_BASE = (130, 125, 118)
SIDEWALK_LIGHT = (150, 145, 138)
SIDEWALK_DARK = (105, 100, 95)
SIDEWALK_CRACK = (80, 76, 70)
TRANSITION_LINE = (90, 85, 78)


def draw_dirty_brick_wall(img, x_off):
    """Red-brown brick pattern with mortar lines and grime."""
    d = ImageDraw.Draw(img)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=BRICK_BASE)

    # Mortar grid (horizontal lines every 4px, staggered verticals)
    for y in range(0, TILE, 4):
        d.line([x_off, y, x_off + TILE - 1, y], fill=MORTAR)

    # Vertical mortar (staggered per row)
    for row in range(8):
        y_top = row * 4 + 1
        offset = 8 if row % 2 == 0 else 0
        for vx in range(offset, TILE, 16):
            mx = x_off + vx
            if mx < x_off + TILE:
                d.line([mx, y_top, mx, min(y_top + 3, TILE - 1)], fill=MORTAR)

    # Brick color variation
    for row in range(8):
        y_top = row * 4 + 1
        offset = 8 if row % 2 == 0 else 0
        for vx in range(offset, TILE, 16):
            bx = x_off + vx + 1
            by = y_top
            bw = min(14, x_off + TILE - bx - 1)
            bh = 3
            if bw > 2 and by + bh <= TILE:
                brick_c = random.choice([BRICK_BASE, BRICK_DARK, BRICK_LIGHT])
                d.rectangle([bx, by, bx + bw - 1, by + bh - 1], fill=brick_c)
                # Occasional highlight
                if random.random() < 0.3:
                    hx = bx + random.randint(0, max(0, bw - 2))
                    img.putpixel((hx, by), (*BRICK_HIGHLIGHT, 255))

    # Grime (dark stains, concentrated at bottom)
    for _ in range(20):
        gx = x_off + random.randint(0, TILE - 1)
        gy = random.randint(TILE // 2, TILE - 1) if random.random() < 0.7 else random.randint(0, TILE - 1)
        c = random.choice([GRIME_DARK, GRIME_STAIN])
        img.putpixel((gx, gy), (*c, 255))

    # Dark mortar variation
    for _ in range(8):
        mx = x_off + random.randint(0, TILE - 1)
        my = random.randint(0, TILE - 1)
        if img.getpixel((mx, my))[:3] == MORTAR[:3]:
            img.putpixel((mx, my), (*MORTAR_DARK, 255))


def draw_cracked_asphalt(img, x_off):
    """Dark gray asphalt with cracks, oil stains, and pebble texture."""
    d = ImageDraw.Draw(img)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=ASPHALT_BASE)

    # Pebble texture
    for _ in range(40):
        px = x_off + random.randint(0, TILE - 1)
        py = random.randint(0, TILE - 1)
        c = random.choice([ASPHALT_LIGHT, ASPHALT_DARK, PEBBLE])
        img.putpixel((px, py), (*c, 255))

    # Main crack (jagged diagonal)
    cx, cy = random.randint(4, 12), 0
    for _ in range(TILE):
        cx += random.randint(-1, 1)
        cy += 1
        px = min(max(x_off + cx, x_off), x_off + TILE - 1)
        py = min(cy, TILE - 1)
        d.point([px, py], fill=ASPHALT_CRACK)
        if random.random() < 0.4:
            d.point([min(px + 1, x_off + TILE - 1), py], fill=ASPHALT_CRACK)
        if cy >= TILE - 1:
            break

    # Secondary crack (shorter)
    cx2, cy2 = random.randint(18, 28), random.randint(8, 16)
    for _ in range(random.randint(8, 14)):
        cx2 += random.randint(-1, 1)
        cy2 += random.choice([0, 1, 1])
        px = min(max(x_off + cx2, x_off), x_off + TILE - 1)
        py = min(cy2, TILE - 1)
        d.point([px, py], fill=ASPHALT_CRACK)

    # Oil stains (dark blotches with slight sheen)
    for _ in range(2):
        ox = x_off + random.randint(4, TILE - 6)
        oy = random.randint(4, TILE - 6)
        r = random.randint(2, 4)
        d.ellipse([ox - r, oy - r, ox + r, oy + r], fill=OIL_STAIN)
        # Sheen dot
        d.point([ox + 1, oy - 1], fill=OIL_SHEEN)


def draw_graffiti_wall(img, x_off):
    """Brick wall base with colorful paint splotches and tags."""
    d = ImageDraw.Draw(img)

    # Start with brick base (same as dirty brick but cleaner)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=BRICK_BASE)

    # Mortar grid
    for y in range(0, TILE, 4):
        d.line([x_off, y, x_off + TILE - 1, y], fill=MORTAR)
    for row in range(8):
        y_top = row * 4 + 1
        offset = 8 if row % 2 == 0 else 0
        for vx in range(offset, TILE, 16):
            mx = x_off + vx
            if mx < x_off + TILE:
                d.line([mx, y_top, mx, min(y_top + 3, TILE - 1)], fill=MORTAR)

    # Brick variation
    for _ in range(15):
        bx = x_off + random.randint(0, TILE - 1)
        by = random.randint(0, TILE - 1)
        c = random.choice([BRICK_DARK, BRICK_LIGHT])
        img.putpixel((bx, by), (*c, 255))

    # Graffiti paint splotches
    colors = [GRAFFITI_PINK, GRAFFITI_GREEN, GRAFFITI_YELLOW, GRAFFITI_BLUE]

    # Large splash 1
    sx, sy = random.randint(4, 14), random.randint(4, 14)
    splash_c = random.choice(colors)
    r = random.randint(4, 6)
    d.ellipse([x_off + sx - r, sy - r, x_off + sx + r, sy + r], fill=splash_c)

    # Large splash 2
    sx2, sy2 = random.randint(16, 28), random.randint(14, 26)
    splash_c2 = random.choice(colors)
    r2 = random.randint(3, 5)
    d.ellipse([x_off + sx2 - r2, sy2 - r2, x_off + sx2 + r2, sy2 + r2], fill=splash_c2)

    # Small splatter dots around splotches
    for _ in range(12):
        dx = x_off + random.randint(0, TILE - 1)
        dy = random.randint(0, TILE - 1)
        sc = random.choice(colors)
        img.putpixel((dx, dy), (*sc, 255))

    # Tag line (crude horizontal streak)
    tag_y = random.randint(10, 22)
    tag_c = random.choice(colors)
    tag_start = x_off + random.randint(2, 8)
    tag_end = x_off + random.randint(20, TILE - 3)
    d.line([tag_start, tag_y, tag_end, tag_y], fill=tag_c, width=1)
    # Tag drip
    drip_x = tag_end - random.randint(1, 4)
    d.line([drip_x, tag_y, drip_x, tag_y + random.randint(2, 5)], fill=tag_c)


def draw_dumpster_trash(img, x_off):
    """Dark green dumpster metal with rust, lid edge, and garbage hints."""
    d = ImageDraw.Draw(img)

    # Dumpster body
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=DUMPSTER_BASE)

    # Lid at top (metal edge)
    d.rectangle([x_off, 0, x_off + TILE - 1, 4], fill=LID_METAL)
    d.line([x_off, 5, x_off + TILE - 1, 5], fill=DUMPSTER_DARK)
    # Lid highlight
    for x in range(x_off + 2, x_off + TILE - 2):
        if random.random() < 0.4:
            img.putpixel((x, 1), (*LID_HIGHLIGHT, 255))

    # Lid handle
    d.rectangle([x_off + 13, 2, x_off + 18, 3], fill=LID_HIGHLIGHT)

    # Dumpster panel lines (vertical ribs)
    d.line([x_off + 10, 6, x_off + 10, TILE - 3], fill=DUMPSTER_DARK)
    d.line([x_off + 21, 6, x_off + 21, TILE - 3], fill=DUMPSTER_DARK)

    # Color variation on panels
    for _ in range(25):
        vx = x_off + random.randint(1, TILE - 2)
        vy = random.randint(6, TILE - 3)
        c = random.choice([DUMPSTER_DARK, DUMPSTER_LIGHT, DUMPSTER_BASE])
        img.putpixel((vx, vy), (*c, 255))

    # Rust spots
    for _ in range(5):
        rx = x_off + random.randint(2, TILE - 4)
        ry = random.randint(8, TILE - 4)
        rr = random.randint(1, 2)
        d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=RUST_DARK)
        d.point([rx, ry], fill=RUST_LIGHT)

    # Garbage hints peeking over lid
    for _ in range(3):
        gx = x_off + random.randint(3, TILE - 4)
        gc = random.choice([TRASH_BROWN, TRASH_WHITE])
        d.rectangle([gx, 0, gx + 1, 1], fill=gc)

    # Bottom edge shadow
    d.line([x_off, TILE - 2, x_off + TILE - 1, TILE - 2], fill=DUMPSTER_DARK)
    d.line([x_off, TILE - 1, x_off + TILE - 1, TILE - 1], fill=GRIME_DARK)


def draw_puddle(img, x_off):
    """Dark asphalt with reflective water puddle, blue-green tint, ripple dots."""
    d = ImageDraw.Draw(img)

    # Asphalt base
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=ASPHALT_BASE)

    # Asphalt texture
    for _ in range(25):
        px = x_off + random.randint(0, TILE - 1)
        py = random.randint(0, TILE - 1)
        c = random.choice([ASPHALT_LIGHT, ASPHALT_DARK])
        img.putpixel((px, py), (*c, 255))

    # Cracks in surrounding asphalt
    for _ in range(2):
        cx = x_off + random.randint(2, TILE - 3)
        cy = random.randint(2, TILE - 3)
        for i in range(random.randint(3, 6)):
            px = min(max(cx + random.randint(-1, 1), x_off), x_off + TILE - 1)
            cy2 = min(cy + i, TILE - 1)
            d.point([px, cy2], fill=ASPHALT_CRACK)

    # Water puddle (irregular ellipse, center-ish)
    puddle_cx = TILE // 2
    puddle_cy = TILE // 2
    puddle_rx = random.randint(9, 12)
    puddle_ry = random.randint(7, 10)
    d.ellipse([x_off + puddle_cx - puddle_rx, puddle_cy - puddle_ry,
               x_off + puddle_cx + puddle_rx, puddle_cy + puddle_ry],
              fill=PUDDLE_WATER)

    # Puddle depth variation (lighter center)
    inner_rx = puddle_rx - 3
    inner_ry = puddle_ry - 3
    if inner_rx > 2 and inner_ry > 2:
        d.ellipse([x_off + puddle_cx - inner_rx, puddle_cy - inner_ry,
                   x_off + puddle_cx + inner_rx, puddle_cy + inner_ry],
                  fill=PUDDLE_LIGHT)

    # Reflection highlights
    for _ in range(4):
        rx = x_off + puddle_cx + random.randint(-inner_rx, inner_rx)
        ry = puddle_cy + random.randint(-inner_ry, inner_ry)
        rx = min(max(rx, x_off), x_off + TILE - 1)
        ry = min(max(ry, 0), TILE - 1)
        img.putpixel((rx, ry), (*PUDDLE_REFLECT, 255))

    # Ripple dots (concentric hints)
    for _ in range(6):
        rip_x = x_off + puddle_cx + random.randint(-puddle_rx + 2, puddle_rx - 2)
        rip_y = puddle_cy + random.randint(-puddle_ry + 2, puddle_ry - 2)
        rip_x = min(max(rip_x, x_off), x_off + TILE - 1)
        rip_y = min(max(rip_y, 0), TILE - 1)
        d.point([rip_x, rip_y], fill=PUDDLE_RIPPLE)


def draw_alley_edge(img, x_off):
    """Top half: brick wall base, bottom half: cracked sidewalk, transition line."""
    d = ImageDraw.Draw(img)

    # Top half: brick wall
    d.rectangle([x_off, 0, x_off + TILE - 1, 14], fill=BRICK_BASE)

    # Brick mortar (top half only)
    for y in range(0, 16, 4):
        if y < 15:
            d.line([x_off, y, x_off + TILE - 1, y], fill=MORTAR)
    for row in range(4):
        y_top = row * 4 + 1
        offset = 8 if row % 2 == 0 else 0
        for vx in range(offset, TILE, 16):
            mx = x_off + vx
            if mx < x_off + TILE:
                d.line([mx, y_top, mx, min(y_top + 3, 14)], fill=MORTAR)

    # Brick variation (top half)
    for _ in range(10):
        bx = x_off + random.randint(0, TILE - 1)
        by = random.randint(0, 14)
        c = random.choice([BRICK_DARK, BRICK_LIGHT, BRICK_HIGHLIGHT])
        img.putpixel((bx, by), (*c, 255))

    # Grime on lower bricks
    for _ in range(6):
        gx = x_off + random.randint(0, TILE - 1)
        gy = random.randint(10, 14)
        img.putpixel((gx, gy), (*GRIME_STAIN, 255))

    # Transition line (wall base meets sidewalk)
    d.line([x_off, 15, x_off + TILE - 1, 15], fill=TRANSITION_LINE)
    d.line([x_off, 16, x_off + TILE - 1, 16], fill=MORTAR_DARK)

    # Bottom half: cracked sidewalk concrete
    d.rectangle([x_off, 17, x_off + TILE - 1, TILE - 1], fill=SIDEWALK_BASE)

    # Sidewalk texture
    for _ in range(20):
        sx = x_off + random.randint(0, TILE - 1)
        sy = random.randint(17, TILE - 1)
        c = random.choice([SIDEWALK_LIGHT, SIDEWALK_DARK])
        img.putpixel((sx, sy), (*c, 255))

    # Sidewalk expansion joint
    d.line([x_off + 16, 17, x_off + 16, TILE - 1], fill=SIDEWALK_CRACK)

    # Cracks in sidewalk
    for _ in range(2):
        cx = x_off + random.randint(4, 28)
        cy = random.randint(19, 28)
        for i in range(random.randint(3, 6)):
            dx = random.randint(-1, 1)
            px = min(max(cx + dx, x_off), x_off + TILE - 1)
            py = min(cy + i, TILE - 1)
            d.point([px, py], fill=SIDEWALK_CRACK)

    # Grime at base of wall (near transition)
    for _ in range(5):
        gx = x_off + random.randint(0, TILE - 1)
        img.putpixel((gx, 17), (*GRIME_STAIN, 255))


def main():
    num_tiles = 6
    width = num_tiles * TILE
    img = Image.new("RGBA", (width, TILE), (0, 0, 0, 0))

    draw_dirty_brick_wall(img, 0 * TILE)
    draw_cracked_asphalt(img, 1 * TILE)
    draw_graffiti_wall(img, 2 * TILE)
    draw_dumpster_trash(img, 3 * TILE)
    draw_puddle(img, 4 * TILE)
    draw_alley_edge(img, 5 * TILE)

    out = OUTPUT_DIR / "tileset_punk_alley.png"
    img.save(out)
    print(f"  [OK] {out.name} ({width}x{TILE}, {num_tiles} tiles)")


if __name__ == "__main__":
    print("Generating CBGB Punk Alley tileset...")
    main()
    print("Done!")
