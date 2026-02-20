#!/usr/bin/env python3
"""Post-process enhancement pass for Disco Cop enemy sprites.

Adds visual depth and thematic effects:
  - Drop shadows for better silhouette reads
  - Edge highlighting for definition
  - Disco sparkle/shimmer for L5 enemies
  - Punk grit/distress for L3-L4 enemies
  - Subtle sub-pixel shading for all from-scratch sprites

Usage:
    python enhance_sprites.py
"""

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
ENEMY_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "enemies"
BOSS_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "bosses"

random.seed(777)


# ── Enhancement helpers ──────────────────────────────────────────────────────

def add_drop_shadow(img, offset=(1, 1), shadow_color=(0, 0, 0, 60)):
    """Add a subtle drop shadow under opaque pixels."""
    px = np.array(img)
    h, w, _ = px.shape
    result = px.copy()
    ox, oy = offset

    for y in range(h):
        for x in range(w):
            if px[y, x, 3] > 20:
                sy, sx = y + oy, x + ox
                if 0 <= sy < h and 0 <= sx < w and result[sy, sx, 3] < 10:
                    result[sy, sx] = shadow_color

    return Image.fromarray(result.astype(np.uint8), "RGBA")


def add_edge_highlight(img, highlight_color=(255, 255, 255, 40)):
    """Add subtle bright pixels along top edges of opaque regions."""
    px = np.array(img)
    h, w, _ = px.shape
    result = px.copy()

    for y in range(1, h):
        for x in range(w):
            if px[y, x, 3] > 50 and px[y - 1, x, 3] < 10:
                # Top edge — add highlight
                cr, cg, cb, ca = result[y, x]
                hr, hg, hb, ha = highlight_color
                blend = ha / 255.0
                result[y, x, 0] = min(int(cr + hr * blend), 255)
                result[y, x, 1] = min(int(cg + hg * blend), 255)
                result[y, x, 2] = min(int(cb + hb * blend), 255)

    return Image.fromarray(result.astype(np.uint8), "RGBA")


def add_disco_sparkle(img, density=0.03):
    """Add random bright sparkle pixels to opaque areas (disco theme)."""
    px = np.array(img)
    h, w, _ = px.shape
    result = px.copy()

    sparkle_colors = [
        (255, 255, 255),  # White
        (255, 240, 100),  # Gold
        (200, 220, 255),  # Ice blue
        (255, 200, 255),  # Pink
    ]

    for y in range(h):
        for x in range(w):
            if px[y, x, 3] > 100 and random.random() < density:
                sc = random.choice(sparkle_colors)
                result[y, x, 0] = sc[0]
                result[y, x, 1] = sc[1]
                result[y, x, 2] = sc[2]

    return Image.fromarray(result.astype(np.uint8), "RGBA")


def add_punk_grit(img, density=0.02):
    """Add dark speckle/grit pixels to opaque areas (punk theme)."""
    px = np.array(img)
    h, w, _ = px.shape
    result = px.copy()

    for y in range(h):
        for x in range(w):
            if px[y, x, 3] > 100 and random.random() < density:
                # Darken the pixel (grit/dirt)
                darken = random.randint(30, 60)
                result[y, x, 0] = max(int(result[y, x, 0]) - darken, 0)
                result[y, x, 1] = max(int(result[y, x, 1]) - darken, 0)
                result[y, x, 2] = max(int(result[y, x, 2]) - darken, 0)

    return Image.fromarray(result.astype(np.uint8), "RGBA")


