#!/usr/bin/env python3
"""Generate Led Zeppelin Concert parallax backgrounds for Disco Cop Level 03.

Creates 3 parallax layers at 640x360:
  - parallax_concert_sky.png  (far)  — dark ceiling, lighting truss, spot lights,
                                        crowd silhouette mass with raised arms
  - parallax_concert_mid.png  (mid)  — Marshall amp stacks, stage scaffolding,
                                        drum kit silhouette, hanging PA speakers
  - parallax_concert_near.png (near) — floor monitors, cables, pyro pots,
                                        mic stand, stage floor wood strip

Usage:
    python create_concert_parallax.py
"""

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "environment"

W, H = 640, 360
random.seed(505)

# Concert palette
CEILING_TOP = (5, 3, 8)
CEILING_MID = (10, 8, 15)
CEILING_LOW = (15, 12, 20)
TRUSS_DARK = (50, 50, 55)
TRUSS_LIGHT = (80, 80, 88)
TRUSS_CHROME = (140, 145, 155)
SPOT_RED = (255, 40, 40)
SPOT_BLUE = (40, 80, 255)
SPOT_GREEN = (40, 255, 80)
SPOT_AMBER = (255, 180, 40)
SPOT_WHITE = (255, 250, 240)
SPOT_PURPLE = (180, 40, 255)
CROWD_MASS = (20, 15, 25)
CROWD_HEAD = (30, 25, 38)
CROWD_ARM = (35, 28, 42)
CROWD_PHONE = (180, 200, 255)
AMP_BLACK = (22, 22, 26)
AMP_DARK = (32, 32, 36)
AMP_GRILLE = (48, 48, 55)
AMP_GOLD = (200, 170, 50)
AMP_CHROME = (170, 175, 185)
SCAFFOLD_GRAY = (70, 70, 78)
SCAFFOLD_LIGHT = (95, 95, 105)
DRUM_DARK = (30, 28, 35)
DRUM_CHROME = (160, 165, 175)
DRUM_CYMBAL = (200, 190, 120)
PA_BLACK = (18, 18, 22)
PA_GRILLE = (40, 40, 48)
STAGE_WOOD = (65, 45, 28)
STAGE_WOOD_LIGHT = (85, 60, 38)
STAGE_GRAIN = (55, 38, 22)
MONITOR_BLACK = (20, 20, 25)
MONITOR_GRILLE = (45, 45, 52)
MONITOR_CHROME = (155, 160, 170)
CABLE_BLACK = (15, 12, 10)
CABLE_DARK = (25, 22, 20)
PYRO_BASE = (50, 45, 40)
PYRO_FLAME_1 = (255, 160, 20)
PYRO_FLAME_2 = (255, 100, 10)
PYRO_FLAME_3 = (255, 60, 5)
MIC_CHROME = (180, 185, 195)
MIC_BLACK = (30, 30, 35)


def draw_truss_segment(d, x1, y, x2, truss_h=8):
    """Draw a horizontal truss segment with cross-bracing."""
    # Top and bottom rails
    d.rectangle([x1, y, x2, y + 1], fill=TRUSS_DARK)
    d.rectangle([x1, y + truss_h - 2, x2, y + truss_h - 1], fill=TRUSS_DARK)
    # Cross bracing
    spacing = 12
    for x in range(x1, x2, spacing):
        end_x = min(x + spacing, x2)
        d.line([x, y + 1, end_x, y + truss_h - 2], fill=TRUSS_LIGHT, width=1)
        d.line([x, y + truss_h - 2, end_x, y + 1], fill=TRUSS_LIGHT, width=1)
    # Highlight on top rail
    for x in range(x1, x2, 3):
        if random.random() < 0.2:
            d.point([x, y], fill=TRUSS_CHROME)


