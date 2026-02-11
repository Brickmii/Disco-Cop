#!/usr/bin/env python3
"""Generate Bee Gees Disco Floor tileset for Disco Cop Level 05.

Creates tileset_disco_floor.png with 6 tiles in a horizontal strip (192x32):
  1. Disco floor tile (purple/magenta glow) — illuminated dance floor square
  2. Disco floor tile variant (blue/cyan) — same pattern, different color
  3. VIP lounge floor — dark burgundy carpet with gold trim
  4. Speaker stack base — black cabinet with speaker cones and chrome trim
  5. Bar counter — dark wood top, brass rail, bottle silhouettes
  6. Dance floor edge — illuminated tile top, chrome strip, shadow below

Usage:
    python create_disco_floor_tiles.py
"""

import random
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "environment"

TILE = 32
random.seed(814)

# Disco floor purple palette
PURPLE_BASE = (140, 40, 160)
PURPLE_GLOW = (180, 60, 200)
PURPLE_BRIGHT = (220, 120, 240)
PURPLE_HOT = (245, 170, 255)
PURPLE_GRID = (60, 20, 80)
PURPLE_DARK = (45, 12, 55)

# Disco floor cyan palette
CYAN_BASE = (40, 130, 160)
CYAN_GLOW = (60, 180, 200)
CYAN_BRIGHT = (120, 220, 240)
CYAN_HOT = (170, 240, 255)
CYAN_GRID = (20, 60, 80)
CYAN_DARK = (12, 40, 55)

# Floor sub-square center glow steps (used for radial gradient in each cell)
FLOOR_BLACK = (15, 8, 18)

# VIP carpet palette
CARPET_BASE = (60, 20, 25)
CARPET_DARK = (50, 15, 20)
CARPET_LIGHT = (72, 28, 32)
CARPET_PILE1 = (55, 18, 22)
CARPET_PILE2 = (68, 24, 28)
CARPET_HIGHLIGHT = (80, 32, 38)
GOLD_TRIM = (200, 170, 60)
GOLD_TRIM_DARK = (180, 150, 40)
GOLD_TRIM_BRIGHT = (225, 195, 80)

# Speaker palette
SPEAKER_BLACK = (20, 20, 22)
SPEAKER_PANEL = (30, 30, 33)
SPEAKER_DARK = (14, 14, 16)
CONE_BASE = (35, 35, 38)
CONE_MID = (45, 45, 50)
CONE_RING = (28, 28, 32)
CONE_CENTER = (55, 55, 62)
CONE_DOT = (18, 18, 20)
CHROME = (160, 165, 175)
CHROME_BRIGHT = (200, 205, 215)
CHROME_DARK = (120, 124, 132)

# Bar palette
BAR_WOOD = (80, 50, 30)
BAR_WOOD_DARK = (60, 38, 22)
BAR_WOOD_LIGHT = (95, 62, 38)
BAR_WOOD_GRAIN = (70, 44, 26)
BRASS_RAIL = (190, 160, 50)
BRASS_DARK = (160, 135, 40)
BRASS_BRIGHT = (215, 185, 70)
BOTTLE_GREEN = (30, 100, 45)
BOTTLE_AMBER = (140, 90, 25)
BOTTLE_BLUE = (40, 60, 130)
BOTTLE_RED = (130, 30, 35)
BOTTLE_CAP = (180, 180, 175)
BAR_FRONT = (55, 34, 18)
BAR_FRONT_DARK = (40, 25, 12)

# Dance floor edge palette
EDGE_CHROME = (170, 175, 185)
EDGE_CHROME_BRIGHT = (200, 205, 215)
EDGE_CHROME_DARK = (130, 134, 142)
EDGE_SHADOW = (10, 8, 12)
EDGE_SHADOW_MID = (18, 15, 22)
EDGE_VOID = (5, 3, 6)


