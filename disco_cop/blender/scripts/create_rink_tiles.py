#!/usr/bin/env python3
"""Generate rink-specific tileset for Disco Cop Level 01: Roller Rink Rumble.

Creates tileset_rink.png with 6 tiles in a horizontal strip (192x32):
  1. Rink floor (warm wood)
  2. Rink floor variant (lighter wood with lane line)
  3. Lobby carpet (deep purple patterned)
  4. Chrome barrier (silver rail)
  5. Rink wall (dark purple background)
  6. Rink edge (transition floor-to-wall)

Usage:
    python create_rink_tiles.py

Output: disco_cop/assets/sprites/environment/tileset_rink.png
"""

import random
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "environment"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TILE = 32
random.seed(42)  # Reproducible output

# ── Rink Palette (from skating_rink_level_plan.md) ────────────────────
WOOD_BASE = (140, 90, 51)       # #8C5A33
WOOD_LIGHT = (212, 167, 106)    # #D4A76A
WOOD_DARK = (100, 65, 35)
WOOD_GRAIN = (120, 78, 43)
CARPET_BASE = (74, 14, 78)      # #4A0E4E
CARPET_LIGHT = (95, 25, 100)
CARPET_DARK = (55, 8, 60)
CHROME = (192, 192, 192)        # #C0C0C0
CHROME_LIGHT = (230, 230, 240)
CHROME_DARK = (120, 120, 130)
CHROME_SHINE = (255, 255, 255)
NEON_PINK = (255, 105, 180)     # #FF69B4
WALL_DARK = (26, 10, 46)        # #1A0A2E
WALL_MID = (40, 18, 65)
LANE_LINE = (180, 140, 80)


def draw_wood_tile(img: Image.Image, x_off: int, variant: int = 0):
    """Draw a polished wood rink floor tile."""
    d = ImageDraw.Draw(img)
    base = WOOD_BASE if variant == 0 else WOOD_LIGHT

    # Fill with base
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=base)

    # Wood grain lines (horizontal, subtle variation)
    for y in range(TILE):
        if random.random() < 0.25:
            grain = WOOD_GRAIN if variant == 0 else WOOD_BASE
            length = random.randint(8, 28)
            sx = x_off + random.randint(0, TILE - length)
            d.line([sx, y, sx + length, y], fill=grain)

    # Polished sheen (lighter horizontal band in middle)
    for y in range(12, 18):
        for x in range(x_off, x_off + TILE):
            r, g, b = img.getpixel((x, y))[:3]
            img.putpixel((x, y), (min(r + 15, 255), min(g + 12, 255), min(b + 8, 255), 255))

    # Lane line for variant 1
    if variant == 1:
        d.line([x_off, 15, x_off + TILE - 1, 15], fill=LANE_LINE)
        d.line([x_off, 16, x_off + TILE - 1, 16], fill=LANE_LINE)

    # Subtle edge darkening (top/bottom 2px)
    for y in [0, 1, TILE - 2, TILE - 1]:
        for x in range(x_off, x_off + TILE):
            r, g, b = img.getpixel((x, y))[:3]
            img.putpixel((x, y), (max(r - 20, 0), max(g - 15, 0), max(b - 10, 0), 255))


def draw_carpet_tile(img: Image.Image, x_off: int):
    """Draw a deep purple lobby carpet tile with diamond pattern."""
    d = ImageDraw.Draw(img)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=CARPET_BASE)

    # Diamond/argyle pattern
    for y in range(TILE):
        for x in range(TILE):
            # Create repeating diamond pattern
            dx = (x % 8) - 4
            dy = (y % 8) - 4
            if abs(dx) + abs(dy) <= 3:
                img.putpixel((x_off + x, y), (*CARPET_LIGHT, 255))
            elif abs(dx) + abs(dy) == 4:
                img.putpixel((x_off + x, y), (*CARPET_DARK, 255))

    # Worn spots (slightly lighter random patches)
    for _ in range(3):
        cx = x_off + random.randint(4, TILE - 5)
        cy = random.randint(4, TILE - 5)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if dx * dx + dy * dy <= 4:
                    px, py = cx + dx, cy + dy
                    if 0 <= py < TILE:
                        r, g, b = img.getpixel((px, py))[:3]
                        img.putpixel((px, py), (min(r + 8, 255), min(g + 5, 255), min(b + 8, 255), 255))


