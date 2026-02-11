#!/usr/bin/env python3
"""Generate CBGB Punk Alley parallax backgrounds for Disco Cop Level 04.

Creates 3 parallax layers at 640x360:
  - parallax_punk_alley_sky.png  (far)  — dark night sky, city skyline silhouette,
                                           moon, stars, grimy haze
  - parallax_punk_alley_mid.png  (mid)  — CBGB-style club facade, fire escapes,
                                           graffiti, trash cans, street lamp, brick walls
  - parallax_punk_alley_near.png (near) — broken bottles, newspapers, chain link fence,
                                           dumpster, puddles, cracked asphalt, rat, flyers

Usage:
    python create_punk_parallax.py
"""

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "environment"

W, H = 640, 360
random.seed(810)

# Punk alley palette
SKY_TOP = (5, 5, 15)
SKY_BOT = (12, 10, 22)
MOON_PALE = (220, 215, 195)
MOON_GLOW = (180, 175, 160)
STAR_WHITE = (240, 240, 255)
HAZE_GRAY = (30, 28, 35)
SKYLINE_DARK = (10, 8, 18)
SKYLINE_MID = (15, 12, 24)
WINDOW_LIT = (200, 180, 60)
WINDOW_DIM = (140, 120, 40)
CLOUD_DARK = (22, 20, 28)
CLOUD_LIGHT = (35, 32, 42)
BRICK_DARK = (80, 40, 30)
BRICK_MID = (100, 55, 40)
BRICK_LIGHT = (120, 65, 48)
BRICK_MORTAR = (60, 50, 45)
AWNING_WHITE = (210, 205, 200)
AWNING_STRIPE = (180, 30, 30)
AWNING_TEXT = (40, 35, 30)
DOOR_DARK = (35, 25, 20)
DOOR_FRAME = (55, 45, 40)
NEON_GREEN = (50, 255, 80)
NEON_GREEN_DIM = (30, 150, 50)
NEON_RED = (255, 50, 40)
FIRE_ESCAPE_DARK = (60, 62, 65)
FIRE_ESCAPE_LIGHT = (85, 88, 92)
FIRE_ESCAPE_RAIL = (75, 78, 82)
GRAFFITI_PINK = (220, 80, 150)
GRAFFITI_GREEN = (60, 200, 80)
GRAFFITI_YELLOW = (230, 210, 50)
GRAFFITI_CYAN = (60, 200, 220)
TRASH_CAN_DARK = (55, 55, 60)
TRASH_CAN_MID = (70, 70, 76)
TRASH_CAN_LID = (80, 82, 88)
LAMP_POLE = (70, 72, 78)
LAMP_AMBER = (255, 190, 80)
LAMP_GLOW = (255, 210, 120)
BOTTLE_GREEN = (40, 140, 50)
BOTTLE_BROWN = (110, 70, 30)
BOTTLE_CLEAR = (180, 190, 200)
NEWSPAPER_BEIGE = (180, 170, 140)
NEWSPAPER_GRAY = (150, 145, 135)
FENCE_GRAY = (120, 122, 128)
FENCE_DARK = (90, 92, 96)
DUMPSTER_GREEN = (35, 80, 40)
DUMPSTER_RUST = (120, 60, 30)
DUMPSTER_DARK = (25, 60, 30)
PUDDLE_DARK = (20, 22, 35)
PUDDLE_BLUE = (30, 35, 55)
ASPHALT_DARK = (40, 38, 42)
ASPHALT_CRACK = (25, 23, 28)
ASPHALT_LIGHT = (55, 52, 58)
RAT_DARK = (35, 30, 28)
RAT_EYE = (180, 30, 30)
FLYER_PINK = (220, 100, 140)
FLYER_BLUE = (80, 120, 200)
FLYER_YELLOW = (220, 200, 60)
FLYER_WHITE = (200, 195, 190)
BOARDED_WOOD = (90, 70, 45)
BOARDED_NAIL = (140, 140, 150)


