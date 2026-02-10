#!/usr/bin/env python3
"""Generate rink-specific parallax backgrounds for Disco Cop Level 01.

Creates 3 parallax layers at 640x360 matching the existing format:
  - parallax_rink_ceiling.png (far)  — dark ceiling, disco ball, colored glow spots
  - parallax_rink_mid.png    (mid)  — bleachers, neon exit signs, spectator silhouettes
  - parallax_rink_near.png   (near) — shoe counter, arcade machines, rink rail detail

Usage:
    python create_rink_parallax.py

Output: disco_cop/assets/sprites/environment/
"""

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "environment"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 640, 360
random.seed(77)

# ── Rink Palette ──────────────────────────────────────────────────────
CEILING_DARK = (12, 6, 24)
CEILING_MID = (20, 10, 35)
RAFTER_COLOR = (35, 20, 55)
RAFTER_LIGHT = (50, 30, 70)
WALL_DARK = (26, 10, 46)
WALL_MID = (40, 18, 65)
BLEACHER_DARK = (30, 15, 50)
BLEACHER_MID = (50, 25, 75)
BLEACHER_LIGHT = (65, 35, 90)
NEON_PINK = (255, 105, 180)
NEON_CYAN = (0, 255, 255)
NEON_GOLD = (255, 215, 0)
NEON_WHITE = (240, 240, 255)
DISCO_COLORS = [
    (255, 20, 147),   # Magenta
    (0, 255, 255),    # Cyan
    (255, 215, 0),    # Gold
    (255, 255, 255),  # White
    (147, 112, 219),  # Medium purple
    (255, 105, 180),  # Hot pink
]
CHROME = (192, 192, 192)
CHROME_LIGHT = (230, 230, 240)
WOOD_BASE = (140, 90, 51)
WOOD_DARK = (100, 65, 35)
CARPET_BASE = (74, 14, 78)
GREEN_EXIT = (0, 200, 0)
SKIN_TONE = (140, 95, 65)
SKIN_DARK = (100, 65, 45)


def draw_glow(img: Image.Image, cx: int, cy: int, radius: int, color: tuple, intensity: float = 0.6):
    """Draw a soft circular glow at (cx, cy)."""
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= radius:
                px, py = cx + dx, cy + dy
                if 0 <= px < W and 0 <= py < H:
                    falloff = 1.0 - (dist / radius)
                    alpha = int(falloff * falloff * intensity * 255)
                    r0, g0, b0, a0 = img.getpixel((px, py))
                    blend = alpha / 255.0
                    r = min(int(r0 + color[0] * blend), 255)
                    g = min(int(g0 + color[1] * blend), 255)
                    b = min(int(b0 + color[2] * blend), 255)
                    img.putpixel((px, py), (r, g, b, max(a0, alpha)))


