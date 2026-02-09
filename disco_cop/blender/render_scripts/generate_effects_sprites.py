"""
Generate pixel-art effect sprite sheets using Pillow.
These are small animated effects too tiny/abstract for Blender.

Run via: python generate_effects_sprites.py

Outputs (horizontal strip sheets):
  assets/sprites/weapons/muzzle_flash_sheet.png  (16x16, 3 frames)
  assets/sprites/weapons/impact_sheet.png         (16x16, 4 frames)
  assets/sprites/effects/explosion_sheet.png      (32x32, 6 frames)
  assets/sprites/effects/shield_break_sheet.png   (32x32, 4 frames)
  assets/sprites/effects/loot_glow_sheet.png      (24x24, 4 frames)
"""

import math
import os
from PIL import Image, ImageDraw

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))
WEAPONS_DIR = os.path.join(BASE_DIR, 'assets', 'sprites', 'weapons')
EFFECTS_DIR = os.path.join(BASE_DIR, 'assets', 'sprites', 'effects')


def ensure_dirs():
    os.makedirs(WEAPONS_DIR, exist_ok=True)
    os.makedirs(EFFECTS_DIR, exist_ok=True)


def save(img, directory, name):
    path = os.path.join(directory, name)
    img.save(path)
    print(f"  Saved: {path}")


