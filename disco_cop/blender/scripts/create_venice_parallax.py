#!/usr/bin/env python3
"""Generate Venice Beach parallax backgrounds for Disco Cop Level 02.

Creates 3 parallax layers at 640x360:
  - parallax_venice_sky.png   (far)  — sunset sky, ocean horizon, distant pier
  - parallax_venice_mid.png   (mid)  — palm trees, boardwalk shops, Muscle Beach sign
  - parallax_venice_near.png  (near) — weight benches, volleyball net, lifeguard tower

Usage:
    python create_venice_parallax.py
"""

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "environment"

W, H = 640, 360
random.seed(202)

# Venice Palette
SKY_TOP = (255, 140, 50)       # Sunset orange
SKY_MID = (255, 180, 100)      # Golden
SKY_LOW = (255, 210, 160)      # Pale horizon
OCEAN_FAR = (40, 100, 140)
OCEAN_NEAR = (30, 80, 120)
OCEAN_HIGHLIGHT = (80, 160, 200)
SUN_COLOR = (255, 220, 100)
PALM_TRUNK = (100, 70, 40)
PALM_TRUNK_LIGHT = (130, 95, 55)
PALM_LEAF = (40, 120, 50)
PALM_LEAF_LIGHT = (70, 160, 70)
PALM_LEAF_DARK = (25, 80, 35)
SHOP_COLORS = [(180, 60, 60), (60, 120, 180), (180, 160, 50), (60, 160, 100), (160, 80, 140)]
BOARDWALK_COLOR = (180, 155, 120)
SAND_COLOR = (235, 210, 165)
CONCRETE_COLOR = (170, 170, 165)
METAL_GRAY = (140, 140, 150)
METAL_LIGHT = (190, 190, 200)
WOOD_BROWN = (140, 100, 60)
RED_FLAG = (220, 40, 40)
WHITE = (255, 255, 255)
NEON_PINK = (255, 80, 150)
NEON_CYAN = (0, 220, 220)


