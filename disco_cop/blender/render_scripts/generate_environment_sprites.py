"""
Generate pixel-art environment sprites using Pillow.
70s disco city nightscape — dark purples, neon accents, city skyline.

Run via: python generate_environment_sprites.py

Outputs:
  assets/sprites/environment/parallax_sky.png        (640x360, far layer)
  assets/sprites/environment/parallax_city_far.png    (640x360, mid layer)
  assets/sprites/environment/parallax_city_near.png   (640x360, near layer)
  assets/sprites/environment/tileset.png              (128x48, 8x3 grid of 16x16 tiles)
"""

import math
import os
import random
from PIL import Image, ImageDraw

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))
ENV_DIR = os.path.join(BASE_DIR, 'assets', 'sprites', 'environment')


def ensure_dirs():
    os.makedirs(ENV_DIR, exist_ok=True)


def save(img, name):
    path = os.path.join(ENV_DIR, name)
    img.save(path)
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# Parallax Layer 1 — Sky (far background, motion_scale 0.1)
# Dark purple night sky with stars and a moon
# Designed to tile horizontally
# ---------------------------------------------------------------------------

def create_parallax_sky():
    W, H = 640, 360
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = img.load()

    random.seed(42)  # Reproducible

    # Gradient sky — dark purple at top, slightly lighter at horizon
    for y in range(H):
        t = y / H
        r = int(12 + 18 * t)
        g = int(5 + 10 * t)
        b = int(20 + 25 * t)
        for x in range(W):
            px[x, y] = (r, g, b, 255)

    # Stars — scattered dots, brighter near top
    for _ in range(200):
        x = random.randint(0, W - 1)
        y = random.randint(0, int(H * 0.7))
        brightness = random.randint(150, 255)
        # Slight color variation — some warm, some cool
        color_type = random.random()
        if color_type < 0.6:
            color = (brightness, brightness, brightness, brightness)
        elif color_type < 0.8:
            color = (brightness, brightness, int(brightness * 0.7), brightness)
        else:
            color = (int(brightness * 0.7), int(brightness * 0.8), brightness, brightness)
        px[x, y] = color
        # Some brighter stars get a small cross
        if brightness > 230 and random.random() < 0.3:
            dim = brightness // 2
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H:
                    px[nx, ny] = (dim, dim, dim, dim)

    # Moon — upper right area
    moon_cx, moon_cy, moon_r = 520, 60, 20
    for y in range(moon_cy - moon_r - 2, moon_cy + moon_r + 3):
        for x in range(moon_cx - moon_r - 2, moon_cx + moon_r + 3):
            if 0 <= x < W and 0 <= y < H:
                dist = math.sqrt((x - moon_cx) ** 2 + (y - moon_cy) ** 2)
                if dist <= moon_r:
                    # Moon surface — pale yellow
                    px[x, y] = (220, 210, 180, 255)
                elif dist <= moon_r + 2:
                    # Glow around moon
                    a = int(80 * (1.0 - (dist - moon_r) / 2.0))
                    r0, g0, b0, _ = px[x, y]
                    px[x, y] = (min(255, r0 + 40), min(255, g0 + 35),
                                min(255, b0 + 20), 255)

    # Moon craters (subtle darker spots)
    craters = [(515, 55, 3), (525, 65, 4), (518, 70, 2), (528, 55, 2)]
    for cx, cy, cr in craters:
        for y in range(cy - cr, cy + cr + 1):
            for x in range(cx - cr, cx + cr + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= cr ** 2:
                    if 0 <= x < W and 0 <= y < H:
                        px[x, y] = (190, 180, 155, 255)

    # Very distant city skyline silhouette at bottom
    # Just dark shapes against the slightly lighter horizon
    buildings = []
    x = 0
    while x < W:
        bw = random.randint(20, 60)
        bh = random.randint(15, 50)
        buildings.append((x, bw, bh))
        x += bw + random.randint(2, 10)

    for bx, bw, bh in buildings:
        for y in range(H - bh, H):
            for x in range(bx, min(bx + bw, W)):
                px[x, y] = (8, 3, 14, 255)

    save(img, 'parallax_sky.png')


# ---------------------------------------------------------------------------
# Parallax Layer 2 — Far City (mid layer, motion_scale 0.3)
# Building silhouettes with some lit windows, neon outlines
# ---------------------------------------------------------------------------

def create_parallax_city_far():
    W, H = 640, 360
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = img.load()

    random.seed(123)

    # Building definitions: (x, width, height) from bottom
    buildings = []
    x = 0
    while x < W + 50:
        bw = random.randint(30, 80)
        bh = random.randint(80, 220)
        buildings.append((x, bw, bh))
        x += bw + random.randint(-5, 8)

    # Draw buildings
    for bx, bw, bh in buildings:
        # Building body — dark with slight color variation
        base_r = random.randint(15, 30)
        base_g = random.randint(8, 18)
        base_b = random.randint(25, 45)
        body_color = (base_r, base_g, base_b, 255)

        for y in range(H - bh, H):
            for x in range(bx, min(bx + bw, W)):
                if x >= 0:
                    px[x, y] = body_color

        # Roof edge — slightly lighter
        roof_y = H - bh
        if 0 <= roof_y < H:
            for x in range(max(0, bx), min(bx + bw, W)):
                px[x, roof_y] = (base_r + 15, base_g + 10, base_b + 15, 255)

        # Windows — small lit rectangles in a grid
        win_start_y = H - bh + 8
        for wy in range(win_start_y, H - 10, 12):
            for wx in range(bx + 5, bx + bw - 5, 8):
                if 0 <= wx < W - 2 and 0 <= wy < H - 3:
                    if random.random() < 0.35:
                        # Lit window — warm yellow or cool blue or neon
                        wtype = random.random()
                        if wtype < 0.5:
                            wc = (180, 160, 80, 200)  # Warm yellow
                        elif wtype < 0.8:
                            wc = (80, 120, 180, 180)  # Cool blue
                        else:
                            wc = (200, 80, 180, 200)  # Neon magenta
                        for dy in range(3):
                            for dx in range(2):
                                if 0 <= wx + dx < W and 0 <= wy + dy < H:
                                    px[wx + dx, wy + dy] = wc

    # Neon accents on some rooftops
    for bx, bw, bh in buildings:
        if random.random() < 0.25:
            roof_y = H - bh - 1
            neon_color = random.choice([
                (255, 50, 200, 200),   # Magenta
                (50, 200, 255, 200),   # Cyan
                (255, 180, 50, 200),   # Gold
            ])
            for x in range(max(0, bx + 2), min(bx + bw - 2, W)):
                if 0 <= roof_y < H:
                    px[x, roof_y] = neon_color
                if 0 <= roof_y + 1 < H:
                    r, g, b, _ = neon_color
                    px[x, roof_y + 1] = (r // 3, g // 3, b // 3, 100)

    save(img, 'parallax_city_far.png')


# ---------------------------------------------------------------------------
# Parallax Layer 3 — Near City (near layer, motion_scale 0.6)
# Closer buildings with neon signs, more detail, disco aesthetic
# ---------------------------------------------------------------------------

def create_parallax_city_near():
    W, H = 640, 360
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = img.load()

    random.seed(777)

    # Larger, more detailed buildings
    buildings = []
    x = -20
    while x < W + 40:
        bw = random.randint(60, 120)
        bh = random.randint(120, 300)
        buildings.append((x, bw, bh))
        x += bw + random.randint(-8, 5)

    for bx, bw, bh in buildings:
        base_r = random.randint(25, 45)
        base_g = random.randint(12, 25)
        base_b = random.randint(35, 60)
        body_color = (base_r, base_g, base_b, 255)
        edge_color = (base_r + 10, base_g + 8, base_b + 10, 255)

        for y in range(H - bh, H):
            for x in range(max(0, bx), min(bx + bw, W)):
                px[x, y] = body_color

        # Vertical edge lines
        for y in range(H - bh, H):
            if 0 <= bx < W:
                px[bx, y] = edge_color
            if 0 <= bx + bw - 1 < W:
                px[bx + bw - 1, y] = edge_color

        # Roof line
        roof_y = H - bh
        for x in range(max(0, bx), min(bx + bw, W)):
            if 0 <= roof_y < H:
                px[x, roof_y] = edge_color

        # Windows — larger, more detailed
        win_start_y = H - bh + 6
        for wy in range(win_start_y, H - 8, 10):
            for wx in range(bx + 4, bx + bw - 6, 10):
                if 0 <= wx < W - 4 and 0 <= wy < H - 5:
                    if random.random() < 0.45:
                        wtype = random.random()
                        if wtype < 0.4:
                            wc = (200, 180, 90, 220)
                        elif wtype < 0.7:
                            wc = (90, 140, 200, 200)
                        elif wtype < 0.85:
                            wc = (220, 60, 180, 220)
                        else:
                            wc = (60, 220, 200, 220)   # Teal
                        for dy in range(4):
                            for dx in range(3):
                                if 0 <= wx + dx < W and 0 <= wy + dy < H:
                                    px[wx + dx, wy + dy] = wc
                        # Window frame
                        for dx in range(4):
                            if 0 <= wx + dx < W:
                                if 0 <= wy - 1 < H:
                                    px[wx + dx, wy - 1] = edge_color
                                if 0 <= wy + 4 < H:
                                    px[wx + dx, wy + 4] = edge_color

    # Neon signs on building faces
    neon_signs = [
        (80, "bar"),
        (250, "club"),
        (420, "bar"),
        (560, "club"),
    ]
    for sign_x, sign_type in neon_signs:
        # Find building at this x to get roof height
        sign_y = H - 150 + random.randint(-20, 40)
        if sign_type == "bar":
            # Horizontal neon bar — magenta
            neon_c = (255, 50, 200, 240)
            glow_c = (255, 50, 200, 60)
            bar_w = random.randint(20, 35)
            for x in range(sign_x, min(sign_x + bar_w, W)):
                if 0 <= sign_y < H:
                    px[x, sign_y] = neon_c
                if 0 <= sign_y + 1 < H:
                    px[x, sign_y + 1] = neon_c
                # Glow above/below
                for dy in [-2, -1, 2, 3]:
                    if 0 <= sign_y + dy < H and 0 <= x < W:
                        r0, g0, b0, a0 = px[x, sign_y + dy]
                        gr, gg, gb, ga = glow_c
                        px[x, sign_y + dy] = (
                            min(255, r0 + gr // 3),
                            min(255, g0 + gg // 3),
                            min(255, b0 + gb // 3), 255)
        else:
            # Vertical neon strip — cyan
            neon_c = (50, 220, 255, 240)
            bar_h = random.randint(15, 30)
            for y in range(sign_y, min(sign_y + bar_h, H)):
                if 0 <= sign_x < W:
                    px[sign_x, y] = neon_c
                if 0 <= sign_x + 1 < W:
                    px[sign_x + 1, y] = neon_c
                # Side glow
                for dx in [-2, -1, 2, 3]:
                    nx = sign_x + dx
                    if 0 <= nx < W and 0 <= y < H:
                        r0, g0, b0, a0 = px[nx, y]
                        px[nx, y] = (
                            min(255, r0 + 15),
                            min(255, g0 + 60),
                            min(255, b0 + 70), 255)

    # Disco ball hanging from a rooftop (fun detail)
    db_x, db_y = 350, H - 230
    # String
    for y in range(db_y - 15, db_y):
        if 0 <= y < H and 0 <= db_x < W:
            px[db_x, y] = (100, 100, 100, 200)
    # Ball
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            if dx ** 2 + dy ** 2 <= 16:
                nx, ny = db_x + dx, db_y + dy
                if 0 <= nx < W and 0 <= ny < H:
                    # Checkerboard mirrored tiles
                    if (dx + dy) % 2 == 0:
                        px[nx, ny] = (200, 200, 220, 255)
                    else:
                        px[nx, ny] = (150, 150, 170, 255)
    # Sparkle
    for dx, dy in [(5, -2), (-5, 1), (3, 4), (-3, -4)]:
        nx, ny = db_x + dx, db_y + dy
        if 0 <= nx < W and 0 <= ny < H:
            px[nx, ny] = (255, 255, 255, 180)

    save(img, 'parallax_city_near.png')


# ---------------------------------------------------------------------------
# Tileset — 128x48, 8 columns x 3 rows of 16x16 tiles
#
# Layout:
#   Row 0: ground_top, ground_fill, plat_left, plat_mid, plat_right, hazard_spike, deco_1, deco_2
#   Row 1: ground_top_alt, ground_fill_dark, plat_left_alt, plat_mid_alt, plat_right_alt, hazard_lava, deco_3, deco_4
#   Row 2: corner_tl, corner_tr, corner_bl, corner_br, wall_left, wall_right, blank, blank
# ---------------------------------------------------------------------------

def create_tileset():
    COLS, ROWS, TILE = 8, 3, 16
    W, H = COLS * TILE, ROWS * TILE
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def tile_rect(col, row):
        x0, y0 = col * TILE, row * TILE
        return x0, y0, x0 + TILE, y0 + TILE

    def fill_tile(col, row, color):
        x0, y0 = col * TILE, row * TILE
        draw.rectangle([x0, y0, x0 + TILE - 1, y0 + TILE - 1], fill=color)

    def set_px(col, row, x, y, color):
        """Set pixel at local (x,y) within tile (col,row)."""
        px = img.load()
        gx, gy = col * TILE + x, row * TILE + y
        if 0 <= gx < W and 0 <= gy < H:
            px[gx, gy] = color

    # Colors — 70s disco nightclub floor/walls
    ground_top = (90, 65, 50, 255)       # Brown surface
    ground_fill = (70, 50, 38, 255)      # Darker brown fill
    ground_dark = (55, 40, 30, 255)      # Even darker
    plat_color = (110, 80, 60, 255)      # Platform lighter brown
    plat_edge = (80, 58, 42, 255)        # Platform edge
    hazard_red = (220, 30, 30, 255)      # Spike red
    hazard_orange = (255, 120, 20, 255)  # Lava orange
    neon_magenta = (255, 50, 200, 255)   # Disco neon
    neon_cyan = (50, 220, 255, 255)      # Disco neon
    tile_purple = (60, 30, 80, 255)      # Disco floor purple
    tile_gold = (200, 170, 50, 255)      # Disco floor gold

    px = img.load()

    # --- Row 0 ---

    # (0,0) Ground Top — surface with grass/edge line
    fill_tile(0, 0, ground_fill)
    for x in range(TILE):
        set_px(0, 0, x, 0, (120, 90, 65, 255))  # Top edge highlight
        set_px(0, 0, x, 1, ground_top)
    # Subtle texture dots
    for x in range(0, TILE, 3):
        set_px(0, 0, x, 5, ground_dark)
        set_px(0, 0, x + 1, 10, ground_dark)

    # (1,0) Ground Fill — solid subsurface
    fill_tile(1, 0, ground_fill)
    for x in range(0, TILE, 4):
        for y in range(0, TILE, 5):
            set_px(1, 0, x, y, ground_dark)
    # Occasional lighter specks
    for x in range(2, TILE, 6):
        set_px(1, 0, x, 3, (85, 60, 45, 255))
        set_px(1, 0, x, 11, (85, 60, 45, 255))

    # (2,0) Platform Left Edge
    fill_tile(2, 0, plat_color)
    for y in range(TILE):
        set_px(2, 0, 0, y, plat_edge)
        set_px(2, 0, 1, y, plat_edge)
    for x in range(TILE):
        set_px(2, 0, x, 0, (130, 100, 75, 255))  # Top highlight

    # (3,0) Platform Middle
    fill_tile(3, 0, plat_color)
    for x in range(TILE):
        set_px(3, 0, x, 0, (130, 100, 75, 255))  # Top highlight
    # Surface texture
    for x in range(0, TILE, 4):
        set_px(3, 0, x + 1, 2, plat_edge)

    # (4,0) Platform Right Edge
    fill_tile(4, 0, plat_color)
    for y in range(TILE):
        set_px(4, 0, TILE - 1, y, plat_edge)
        set_px(4, 0, TILE - 2, y, plat_edge)
    for x in range(TILE):
        set_px(4, 0, x, 0, (130, 100, 75, 255))

    # (5,0) Hazard Spike — triangular spikes
    for spike_x in [1, 5, 9, 13]:
        for h in range(6):
            w = 3 - h // 2
            for dx in range(-w, w + 1):
                x = spike_x + dx
                y = TILE - 1 - h
                if 0 <= x < TILE and 0 <= y < TILE:
                    if h < 2:
                        set_px(5, 0, x, y, (180, 25, 25, 255))
                    elif h < 4:
                        set_px(5, 0, x, y, hazard_red)
                    else:
                        set_px(5, 0, x, y, (255, 60, 40, 255))

    # (6,0) Deco 1 — disco floor tile (checkered purple/gold)
    for y in range(TILE):
        for x in range(TILE):
            if (x // 4 + y // 4) % 2 == 0:
                set_px(6, 0, x, y, tile_purple)
            else:
                set_px(6, 0, x, y, tile_gold)

    # (7,0) Deco 2 — neon stripe tile
    fill_tile(7, 0, (35, 20, 50, 255))
    for x in range(TILE):
        set_px(7, 0, x, 7, neon_magenta)
        set_px(7, 0, x, 8, neon_magenta)
        # Glow
        set_px(7, 0, x, 6, (150, 30, 120, 180))
        set_px(7, 0, x, 9, (150, 30, 120, 180))

    # --- Row 1 ---

    # (0,1) Ground Top Alt — slightly different color
    fill_tile(0, 1, (65, 48, 36, 255))
    for x in range(TILE):
        set_px(0, 1, x, 0, (105, 80, 58, 255))
        set_px(0, 1, x, 1, (85, 62, 48, 255))
    for x in range(1, TILE, 4):
        set_px(0, 1, x, 6, (55, 40, 30, 255))

    # (1,1) Ground Fill Dark
    fill_tile(1, 1, ground_dark)
    for x in range(0, TILE, 5):
        for y in range(2, TILE, 4):
            set_px(1, 1, x, y, (45, 32, 24, 255))

    # (2,1) Platform Left Alt (thinner, for 16px-tall platforms)
    fill_tile(2, 1, (100, 75, 55, 255))
    for y in range(TILE):
        set_px(2, 1, 0, y, (75, 55, 40, 255))
    for x in range(TILE):
        set_px(2, 1, x, 0, (125, 95, 70, 255))
        set_px(2, 1, x, TILE - 1, (75, 55, 40, 255))

    # (3,1) Platform Mid Alt
    fill_tile(3, 1, (100, 75, 55, 255))
    for x in range(TILE):
        set_px(3, 1, x, 0, (125, 95, 70, 255))
        set_px(3, 1, x, TILE - 1, (75, 55, 40, 255))

    # (4,1) Platform Right Alt
    fill_tile(4, 1, (100, 75, 55, 255))
    for y in range(TILE):
        set_px(4, 1, TILE - 1, y, (75, 55, 40, 255))
    for x in range(TILE):
        set_px(4, 1, x, 0, (125, 95, 70, 255))
        set_px(4, 1, x, TILE - 1, (75, 55, 40, 255))

    # (5,1) Hazard Lava — bubbling orange
    for y in range(TILE):
        for x in range(TILE):
            # Wavy lava surface
            wave = math.sin(x * 0.5) * 2
            if y > TILE // 2 + wave:
                set_px(5, 1, x, y, (200, 80, 10, 255))
            elif y > TILE // 2 + wave - 2:
                set_px(5, 1, x, y, hazard_orange)
            elif y > TILE // 2 + wave - 3:
                set_px(5, 1, x, y, (255, 200, 50, 220))
    # Bubble highlights
    for bx, by in [(3, 6), (10, 5), (7, 9)]:
        set_px(5, 1, bx, by, (255, 240, 100, 255))

    # (6,1) Deco 3 — disco floor tile (neon grid)
    fill_tile(6, 1, (20, 10, 30, 255))
    for x in range(TILE):
        set_px(6, 1, x, 0, neon_cyan)
        set_px(6, 1, x, TILE - 1, neon_cyan)
    for y in range(TILE):
        set_px(6, 1, 0, y, neon_cyan)
        set_px(6, 1, TILE - 1, y, neon_cyan)
    # Inner glow lines
    for x in range(TILE):
        set_px(6, 1, x, TILE // 2, (30, 100, 130, 150))
    for y in range(TILE):
        set_px(6, 1, TILE // 2, y, (30, 100, 130, 150))

    # (7,1) Deco 4 — brick wall
    brick = (80, 40, 35, 255)
    mortar = (50, 30, 25, 255)
    fill_tile(7, 1, brick)
    # Horizontal mortar lines
    for x in range(TILE):
        set_px(7, 1, x, 3, mortar)
        set_px(7, 1, x, 7, mortar)
        set_px(7, 1, x, 11, mortar)
        set_px(7, 1, x, 15, mortar)
    # Vertical mortar (staggered)
    for y in range(0, 4):
        set_px(7, 1, 7, y, mortar)
    for y in range(4, 8):
        set_px(7, 1, 3, y, mortar)
        set_px(7, 1, 11, y, mortar)
    for y in range(8, 12):
        set_px(7, 1, 7, y, mortar)
    for y in range(12, 16):
        set_px(7, 1, 3, y, mortar)
        set_px(7, 1, 11, y, mortar)

    # --- Row 2 ---

    # (0,2) Corner Top-Left
    fill_tile(0, 2, ground_fill)
    for x in range(TILE):
        set_px(0, 2, x, 0, (120, 90, 65, 255))
    for y in range(TILE):
        set_px(0, 2, 0, y, (120, 90, 65, 255))

    # (1,2) Corner Top-Right
    fill_tile(1, 2, ground_fill)
    for x in range(TILE):
        set_px(1, 2, x, 0, (120, 90, 65, 255))
    for y in range(TILE):
        set_px(1, 2, TILE - 1, y, (120, 90, 65, 255))

    # (2,2) Corner Bottom-Left
    fill_tile(2, 2, ground_fill)
    for y in range(TILE):
        set_px(2, 2, 0, y, (120, 90, 65, 255))
    for x in range(TILE):
        set_px(2, 2, x, TILE - 1, (120, 90, 65, 255))

    # (3,2) Corner Bottom-Right
    fill_tile(3, 2, ground_fill)
    for y in range(TILE):
        set_px(3, 2, TILE - 1, y, (120, 90, 65, 255))
    for x in range(TILE):
        set_px(3, 2, x, TILE - 1, (120, 90, 65, 255))

    # (4,2) Wall Left — vertical surface
    fill_tile(4, 2, ground_fill)
    for y in range(TILE):
        set_px(4, 2, 0, y, (120, 90, 65, 255))
        set_px(4, 2, 1, y, ground_top)

    # (5,2) Wall Right — vertical surface
    fill_tile(5, 2, ground_fill)
    for y in range(TILE):
        set_px(5, 2, TILE - 1, y, (120, 90, 65, 255))
        set_px(5, 2, TILE - 2, y, ground_top)

    # (6,2) and (7,2) — empty/blank (reserved)

    save(img, 'tileset.png')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ensure_dirs()

    print("=== Generating Parallax Backgrounds ===")
    create_parallax_sky()
    create_parallax_city_far()
    create_parallax_city_near()

    print("\n=== Generating Tileset ===")
    create_tileset()

    print("\nDone! 3 parallax layers + 1 tileset generated.")


if __name__ == '__main__':
    main()