def draw_circle(px, cx, cy, r, color, w, h):
    """Draw a filled circle with bounds checking."""
    for y in range(max(0, cy - r), min(h, cy + r + 1)):
        for x in range(max(0, cx - r), min(w, cx + r + 1)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                px[x, y] = color


def blend_pixel(px, x, y, color, w, h):
    """Alpha-blend a color onto existing pixel."""
    if 0 <= x < w and 0 <= y < h:
        r2, g2, b2, a2 = color
        r1, g1, b1, a1 = px[x, y]
        if a1 == 0:
            px[x, y] = color
        else:
            a_out = a2 + a1 * (255 - a2) // 255
            if a_out > 0:
                r = (r2 * a2 + r1 * a1 * (255 - a2) // 255) // a_out
                g = (g2 * a2 + g1 * a1 * (255 - a2) // 255) // a_out
                b = (b2 * a2 + b1 * a1 * (255 - a2) // 255) // a_out
                px[x, y] = (r, g, b, a_out)


def draw_ring(px, cx, cy, r, color, w, h):
    """Draw a 1px ring."""
    for angle in range(360):
        rad = math.radians(angle)
        x = int(cx + r * math.cos(rad))
        y = int(cy + r * math.sin(rad))
        if 0 <= x < w and 0 <= y < h:
            px[x, y] = color


# ---------------------------------------------------------------------------
# Muzzle Flash — 16x16, 3 frames
# Disco theme: bright magenta-white star burst
# ---------------------------------------------------------------------------

def create_muzzle_flash():
    """3-frame muzzle flash: burst → expand → fade."""
    W, H, FRAMES = 16, 16, 3
    sheet = Image.new('RGBA', (W * FRAMES, H), (0, 0, 0, 0))

    for f in range(FRAMES):
        frame = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        px = frame.load()
        cx, cy = 7, 7

        if f == 0:  # Bright initial burst
            # Core white
            draw_circle(px, cx, cy, 3, (255, 255, 255, 255), W, H)
            # Inner glow — hot yellow
            draw_circle(px, cx, cy, 5, (255, 240, 150, 200), W, H)
            draw_circle(px, cx, cy, 3, (255, 255, 255, 255), W, H)
            # Rays (4 directions)
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                for i in range(4, 7):
                    a = 255 - (i - 4) * 60
                    blend_pixel(px, cx + dx * i, cy + dy * i,
                                (255, 220, 100, max(a, 60)), W, H)
            # Diagonal sparks
            for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                for i in range(3, 5):
                    blend_pixel(px, cx + dx * i, cy + dy * i,
                                (255, 200, 50, 150), W, H)

        elif f == 1:  # Expanding, slightly dimmer
            draw_circle(px, cx, cy, 4, (255, 220, 100, 180), W, H)
            draw_circle(px, cx, cy, 2, (255, 255, 200, 255), W, H)
            # Wider rays
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                for i in range(3, 8):
                    a = 200 - (i - 3) * 35
                    blend_pixel(px, cx + dx * i, cy + dy * i,
                                (255, 200, 80, max(a, 40)), W, H)

        else:  # Fading out
            draw_circle(px, cx, cy, 5, (255, 200, 80, 80), W, H)
            draw_circle(px, cx, cy, 2, (255, 240, 150, 140), W, H)

        sheet.paste(frame, (f * W, 0))

    save(sheet, WEAPONS_DIR, 'muzzle_flash_sheet.png')


# ---------------------------------------------------------------------------
# Bullet Impact — 16x16, 4 frames
# Spark burst on hit — gold/white sparks
# ---------------------------------------------------------------------------

def create_impact():
    """4-frame impact: sparks fly outward then fade."""
    W, H, FRAMES = 16, 16, 4
    sheet = Image.new('RGBA', (W * FRAMES, H), (0, 0, 0, 0))

    # Spark positions expand outward per frame
    spark_angles = [0, 45, 90, 135, 180, 225, 270, 315]

    for f in range(FRAMES):
        frame = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        px = frame.load()
        cx, cy = 7, 7
        t = f / 3.0  # 0.0 to 1.0

        # Central flash (bright early, fades)
        if f < 2:
            core_a = 255 - f * 80
            draw_circle(px, cx, cy, 2 - f, (255, 255, 200, core_a), W, H)

        # Spark particles flying outward
        for angle_deg in spark_angles:
            rad = math.radians(angle_deg)
            dist = 2 + f * 2
            sx = int(cx + dist * math.cos(rad))
            sy = int(cy + dist * math.sin(rad))
            alpha = int(255 * (1.0 - t * 0.8))
            color = (255, 230, 100, alpha) if angle_deg % 90 == 0 else (255, 200, 50, alpha)
            if 0 <= sx < W and 0 <= sy < H:
                px[sx, sy] = color
                # Sub-pixel trail behind spark
                tx = int(cx + (dist - 1) * math.cos(rad))
                ty = int(cy + (dist - 1) * math.sin(rad))
                if 0 <= tx < W and 0 <= ty < H:
                    px[tx, ty] = (255, 200, 80, alpha // 2)

        sheet.paste(frame, (f * W, 0))

    save(sheet, WEAPONS_DIR, 'impact_sheet.png')


# ---------------------------------------------------------------------------
# Explosion — 32x32, 6 frames
# Disco-themed: magenta/orange fireball expanding
# ---------------------------------------------------------------------------

def create_explosion():
    """6-frame explosion: flash → fireball → expand → smoke → dissipate → gone."""
    W, H, FRAMES = 32, 32, 6
    sheet = Image.new('RGBA', (W * FRAMES, H), (0, 0, 0, 0))
    cx, cy = 15, 15

    for f in range(FRAMES):
        frame = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        px = frame.load()

        if f == 0:  # Initial white flash
            draw_circle(px, cx, cy, 5, (255, 255, 255, 255), W, H)
            draw_circle(px, cx, cy, 8, (255, 200, 100, 180), W, H)
            draw_circle(px, cx, cy, 5, (255, 255, 255, 255), W, H)

        elif f == 1:  # Fireball — orange/magenta
            draw_circle(px, cx, cy, 10, (200, 60, 20, 200), W, H)
            draw_circle(px, cx, cy, 7, (255, 140, 30, 240), W, H)
            draw_circle(px, cx, cy, 4, (255, 220, 100, 255), W, H)
            draw_circle(px, cx, cy, 2, (255, 255, 200, 255), W, H)

        elif f == 2:  # Expanding fireball
            draw_circle(px, cx, cy, 13, (180, 40, 60, 160), W, H)
            draw_circle(px, cx, cy, 10, (220, 100, 30, 200), W, H)
            draw_circle(px, cx, cy, 6, (255, 180, 60, 230), W, H)
            draw_circle(px, cx, cy, 3, (255, 240, 150, 255), W, H)

        elif f == 3:  # Peak — large, starting to smoke
            draw_circle(px, cx, cy, 14, (100, 30, 40, 120), W, H)
            draw_circle(px, cx, cy, 11, (180, 60, 30, 160), W, H)
            draw_circle(px, cx, cy, 7, (220, 120, 40, 180), W, H)
            draw_circle(px, cx, cy, 3, (255, 200, 100, 200), W, H)

        elif f == 4:  # Smoke phase
            draw_circle(px, cx, cy, 14, (60, 20, 30, 80), W, H)
            draw_circle(px, cx, cy, 10, (100, 40, 30, 120), W, H)
            draw_circle(px, cx, cy, 5, (160, 80, 40, 140), W, H)

        else:  # Dissipating
            draw_circle(px, cx, cy, 12, (40, 15, 20, 40), W, H)
            draw_circle(px, cx, cy, 6, (80, 30, 25, 60), W, H)

        sheet.paste(frame, (f * W, 0))

    save(sheet, EFFECTS_DIR, 'explosion_sheet.png')


# ---------------------------------------------------------------------------
# Shield Break — 32x32, 4 frames
# Cyan shield shattering into fragments
# ---------------------------------------------------------------------------

def create_shield_break():
    """4-frame shield break: intact flash → crack → shatter → fragments fly."""
    W, H, FRAMES = 32, 32, 4
    sheet = Image.new('RGBA', (W * FRAMES, H), (0, 0, 0, 0))
    cx, cy = 15, 15

    for f in range(FRAMES):
        frame = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        px = frame.load()

        if f == 0:  # Shield intact, bright flash
            # Shield dome shape — half circle on right
            draw_ring(px, cx, cy, 10, (100, 220, 255, 255), W, H)
            draw_ring(px, cx, cy, 9, (150, 240, 255, 200), W, H)
            draw_ring(px, cx, cy, 11, (80, 200, 255, 180), W, H)
            # Interior glow
            draw_circle(px, cx, cy, 8, (100, 200, 255, 60), W, H)
            # Flash at center
            draw_circle(px, cx, cy, 3, (255, 255, 255, 200), W, H)

        elif f == 1:  # Cracks forming
            draw_ring(px, cx, cy, 10, (100, 220, 255, 200), W, H)
            draw_ring(px, cx, cy, 9, (150, 240, 255, 160), W, H)
            # Crack lines radiating from center
            for angle_deg in [30, 110, 200, 290, 350]:
                rad = math.radians(angle_deg)
                for i in range(2, 11):
                    x = int(cx + i * math.cos(rad))
                    y = int(cy + i * math.sin(rad))
                    if 0 <= x < W and 0 <= y < H:
                        px[x, y] = (255, 255, 255, 220)

        elif f == 2:  # Shattering — fragments separating
            # Draw fragments as small triangular shards flying outward
            shard_angles = [20, 70, 130, 190, 250, 320]
            for angle_deg in shard_angles:
                rad = math.radians(angle_deg)
                dist = 8
                sx = int(cx + dist * math.cos(rad))
                sy = int(cy + dist * math.sin(rad))
                # Each shard is a small 3x3 cluster
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if abs(dx) + abs(dy) <= 1:
                            nx, ny = sx + dx, sy + dy
                            if 0 <= nx < W and 0 <= ny < H:
                                px[nx, ny] = (120, 220, 255, 200)
            # Central flash dissipating
            draw_circle(px, cx, cy, 4, (200, 240, 255, 100), W, H)

        else:  # Fragments flying away, fading
            shard_angles = [20, 70, 130, 190, 250, 320]
            for angle_deg in shard_angles:
                rad = math.radians(angle_deg)
                dist = 13
                sx = int(cx + dist * math.cos(rad))
                sy = int(cy + dist * math.sin(rad))
                if 0 <= sx < W and 0 <= sy < H:
                    px[sx, sy] = (100, 200, 255, 120)
                    # Trail
                    tx = int(cx + (dist - 2) * math.cos(rad))
                    ty = int(cy + (dist - 2) * math.sin(rad))
                    if 0 <= tx < W and 0 <= ty < H:
                        px[tx, ty] = (80, 180, 255, 60)

        sheet.paste(frame, (f * W, 0))

    save(sheet, EFFECTS_DIR, 'shield_break_sheet.png')


# ---------------------------------------------------------------------------
# Loot Glow — 24x24, 4 frames
# Pulsing golden glow around loot drops
# ---------------------------------------------------------------------------

def create_loot_glow():
    """4-frame loot glow: pulsing golden aura."""
    W, H, FRAMES = 24, 24, 4
    sheet = Image.new('RGBA', (W * FRAMES, H), (0, 0, 0, 0))
    cx, cy = 11, 11

    for f in range(FRAMES):
        frame = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        px = frame.load()

        # Pulsing radius and alpha
        pulse = [0.8, 1.0, 1.2, 1.0][f]
        alpha_mul = [0.6, 1.0, 0.8, 0.9][f]

        # Outer glow ring
        r_outer = int(10 * pulse)
        a_outer = int(40 * alpha_mul)
        draw_circle(px, cx, cy, r_outer, (255, 200, 50, a_outer), W, H)

        # Mid glow
        r_mid = int(7 * pulse)
        a_mid = int(80 * alpha_mul)
        draw_circle(px, cx, cy, r_mid, (255, 220, 80, a_mid), W, H)

        # Inner bright
        r_inner = int(4 * pulse)
        a_inner = int(120 * alpha_mul)
        draw_circle(px, cx, cy, r_inner, (255, 240, 150, a_inner), W, H)

        # Sparkle points (rotate with frame)
        base_angle = f * 22.5
        for i in range(4):
            angle_deg = base_angle + i * 90
            rad = math.radians(angle_deg)
            dist = int(8 * pulse)
            sx = int(cx + dist * math.cos(rad))
            sy = int(cy + dist * math.sin(rad))
            if 0 <= sx < W and 0 <= sy < H:
                px[sx, sy] = (255, 255, 200, int(200 * alpha_mul))

        sheet.paste(frame, (f * W, 0))

    save(sheet, EFFECTS_DIR, 'loot_glow_sheet.png')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ensure_dirs()

    print("=== Generating Effect Sprite Sheets ===")
    create_muzzle_flash()
    create_impact()
    create_explosion()
    create_shield_break()
    create_loot_glow()

    print("\nDone! 5 effect sheets generated.")


if __name__ == '__main__':
    main()