def draw_barrier_tile(img: Image.Image, x_off: int):
    """Draw a chrome rink barrier with neon glow accent."""
    d = ImageDraw.Draw(img)

    # Background (dark, mostly transparent behind barrier)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=(*WALL_DARK, 255))

    # Main barrier body (chrome horizontal rails)
    # Top rail
    d.rectangle([x_off, 4, x_off + TILE - 1, 8], fill=CHROME)
    d.line([x_off, 4, x_off + TILE - 1, 4], fill=CHROME_LIGHT)
    d.line([x_off, 5, x_off + TILE - 1, 5], fill=CHROME_SHINE)
    d.line([x_off, 8, x_off + TILE - 1, 8], fill=CHROME_DARK)

    # Bottom rail
    d.rectangle([x_off, 18, x_off + TILE - 1, 22], fill=CHROME)
    d.line([x_off, 18, x_off + TILE - 1, 18], fill=CHROME_LIGHT)
    d.line([x_off, 19, x_off + TILE - 1, 19], fill=CHROME_SHINE)
    d.line([x_off, 22, x_off + TILE - 1, 22], fill=CHROME_DARK)

    # Vertical support posts at edges
    for px in [x_off + 2, x_off + TILE - 3]:
        d.rectangle([px, 2, px + 1, 28], fill=CHROME)
        d.line([px, 2, px, 28], fill=CHROME_LIGHT)

    # Neon glow strip along bottom
    d.line([x_off, 26, x_off + TILE - 1, 26], fill=NEON_PINK)
    d.line([x_off, 27, x_off + TILE - 1, 27], fill=(200, 60, 120, 255))  # Dimmer glow
    # Glow halo (very faint)
    d.line([x_off, 25, x_off + TILE - 1, 25], fill=(120, 30, 70, 180))
    d.line([x_off, 28, x_off + TILE - 1, 28], fill=(100, 25, 60, 140))


def draw_wall_tile(img: Image.Image, x_off: int):
    """Draw a dark rink interior wall."""
    d = ImageDraw.Draw(img)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=WALL_DARK)

    # Subtle brick/panel pattern
    for y in range(0, TILE, 8):
        offset = 16 if (y // 8) % 2 else 0
        for x in range(0, TILE, 16):
            bx = x_off + (x + offset) % TILE
            d.rectangle([bx, y, bx + 14, y + 6], outline=WALL_MID)

    # Occasional neon accent pixel
    for _ in range(2):
        nx = x_off + random.randint(2, TILE - 3)
        ny = random.randint(2, TILE - 3)
        color = random.choice([NEON_PINK, (0, 255, 255), (255, 215, 0)])
        img.putpixel((nx, ny), (*color, 160))


def draw_edge_tile(img: Image.Image, x_off: int):
    """Draw a rink edge — wood floor on top, wall on bottom with trim."""
    d = ImageDraw.Draw(img)

    # Top half: wood floor
    d.rectangle([x_off, 0, x_off + TILE - 1, 15], fill=WOOD_BASE)
    for y in range(16):
        if random.random() < 0.2:
            length = random.randint(6, 20)
            sx = x_off + random.randint(0, TILE - length)
            d.line([sx, y, sx + length, y], fill=WOOD_GRAIN)

    # Trim line (chrome strip)
    d.line([x_off, 15, x_off + TILE - 1, 15], fill=CHROME_LIGHT)
    d.line([x_off, 16, x_off + TILE - 1, 16], fill=CHROME)
    d.line([x_off, 17, x_off + TILE - 1, 17], fill=CHROME_DARK)

    # Bottom half: dark wall
    d.rectangle([x_off, 18, x_off + TILE - 1, TILE - 1], fill=WALL_DARK)
    for y in range(18, TILE, 6):
        offset = 8 if ((y - 18) // 6) % 2 else 0
        for x in range(0, TILE, 16):
            bx = x_off + (x + offset) % TILE
            d.rectangle([bx, y, min(bx + 14, x_off + TILE - 1), min(y + 4, TILE - 1)], outline=WALL_MID)


def main():
    num_tiles = 6
    width = num_tiles * TILE  # 192
    img = Image.new("RGBA", (width, TILE), (0, 0, 0, 0))

    draw_wood_tile(img, 0 * TILE, variant=0)   # Rink floor base
    draw_wood_tile(img, 1 * TILE, variant=1)   # Rink floor + lane line
    draw_carpet_tile(img, 2 * TILE)            # Lobby carpet
    draw_barrier_tile(img, 3 * TILE)           # Chrome barrier
    draw_wall_tile(img, 4 * TILE)              # Rink wall
    draw_edge_tile(img, 5 * TILE)              # Floor-to-wall edge

    out = OUTPUT_DIR / "tileset_rink.png"
    img.save(out)
    print(f"  [OK] {out} ({width}x{TILE}, {num_tiles} tiles)")


if __name__ == "__main__":
    print("Generating rink tileset...")
    main()
    print("Done!")