def add_bottom_shadow(img, frame_w):
    """Add a ground shadow line at the bottom of each frame."""
    px = np.array(img)
    h, w, _ = px.shape
    result = px.copy()

    n_frames = w // frame_w

    for f in range(n_frames):
        fx_start = f * frame_w
        fx_end = fx_start + frame_w

        # Find the lowest opaque pixel in this frame
        bottom_y = 0
        left_x = frame_w
        right_x = 0
        for y in range(h - 1, -1, -1):
            for x in range(fx_start, fx_end):
                if px[y, x, 3] > 20:
                    if y > bottom_y:
                        bottom_y = y
                    if x - fx_start < left_x:
                        left_x = x - fx_start
                    if x - fx_start > right_x:
                        right_x = x - fx_start

        # Draw a small shadow ellipse at the bottom
        shadow_y = min(bottom_y + 1, h - 1)
        shadow_cx = fx_start + (left_x + right_x) // 2
        shadow_hw = max((right_x - left_x) // 3, 2)

        for sx in range(shadow_cx - shadow_hw, shadow_cx + shadow_hw + 1):
            if fx_start <= sx < fx_end and 0 <= shadow_y < h:
                if result[shadow_y, sx, 3] < 10:
                    dist = abs(sx - shadow_cx) / max(shadow_hw, 1)
                    alpha = int(40 * (1 - dist))
                    result[shadow_y, sx] = [0, 0, 0, alpha]

    return Image.fromarray(result.astype(np.uint8), "RGBA")


# ── Enhancement configurations ───────────────────────────────────────────────

# L3 Concert enemies (punk theme — groupie, pyrotech, roadie, speaker)
CONCERT_SPRITES = [
    "groupie_skate_sheet.png", "groupie_shoot_skate_sheet.png",
    "groupie_hurt_sheet.png", "groupie_death_sheet.png",
    "pyrotech_skate_sheet.png", "pyrotech_shoot_skate_sheet.png",
    "pyrotech_hurt_sheet.png", "pyrotech_death_sheet.png",
    "roadie_walk_sheet.png", "roadie_charge_sheet.png",
    "roadie_hurt_sheet.png", "roadie_death_sheet.png",
    "speaker_walk_sheet.png", "speaker_attack_sheet.png",
    "speaker_hurt_sheet.png", "speaker_death_sheet.png",
]

# L4 CBGB enemies (punk theme — bottle thrower, pogo punk, bouncer, stage diver)
CBGB_SPRITES = [
    "bottle_thrower_walk_sheet.png", "bottle_thrower_attack_sheet.png",
    "bottle_thrower_hurt_sheet.png", "bottle_thrower_death_sheet.png",
    "pogo_punk_walk_sheet.png", "pogo_punk_attack_sheet.png",
    "pogo_punk_hurt_sheet.png", "pogo_punk_death_sheet.png",
    "bouncer_walk_sheet.png", "bouncer_attack_sheet.png",
    "bouncer_hurt_sheet.png", "bouncer_death_sheet.png",
    "stage_diver_walk_sheet.png", "stage_diver_charge_sheet.png",
    "stage_diver_hurt_sheet.png", "stage_diver_death_sheet.png",
]

# L5 Disco Floor enemies (disco theme — disco dancer, floor bouncer, mirror ball)
DISCO_SPRITES = [
    "disco_dancer_walk_sheet.png", "disco_dancer_attack_sheet.png",
    "disco_dancer_hurt_sheet.png", "disco_dancer_death_sheet.png",
    "floor_bouncer_walk_sheet.png", "floor_bouncer_attack_sheet.png",
    "floor_bouncer_hurt_sheet.png", "floor_bouncer_death_sheet.png",
    "mirror_ball_walk_sheet.png", "mirror_ball_attack_sheet.png",
    "mirror_ball_hurt_sheet.png", "mirror_ball_death_sheet.png",
]


def enhance_sprite(filepath, theme="neutral"):
    """Apply enhancement stack to a sprite sheet."""
    if not filepath.exists():
        return False

    img = Image.open(filepath).convert("RGBA")
    w, h = img.size

    # Determine frame width from height (square-ish frames or known ratios)
    # Estimate: single frame is roughly as wide as the sprite is tall
    frame_w = h  # Default guess

    # Common known sizes
    if h == 40:
        frame_w = 20
    elif h == 55:
        frame_w = 30
    elif h == 50:
        frame_w = 30
    elif h == 48:
        frame_w = 26
    elif h == 24:
        frame_w = 24
    elif h == 42:
        frame_w = 20
    elif h == 45:
        frame_w = 20
    elif h == 100:
        frame_w = 50

    # Step 1: Edge highlight (subtle top-edge brightening)
    img = add_edge_highlight(img)

    # Step 2: Drop shadow
    img = add_drop_shadow(img)

    # Step 3: Ground shadow
    img = add_bottom_shadow(img, frame_w)

    # Step 4: Theme-specific effects
    if theme == "punk":
        img = add_punk_grit(img, density=0.015)
    elif theme == "disco":
        img = add_disco_sparkle(img, density=0.025)

    img.save(filepath)
    return True


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Enhancing L3-L5 sprites with shading and thematic effects...\n")

    count = 0

    print("L3 Concert enemies (punk grit):")
    for name in CONCERT_SPRITES:
        path = ENEMY_DIR / name
        if enhance_sprite(path, theme="punk"):
            print(f"  [OK] {name}")
            count += 1

    print("\nL4 CBGB enemies (punk grit):")
    for name in CBGB_SPRITES:
        path = ENEMY_DIR / name
        if enhance_sprite(path, theme="punk"):
            print(f"  [OK] {name}")
            count += 1

    print("\nL5 Disco Floor enemies (disco sparkle):")
    for name in DISCO_SPRITES:
        path = ENEMY_DIR / name
        if enhance_sprite(path, theme="disco"):
            print(f"  [OK] {name}")
            count += 1

    print(f"\nDone! {count} sprite sheets enhanced.")


if __name__ == "__main__":
    main()