def _draw_disco_subcells(img, x_off, base, glow, bright, hot, grid, dark):
    """Draw a 4x4 grid of glowing sub-squares within a tile.

    Each sub-square is 8x8 with grid lines between them. Each cell has a
    radial-ish glow gradient from dark edges to a bright center dot.
    """
    d = ImageDraw.Draw(img)

    # Fill entire tile with darkest color (grid line color)
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=dark)

    # Draw grid lines (1px between each 8x8 cell gives 7px cells with borders)
    # Layout: 4 cells across = 4*7 + 5 grid lines = 33, so use 8px cells with
    # shared 1px grid lines. Each cell occupies [col*8, col*8+7].
    cell_size = 8  # 4 cells * 8 = 32
    for row in range(4):
        for col in range(4):
            cx = x_off + col * cell_size
            cy = row * cell_size

            # Grid border (outermost pixel ring of each cell)
            # Top and bottom borders
            d.line([cx, cy, cx + cell_size - 1, cy], fill=grid)
            d.line([cx, cy + cell_size - 1, cx + cell_size - 1, cy + cell_size - 1],
                   fill=grid)
            # Left and right borders
            d.line([cx, cy, cx, cy + cell_size - 1], fill=grid)
            d.line([cx + cell_size - 1, cy, cx + cell_size - 1, cy + cell_size - 1],
                   fill=grid)

            # Inner area (6x6 inside the 8x8 cell): gradient glow
            inner_x = cx + 1
            inner_y = cy + 1

            # Outermost ring of inner area (dark base)
            d.rectangle([inner_x, inner_y,
                         inner_x + 5, inner_y + 5], fill=dark)

            # Layer 1: base color (5x5 centered — skip corners for roundness)
            d.rectangle([inner_x, inner_y,
                         inner_x + 5, inner_y + 5], fill=base)

            # Darken corners of the base square to simulate radial falloff
            for corner in [(inner_x, inner_y),
                           (inner_x + 5, inner_y),
                           (inner_x, inner_y + 5),
                           (inner_x + 5, inner_y + 5)]:
                img.putpixel(corner, (*dark, 255))

            # Layer 2: glow ring (4x4 centered)
            d.rectangle([inner_x + 1, inner_y + 1,
                         inner_x + 4, inner_y + 4], fill=glow)

            # Layer 3: bright core (2x2 centered)
            d.rectangle([inner_x + 2, inner_y + 2,
                         inner_x + 3, inner_y + 3], fill=bright)

            # Layer 4: hot center dot (single pixel)
            center_px = inner_x + 2 + random.randint(0, 1)
            center_py = inner_y + 2 + random.randint(0, 1)
            img.putpixel((center_px, center_py), (*hot, 255))

    # Add subtle variation — a few random pixels slightly brighter or darker
    for _ in range(12):
        rx = x_off + random.randint(2, TILE - 3)
        ry = random.randint(2, TILE - 3)
        pixel = img.getpixel((rx, ry))[:3]
        # Only modify non-grid pixels
        if pixel != grid and pixel != dark:
            # Slightly shift brightness
            shift = random.choice([-15, -10, 10, 15])
            mod = tuple(max(0, min(255, c + shift)) for c in pixel)
            img.putpixel((rx, ry), (*mod, 255))


def draw_disco_purple(img, x_off):
    """Illuminated dance floor square in purple/magenta color scheme."""
    _draw_disco_subcells(img, x_off,
                         PURPLE_BASE, PURPLE_GLOW, PURPLE_BRIGHT,
                         PURPLE_HOT, PURPLE_GRID, PURPLE_DARK)


def draw_disco_cyan(img, x_off):
    """Illuminated dance floor square in blue/cyan color scheme."""
    _draw_disco_subcells(img, x_off,
                         CYAN_BASE, CYAN_GLOW, CYAN_BRIGHT,
                         CYAN_HOT, CYAN_GRID, CYAN_DARK)