def create_ceiling_layer():
    """Far parallax: dark ceiling with disco ball and colored glow spots."""
    img = Image.new("RGBA", (W, H), (*CEILING_DARK, 255))
    d = ImageDraw.Draw(img)

    # Gradient: slightly lighter at bottom (ambient rink light)
    for y in range(H):
        t = y / H
        r = int(CEILING_DARK[0] + (CEILING_MID[0] - CEILING_DARK[0]) * t * 0.5)
        g = int(CEILING_DARK[1] + (CEILING_MID[1] - CEILING_DARK[1]) * t * 0.5)
        b = int(CEILING_DARK[2] + (CEILING_MID[2] - CEILING_DARK[2]) * t * 0.5)
        d.line([0, y, W - 1, y], fill=(r, g, b, 255))

    # Ceiling rafters/beams (horizontal structural lines)
    for y in [40, 80, 120]:
        d.rectangle([0, y, W - 1, y + 4], fill=RAFTER_COLOR)
        d.line([0, y, W - 1, y], fill=RAFTER_LIGHT)

    # Vertical support beams
    for x in [100, 320, 540]:
        d.rectangle([x, 0, x + 6, 140], fill=RAFTER_COLOR)
        d.line([x, 0, x, 140], fill=RAFTER_LIGHT)

    # ── Disco ball (center-ish, hanging from ceiling) ──
    ball_cx, ball_cy = 320, 65
    ball_r = 20

    # Mounting rod
    d.rectangle([ball_cx - 1, 0, ball_cx + 1, ball_cy - ball_r], fill=CHROME)

    # Ball body
    d.ellipse([ball_cx - ball_r, ball_cy - ball_r,
               ball_cx + ball_r, ball_cy + ball_r], fill=(160, 160, 170))

    # Mirror facets (grid of shiny squares)
    for angle_deg in range(0, 360, 20):
        for ring in range(3, ball_r - 2, 5):
            fx = ball_cx + int(ring * math.cos(math.radians(angle_deg)))
            fy = ball_cy + int(ring * math.sin(math.radians(angle_deg)))
            # Check if inside ball
            if (fx - ball_cx) ** 2 + (fy - ball_cy) ** 2 < ball_r ** 2:
                color = random.choice([(220, 220, 230), (255, 255, 255), (200, 200, 210)])
                d.rectangle([fx - 1, fy - 1, fx + 1, fy + 1], fill=color)

    # Ball highlight
    d.ellipse([ball_cx - 8, ball_cy - 10, ball_cx, ball_cy - 4], fill=(230, 230, 240, 180))

    # ── Disco glow spots scattered across ceiling and upper walls ──
    glow_positions = []
    for _ in range(25):
        gx = random.randint(20, W - 20)
        gy = random.randint(130, H - 40)
        color = random.choice(DISCO_COLORS)
        radius = random.randint(12, 30)
        intensity = random.uniform(0.15, 0.35)
        glow_positions.append((gx, gy, radius, color, intensity))

    for gx, gy, radius, color, intensity in glow_positions:
        draw_glow(img, gx, gy, radius, color, intensity)

    # Light beams radiating from disco ball (thin lines with color)
    for i in range(12):
        angle = math.radians(i * 30 + 15)
        length = random.randint(80, 200)
        ex = ball_cx + int(length * math.cos(angle))
        ey = ball_cy + int(length * math.sin(angle))
        if ey > ball_cy:  # Only beams going downward
            color = random.choice(DISCO_COLORS)
            # Faint beam line
            d.line([ball_cx, ball_cy + ball_r, ex, ey],
                   fill=(*color[:3], 40), width=1)

    out = OUTPUT_DIR / "parallax_rink_ceiling.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def create_mid_layer():
    """Mid parallax: bleachers with spectator silhouettes, neon exit signs."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # ── Bleachers along the top 40% ──
    bleacher_top = 20
    bleacher_bot = 160
    num_rows = 5
    row_h = (bleacher_bot - bleacher_top) // num_rows

    for row in range(num_rows):
        y = bleacher_top + row * row_h
        # Each row is a step: lighter at front (bottom), darker at back (top)
        shade = BLEACHER_DARK if row < 2 else BLEACHER_MID if row < 4 else BLEACHER_LIGHT
        d.rectangle([0, y, W - 1, y + row_h - 2], fill=shade)
        # Seat edge highlight
        d.line([0, y + row_h - 2, W - 1, y + row_h - 2], fill=BLEACHER_LIGHT)

        # Spectator silhouettes (more in front rows)
        num_spectators = 8 + (num_rows - row) * 3
        for _ in range(num_spectators):
            sx = random.randint(10, W - 10)
            sy = y + 2
            # Head
            head_color = random.choice([SKIN_TONE, SKIN_DARK, (80, 50, 35), (170, 130, 100)])
            d.ellipse([sx - 3, sy, sx + 3, sy + 5], fill=head_color)
            # Body
            body_color = random.choice([(60, 20, 80), (80, 30, 40), (30, 50, 80), (70, 60, 20)])
            d.rectangle([sx - 4, sy + 5, sx + 4, sy + row_h - 4], fill=body_color)

    # ── Rink wall section (below bleachers) ──
    wall_top = bleacher_bot
    wall_bot = 220
    d.rectangle([0, wall_top, W - 1, wall_bot], fill=WALL_DARK)

    # Wall panel outlines
    panel_w = 80
    for x in range(0, W, panel_w):
        d.rectangle([x + 1, wall_top + 2, x + panel_w - 2, wall_bot - 2], outline=WALL_MID)

    # Neon strip along wall top
    d.line([0, wall_top, W - 1, wall_top], fill=NEON_PINK)
    d.line([0, wall_top + 1, W - 1, wall_top + 1], fill=(180, 60, 120, 200))

    # ── Exit signs ──
    for ex in [80, 380, 560]:
        # Green EXIT sign
        d.rectangle([ex, wall_top + 8, ex + 30, wall_top + 18], fill=(0, 60, 0))
        d.rectangle([ex + 1, wall_top + 9, ex + 29, wall_top + 17], outline=GREEN_EXIT)
        # "EXIT" text (simplified as green dots in a row)
        for i, letter_x in enumerate(range(ex + 4, ex + 26, 6)):
            d.rectangle([letter_x, wall_top + 11, letter_x + 3, wall_top + 15], fill=GREEN_EXIT)

    # ── Scoreboard / clock ──
    sb_x, sb_y = 250, wall_top + 6
    d.rectangle([sb_x, sb_y, sb_x + 60, sb_y + 14], fill=(10, 5, 20))
    d.rectangle([sb_x, sb_y, sb_x + 60, sb_y + 14], outline=CHROME)
    # Score numbers (simplified as colored blocks)
    d.rectangle([sb_x + 5, sb_y + 3, sb_x + 25, sb_y + 11], fill=(200, 0, 0, 200))
    d.rectangle([sb_x + 35, sb_y + 3, sb_x + 55, sb_y + 11], fill=(0, 100, 200, 200))

    out = OUTPUT_DIR / "parallax_rink_mid.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def create_near_layer():
    """Near parallax: shoe counter, arcade machines, rink rail close-up."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # ── Rink rail / barrier in foreground (lower portion) ──
    rail_y = 280

    # Rail posts
    for x in range(20, W, 80):
        # Vertical post
        d.rectangle([x, rail_y - 40, x + 6, rail_y + 20], fill=CHROME)
        d.line([x, rail_y - 40, x, rail_y + 20], fill=CHROME_LIGHT)
        d.line([x + 6, rail_y - 40, x + 6, rail_y + 20], fill=(100, 100, 110))

    # Horizontal rails
    d.rectangle([0, rail_y - 30, W - 1, rail_y - 26], fill=CHROME)
    d.line([0, rail_y - 30, W - 1, rail_y - 30], fill=CHROME_LIGHT)
    d.rectangle([0, rail_y, W - 1, rail_y + 4], fill=CHROME)
    d.line([0, rail_y, W - 1, rail_y], fill=CHROME_LIGHT)

    # Neon strip under bottom rail
    d.line([0, rail_y + 6, W - 1, rail_y + 6], fill=NEON_CYAN)
    d.line([0, rail_y + 7, W - 1, rail_y + 7], fill=(0, 160, 180, 180))

    # ── Shoe rental counter (left side) ──
    counter_x = 30
    counter_y = rail_y + 20
    counter_w = 100
    counter_h = 50

    # Counter body
    d.rectangle([counter_x, counter_y, counter_x + counter_w, counter_y + counter_h],
                fill=WOOD_BASE)
    d.rectangle([counter_x, counter_y, counter_x + counter_w, counter_y + counter_h],
                outline=WOOD_DARK)
    # Counter top (lighter)
    d.rectangle([counter_x - 2, counter_y, counter_x + counter_w + 2, counter_y + 4],
                fill=(180, 120, 70))
    # Shoe cubbies (grid of dark rectangles)
    for row in range(2):
        for col in range(5):
            cx = counter_x + 6 + col * 19
            cy = counter_y + 10 + row * 18
            d.rectangle([cx, cy, cx + 15, cy + 14], fill=(60, 35, 20))
            # Shoe silhouette inside some cubbies
            if random.random() < 0.6:
                shoe_color = random.choice([(200, 50, 50), (50, 50, 200), (200, 200, 50), (255, 255, 255)])
                d.rectangle([cx + 3, cy + 6, cx + 12, cy + 12], fill=shoe_color)

    # "SHOES" sign above
    sign_x = counter_x + 15
    sign_y = counter_y - 16
    d.rectangle([sign_x, sign_y, sign_x + 70, sign_y + 14], fill=(10, 5, 20))
    d.rectangle([sign_x, sign_y, sign_x + 70, sign_y + 14], outline=NEON_PINK)
    # Simplified text (pixel blocks)
    for i, lx in enumerate(range(sign_x + 6, sign_x + 62, 12)):
        d.rectangle([lx, sign_y + 3, lx + 8, sign_y + 11], fill=NEON_PINK)

    # ── Arcade machines (right side) ──
    for i, ax in enumerate([420, 490, 560]):
        ay = rail_y + 15
        machine_h = 60
        # Cabinet body
        cab_color = random.choice([(60, 20, 80), (20, 50, 80), (80, 20, 40)])
        d.rectangle([ax, ay, ax + 40, ay + machine_h], fill=cab_color)
        d.rectangle([ax, ay, ax + 40, ay + machine_h], outline=(40, 15, 55))
        # Screen
        screen_color = random.choice([(0, 40, 60), (40, 0, 60), (0, 50, 30)])
        d.rectangle([ax + 4, ay + 4, ax + 36, ay + 24], fill=screen_color)
        # Screen content (random pixels = game graphics)
        for _ in range(15):
            px = random.randint(ax + 6, ax + 34)
            py = random.randint(ay + 6, ay + 22)
            pcolor = random.choice(DISCO_COLORS)
            img.putpixel((px, py), (*pcolor, 255))
        # Controls panel
        d.rectangle([ax + 4, ay + 28, ax + 36, ay + 38], fill=(30, 30, 30))
        # Joystick
        d.ellipse([ax + 8, ay + 30, ax + 14, ay + 36], fill=(200, 200, 200))
        # Buttons
        for bx in [ax + 20, ax + 27]:
            button_c = random.choice([NEON_PINK, NEON_CYAN, NEON_GOLD])
            d.ellipse([bx, ay + 31, bx + 5, ay + 35], fill=button_c)

    # ── Floor below rail (carpet / lobby transition) ──
    floor_y = rail_y + 50
    if floor_y < H:
        d.rectangle([0, floor_y, W - 1, H - 1], fill=CARPET_BASE)
        # Carpet pattern
        for y in range(floor_y, H):
            for x in range(0, W, 8):
                dx = (x % 16) - 8
                dy = ((y - floor_y) % 16) - 8
                if abs(dx) + abs(dy) <= 6:
                    d.point([x, y], fill=(95, 25, 100, 255))

    out = OUTPUT_DIR / "parallax_rink_near.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def main():
    print("Generating rink parallax layers...")
    create_ceiling_layer()
    create_mid_layer()
    create_near_layer()
    print("Done!")


if __name__ == "__main__":
    main()