def draw_brick_wall(d, x1, y1, x2, y2):
    """Draw a brick wall pattern within the given rectangle."""
    d.rectangle([x1, y1, x2, y2], fill=BRICK_DARK)
    brick_w = 12
    brick_h = 6
    row = 0
    for by in range(y1, y2, brick_h):
        offset = (brick_w // 2) if row % 2 else 0
        for bx in range(x1 - offset, x2, brick_w):
            if bx + brick_w < x1 or bx > x2:
                continue
            cx1 = max(bx, x1)
            cy1 = max(by, y1)
            cx2 = min(bx + brick_w - 1, x2)
            cy2 = min(by + brick_h - 1, y2)
            color = random.choice([BRICK_DARK, BRICK_MID, BRICK_LIGHT])
            d.rectangle([cx1 + 1, cy1 + 1, cx2, cy2], fill=color)
            # Mortar lines (top and left of each brick)
            d.line([cx1, cy1, cx2, cy1], fill=BRICK_MORTAR)
            d.line([cx1, cy1, cx1, cy2], fill=BRICK_MORTAR)
        row += 1


def draw_fire_escape(d, x, y_top, y_bot, side_width=35):
    """Draw a fire escape zigzag staircase on a building wall."""
    # Platforms
    platform_spacing = 45
    platforms = []
    for py in range(y_top, y_bot, platform_spacing):
        platforms.append(py)
        # Platform bar
        d.rectangle([x, py, x + side_width, py + 2], fill=FIRE_ESCAPE_DARK)
        # Railing
        d.rectangle([x, py - 10, x + 1, py], fill=FIRE_ESCAPE_RAIL)
        d.rectangle([x + side_width - 1, py - 10, x + side_width, py],
                     fill=FIRE_ESCAPE_RAIL)
        # Top rail
        d.line([x, py - 10, x + side_width, py - 10], fill=FIRE_ESCAPE_RAIL)
        # Support brackets
        d.line([x + 2, py + 2, x + 2, py + 6], fill=FIRE_ESCAPE_LIGHT)
        d.line([x + side_width - 3, py + 2, x + side_width - 3, py + 6],
               fill=FIRE_ESCAPE_LIGHT)

    # Zigzag stairs between platforms
    for i in range(len(platforms) - 1):
        top_y = platforms[i] + 2
        bot_y = platforms[i + 1]
        if i % 2 == 0:
            d.line([x + side_width, top_y, x, bot_y], fill=FIRE_ESCAPE_DARK, width=1)
        else:
            d.line([x, top_y, x + side_width, bot_y], fill=FIRE_ESCAPE_DARK, width=1)

    # Ladder at bottom
    if platforms:
        last_py = platforms[-1]
        lx = x + side_width // 2
        d.line([lx - 3, last_py + 2, lx - 3, last_py + 25], fill=FIRE_ESCAPE_RAIL)
        d.line([lx + 3, last_py + 2, lx + 3, last_py + 25], fill=FIRE_ESCAPE_RAIL)
        for ry in range(last_py + 5, last_py + 25, 4):
            d.line([lx - 3, ry, lx + 3, ry], fill=FIRE_ESCAPE_LIGHT)


def create_sky_layer():
    """Far: dark night sky, city skyline, moon, stars, grimy haze."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    # ── Night sky gradient ──
    for y in range(H):
        t = y / H
        r = int(SKY_TOP[0] * (1 - t) + SKY_BOT[0] * t)
        g = int(SKY_TOP[1] * (1 - t) + SKY_BOT[1] * t)
        b = int(SKY_TOP[2] * (1 - t) + SKY_BOT[2] * t)
        d.line([0, y, W - 1, y], fill=(r, g, b, 255))

    # ── Stars (upper sky) ──
    for _ in range(120):
        sx = random.randint(0, W - 1)
        sy = random.randint(0, 160)
        bright = random.randint(160, 255)
        d.point([sx, sy], fill=(bright, bright, min(bright + 15, 255), 255))
        # Occasional slightly larger star
        if random.random() < 0.1:
            d.point([sx + 1, sy], fill=(bright - 30, bright - 30, bright, 255))

    # ── Moon (upper right) ──
    moon_x, moon_y = 520, 50
    moon_r = 14
    d.ellipse([moon_x - moon_r, moon_y - moon_r,
               moon_x + moon_r, moon_y + moon_r], fill=MOON_PALE)
    # Subtle crater spots
    for _ in range(5):
        cx = moon_x + random.randint(-8, 8)
        cy = moon_y + random.randint(-8, 8)
        cr = random.randint(1, 3)
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=MOON_GLOW)
    # Moon glow halo
    for ring in range(1, 8):
        alpha = max(5, 40 - ring * 6)
        for angle in range(0, 360, 2):
            rad = math.radians(angle)
            px = moon_x + int((moon_r + ring * 2) * math.cos(rad))
            py = moon_y + int((moon_r + ring * 2) * math.sin(rad))
            if 0 <= px < W and 0 <= py < H:
                r0, g0, b0, _ = img.getpixel((px, py))
                nr = min(r0 + alpha, 255)
                ng = min(g0 + alpha, 255)
                nb = min(b0 + alpha - 2, 255)
                img.putpixel((px, py), (nr, ng, max(nb, 0), 255))

    # ── Grimy clouds / haze wisps ──
    for _ in range(12):
        cx = random.randint(0, W)
        cy = random.randint(40, 180)
        cloud_w = random.randint(60, 160)
        cloud_h = random.randint(8, 20)
        for px in range(cx - cloud_w // 2, cx + cloud_w // 2):
            if 0 <= px < W:
                for py in range(cy - cloud_h // 2, cy + cloud_h // 2):
                    if 0 <= py < H:
                        dx = (px - cx) / (cloud_w / 2)
                        dy = (py - cy) / (cloud_h / 2)
                        dist = dx * dx + dy * dy
                        if dist < 1.0 and random.random() < (1 - dist) * 0.4:
                            cloud_c = random.choice([CLOUD_DARK, CLOUD_LIGHT])
                            r0, g0, b0, _ = img.getpixel((px, py))
                            blend = 0.3
                            nr = int(r0 * (1 - blend) + cloud_c[0] * blend)
                            ng = int(g0 * (1 - blend) + cloud_c[1] * blend)
                            nb = int(b0 * (1 - blend) + cloud_c[2] * blend)
                            img.putpixel((px, py), (nr, ng, nb, 255))

    # ── City skyline silhouette ──
    skyline_y = 200
    buildings = []
    bx = 0
    while bx < W:
        bw = random.randint(25, 70)
        bh = random.randint(30, 100)
        buildings.append((bx, skyline_y - bh, bw, bh))
        bx += bw + random.randint(0, 5)

    for bx, by, bw, bh in buildings:
        color = random.choice([SKYLINE_DARK, SKYLINE_MID])
        d.rectangle([bx, by, bx + bw, skyline_y + 60], fill=color)
        # Lit windows (tiny yellow dots)
        for wy in range(by + 4, skyline_y, 8):
            for wx in range(bx + 3, bx + bw - 3, 6):
                if random.random() < 0.25:
                    wc = random.choice([WINDOW_LIT, WINDOW_DIM])
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=wc)
        # Rooftop details
        if random.random() < 0.4:
            # Water tower or antenna
            ax = bx + bw // 2
            d.line([ax, by, ax, by - random.randint(5, 15)], fill=SKYLINE_DARK)

    # Fill below skyline
    d.rectangle([0, skyline_y + 60, W - 1, H - 1], fill=SKYLINE_DARK)

    out = OUTPUT_DIR / "parallax_punk_alley_sky.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def create_mid_layer():
    """Mid: CBGB-style club, fire escapes, graffiti, trash cans, street lamp, brick."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    ground_y = 300

    # ── Brick building facades stretching across ──
    # Left building block
    draw_brick_wall(d, 0, 80, 200, ground_y)
    # CBGB building (center-left)
    draw_brick_wall(d, 200, 60, 400, ground_y)
    # Right building block
    draw_brick_wall(d, 400, 90, W - 1, ground_y)

    # ── CBGB-style club storefront (center-left) ──
    club_x = 220
    club_w = 160

    # Iconic awning (white with text blocks)
    awning_y = 180
    awning_h = 28
    d.rectangle([club_x - 5, awning_y, club_x + club_w + 5, awning_y + awning_h],
                fill=AWNING_WHITE)
    # Red border stripes
    d.rectangle([club_x - 5, awning_y, club_x + club_w + 5, awning_y + 3],
                fill=AWNING_STRIPE)
    d.rectangle([club_x - 5, awning_y + awning_h - 3, club_x + club_w + 5,
                 awning_y + awning_h], fill=AWNING_STRIPE)
    # Text blocks on awning (crude letter blocks)
    text_y = awning_y + 8
    text_blocks = [
        club_x + 10, club_x + 24, club_x + 38, club_x + 52,  # C B G B
    ]
    for tx in text_blocks:
        d.rectangle([tx, text_y, tx + 10, text_y + 12], fill=AWNING_TEXT)
    # Extra text "OMFUG" (smaller)
    for tx in range(club_x + 75, club_x + 135, 10):
        d.rectangle([tx, text_y + 2, tx + 7, text_y + 10], fill=AWNING_TEXT)

    # Door
    door_x = club_x + club_w // 2 - 10
    door_y = ground_y - 50
    d.rectangle([door_x, door_y, door_x + 22, ground_y], fill=DOOR_DARK,
                outline=DOOR_FRAME)
    # Door handle
    d.rectangle([door_x + 17, door_y + 22, door_x + 19, door_y + 28],
                fill=(140, 140, 150))

    # Boarded windows
    for wx in [club_x + 10, club_x + club_w - 38]:
        wy = awning_y + awning_h + 10
        d.rectangle([wx, wy, wx + 28, wy + 35], fill=DOOR_DARK)
        # Boards
        for by in range(wy + 2, wy + 33, 7):
            d.rectangle([wx + 1, by, wx + 27, by + 5], fill=BOARDED_WOOD)
            # Nails
            d.point([wx + 4, by + 2], fill=BOARDED_NAIL)
            d.point([wx + 24, by + 2], fill=BOARDED_NAIL)

    # Neon "OPEN" sign hint (above door)
    neon_y = door_y - 12
    neon_x = door_x + 2
    # Glow background
    d.rectangle([neon_x - 2, neon_y - 2, neon_x + 34, neon_y + 10],
                fill=(15, 30, 18, 180))
    # Letters (crude neon style)
    for i, offset in enumerate([0, 8, 16, 24]):
        c = NEON_GREEN if (i % 2 == 0) else NEON_GREEN_DIM
        d.rectangle([neon_x + offset, neon_y, neon_x + offset + 5, neon_y + 7],
                     fill=c)
    # Glow around neon
    for gx in range(neon_x - 4, neon_x + 38):
        for gy in range(neon_y - 4, neon_y + 12):
            if 0 <= gx < W and 0 <= gy < H:
                r0, g0, b0, a0 = img.getpixel((gx, gy))
                if a0 > 0:
                    ng = min(g0 + 15, 255)
                    img.putpixel((gx, gy), (r0, ng, b0, a0))

    # ── Fire escapes ──
    draw_fire_escape(d, 30, 100, ground_y - 20, 35)
    draw_fire_escape(d, 450, 110, ground_y - 20, 32)
    draw_fire_escape(d, 560, 120, ground_y - 10, 30)

    # ── Graffiti tags on walls ──
    graffiti_colors = [GRAFFITI_PINK, GRAFFITI_GREEN, GRAFFITI_YELLOW, GRAFFITI_CYAN]
    graffiti_spots = [
        (50, 200, 35, 15), (140, 170, 40, 12), (420, 190, 45, 18),
        (510, 160, 30, 14), (100, 250, 25, 10), (490, 240, 38, 16),
        (170, 230, 32, 11), (555, 210, 28, 13),
    ]
    for gx, gy, gw, gh in graffiti_spots:
        color = random.choice(graffiti_colors)
        # Tag shape (rounded blob)
        d.rounded_rectangle([gx, gy, gx + gw, gy + gh], radius=3, fill=color)
        # Drip line
        if random.random() < 0.5:
            drip_x = gx + random.randint(3, gw - 3)
            drip_len = random.randint(5, 15)
            d.line([drip_x, gy + gh, drip_x, gy + gh + drip_len], fill=color, width=1)

    # ── Trash cans ──
    trash_positions = [185, 405, 530]
    for tx in trash_positions:
        ty = ground_y - 22
        tw, th = 14, 22
        # Can body (cylinder)
        d.rectangle([tx, ty, tx + tw, ty + th], fill=TRASH_CAN_DARK)
        d.rectangle([tx + 1, ty + 1, tx + tw - 1, ty + th - 1], fill=TRASH_CAN_MID)
        # Lid
        d.rectangle([tx - 1, ty - 3, tx + tw + 1, ty], fill=TRASH_CAN_LID)
        d.ellipse([tx - 1, ty - 5, tx + tw + 1, ty - 1], fill=TRASH_CAN_LID)
        # Handle on lid
        d.rectangle([tx + tw // 2 - 2, ty - 7, tx + tw // 2 + 2, ty - 5],
                     fill=TRASH_CAN_DARK)
        # Horizontal ribs
        for ry in range(ty + 5, ty + th - 2, 6):
            d.line([tx + 1, ry, tx + tw - 1, ry], fill=TRASH_CAN_DARK)

    # ── Street lamp ──
    lamp_x = 155
    lamp_base_y = ground_y
    lamp_top_y = 80
    # Pole
    d.rectangle([lamp_x - 2, lamp_top_y, lamp_x + 2, lamp_base_y], fill=LAMP_POLE)
    # Lamp housing at top
    d.rectangle([lamp_x - 8, lamp_top_y - 2, lamp_x + 8, lamp_top_y + 4],
                fill=LAMP_POLE)
    # Bulb / amber glow
    d.rectangle([lamp_x - 5, lamp_top_y + 4, lamp_x + 5, lamp_top_y + 8],
                fill=LAMP_AMBER)
    # Light cone glow
    for dist in range(1, 50):
        t = dist / 50
        alpha = max(3, int(30 * (1 - t)))
        cone_y = lamp_top_y + 8 + dist
        spread = int(dist * 0.6)
        if cone_y >= H:
            break
        for lx in range(lamp_x - spread, lamp_x + spread + 1):
            if 0 <= lx < W:
                r0, g0, b0, a0 = img.getpixel((lx, cone_y))
                if a0 > 0:
                    nr = min(r0 + alpha, 255)
                    ng = min(g0 + int(alpha * 0.7), 255)
                    nb = min(b0 + int(alpha * 0.2), 255)
                    img.putpixel((lx, cone_y), (nr, ng, nb, a0))

    out = OUTPUT_DIR / "parallax_punk_alley_mid.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def create_near_layer():
    """Near: broken bottles, newspapers, chain link fence, dumpster, puddles,
    cracked asphalt, rat, concert flyers."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    ground_y = 310

    # ── Cracked asphalt strip at bottom ──
    d.rectangle([0, ground_y, W - 1, H - 1], fill=ASPHALT_DARK)
    # Asphalt texture
    for _ in range(200):
        px = random.randint(0, W - 1)
        py = random.randint(ground_y, H - 1)
        c = random.choice([ASPHALT_DARK, ASPHALT_LIGHT, ASPHALT_CRACK])
        d.point([px, py], fill=c)
    # Cracks
    for _ in range(8):
        cx = random.randint(20, W - 20)
        cy = random.randint(ground_y + 5, H - 10)
        for seg in range(random.randint(5, 15)):
            nx = cx + random.randint(-5, 5)
            ny = cy + random.randint(-2, 4)
            d.line([cx, cy, nx, ny], fill=ASPHALT_CRACK, width=1)
            cx, cy = nx, ny

    # ── Chain link fence section (left side) ──
    fence_x1 = 0
    fence_x2 = 90
    fence_y1 = ground_y - 80
    fence_y2 = ground_y
    # Top rail
    d.rectangle([fence_x1, fence_y1, fence_x2, fence_y1 + 2], fill=FENCE_GRAY)
    # Posts
    for px in range(fence_x1, fence_x2 + 1, 30):
        d.rectangle([px, fence_y1, px + 2, fence_y2], fill=FENCE_GRAY)
    # Diamond chain link pattern
    diamond_size = 6
    for fy in range(fence_y1 + 4, fence_y2, diamond_size):
        for fx in range(fence_x1 + 2, fence_x2 - 2, diamond_size):
            offset = (diamond_size // 2) if ((fy - fence_y1) // diamond_size) % 2 else 0
            ax = fx + offset
            # Diamond shape
            mid_x = ax + diamond_size // 2
            mid_y = fy + diamond_size // 2
            if mid_x < fence_x2 and mid_y < fence_y2:
                d.line([mid_x, fy, ax + diamond_size, mid_y],
                       fill=FENCE_DARK, width=1)
                d.line([ax + diamond_size, mid_y, mid_x, fy + diamond_size],
                       fill=FENCE_DARK, width=1)
                d.line([mid_x, fy + diamond_size, ax, mid_y],
                       fill=FENCE_DARK, width=1)
                d.line([ax, mid_y, mid_x, fy], fill=FENCE_DARK, width=1)

    # ── Dumpster (dark green with rust, open lid) ──
    dump_x = 500
    dump_y = ground_y - 40
    dump_w = 70
    dump_h = 40
    # Body
    d.rectangle([dump_x, dump_y, dump_x + dump_w, dump_y + dump_h],
                fill=DUMPSTER_GREEN, outline=DUMPSTER_DARK)
    # Rust patches
    for _ in range(8):
        rx = dump_x + random.randint(3, dump_w - 3)
        ry = dump_y + random.randint(3, dump_h - 3)
        rw = random.randint(3, 10)
        rh = random.randint(2, 6)
        d.rectangle([rx, ry, rx + rw, ry + rh], fill=DUMPSTER_RUST)
    # Open lid (tilted back)
    lid_y = dump_y - 6
    d.polygon([(dump_x, dump_y), (dump_x + 3, lid_y), (dump_x + dump_w - 3, lid_y),
               (dump_x + dump_w, dump_y)], fill=DUMPSTER_DARK, outline=DUMPSTER_GREEN)
    # Side ridges
    for ry in [dump_y + dump_h // 3, dump_y + 2 * dump_h // 3]:
        d.line([dump_x + 2, ry, dump_x + dump_w - 2, ry], fill=DUMPSTER_DARK)
    # Wheels
    for wx in [dump_x + 8, dump_x + dump_w - 8]:
        d.ellipse([wx - 3, dump_y + dump_h - 2, wx + 3, dump_y + dump_h + 4],
                  fill=(30, 30, 30), outline=(50, 50, 55))

    # ── Puddles on ground ──
    puddle_spots = [(120, ground_y + 15), (280, ground_y + 20), (430, ground_y + 12),
                    (350, ground_y + 25), (550, ground_y + 30)]
    for px, py in puddle_spots:
        pw = random.randint(20, 45)
        ph = random.randint(4, 8)
        d.ellipse([px, py, px + pw, py + ph], fill=PUDDLE_DARK)
        # Slight blue tint reflection
        d.ellipse([px + 3, py + 1, px + pw - 3, py + ph - 1], fill=PUDDLE_BLUE)
        # Highlight shimmer
        shimmer_x = px + pw // 3
        d.point([shimmer_x, py + 1], fill=(60, 65, 90))

    # ── Broken bottles on ground ──
    bottle_colors = [BOTTLE_GREEN, BOTTLE_BROWN, BOTTLE_CLEAR]
    for _ in range(18):
        bx = random.randint(30, W - 30)
        by = random.randint(ground_y + 2, H - 8)
        color = random.choice(bottle_colors)
        # Shard shapes (small triangles/rectangles)
        shape = random.choice(["shard", "base"])
        if shape == "shard":
            sw = random.randint(2, 5)
            sh = random.randint(2, 4)
            d.polygon([(bx, by), (bx + sw, by + sh // 2), (bx + sw // 2, by + sh)],
                      fill=color)
        else:
            # Bottle base (small circle)
            d.ellipse([bx, by, bx + 3, by + 3], fill=color)
        # Glass glint
        if random.random() < 0.4:
            d.point([bx + 1, by], fill=(230, 235, 245))

    # ── Crumpled newspapers ──
    for _ in range(7):
        nx = random.randint(50, W - 50)
        ny = random.randint(ground_y + 5, H - 8)
        nw = random.randint(8, 16)
        nh = random.randint(5, 10)
        nc = random.choice([NEWSPAPER_BEIGE, NEWSPAPER_GRAY])
        d.rectangle([nx, ny, nx + nw, ny + nh], fill=nc)
        # "Text" lines
        for ly in range(ny + 2, ny + nh - 1, 2):
            lw = random.randint(3, nw - 3)
            d.line([nx + 1, ly, nx + 1 + lw, ly], fill=(120, 115, 105))

    # ── Concert flyers on wall (torn poster remnants, upper area) ──
    flyer_colors = [FLYER_PINK, FLYER_BLUE, FLYER_YELLOW, FLYER_WHITE]
    flyer_spots = [
        (105, 250), (250, 260), (400, 255), (470, 265),
        (320, 270), (580, 258),
    ]
    for fx, fy in flyer_spots:
        fw = random.randint(12, 22)
        fh = random.randint(14, 24)
        color = random.choice(flyer_colors)
        d.rectangle([fx, fy, fx + fw, fy + fh], fill=color)
        # Torn edge (irregular bottom)
        for tx in range(fx, fx + fw):
            tear_y = fy + fh - random.randint(0, 4)
            d.rectangle([tx, tear_y, tx, fy + fh + 2], fill=(0, 0, 0, 0))
        # Staple/tack at top
        d.point([fx + fw // 2, fy], fill=(160, 160, 170))

    # ── Rat silhouette ──
    rat_x = 460
    rat_y = ground_y + 8
    # Body
    d.ellipse([rat_x, rat_y, rat_x + 10, rat_y + 6], fill=RAT_DARK)
    # Head
    d.ellipse([rat_x + 8, rat_y + 1, rat_x + 14, rat_y + 5], fill=RAT_DARK)
    # Ear
    d.ellipse([rat_x + 11, rat_y - 1, rat_x + 14, rat_y + 2], fill=(50, 42, 38))
    # Eye
    d.point([rat_x + 12, rat_y + 2], fill=RAT_EYE)
    # Tail (curved line)
    d.line([rat_x, rat_y + 3, rat_x - 5, rat_y + 1], fill=RAT_DARK, width=1)
    d.line([rat_x - 5, rat_y + 1, rat_x - 10, rat_y + 4], fill=RAT_DARK, width=1)
    # Whiskers
    d.line([rat_x + 13, rat_y + 3, rat_x + 17, rat_y + 1], fill=(60, 55, 50))
    d.line([rat_x + 13, rat_y + 3, rat_x + 17, rat_y + 5], fill=(60, 55, 50))

    out = OUTPUT_DIR / "parallax_punk_alley_near.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def main():
    print("Generating CBGB Punk Alley parallax layers...")
    create_sky_layer()
    create_mid_layer()
    create_near_layer()
    print("Done!")


if __name__ == "__main__":
    main()