def draw_vip_lounge(img, x_off):
    """Dark burgundy carpet texture with gold trim along the top edge."""
    d = ImageDraw.Draw(img)

    # Carpet base
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=CARPET_BASE)

    # Gold/brass trim strip along top edge (3px tall)
    d.rectangle([x_off, 0, x_off + TILE - 1, 2], fill=GOLD_TRIM)
    # Trim shading: top row brighter, bottom row darker
    for x in range(x_off, x_off + TILE):
        img.putpixel((x, 0), (*GOLD_TRIM_BRIGHT, 255))
    for x in range(x_off, x_off + TILE):
        if random.random() < 0.5:
            img.putpixel((x, 1), (*GOLD_TRIM, 255))
        else:
            img.putpixel((x, 1), (*GOLD_TRIM_BRIGHT, 255))
    for x in range(x_off, x_off + TILE):
        img.putpixel((x, 2), (*GOLD_TRIM_DARK, 255))

    # Decorative notch pattern on the trim (every 4px, a darker dip)
    for x in range(x_off + 3, x_off + TILE, 4):
        img.putpixel((x, 1), (*GOLD_TRIM_DARK, 255))

    # Carpet pile texture — random subtle dots across the carpet area
    for _ in range(80):
        px = x_off + random.randint(0, TILE - 1)
        py = random.randint(3, TILE - 1)
        c = random.choice([CARPET_DARK, CARPET_LIGHT, CARPET_PILE1,
                           CARPET_PILE2, CARPET_BASE])
        img.putpixel((px, py), (*c, 255))

    # Occasional brighter highlight fiber
    for _ in range(8):
        hx = x_off + random.randint(0, TILE - 1)
        hy = random.randint(5, TILE - 1)
        img.putpixel((hx, hy), (*CARPET_HIGHLIGHT, 255))

    # Subtle carpet pattern — faint diagonal cross-hatch every 8 pixels
    for y in range(4, TILE, 8):
        for x in range(0, TILE, 8):
            px = x_off + x
            py = y
            if 0 <= py < TILE:
                c = CARPET_DARK if random.random() < 0.6 else CARPET_PILE1
                img.putpixel((px, py), (*c, 255))
                # Diagonal hint
                if x + 1 < TILE and py + 1 < TILE:
                    img.putpixel((px + 1, py + 1), (*c, 255))

    # Shadow line just below the gold trim
    for x in range(x_off, x_off + TILE):
        if random.random() < 0.7:
            img.putpixel((x, 3), (*CARPET_DARK, 255))


def draw_speaker_stack(img, x_off):
    """Black speaker cabinet with speaker cones and chrome trim."""
    d = ImageDraw.Draw(img)

    # Cabinet body
    d.rectangle([x_off, 0, x_off + TILE - 1, TILE - 1], fill=SPEAKER_BLACK)

    # Chrome trim at top and bottom edges (2px each)
    d.rectangle([x_off, 0, x_off + TILE - 1, 1], fill=CHROME)
    d.rectangle([x_off, TILE - 2, x_off + TILE - 1, TILE - 1], fill=CHROME)
    # Chrome highlight on top row
    for x in range(x_off + 1, x_off + TILE - 1, 2):
        img.putpixel((x, 0), (*CHROME_BRIGHT, 255))
    # Chrome shadow on bottom row
    for x in range(x_off, x_off + TILE, 2):
        img.putpixel((x, TILE - 1), (*CHROME_DARK, 255))

    # Panel area (slightly lighter than body)
    d.rectangle([x_off + 2, 3, x_off + TILE - 3, TILE - 4], fill=SPEAKER_PANEL)

    # Panel edge bevel
    d.line([x_off + 2, 3, x_off + TILE - 3, 3], fill=SPEAKER_DARK)
    d.line([x_off + 2, 3, x_off + 2, TILE - 4], fill=SPEAKER_DARK)
    d.line([x_off + TILE - 3, 3, x_off + TILE - 3, TILE - 4], fill=SPEAKER_BLACK)
    d.line([x_off + 2, TILE - 4, x_off + TILE - 3, TILE - 4], fill=SPEAKER_BLACK)

    # Three speaker cones arranged vertically
    # Cone 1 (top, smaller — tweeter): center at (16, 8), radius 3
    _draw_speaker_cone(img, d, x_off + 16, 8, 3)

    # Cone 2 (middle, larger — woofer): center at (16, 17), radius 5
    _draw_speaker_cone(img, d, x_off + 16, 17, 5)

    # Cone 3 (bottom, medium — mid): center at (16, 25), radius 4
    _draw_speaker_cone(img, d, x_off + 16, 25, 4)

    # Panel texture — subtle noise
    for _ in range(15):
        nx = x_off + random.randint(3, TILE - 4)
        ny = random.randint(4, TILE - 5)
        pixel = img.getpixel((nx, ny))[:3]
        if pixel == SPEAKER_PANEL:
            c = random.choice([SPEAKER_BLACK, SPEAKER_PANEL, SPEAKER_DARK])
            img.putpixel((nx, ny), (*c, 255))

    # Screw holes in corners of the panel
    for sx, sy in [(x_off + 4, 5), (x_off + TILE - 5, 5),
                   (x_off + 4, TILE - 6), (x_off + TILE - 5, TILE - 6)]:
        img.putpixel((sx, sy), (*CHROME_DARK, 255))


