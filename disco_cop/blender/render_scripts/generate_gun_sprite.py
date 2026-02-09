"""
Generate a proper pixel-art gun sprite to replace the AimLine ColorRect.
Also generates updated near parallax with disco club tables.

Run via: python generate_gun_sprite.py

Outputs:
  assets/sprites/weapons/gun.png  (24x10, pistol facing right)
  assets/sprites/environment/parallax_city_near.png  (640x360, updated with tables)
"""

import math
import os
import random
from PIL import Image, ImageDraw

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))
WEAPONS_DIR = os.path.join(BASE_DIR, 'assets', 'sprites', 'weapons')
ENV_DIR = os.path.join(BASE_DIR, 'assets', 'sprites', 'environment')


def ensure_dirs():
    os.makedirs(WEAPONS_DIR, exist_ok=True)
    os.makedirs(ENV_DIR, exist_ok=True)


def save(img, directory, name):
    path = os.path.join(directory, name)
    img.save(path)
    print(f"  Saved: {path}")


def draw_rect(px, x1, y1, x2, y2, color, w, h):
    for y in range(max(0, y1), min(h, y2 + 1)):
        for x in range(max(0, x1), min(w, x2 + 1)):
            px[x, y] = color


# ---------------------------------------------------------------------------
# Gun Sprite — 24x10, detailed pistol facing right
# Disco cop's sidearm — chrome/silver with gold accents
# ---------------------------------------------------------------------------

def create_gun():
    W, H = 24, 10
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = img.load()

    # Colors
    chrome = (180, 185, 195, 255)       # Main body
    chrome_hi = (220, 225, 235, 255)    # Highlights
    chrome_dk = (120, 125, 135, 255)    # Dark edges
    barrel_dk = (90, 92, 100, 255)      # Barrel interior
    gold = (200, 170, 50, 255)          # Gold accents (disco!)
    gold_dk = (160, 130, 35, 255)       # Dark gold
    grip_dk = (50, 35, 25, 255)         # Grip (dark wood/rubber)
    grip = (70, 50, 35, 255)            # Grip body
    grip_hi = (90, 65, 45, 255)         # Grip highlight
    black = (30, 30, 35, 255)           # Outlines/barrel bore

    # --- Barrel (rows 2-4, cols 10-23) ---
    # Top barrel edge
    draw_rect(px, 10, 2, 22, 2, chrome_dk, W, H)
    # Barrel body
    draw_rect(px, 10, 3, 22, 4, chrome, W, H)
    # Barrel highlight
    draw_rect(px, 12, 3, 20, 3, chrome_hi, W, H)
    # Muzzle tip
    px[23, 3] = chrome_dk
    px[23, 4] = chrome_dk
    # Muzzle bore (dark hole at end)
    px[22, 3] = barrel_dk
    px[23, 3] = black
    px[23, 4] = black

    # --- Slide / Upper receiver (rows 1-5, cols 5-14) ---
    draw_rect(px, 5, 1, 14, 1, chrome_dk, W, H)  # Top edge
    draw_rect(px, 5, 2, 9, 4, chrome, W, H)       # Body
    draw_rect(px, 6, 2, 9, 2, chrome_hi, W, H)    # Top highlight
    draw_rect(px, 5, 5, 14, 5, chrome_dk, W, H)   # Bottom edge

    # Slide serrations (rear grip lines)
    for x in [6, 8]:
        px[x, 3] = chrome_dk
        px[x, 4] = chrome_dk

    # --- Ejection port ---
    px[11, 2] = barrel_dk
    px[12, 2] = barrel_dk

    # --- Trigger guard (rows 5-7, cols 7-10) ---
    px[7, 6] = chrome_dk
    px[8, 6] = (0, 0, 0, 0)  # Open space
    px[9, 6] = (0, 0, 0, 0)
    px[10, 6] = chrome_dk
    px[7, 7] = chrome_dk
    px[8, 7] = chrome_dk
    px[9, 7] = chrome_dk
    px[10, 7] = chrome_dk

    # --- Trigger ---
    px[9, 5] = chrome_dk
    px[9, 6] = gold
    # px[9, 7] already set as guard

    # --- Grip (rows 5-9, cols 3-7) ---
    draw_rect(px, 3, 5, 7, 9, grip, W, H)
    # Grip left edge
    for y in range(5, 10):
        px[3, y] = grip_dk
    # Grip highlight
    draw_rect(px, 5, 6, 6, 8, grip_hi, W, H)
    # Grip texture lines
    for y in [6, 8]:
        px[4, y] = grip_dk
        px[5, y] = grip_dk
    # Grip bottom
    draw_rect(px, 3, 9, 7, 9, grip_dk, W, H)
    # Magazine base plate
    draw_rect(px, 4, 9, 6, 9, chrome_dk, W, H)

    # --- Gold accents (disco flair!) ---
    # Gold stripe along slide
    draw_rect(px, 10, 4, 14, 4, gold, W, H)
    draw_rect(px, 10, 5, 14, 5, gold_dk, W, H)

    # --- Front sight ---
    px[14, 1] = chrome_hi
    px[14, 0] = chrome_dk

    # --- Rear sight ---
    px[5, 0] = chrome_dk
    px[6, 0] = (0, 0, 0, 0)
    px[7, 0] = chrome_dk

    # --- Hammer (back of slide) ---
    px[4, 1] = chrome_dk
    px[4, 2] = chrome_dk

    save(img, WEAPONS_DIR, 'gun.png')