def draw_spot_light(img, x, y, color, beam_angle=15, beam_len=120):
    """Draw a spot light fixture with beam cone."""
    d = ImageDraw.Draw(img)
    # Fixture housing
    d.rectangle([x - 3, y, x + 3, y + 5], fill=TRUSS_DARK)
    d.rectangle([x - 4, y + 5, x + 4, y + 8], fill=color)
    # Lens glow
    d.ellipse([x - 2, y + 5, x + 2, y + 9], fill=color)

    # Light beam (cone of semi-transparent color)
    angle_rad = math.radians(beam_angle)
    for dist in range(10, beam_len):
        t = dist / beam_len
        width = int(dist * math.tan(angle_rad))
        alpha = max(2, int(40 * (1 - t * t)))
        beam_y = y + 8 + dist
        if beam_y >= H:
            break
        for bx in range(x - width, x + width + 1):
            if 0 <= bx < W:
                r0, g0, b0, a0 = img.getpixel((bx, beam_y))
                blend = alpha / 255.0
                nr = min(int(r0 + color[0] * blend * 0.4), 255)
                ng = min(int(g0 + color[1] * blend * 0.4), 255)
                nb = min(int(b0 + color[2] * blend * 0.4), 255)
                img.putpixel((bx, beam_y), (nr, ng, nb, max(a0, alpha)))