def _draw_speaker_cone(img, d, cx, cy, radius):
    """Draw concentric circles for a speaker cone at (cx, cy)."""
    # Outer ring
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              fill=CONE_BASE, outline=CONE_RING)

    # Middle ring
    if radius > 2:
        mid_r = radius - 1
        d.ellipse([cx - mid_r, cy - mid_r, cx + mid_r, cy + mid_r],
                  fill=CONE_MID, outline=CONE_RING)

    # Inner ring
    if radius > 3:
        inner_r = radius - 2
        d.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                  fill=CONE_BASE, outline=CONE_RING)

    # Center highlight
    if radius > 2:
        center_r = max(1, radius - 3)
        d.ellipse([cx - center_r, cy - center_r, cx + center_r, cy + center_r],
                  fill=CONE_CENTER)

    # Center dot (dust cap)
    img.putpixel((cx, cy), (*CONE_DOT, 255))


def draw_bar_counter(img, x_off):
    """Dark wood counter top with brass rail and bottle silhouettes."""
    d = ImageDraw.Draw(img)

    # Bar front face (lower portion, visible from side)
    d.rectangle([x_off, 16, x_off + TILE - 1, TILE - 1], fill=BAR_FRONT)

    # Bar front panel detail
    d.line([x_off, 16, x_off + TILE - 1, 16], fill=BAR_FRONT_DARK)
    d.line([x_off, TILE - 1, x_off + TILE - 1, TILE - 1], fill=BAR_FRONT_DARK)
    # Vertical panel lines on front
    d.line([x_off + 10, 17, x_off + 10, TILE - 2], fill=BAR_FRONT_DARK)
    d.line([x_off + 21, 17, x_off + 21, TILE - 2], fill=BAR_FRONT_DARK)
    # Panel texture
    for _ in range(20):
        fx = x_off + random.randint(1, TILE - 2)
        fy = random.randint(17, TILE - 2)
        c = random.choice([BAR_FRONT, BAR_FRONT_DARK, BAR_FRONT])
        img.putpixel((fx, fy), (*c, 255))

    # Wood counter top surface (top area)
    d.rectangle([x_off, 10, x_off + TILE - 1, 15], fill=BAR_WOOD)

    # Wood grain texture (subtle horizontal lines across the top)
    for y in range(10, 16):
        for x in range(x_off, x_off + TILE):
            if random.random() < 0.15:
                c = random.choice([BAR_WOOD_DARK, BAR_WOOD_GRAIN, BAR_WOOD_LIGHT])
                img.putpixel((x, y), (*c, 255))
    # Prominent grain lines
    for grain_y in [11, 13]:
        for x in range(x_off, x_off + TILE):
            if random.random() < 0.35:
                img.putpixel((x, grain_y), (*BAR_WOOD_GRAIN, 255))

    # Top edge highlight (light hitting the counter edge)
    for x in range(x_off, x_off + TILE):
        if random.random() < 0.6:
            img.putpixel((x, 10), (*BAR_WOOD_LIGHT, 255))

    # Brass rail (gold/yellow metallic strip, 2px, sits on top of counter)
    d.rectangle([x_off, 8, x_off + TILE - 1, 9], fill=BRASS_RAIL)
    # Rail highlight
    for x in range(x_off, x_off + TILE):
        if random.random() < 0.4:
            img.putpixel((x, 8), (*BRASS_BRIGHT, 255))
    for x in range(x_off, x_off + TILE):
        if random.random() < 0.3:
            img.putpixel((x, 9), (*BRASS_DARK, 255))
    # Rail bracket supports (small chrome squares every 10px)
    for bx in range(x_off + 5, x_off + TILE, 10):
        img.putpixel((bx, 9), (*CHROME_DARK, 255))

    # Bottle silhouettes peeking above the bar (behind the rail)
    bottles = [
        (x_off + 3, BOTTLE_GREEN, 5),
        (x_off + 8, BOTTLE_AMBER, 6),
        (x_off + 13, BOTTLE_BLUE, 4),
        (x_off + 18, BOTTLE_RED, 5),
        (x_off + 23, BOTTLE_GREEN, 6),
        (x_off + 28, BOTTLE_AMBER, 4),
    ]
    for bx, color, height in bottles:
        # Bottle body (1-2px wide rectangle above the rail)
        top_y = 8 - height
        if top_y < 0:
            top_y = 0
        d.rectangle([bx, top_y, bx + 1, 7], fill=color)
        # Bottle neck (1px wide, 1-2px above body)
        if top_y > 1:
            img.putpixel((bx, top_y - 1), (*color, 255))
        # Cap / cork highlight
        if top_y > 0:
            img.putpixel((bx, max(0, top_y - 1)), (*BOTTLE_CAP, 255))

    # Slight shadow under the counter top
    for x in range(x_off, x_off + TILE):
        if random.random() < 0.5:
            img.putpixel((x, 16), (*BAR_FRONT_DARK, 255))