# ---------------------------------------------------------------------------
# Updated Parallax City Near — with disco club tables instead of building pillars
# Dark buildings in background, foreground has club interiors with tables,
# chairs, people silhouettes, and neon signs
# ---------------------------------------------------------------------------

def create_parallax_city_near():
    W, H = 640, 360
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = img.load()

    random.seed(777)

    # Background buildings (same as before but cleaner/crisper)
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
        edge_color = (base_r + 15, base_g + 12, base_b + 15, 255)

        # Crisp building body
        for y in range(max(0, H - bh), H):
            for xx in range(max(0, bx), min(bx + bw, W)):
                px[xx, y] = body_color

        # Clean vertical edges (2px wide for crispness)
        for y in range(max(0, H - bh), H):
            for dx in range(2):
                if 0 <= bx + dx < W:
                    px[bx + dx, y] = edge_color
                if 0 <= bx + bw - 1 - dx < W:
                    px[bx + bw - 1 - dx, y] = edge_color

        # Clean roof line (2px thick)
        roof_y = H - bh
        for dy in range(2):
            for xx in range(max(0, bx), min(bx + bw, W)):
                if 0 <= roof_y + dy < H:
                    px[xx, roof_y + dy] = edge_color

        # Crisp windows — even grid, sharp rectangles
        win_start_y = H - bh + 8
        for wy in range(win_start_y, H - 12, 12):
            for wx in range(bx + 6, bx + bw - 8, 12):
                if random.random() < 0.45:
                    wtype = random.random()
                    if wtype < 0.4:
                        wc = (200, 180, 90, 220)    # Warm yellow
                    elif wtype < 0.7:
                        wc = (90, 140, 200, 200)    # Cool blue
                    elif wtype < 0.85:
                        wc = (220, 60, 180, 220)    # Neon magenta
                    else:
                        wc = (60, 220, 200, 220)    # Teal
                    # Sharp 4x5 window
                    for dy in range(5):
                        for dx in range(4):
                            nx, ny = wx + dx, wy + dy
                            if 0 <= nx < W and 0 <= ny < H:
                                px[nx, ny] = wc
                    # Window frame (1px border)
                    for dx in range(-1, 5):
                        for ny in [wy - 1, wy + 5]:
                            nx = wx + dx
                            if 0 <= nx < W and 0 <= ny < H:
                                px[nx, ny] = edge_color
                    for dy in range(-1, 6):
                        for nx in [wx - 1, wx + 4]:
                            ny = wy + dy
                            if 0 <= nx < W and 0 <= ny < H:
                                px[nx, ny] = edge_color

    # --- Disco club tables at ground level ---
    # These sit in front of the buildings in the lower portion of the image
    # Representing a disco nightclub patio/interior visible through windows

    table_positions = [
        (30, 310), (100, 315), (180, 308), (260, 312),
        (340, 310), (430, 315), (510, 308), (580, 312),
    ]

    for tx, ty in table_positions:
        # Table top — circular/oval (dark wood with gold trim)
        table_w = random.randint(28, 40)
        table_h = 6

        # Table surface (dark wood)
        wood = (60, 35, 20, 255)
        wood_hi = (80, 50, 30, 255)
        wood_edge = (45, 25, 15, 255)
        gold_trim = (180, 150, 40, 255)

        # Table top
        draw_rect(px, tx, ty, tx + table_w, ty + table_h, wood, W, H)
        # Top edge highlight
        draw_rect(px, tx + 1, ty, tx + table_w - 1, ty + 1, wood_hi, W, H)
        # Gold trim on edge
        draw_rect(px, tx, ty + table_h, tx + table_w, ty + table_h, gold_trim, W, H)
        # Bottom shadow
        draw_rect(px, tx + 2, ty + table_h + 1, tx + table_w - 2, ty + table_h + 1, wood_edge, W, H)

        # Table leg (center, thin)
        leg_x = tx + table_w // 2
        for y in range(ty + table_h + 1, min(ty + table_h + 18, H)):
            if 0 <= leg_x < W and 0 <= y < H:
                px[leg_x, y] = wood_edge
            if 0 <= leg_x + 1 < W and 0 <= y < H:
                px[leg_x + 1, y] = wood_edge

        # Table base (wider foot)
        base_y = min(ty + table_h + 17, H - 1)
        draw_rect(px, leg_x - 4, base_y, leg_x + 5, base_y + 1, wood_edge, W, H)

        # --- Items on table ---
        # Drinks/glasses
        for i in range(random.randint(1, 3)):
            gx = tx + random.randint(3, table_w - 5)
            # Glass (small bright rectangle)
            glass_colors = [
                (255, 100, 180, 200),  # Pink cocktail
                (100, 200, 255, 200),  # Blue drink
                (255, 200, 50, 200),   # Gold drink
                (200, 255, 200, 200),  # Green drink
            ]
            gc = random.choice(glass_colors)
            # Glass body
            for dy in range(-4, 0):
                for dx in range(2):
                    nx, ny = gx + dx, ty + dy
                    if 0 <= nx < W and 0 <= ny < H:
                        px[nx, ny] = gc
            # Glass rim
            if 0 <= gx < W and 0 <= ty - 4 < H:
                px[gx, ty - 4] = (255, 255, 255, 180)
            if 0 <= gx + 1 < W and 0 <= ty - 4 < H:
                px[gx + 1, ty - 4] = (255, 255, 255, 180)

        # --- Chairs (on each side) ---
        chair_dk = (40, 25, 15, 255)
        chair_seat = (55, 32, 20, 255)

        # Left chair
        cx_l = tx - 8
        chair_y = ty + 2
        # Seat
        draw_rect(px, cx_l, chair_y, cx_l + 8, chair_y + 3, chair_seat, W, H)
        # Back rest
        draw_rect(px, cx_l, chair_y - 8, cx_l + 1, chair_y, chair_dk, W, H)
        # Legs
        for ly in range(chair_y + 4, min(chair_y + 14, H)):
            if 0 <= cx_l < W and 0 <= ly < H:
                px[cx_l, ly] = chair_dk
            if 0 <= cx_l + 7 < W and 0 <= ly < H:
                px[cx_l + 7, ly] = chair_dk

        # Right chair
        cx_r = tx + table_w + 2
        draw_rect(px, cx_r, chair_y, cx_r + 8, chair_y + 3, chair_seat, W, H)
        # Back rest
        draw_rect(px, cx_r + 7, chair_y - 8, cx_r + 8, chair_y, chair_dk, W, H)
        # Legs
        for ly in range(chair_y + 4, min(chair_y + 14, H)):
            if 0 <= cx_r < W and 0 <= ly < H:
                px[cx_r, ly] = chair_dk
            if 0 <= cx_r + 7 < W and 0 <= ly < H:
                px[cx_r + 7, ly] = chair_dk

        # --- Person silhouette at table (some tables) ---
        if random.random() < 0.6:
            # Simple silhouette sitting at the table
            px_side = random.choice([-1, 1])
            person_x = tx + (table_w + 6 if px_side > 0 else -6)
            person_y = ty - 4

            # Head (circle, 4px diameter)
            skin = (45, 30, 20, 230)
            for dy in range(-2, 2):
                for dx in range(-2, 2):
                    if dx * dx + dy * dy <= 4:
                        nx, ny = person_x + dx, person_y - 10 + dy
                        if 0 <= nx < W and 0 <= ny < H:
                            px[nx, ny] = skin

            # Body (seated torso)
            body_c = random.choice([
                (180, 50, 160, 220),  # Magenta shirt
                (50, 160, 200, 220),  # Blue shirt
                (200, 180, 50, 220),  # Gold shirt
                (255, 255, 255, 200), # White shirt
            ])
            for dy in range(-6, 0):
                for dx in range(-2, 3):
                    nx, ny = person_x + dx, person_y + dy
                    if 0 <= nx < W and 0 <= ny < H:
                        px[nx, ny] = body_c

    # --- Neon signs (crisper, brighter) ---
    neon_signs = [
        (70, 200, "DISCO", (255, 50, 200, 255)),     # Magenta
        (240, 180, "CLUB", (50, 220, 255, 255)),      # Cyan
        (420, 195, "BAR", (255, 200, 50, 255)),        # Gold
        (560, 210, "LIVE", (50, 255, 120, 255)),       # Green
    ]

    for sx, sy, text, neon_c in neon_signs:
        # Each letter is 3px wide, 5px tall, 1px spacing
        letter_w = 3
        total_w = len(text) * (letter_w + 1) - 1

        # Glow behind sign
        glow_r, glow_g, glow_b, _ = neon_c
        for dy in range(-2, 8):
            for dx in range(-2, total_w + 2):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < W and 0 <= ny < H:
                    r0, g0, b0, a0 = px[nx, ny]
                    if a0 > 0:
                        px[nx, ny] = (
                            min(255, r0 + glow_r // 6),
                            min(255, g0 + glow_g // 6),
                            min(255, b0 + glow_b // 6), 255)

        # Simple block letters (each letter is a 3x5 bitmap)
        letter_bitmaps = {
            'D': [(0,0),(0,1),(0,2),(0,3),(0,4),(1,0),(1,4),(2,1),(2,2),(2,3)],
            'I': [(0,0),(1,0),(2,0),(1,1),(1,2),(1,3),(0,4),(1,4),(2,4)],
            'S': [(0,0),(1,0),(2,0),(0,1),(0,2),(1,2),(2,2),(2,3),(0,4),(1,4),(2,4)],
            'C': [(0,0),(1,0),(2,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4)],
            'O': [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(1,4),(2,4)],
            'L': [(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4)],
            'U': [(0,0),(2,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(1,4),(2,4)],
            'B': [(0,0),(1,0),(0,1),(2,1),(0,2),(1,2),(0,3),(2,3),(0,4),(1,4)],
            'A': [(1,0),(0,1),(2,1),(0,2),(1,2),(2,2),(0,3),(2,3),(0,4),(2,4)],
            'R': [(0,0),(1,0),(0,1),(2,1),(0,2),(1,2),(0,3),(2,3),(0,4),(2,4)],
            'V': [(0,0),(2,0),(0,1),(2,1),(0,2),(2,2),(1,3),(1,4)],
            'E': [(0,0),(1,0),(2,0),(0,1),(0,2),(1,2),(0,3),(0,4),(1,4),(2,4)],
        }

        for ci, ch in enumerate(text):
            offset_x = sx + ci * (letter_w + 1)
            bitmap = letter_bitmaps.get(ch, [])
            for dx, dy in bitmap:
                nx, ny = offset_x + dx, sy + dy
                if 0 <= nx < W and 0 <= ny < H:
                    px[nx, ny] = neon_c

    # --- Disco ball hanging from a rooftop ---
    db_x, db_y = 350, 140
    # String
    for y in range(db_y - 15, db_y):
        if 0 <= y < H and 0 <= db_x < W:
            px[db_x, y] = (100, 100, 100, 200)
    # Ball (larger, crisper)
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            if dx ** 2 + dy ** 2 <= 25:
                nx, ny = db_x + dx, db_y + dy
                if 0 <= nx < W and 0 <= ny < H:
                    if (dx + dy) % 2 == 0:
                        px[nx, ny] = (210, 210, 230, 255)
                    else:
                        px[nx, ny] = (160, 160, 180, 255)
    # Sparkle rays
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        for dist in range(6, 10):
            nx = int(db_x + dist * math.cos(rad))
            ny = int(db_y + dist * math.sin(rad))
            if 0 <= nx < W and 0 <= ny < H:
                a = 200 - (dist - 6) * 40
                px[nx, ny] = (255, 255, 255, max(a, 60))

    save(img, ENV_DIR, 'parallax_city_near.png')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ensure_dirs()

    print("=== Generating Gun Sprite ===")
    create_gun()

    print("\n=== Generating Updated Near Parallax (with tables) ===")
    create_parallax_city_near()

    print("\nDone!")


if __name__ == '__main__':
    main()