def create_sky_layer():
    """Far: dark ceiling, lighting truss grid, spot lights, crowd mass."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    # ── Dark ceiling gradient ──
    for y in range(H):
        t = y / H
        r = int(CEILING_TOP[0] * (1 - t) + CEILING_LOW[0] * t)
        g = int(CEILING_TOP[1] * (1 - t) + CEILING_LOW[1] * t)
        b = int(CEILING_TOP[2] * (1 - t) + CEILING_LOW[2] * t)
        d.line([0, y, W - 1, y], fill=(r, g, b, 255))

    # ── Lighting truss grid ──
    # Main horizontal trusses
    draw_truss_segment(d, 0, 30, W - 1, 10)
    draw_truss_segment(d, 0, 70, W - 1, 8)
    # Cross trusses (vertical segments)
    for tx in range(80, W, 140):
        d.rectangle([tx, 30, tx + 2, 78], fill=TRUSS_DARK)
        d.rectangle([tx + 1, 30, tx + 1, 78], fill=TRUSS_LIGHT)

    # ── Spot lights hanging from trusses ──
    spot_configs = [
        (60, 40, SPOT_RED, 12, 140),
        (160, 40, SPOT_BLUE, 15, 130),
        (280, 40, SPOT_AMBER, 10, 150),
        (380, 40, SPOT_GREEN, 13, 135),
        (500, 40, SPOT_PURPLE, 14, 125),
        (580, 40, SPOT_RED, 11, 140),
        (120, 78, SPOT_WHITE, 8, 100),
        (320, 78, SPOT_AMBER, 10, 110),
        (440, 78, SPOT_BLUE, 9, 105),
    ]
    for sx, sy, color, angle, length in spot_configs:
        draw_spot_light(img, sx, sy, color, angle, length)

    # ── Haze / atmosphere (subtle fog layer) ──
    for y in range(100, 200):
        t = (y - 100) / 100
        haze_alpha = int(15 * math.sin(t * math.pi))
        for x in range(0, W, 2):
            r0, g0, b0, _ = img.getpixel((x, y))
            nr = min(r0 + haze_alpha, 255)
            ng = min(g0 + haze_alpha, 255)
            nb = min(b0 + haze_alpha + 2, 255)
            img.putpixel((x, y), (nr, ng, nb, 255))

    # ── Crowd silhouette mass (bottom third) ──
    crowd_top = 240
    d.rectangle([0, crowd_top, W - 1, H - 1], fill=CROWD_MASS)

    # Individual head bumps along crowd top
    for hx in range(0, W, 5):
        hy = crowd_top - random.randint(0, 12)
        hw = random.randint(3, 5)
        hh = random.randint(4, 7)
        d.ellipse([hx, hy, hx + hw, hy + hh], fill=CROWD_HEAD)
        # Body below
        d.rectangle([hx - 1, hy + hh, hx + hw + 1, crowd_top + 10], fill=CROWD_MASS)

    # Raised arms
    for _ in range(25):
        ax = random.randint(10, W - 10)
        ay = crowd_top - random.randint(8, 25)
        arm_h = random.randint(10, 20)
        d.line([ax, ay + arm_h, ax, ay], fill=CROWD_ARM, width=1)
        # Fist/hand at top
        d.rectangle([ax - 1, ay - 1, ax + 1, ay + 1], fill=CROWD_ARM)

    # Phone screen glows in crowd
    for _ in range(15):
        px = random.randint(5, W - 5)
        py = random.randint(crowd_top + 5, H - 10)
        glow = random.choice([CROWD_PHONE, (200, 180, 255), (180, 255, 200)])
        d.rectangle([px, py, px + 1, py + 2], fill=glow)
        # Glow halo
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = px + dx, py + dy
                if 0 <= nx < W and 0 <= ny < H:
                    r0, g0, b0, _ = img.getpixel((nx, ny))
                    nr = min(r0 + glow[0] // 10, 255)
                    ng = min(g0 + glow[1] // 10, 255)
                    nb = min(b0 + glow[2] // 10, 255)
                    img.putpixel((nx, ny), (nr, ng, nb, 255))

    out = OUTPUT_DIR / "parallax_concert_sky.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def draw_amp_stack(d, x, y, w=40, h=60):
    """Draw a Marshall-style amp stack."""
    # Cabinet body
    d.rectangle([x, y, x + w, y + h], fill=AMP_BLACK, outline=AMP_DARK)
    # Top head unit
    head_h = h // 4
    d.rectangle([x + 1, y + 1, x + w - 1, y + head_h], fill=AMP_DARK)
    # Gold logo on head
    for lx in range(x + 6, x + w - 6, 2):
        d.point([lx, y + head_h // 2], fill=AMP_GOLD)
    # Knobs on head
    for kx in range(x + 4, x + w - 4, 5):
        d.point([kx, y + head_h - 3], fill=AMP_CHROME)

    # Speaker cab below head
    cab_y = y + head_h + 2
    cab_h = h - head_h - 4
    d.rectangle([x + 2, cab_y, x + w - 2, y + h - 2], fill=AMP_BLACK)
    # Grille pattern
    for gy in range(cab_y + 2, y + h - 4, 2):
        for gx in range(x + 4, x + w - 4, 2):
            if (gx + gy) % 4 == 0:
                d.point([gx, gy], fill=AMP_GRILLE)

    # Speaker cone hints
    for cone_y in [cab_y + cab_h // 4, cab_y + 3 * cab_h // 4]:
        cx = x + w // 2
        d.ellipse([cx - 6, cone_y - 6, cx + 6, cone_y + 6], outline=AMP_GRILLE)
        d.ellipse([cx - 2, cone_y - 2, cx + 2, cone_y + 2], fill=AMP_BLACK)

    # Chrome corners
    for cx, cy in [(x + 1, y + 1), (x + w - 2, y + 1),
                   (x + 1, y + h - 2), (x + w - 2, y + h - 2)]:
        d.rectangle([cx, cy, cx + 1, cy + 1], fill=AMP_CHROME)


def draw_pa_speaker(d, x, y, w=25, h=18):
    """Draw a hanging PA speaker box."""
    d.rectangle([x, y, x + w, y + h], fill=PA_BLACK, outline=PA_GRILLE)
    # Grille
    for gy in range(y + 2, y + h - 2, 2):
        for gx in range(x + 2, x + w - 2, 3):
            d.point([gx, gy], fill=PA_GRILLE)
    # Rigging point at top
    d.rectangle([x + w // 2 - 1, y - 3, x + w // 2 + 1, y], fill=SCAFFOLD_GRAY)


def create_mid_layer():
    """Mid: Marshall amp stacks, scaffolding, drum kit, PA speakers."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    ground_y = 260

    # ── Amp stacks (wall of amps across back) ──
    amp_positions = [20, 70, 130, 420, 480, 550]
    for ax in amp_positions:
        # Double stack (two cabs)
        draw_amp_stack(d, ax, ground_y - 120, 42, 55)
        draw_amp_stack(d, ax, ground_y - 60, 42, 55)

    # ── Stage scaffolding (side towers) ──
    for scaffold_x in [0, W - 30]:
        # Vertical poles
        d.rectangle([scaffold_x + 5, 40, scaffold_x + 8, ground_y], fill=SCAFFOLD_GRAY)
        d.rectangle([scaffold_x + 20, 40, scaffold_x + 23, ground_y], fill=SCAFFOLD_GRAY)
        # Cross braces
        for sy in range(50, ground_y, 30):
            d.line([scaffold_x + 5, sy, scaffold_x + 23, sy + 25], fill=SCAFFOLD_LIGHT, width=1)
            d.line([scaffold_x + 23, sy, scaffold_x + 5, sy + 25], fill=SCAFFOLD_LIGHT, width=1)
        # Horizontal bars
        for sy in range(50, ground_y, 30):
            d.line([scaffold_x + 5, sy, scaffold_x + 23, sy], fill=SCAFFOLD_GRAY, width=1)

    # ── Drum kit silhouette (center-right) ──
    drum_cx = 320
    drum_y = ground_y - 30

    # Bass drum (large circle)
    d.ellipse([drum_cx - 15, drum_y - 10, drum_cx + 15, drum_y + 20],
              fill=DRUM_DARK, outline=DRUM_CHROME)
    # Front head logo circle
    d.ellipse([drum_cx - 8, drum_y - 2, drum_cx + 8, drum_y + 12], outline=(50, 45, 55))

    # Tom drums
    d.ellipse([drum_cx - 25, drum_y - 20, drum_cx - 10, drum_y - 8],
              fill=DRUM_DARK, outline=DRUM_CHROME)
    d.ellipse([drum_cx + 10, drum_y - 20, drum_cx + 25, drum_y - 8],
              fill=DRUM_DARK, outline=DRUM_CHROME)

    # Floor tom
    d.ellipse([drum_cx + 25, drum_y - 5, drum_cx + 45, drum_y + 10],
              fill=DRUM_DARK, outline=DRUM_CHROME)

    # Cymbals
    for cy_x, cy_y in [(drum_cx - 30, drum_y - 30), (drum_cx + 30, drum_y - 28),
                        (drum_cx + 50, drum_y - 25)]:
        d.ellipse([cy_x - 8, cy_y, cy_x + 8, cy_y + 3], fill=DRUM_CYMBAL)
        # Stand
        d.line([cy_x, cy_y + 3, cy_x, drum_y + 15], fill=DRUM_CHROME, width=1)

    # Hi-hat
    hh_x = drum_cx - 35
    d.ellipse([hh_x - 6, drum_y - 15, hh_x + 6, drum_y - 12], fill=DRUM_CYMBAL)
    d.ellipse([hh_x - 6, drum_y - 12, hh_x + 6, drum_y - 9], fill=DRUM_CYMBAL)
    d.line([hh_x, drum_y - 9, hh_x, drum_y + 15], fill=DRUM_CHROME, width=1)

    # Drum stool
    d.ellipse([drum_cx - 8, drum_y + 8, drum_cx + 8, drum_y + 14], fill=DRUM_DARK)
    d.line([drum_cx, drum_y + 14, drum_cx, drum_y + 22], fill=DRUM_CHROME, width=2)

    # ── Hanging PA speakers ──
    pa_positions = [(100, 60), (200, 55), (440, 58), (540, 62)]
    for px, py in pa_positions:
        # Rigging cable
        d.line([px + 12, 0, px + 12, py], fill=SCAFFOLD_GRAY, width=1)
        draw_pa_speaker(d, px, py)

    out = OUTPUT_DIR / "parallax_concert_mid.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def create_near_layer():
    """Near: floor monitors, cables, pyro pots, mic stand, stage floor strip."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    ground_y = 300

    # ── Stage floor wood strip (bottom) ──
    d.rectangle([0, ground_y, W - 1, H - 1], fill=STAGE_WOOD)
    # Plank lines
    for y in range(ground_y, H, 8):
        d.line([0, y, W - 1, y], fill=(50, 35, 20, 255))
    # Wood grain
    for _ in range(80):
        gx = random.randint(0, W - 1)
        gy = random.randint(ground_y, H - 1)
        length = random.randint(8, 30)
        d.line([gx, gy, gx + length, gy], fill=STAGE_GRAIN)
    # Highlights
    for _ in range(40):
        hx = random.randint(0, W - 1)
        hy = random.randint(ground_y, H - 1)
        img.putpixel((hx, hy), (*STAGE_WOOD_LIGHT, 255))

    # ── Floor monitor wedges ──
    monitor_positions = [60, 200, 380, 520]
    for mx in monitor_positions:
        my = ground_y - 12
        mw, mh = 30, 18
        # Wedge shape (trapezoid)
        d.polygon([(mx, my + mh), (mx + 4, my), (mx + mw - 4, my), (mx + mw, my + mh)],
                  fill=MONITOR_BLACK, outline=MONITOR_GRILLE)
        # Grille on angled face
        for gy in range(my + 2, my + mh - 2, 2):
            for gx in range(mx + 5, mx + mw - 5, 3):
                d.point([gx, gy], fill=MONITOR_GRILLE)
        # Chrome handle
        d.line([mx + 8, my + 1, mx + mw - 8, my + 1], fill=MONITOR_CHROME)

    # ── Cables snaking across stage ──
    cable_paths = [
        [(0, ground_y + 10), (80, ground_y + 15), (150, ground_y + 8), (220, ground_y + 12)],
        [(300, ground_y + 20), (400, ground_y + 18), (500, ground_y + 22), (W, ground_y + 16)],
        [(180, ground_y + 25), (250, ground_y + 30), (350, ground_y + 28), (420, ground_y + 32)],
    ]
    for path in cable_paths:
        cable_color = random.choice([CABLE_BLACK, CABLE_DARK, (20, 15, 12)])
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            d.line([x1, y1, x2, y2], fill=cable_color, width=2)
        # XLR connector at end
        ex, ey = path[-1]
        d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=MIC_CHROME)

    # ── Pyro flame pots ──
    pyro_positions = [100, 300, 500]
    for px in pyro_positions:
        py = ground_y - 5
        # Pot base
        d.rectangle([px - 5, py, px + 5, py + 6], fill=PYRO_BASE)
        d.rectangle([px - 6, py + 6, px + 6, py + 8], fill=PYRO_BASE)
        # Flame (randomized tongues)
        for _ in range(5):
            fx = px + random.randint(-4, 4)
            flame_h = random.randint(8, 22)
            fy = py - flame_h
            flame_c = random.choice([PYRO_FLAME_1, PYRO_FLAME_2, PYRO_FLAME_3])
            d.line([fx, py, fx, fy], fill=flame_c, width=2)
            # Flame tip (thinner)
            d.line([fx, fy, fx + random.randint(-2, 2), fy - 4], fill=PYRO_FLAME_1, width=1)
        # Glow on ground
        for gx in range(px - 8, px + 9):
            if 0 <= gx < W:
                for gy in range(py + 8, min(py + 14, H)):
                    r0, g0, b0, a0 = img.getpixel((gx, gy))
                    if a0 > 0:
                        img.putpixel((gx, gy), (min(r0 + 30, 255), min(g0 + 15, 255), b0, a0))

    # ── Mic stand (center stage) ──
    mic_x = W // 2 + 20
    mic_base_y = ground_y - 2
    mic_top_y = ground_y - 55

    # Base (tripod feet)
    d.line([mic_x - 8, mic_base_y, mic_x, mic_base_y - 4], fill=MIC_CHROME, width=2)
    d.line([mic_x + 8, mic_base_y, mic_x, mic_base_y - 4], fill=MIC_CHROME, width=2)
    d.line([mic_x, mic_base_y, mic_x, mic_base_y - 4], fill=MIC_CHROME, width=2)
    # Pole
    d.line([mic_x, mic_base_y - 4, mic_x, mic_top_y], fill=MIC_CHROME, width=2)
    # Mic clip
    d.rectangle([mic_x - 1, mic_top_y - 2, mic_x + 1, mic_top_y], fill=MIC_BLACK)
    # Mic head (sphere)
    d.ellipse([mic_x - 4, mic_top_y - 10, mic_x + 4, mic_top_y - 2], fill=MIC_BLACK)
    d.ellipse([mic_x - 3, mic_top_y - 9, mic_x + 3, mic_top_y - 3],
              outline=MIC_CHROME)
    # Cable drooping from mic
    for i in range(15):
        t = i / 15
        cx = mic_x + int(8 * math.sin(t * math.pi))
        cy = mic_top_y + int(i * 2)
        if 0 <= cx < W and 0 <= cy < H:
            d.point([cx, cy], fill=CABLE_BLACK)

    # ── Gaffer tape marks on stage ──
    for _ in range(4):
        tx = random.randint(50, W - 50)
        ty = random.randint(ground_y + 5, H - 10)
        tw = random.randint(15, 40)
        d.rectangle([tx, ty, tx + tw, ty + 1], fill=(160, 160, 165, 200))

    out = OUTPUT_DIR / "parallax_concert_near.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def main():
    print("Generating Led Zeppelin Concert parallax layers...")
    create_sky_layer()
    create_mid_layer()
    create_near_layer()
    print("Done!")


if __name__ == "__main__":
    main()