def draw_palm_tree(img, x, ground_y, height, lean=0):
    """Draw a palm tree with trunk and fronds."""
    d = ImageDraw.Draw(img)
    # Trunk (slightly curved)
    for i in range(height):
        t = i / height
        tx = x + int(lean * t * t)
        ty = ground_y - i
        width = max(1, int(4 * (1 - t * 0.5)))
        trunk_c = PALM_TRUNK if i % 6 < 3 else PALM_TRUNK_LIGHT
        d.rectangle([tx - width // 2, ty, tx + width // 2, ty + 1], fill=trunk_c)

    # Frond crown at top
    top_x = x + int(lean)
    top_y = ground_y - height
    for angle_deg in range(0, 360, 30):
        angle = math.radians(angle_deg)
        frond_len = random.randint(20, 35)
        droop = 0.4  # Fronds droop
        for j in range(frond_len):
            t = j / frond_len
            fx = top_x + int(j * math.cos(angle))
            fy = top_y + int(j * math.sin(angle) + j * droop * t)
            if 0 <= fx < W and 0 <= fy < H:
                leaf_c = PALM_LEAF if t < 0.6 else PALM_LEAF_DARK
                if random.random() < 0.3:
                    leaf_c = PALM_LEAF_LIGHT
                img.putpixel((fx, fy), (*leaf_c, 255))
                # Width of frond
                if t < 0.7:
                    for dy in [-1, 1]:
                        ny = fy + dy
                        if 0 <= ny < H:
                            img.putpixel((fx, ny), (*PALM_LEAF_DARK, 200))


def create_sky_layer():
    """Far: sunset sky, ocean horizon, distant pier, setting sun."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    horizon_y = 200

    # Sky gradient (sunset orange to golden)
    for y in range(horizon_y):
        t = y / horizon_y
        r = int(SKY_TOP[0] * (1 - t) + SKY_LOW[0] * t)
        g = int(SKY_TOP[1] * (1 - t) + SKY_LOW[1] * t)
        b = int(SKY_TOP[2] * (1 - t) + SKY_LOW[2] * t)
        d.line([0, y, W - 1, y], fill=(r, g, b, 255))

    # Sun (large, near horizon)
    sun_cx, sun_cy = 480, 160
    sun_r = 30
    for dy in range(-sun_r - 10, sun_r + 11):
        for dx in range(-sun_r - 10, sun_r + 11):
            dist = math.sqrt(dx * dx + dy * dy)
            px, py = sun_cx + dx, sun_cy + dy
            if 0 <= px < W and 0 <= py < horizon_y:
                if dist <= sun_r:
                    img.putpixel((px, py), (*SUN_COLOR, 255))
                elif dist <= sun_r + 8:
                    # Glow
                    falloff = 1.0 - (dist - sun_r) / 8.0
                    alpha = int(falloff * 150)
                    r0, g0, b0, _ = img.getpixel((px, py))
                    blend = alpha / 255.0
                    nr = min(int(r0 + SUN_COLOR[0] * blend * 0.5), 255)
                    ng = min(int(g0 + SUN_COLOR[1] * blend * 0.5), 255)
                    nb = min(int(b0 + SUN_COLOR[2] * blend * 0.3), 255)
                    img.putpixel((px, py), (nr, ng, nb, 255))

    # Ocean (below horizon)
    for y in range(horizon_y, H):
        t = (y - horizon_y) / (H - horizon_y)
        r = int(OCEAN_FAR[0] * (1 - t) + OCEAN_NEAR[0] * t)
        g = int(OCEAN_FAR[1] * (1 - t) + OCEAN_NEAR[1] * t)
        b = int(OCEAN_FAR[2] * (1 - t) + OCEAN_NEAR[2] * t)
        d.line([0, y, W - 1, y], fill=(r, g, b, 255))

    # Sun reflection on water
    for y in range(horizon_y, min(horizon_y + 80, H)):
        t = (y - horizon_y) / 80
        ref_w = int(15 * (1 + t * 3))
        cx = sun_cx + random.randint(-3, 3)
        alpha = int((1 - t) * 120)
        for dx in range(-ref_w, ref_w + 1):
            px = cx + dx
            if 0 <= px < W and random.random() < 0.5:
                r0, g0, b0, _ = img.getpixel((px, y))
                blend = alpha / 255.0
                nr = min(int(r0 + 200 * blend), 255)
                ng = min(int(g0 + 180 * blend), 255)
                nb = min(int(b0 + 80 * blend), 255)
                img.putpixel((px, y), (nr, ng, nb, 255))

    # Wave lines on ocean
    for wy in range(horizon_y + 5, H, 12):
        wx = random.randint(0, 50)
        wlen = random.randint(40, 120)
        d.line([wx, wy, wx + wlen, wy], fill=(*OCEAN_HIGHLIGHT, 80))

    # Distant pier silhouette
    pier_y = horizon_y + 10
    d.rectangle([50, pier_y, 200, pier_y + 3], fill=(60, 50, 45, 200))
    # Pier supports
    for px in range(60, 200, 25):
        d.line([px, pier_y + 3, px, pier_y + 20], fill=(50, 40, 35, 180))

    # Clouds
    for _ in range(4):
        cx = random.randint(30, W - 30)
        cy = random.randint(20, 100)
        for _ in range(8):
            bx = cx + random.randint(-25, 25)
            by = cy + random.randint(-6, 6)
            br = random.randint(8, 16)
            d.ellipse([bx - br, by - br // 2, bx + br, by + br // 2],
                      fill=(255, 240, 220, 60))

    out = OUTPUT_DIR / "parallax_venice_sky.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def create_mid_layer():
    """Mid: palm trees, boardwalk shop fronts, Muscle Beach sign."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    ground_y = 240

    # Palm trees (scattered, various heights)
    tree_positions = [40, 130, 280, 400, 530, 600]
    for tx in tree_positions:
        height = random.randint(100, 160)
        lean = random.randint(-10, 15)
        draw_palm_tree(img, tx, ground_y, height, lean)

    # Boardwalk shop fronts (lower area)
    shop_y = ground_y + 10
    shop_h = 60
    for sx in range(0, W, 80):
        color = random.choice(SHOP_COLORS)
        # Shop body
        d.rectangle([sx + 2, shop_y, sx + 76, shop_y + shop_h], fill=color)
        d.rectangle([sx + 2, shop_y, sx + 76, shop_y + shop_h], outline=(40, 30, 25))
        # Awning
        awning_c = tuple(min(c + 40, 255) for c in color)
        d.rectangle([sx, shop_y - 8, sx + 78, shop_y], fill=awning_c)
        # Awning stripes
        for stripe_x in range(sx, sx + 78, 8):
            d.rectangle([stripe_x, shop_y - 8, stripe_x + 3, shop_y], fill=WHITE)
        # Window/door
        d.rectangle([sx + 10, shop_y + 10, sx + 35, shop_y + 45], fill=(40, 60, 80))
        d.rectangle([sx + 42, shop_y + 10, sx + 67, shop_y + 45], fill=(40, 60, 80))
        # Window reflection
        d.rectangle([sx + 12, shop_y + 12, sx + 20, shop_y + 20], fill=(100, 140, 180, 100))

    # "MUSCLE BEACH" sign
    sign_x = 240
    sign_y = ground_y - 20
    d.rectangle([sign_x, sign_y, sign_x + 120, sign_y + 18], fill=(20, 10, 5))
    d.rectangle([sign_x + 1, sign_y + 1, sign_x + 119, sign_y + 17], outline=NEON_PINK)
    # Text blocks
    for i, lx in enumerate(range(sign_x + 8, sign_x + 110, 9)):
        d.rectangle([lx, sign_y + 4, lx + 6, sign_y + 14], fill=NEON_PINK)
    # Sign posts
    d.rectangle([sign_x + 10, sign_y + 18, sign_x + 13, ground_y], fill=METAL_GRAY)
    d.rectangle([sign_x + 106, sign_y + 18, sign_x + 109, ground_y], fill=METAL_GRAY)

    out = OUTPUT_DIR / "parallax_venice_mid.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def create_near_layer():
    """Near: weight benches, dumbbells, volleyball net, lifeguard tower."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    ground_y = 290

    # ── Weight bench (left area) ──
    bench_x = 40
    bench_y = ground_y - 20
    # Bench frame (metal)
    d.rectangle([bench_x, bench_y, bench_x + 60, bench_y + 8], fill=METAL_GRAY)
    d.rectangle([bench_x, bench_y, bench_x + 60, bench_y + 8], outline=METAL_LIGHT)
    # Bench pad
    d.rectangle([bench_x + 5, bench_y - 4, bench_x + 55, bench_y], fill=(40, 40, 40))
    # Bench legs
    d.rectangle([bench_x + 5, bench_y + 8, bench_x + 8, ground_y], fill=METAL_GRAY)
    d.rectangle([bench_x + 52, bench_y + 8, bench_x + 55, ground_y], fill=METAL_GRAY)
    # Barbell rack
    d.rectangle([bench_x + 15, bench_y - 25, bench_x + 18, bench_y - 4], fill=METAL_GRAY)
    d.rectangle([bench_x + 42, bench_y - 25, bench_x + 45, bench_y - 4], fill=METAL_GRAY)
    # Barbell
    d.line([bench_x + 8, bench_y - 22, bench_x + 52, bench_y - 22], fill=METAL_LIGHT)
    # Weight plates
    for wx in [bench_x + 8, bench_x + 48]:
        d.rectangle([wx, bench_y - 28, wx + 4, bench_y - 16], fill=(50, 50, 55))

    # ── Dumbbells on ground ──
    for dx in [130, 155]:
        dy = ground_y - 6
        d.rectangle([dx, dy, dx + 16, dy + 4], fill=METAL_GRAY)
        d.rectangle([dx - 2, dy - 2, dx + 2, dy + 6], fill=(50, 50, 55))
        d.rectangle([dx + 14, dy - 2, dx + 18, dy + 6], fill=(50, 50, 55))

    # ── Volleyball net (center) ──
    net_x1, net_x2 = 260, 380
    net_top = ground_y - 60
    net_bot = ground_y - 10
    # Poles
    d.rectangle([net_x1 - 2, net_top - 5, net_x1 + 2, ground_y], fill=METAL_GRAY)
    d.rectangle([net_x2 - 2, net_top - 5, net_x2 + 2, ground_y], fill=METAL_GRAY)
    # Net (horizontal lines)
    for ny in range(net_top, net_bot, 6):
        d.line([net_x1, ny, net_x2, ny], fill=(*WHITE, 150))
    # Net (vertical lines)
    for nx in range(net_x1, net_x2 + 1, 8):
        d.line([nx, net_top, nx, net_bot], fill=(*WHITE, 100))
    # Top rope
    d.line([net_x1, net_top, net_x2, net_top], fill=WHITE)

    # ── Lifeguard tower (right) ──
    tower_x = 500
    tower_y = ground_y - 70
    tower_w = 50
    tower_h = 40
    # Tower legs (angled)
    d.line([tower_x + 5, tower_y + tower_h, tower_x - 5, ground_y], fill=WOOD_BROWN, width=3)
    d.line([tower_x + tower_w - 5, tower_y + tower_h, tower_x + tower_w + 5, ground_y],
           fill=WOOD_BROWN, width=3)
    # Platform
    d.rectangle([tower_x - 3, tower_y + tower_h - 3, tower_x + tower_w + 3, tower_y + tower_h],
                fill=WOOD_BROWN)
    # Cabin
    d.rectangle([tower_x, tower_y, tower_x + tower_w, tower_y + tower_h], fill=(220, 220, 210))
    d.rectangle([tower_x, tower_y, tower_x + tower_w, tower_y + tower_h], outline=WOOD_BROWN)
    # Roof
    d.polygon([(tower_x - 5, tower_y), (tower_x + tower_w + 5, tower_y),
               (tower_x + tower_w // 2, tower_y - 12)], fill=RED_FLAG)
    # Window
    d.rectangle([tower_x + 8, tower_y + 8, tower_x + tower_w - 8, tower_y + tower_h - 8],
                fill=(100, 160, 200))
    # Flag
    flag_x = tower_x + tower_w + 5
    d.line([flag_x, tower_y - 12, flag_x, tower_y - 35], fill=WOOD_BROWN)
    d.rectangle([flag_x + 1, tower_y - 35, flag_x + 15, tower_y - 25], fill=RED_FLAG)

    # ── Sand floor ──
    d.rectangle([0, ground_y, W - 1, H - 1], fill=SAND_COLOR)
    for _ in range(100):
        x = random.randint(0, W - 1)
        y = random.randint(ground_y, H - 1)
        c = random.choice([(215, 190, 145), (225, 200, 155)])
        img.putpixel((x, y), (*c, 255))

    out = OUTPUT_DIR / "parallax_venice_near.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def main():
    print("Generating Venice Beach parallax layers...")
    create_sky_layer()
    create_mid_layer()
    create_near_layer()
    print("Done!")


if __name__ == "__main__":
    main()