def draw_dance_floor_edge(img, x_off):
    """Top: illuminated tile, middle: chrome edge strip, bottom: shadow void."""
    d = ImageDraw.Draw(img)

    # --- Top portion: illuminated floor (rows 0-20, ~21px) ---
    # Fill with dark purple base first
    d.rectangle([x_off, 0, x_off + TILE - 1, 20], fill=PURPLE_DARK)

    # Draw partial disco floor cells (3 rows of 4 sub-squares, 7px each)
    cell_w = 8
    for row in range(3):
        for col in range(4):
            cx = x_off + col * cell_w
            cy = row * cell_w

            # Alternate purple and cyan per cell in a checkerboard
            if (row + col) % 2 == 0:
                base, glow, bright, hot, grid = (
                    PURPLE_BASE, PURPLE_GLOW, PURPLE_BRIGHT, PURPLE_HOT,
                    PURPLE_GRID)
            else:
                base, glow, bright, hot, grid = (
                    CYAN_BASE, CYAN_GLOW, CYAN_BRIGHT, CYAN_HOT, CYAN_GRID)

            # Clamp drawing to top portion (rows 0-20)
            cell_bottom = min(cy + cell_w - 1, 20)

            # Grid border
            d.line([cx, cy, cx + cell_w - 1, cy], fill=grid)
            if cell_bottom <= 20:
                d.line([cx, cell_bottom, cx + cell_w - 1, cell_bottom], fill=grid)
            d.line([cx, cy, cx, cell_bottom], fill=grid)
            d.line([cx + cell_w - 1, cy, cx + cell_w - 1, cell_bottom], fill=grid)

            # Inner glow (only if enough space)
            inner_x = cx + 1
            inner_y = cy + 1
            inner_bottom = min(inner_y + 5, 20)
            if inner_y <= 20:
                dark_c = PURPLE_DARK if (row + col) % 2 == 0 else CYAN_DARK
                d.rectangle([inner_x, inner_y, inner_x + 5, inner_bottom],
                            fill=base)
                # Darken corners
                for corner_x, corner_y in [(inner_x, inner_y),
                                           (inner_x + 5, inner_y),
                                           (inner_x, inner_bottom),
                                           (inner_x + 5, inner_bottom)]:
                    if corner_y <= 20:
                        img.putpixel((corner_x, corner_y), (*dark_c, 255))

                # Glow center
                if inner_y + 1 <= 20 and inner_y + 4 <= 20:
                    d.rectangle([inner_x + 1, inner_y + 1,
                                 inner_x + 4, inner_y + 4], fill=glow)
                # Bright core
                if inner_y + 2 <= 20 and inner_y + 3 <= 20:
                    d.rectangle([inner_x + 2, inner_y + 2,
                                 inner_x + 3, inner_y + 3], fill=bright)
                # Hot dot
                if inner_y + 2 <= 20:
                    hot_x = inner_x + 2 + random.randint(0, 1)
                    hot_y = inner_y + 2
                    if hot_y <= 20:
                        img.putpixel((hot_x, hot_y), (*hot, 255))

    # --- Middle: chrome/metallic edge strip (rows 21-24, 4px) ---
    d.rectangle([x_off, 21, x_off + TILE - 1, 24], fill=EDGE_CHROME)
    # Top highlight line
    for x in range(x_off, x_off + TILE):
        img.putpixel((x, 21), (*EDGE_CHROME_BRIGHT, 255))
    # Middle variation
    for x in range(x_off, x_off + TILE):
        if random.random() < 0.3:
            img.putpixel((x, 22), (*EDGE_CHROME_BRIGHT, 255))
    # Lower shadow
    for x in range(x_off, x_off + TILE):
        img.putpixel((x, 24), (*EDGE_CHROME_DARK, 255))
    # Rivet/bolt details every 8px
    for rx in range(x_off + 3, x_off + TILE, 8):
        img.putpixel((rx, 22), (*CHROME_BRIGHT, 255))
        img.putpixel((rx, 23), (*CHROME_DARK, 255))

    # --- Bottom: dark void/shadow (rows 25-31, 7px) ---
    d.rectangle([x_off, 25, x_off + TILE - 1, TILE - 1], fill=EDGE_SHADOW)

    # Gradient from shadow-mid at top to full void at bottom
    for y in range(25, TILE):
        depth = y - 25  # 0 to 6
        if depth < 2:
            c = EDGE_SHADOW_MID
        elif depth < 4:
            c = EDGE_SHADOW
        else:
            c = EDGE_VOID
        for x in range(x_off, x_off + TILE):
            img.putpixel((x, y), (*c, 255))

    # A few faint structural lines in the shadow (support beams)
    for bx in range(x_off + 7, x_off + TILE, 8):
        for y in range(25, TILE):
            depth = y - 25
            if depth < 2:
                beam_c = EDGE_SHADOW_MID
            else:
                beam_c = EDGE_SHADOW
            # Beam is slightly lighter than void
            cur = img.getpixel((bx, y))[:3]
            lighter = tuple(min(255, c + 5) for c in cur)
            img.putpixel((bx, y), (*lighter, 255))


def main():
    num_tiles = 6
    width = num_tiles * TILE
    img = Image.new("RGBA", (width, TILE), (0, 0, 0, 0))

    draw_disco_purple(img, 0 * TILE)
    draw_disco_cyan(img, 1 * TILE)
    draw_vip_lounge(img, 2 * TILE)
    draw_speaker_stack(img, 3 * TILE)
    draw_bar_counter(img, 4 * TILE)
    draw_dance_floor_edge(img, 5 * TILE)

    out = OUTPUT_DIR / "tileset_disco_floor.png"
    img.save(out)
    print(f"  [OK] {out.name} ({width}x{TILE}, {num_tiles} tiles)")


if __name__ == "__main__":
    print("Generating Bee Gees Disco Floor tileset...")
    main()
    print("Done!")
