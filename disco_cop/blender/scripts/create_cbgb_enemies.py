#!/usr/bin/env python3
"""Generate CBGB Blondie Concert enemy sprites for Disco Cop Level 04.

Palette-swap enemies (from shooter sheets, 20x40/frame):
  - Bottle Thrower: dark teal/green punk outfit, bandana
  - Pogo Punk: neon yellow/green mohawk, ripped black vest

From-scratch enemies:
  - Bouncer (30x55/frame): black suit, shaved head, earpiece, big build
  - Stage Diver (20x42/frame): shirtless, ripped jeans, leaping dive

Usage:
    python create_cbgb_enemies.py
"""

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
ENEMY_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "enemies"

random.seed(812)

# -- Palette-swap remap functions ----------------------------------------------


def remap_bottle_thrower(r, g, b, a):
    """Shooter -> Bottle Thrower: dark teal shirt, green cargo pants, olive accents."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 130:
        # Light body -> dark teal shirt
        return (max(int(r * 0.3), 20), min(int(g * 1.0), 140), min(int(b * 1.2), 150), a)
    elif is_gray and brightness > 80:
        # Mid body -> darker green cargo pants
        return (max(int(r * 0.4), 30), min(int(g * 0.8), 100), max(int(b * 0.4), 40), a)
    elif brightness > 100 and r > g:
        # Warm accents -> olive/brown bandana accents
        return (min(int(r * 0.8), 160), min(int(g * 0.9), 140), max(int(b * 0.4), 40), a)
    elif brightness > 50:
        # Mid tones -> teal-tinted skin shadow
        return (min(int(r * 0.9), 160), min(int(g * 1.0), 155), min(int(b * 0.9), 130), a)
    else:
        # Dark (outlines, hair) -> keep dark with teal tint
        return (r, min(g + 8, 50), min(b + 12, 65), a)


def remap_pogo_punk(r, g, b, a):
    """Shooter -> Pogo Punk: neon yellow/green mohawk, ripped black vest."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 130:
        # Light body -> neon yellow/green
        return (min(int(r * 1.2), 230), min(int(g * 1.4), 255), max(int(b * 0.2), 15), a)
    elif is_gray and brightness > 80:
        # Mid body -> ripped black vest
        return (max(int(r * 0.25), 18), max(int(g * 0.25), 18), max(int(b * 0.3), 22), a)
    elif brightness > 100 and r > g:
        # Warm accents -> bright orange/yellow skin accents
        return (min(int(r * 1.4), 255), min(int(g * 1.1), 200), max(int(b * 0.2), 15), a)
    elif brightness > 50:
        # Mid tones -> pale punk skin
        return (min(int(r * 1.1), 200), min(int(g * 1.0), 170), max(int(b * 0.8), 100), a)
    else:
        # Dark (outlines) -> keep dark
        return (r, g, b, a)


def swap_explicit(mappings, remap_fn):
    """Apply remap function to source sheets with explicit src->dst name mapping.

    mappings: list of (src_name, dst_name) tuples.
    """
    for src_name, dst_name in mappings:
        src_path = ENEMY_DIR / src_name
        if not src_path.exists():
            print(f"  [SKIP] {src_name} -- not found")
            continue

        img = Image.open(src_path).convert("RGBA")
        px = np.array(img)
        h, w, _ = px.shape
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[y, x]
                px[y, x] = remap_fn(int(r), int(g), int(b), int(a))

        dst_path = ENEMY_DIR / dst_name
        Image.fromarray(px.astype(np.uint8), "RGBA").save(dst_path)
        print(f"  [OK] {dst_name}")


# -- From-scratch enemies -----------------------------------------------------

# Bouncer palette (30x55)
BOUNCER_SKIN = (185, 145, 120)
BOUNCER_SKIN_SHADOW = (150, 115, 90)
BOUNCER_SUIT = (20, 20, 25)
BOUNCER_SUIT_LIGHT = (35, 35, 42)
BOUNCER_SHIRT = (230, 230, 235)
BOUNCER_SHIRT_SHADOW = (190, 190, 200)
BOUNCER_HEAD = (110, 85, 65)
BOUNCER_HEAD_STUBBLE = (90, 70, 52)
BOUNCER_EARPIECE = (50, 55, 70)
BOUNCER_EARPIECE_LIGHT = (80, 85, 100)
BOUNCER_SHOES = (15, 15, 18)
BOUNCER_SHOES_SOLE = (40, 38, 35)
BOUNCER_OUTLINE = (10, 8, 8)

# Stage Diver palette (20x42)
DIVER_SKIN = (200, 165, 135)
DIVER_SKIN_SHADOW = (170, 135, 105)
DIVER_JEANS = (60, 70, 120)
DIVER_JEANS_RIP = (140, 130, 115)
DIVER_JEANS_DARK = (40, 48, 90)
DIVER_SNEAKER = (230, 230, 230)
DIVER_SNEAKER_SOLE = (60, 60, 65)
DIVER_HAIR = (70, 50, 30)
DIVER_HAIR_LIGHT = (100, 75, 45)
DIVER_OUTLINE = (15, 10, 10)


# -- Bouncer (30x55) ----------------------------------------------------------


def draw_bouncer_frame(img, x_off, y_off, fw, fh, pose="stand", frame=0):
    """Draw a single bouncer frame at given offset. 30x55."""
    d = ImageDraw.Draw(img)
    cx = x_off + fw // 2
    head_y = y_off + 3
    torso_y = y_off + 17
    hip_y = y_off + 34
    foot_y = y_off + fh - 4

    # Pose offsets
    if pose == "walk":
        leg_offsets = [(-3, 3), (3, -3), (-2, 2), (2, -2)]
        lo = leg_offsets[frame % 4]
        arm_swing = [(-2, 2), (2, -2), (-1, 1), (1, -1)]
        ao = arm_swing[frame % 4]
    elif pose == "attack":
        # Heavy punch: wind up, extend, connect, pull back
        lo = (0, 0)
        punch_ext = [0, 5, 8, 3][frame % 4]
        ao = (punch_ext, -1)
    elif pose == "hurt":
        lo = (0, 0)
        ao = (2, -2) if frame == 0 else (-2, 2)
    elif pose == "death":
        collapse = min(frame, 3)
        lo = (0, 0)
        ao = (collapse * 2, -collapse)
        torso_y += collapse * 3
        hip_y += collapse * 4
        foot_y = min(foot_y + collapse * 2, y_off + fh - 1)
        head_y += collapse * 4
    else:
        lo = (0, 0)
        ao = (0, 0)

    # -- Head (shaved, thick neck) --
    head_w, head_h = 10, 10
    # Thick neck first (drawn behind head)
    neck_w = 8
    if pose != "death" or frame < 3:
        d.rectangle([cx - neck_w // 2, head_y + head_h - 2, cx + neck_w // 2, torso_y + 1],
                    fill=BOUNCER_SKIN, outline=BOUNCER_OUTLINE)
    # Head ellipse
    d.ellipse([cx - head_w // 2, head_y, cx + head_w // 2, head_y + head_h],
              fill=BOUNCER_SKIN, outline=BOUNCER_OUTLINE)
    # Shaved head stubble (close crop on top half)
    d.arc([cx - head_w // 2, head_y, cx + head_w // 2, head_y + head_h],
          200, 340, fill=BOUNCER_HEAD_STUBBLE, width=2)
    # Brow ridge (tough look)
    d.line([cx - 3, head_y + 4, cx + 3, head_y + 4], fill=BOUNCER_OUTLINE, width=1)
    # Eyes (small, stern)
    d.point([cx - 2, head_y + 5], fill=BOUNCER_OUTLINE)
    d.point([cx + 2, head_y + 5], fill=BOUNCER_OUTLINE)
    # Earpiece (small dot on right side)
    d.point([cx + head_w // 2 - 1, head_y + 5], fill=BOUNCER_EARPIECE)
    d.point([cx + head_w // 2, head_y + 5], fill=BOUNCER_EARPIECE_LIGHT)
    # Earpiece wire down neck
    if pose != "death" or frame < 2:
        d.line([cx + head_w // 2 - 1, head_y + 6, cx + neck_w // 2 - 1, torso_y],
               fill=BOUNCER_EARPIECE, width=1)

    # -- Torso (broad black suit jacket) --
    torso_w = 16
    d.rectangle([cx - torso_w // 2, torso_y, cx + torso_w // 2, hip_y],
                fill=BOUNCER_SUIT, outline=BOUNCER_OUTLINE)
    # Suit jacket lapels
    d.line([cx - 2, torso_y, cx - 4, torso_y + 8], fill=BOUNCER_SUIT_LIGHT, width=1)
    d.line([cx + 2, torso_y, cx + 4, torso_y + 8], fill=BOUNCER_SUIT_LIGHT, width=1)
    # White shirt collar peeking at top
    d.rectangle([cx - 3, torso_y, cx + 3, torso_y + 2], fill=BOUNCER_SHIRT)
    d.point([cx, torso_y + 1], fill=BOUNCER_SHIRT_SHADOW)
    # Suit button
    d.point([cx, torso_y + 6], fill=BOUNCER_SUIT_LIGHT)
    d.point([cx, torso_y + 10], fill=BOUNCER_SUIT_LIGHT)

    # -- Arms (suit sleeves, big fists) --
    arm_y = torso_y + 2
    arm_len = 14
    if pose == "death" and frame >= 2:
        d.rectangle([cx - torso_w // 2 - 5, arm_y + 4, cx - torso_w // 2, arm_y + 8],
                     fill=BOUNCER_SUIT, outline=BOUNCER_OUTLINE)
        d.rectangle([cx + torso_w // 2, arm_y + 4, cx + torso_w // 2 + 5, arm_y + 8],
                     fill=BOUNCER_SUIT, outline=BOUNCER_OUTLINE)
    else:
        # Left arm (suit sleeve)
        la_end_y = arm_y + arm_len + ao[0]
        d.line([cx - torso_w // 2, arm_y, cx - torso_w // 2 - 3, la_end_y],
               fill=BOUNCER_SUIT, width=3)
        # Big fist
        d.rectangle([cx - torso_w // 2 - 5, la_end_y - 2, cx - torso_w // 2 - 1, la_end_y + 2],
                     fill=BOUNCER_SKIN, outline=BOUNCER_OUTLINE)
        # Right arm
        ra_end_y = arm_y + arm_len + ao[1]
        d.line([cx + torso_w // 2, arm_y, cx + torso_w // 2 + 3, ra_end_y],
               fill=BOUNCER_SUIT, width=3)
        # Big fist
        d.rectangle([cx + torso_w // 2 + 1, ra_end_y - 2, cx + torso_w // 2 + 5, ra_end_y + 2],
                     fill=BOUNCER_SKIN, outline=BOUNCER_OUTLINE)

    # -- Legs (suit pants, dress shoes) --
    leg_w = 6
    if pose == "death" and frame >= 3:
        d.rectangle([cx - 7, hip_y, cx + 7, hip_y + 4], fill=BOUNCER_SUIT)
    else:
        # Left leg
        ll_x = cx - 5 + lo[0]
        d.rectangle([ll_x - leg_w // 2, hip_y, ll_x + leg_w // 2, foot_y],
                    fill=BOUNCER_SUIT, outline=BOUNCER_OUTLINE)
        # Right leg
        rl_x = cx + 5 + lo[1]
        d.rectangle([rl_x - leg_w // 2, hip_y, rl_x + leg_w // 2, foot_y],
                    fill=BOUNCER_SUIT, outline=BOUNCER_OUTLINE)

        # Dress shoes
        d.rectangle([ll_x - leg_w // 2 - 1, foot_y - 2, ll_x + leg_w // 2 + 1, foot_y + 1],
                    fill=BOUNCER_SHOES)
        d.rectangle([ll_x - leg_w // 2, foot_y, ll_x + leg_w // 2, foot_y + 1],
                    fill=BOUNCER_SHOES_SOLE)
        d.rectangle([rl_x - leg_w // 2 - 1, foot_y - 2, rl_x + leg_w // 2 + 1, foot_y + 1],
                    fill=BOUNCER_SHOES)
        d.rectangle([rl_x - leg_w // 2, foot_y, rl_x + leg_w // 2, foot_y + 1],
                    fill=BOUNCER_SHOES_SOLE)

    # Hurt flash
    if pose == "hurt":
        d.rectangle([cx - 3, torso_y + 3, cx + 3, torso_y + 8],
                     fill=(255, 255, 255, 80))

    # Attack: impact spark on punch connect
    if pose == "attack" and frame == 2:
        fist_x = cx + torso_w // 2 + 6
        fist_y = arm_y + arm_len + ao[1]
        d.point([fist_x + 1, fist_y], fill=(255, 255, 200, 200))
        d.point([fist_x + 2, fist_y - 1], fill=(255, 255, 150, 150))
        d.point([fist_x + 2, fist_y + 1], fill=(255, 255, 150, 150))


def create_bouncer_sheets():
    """Generate bouncer sprite sheets."""
    fw, fh = 30, 55

    sheets = {
        "bouncer_walk_sheet.png": ("walk", 4),
        "bouncer_attack_sheet.png": ("attack", 4),
        "bouncer_hurt_sheet.png": ("hurt", 2),
        "bouncer_death_sheet.png": ("death", 4),
    }

    for name, (pose, nframes) in sheets.items():
        img = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))
        for f in range(nframes):
            draw_bouncer_frame(img, f * fw, 0, fw, fh, pose, f)
        path = ENEMY_DIR / name
        img.save(path)
        print(f"  [OK] {name}")


# -- Stage Diver (20x42) ------------------------------------------------------


def draw_stage_diver_frame(img, x_off, y_off, fw, fh, pose="stand", frame=0):
    """Draw a single stage diver frame at given offset. 20x42."""
    d = ImageDraw.Draw(img)
    cx = x_off + fw // 2
    head_y = y_off + 4
    torso_y = y_off + 15
    hip_y = y_off + 26
    foot_y = y_off + fh - 3

    # Forward lean for charge (leaping dive)
    lean = 0
    dive_y_shift = 0
    if pose == "charge":
        lean = [1, 3, 5, 4][frame % 4]
        dive_y_shift = [0, -3, -5, -2][frame % 4]

    # Pose offsets
    if pose == "walk":
        leg_offsets = [(-2, 2), (2, -2), (-1, 1), (1, -1), (-2, 2), (2, -2)]
        lo = leg_offsets[frame % 6]
        arm_swing = [(-2, 2), (2, -2), (-1, 1), (1, -1), (-2, 2), (2, -2)]
        ao = arm_swing[frame % 6]
    elif pose == "charge":
        # Arms stretched forward for diving
        lo = [(-3, 3), (3, -3), (-2, 2), (2, -2)][frame % 4]
        ao = [(-5, -5), (-6, -6), (-7, -7), (-5, -5)][frame % 4]
    elif pose == "hurt":
        lo = (0, 0)
        ao = (3, -3) if frame == 0 else (-3, 3)
    elif pose == "death":
        collapse = min(frame, 3)
        lo = (0, 0)
        ao = (collapse * 2, -collapse)
        torso_y += collapse * 3
        hip_y += collapse * 3
        foot_y = min(foot_y + collapse * 2, y_off + fh - 1)
        head_y += collapse * 4
    else:
        lo = (0, 0)
        ao = (0, 0)

    # Adjust for dive lean
    head_x_shift = lean
    torso_x_shift = lean // 2
    body_y_shift = dive_y_shift

    # Apply vertical shift for dive arc
    head_y += body_y_shift
    torso_y += body_y_shift
    hip_y += body_y_shift

    # -- Messy hair --
    if pose != "death" or frame < 3:
        hair_base_y = head_y - 1
        hcx = cx + head_x_shift
        for sx in range(-3, 4):
            hair_x = hcx + sx
            hair_h = random.randint(2, 5)
            d.line([hair_x, hair_base_y, hair_x, hair_base_y - hair_h],
                   fill=DIVER_HAIR, width=1)
            if random.random() > 0.5:
                d.point([hair_x, hair_base_y - hair_h], fill=DIVER_HAIR_LIGHT)

    # -- Head (ellipse) --
    head_w, head_h = 7, 8
    hcx = cx + head_x_shift
    d.ellipse([hcx - head_w // 2, head_y, hcx + head_w // 2, head_y + head_h],
              fill=DIVER_SKIN, outline=DIVER_OUTLINE)
    # Eyes
    d.point([hcx - 2, head_y + 4], fill=DIVER_OUTLINE)
    d.point([hcx + 1, head_y + 4], fill=DIVER_OUTLINE)
    # Mouth (open yell for charge)
    if pose == "charge":
        d.rectangle([hcx - 1, head_y + 6, hcx + 1, head_y + 7], fill=DIVER_OUTLINE)
    else:
        d.point([hcx, head_y + 6], fill=DIVER_OUTLINE)

    # -- Torso (shirtless - bare skin upper body) --
    torso_w = 9
    tcx = cx + torso_x_shift
    d.rectangle([tcx - torso_w // 2, torso_y, tcx + torso_w // 2, hip_y],
                fill=DIVER_SKIN, outline=DIVER_OUTLINE)
    # Chest definition (subtle shadow lines for lean build)
    d.line([tcx, torso_y + 1, tcx, torso_y + 4], fill=DIVER_SKIN_SHADOW, width=1)
    # Navel
    d.point([tcx, hip_y - 2], fill=DIVER_SKIN_SHADOW)
    # Subtle rib shadow for lean look
    d.point([tcx - 3, torso_y + 5], fill=DIVER_SKIN_SHADOW)
    d.point([tcx + 3, torso_y + 5], fill=DIVER_SKIN_SHADOW)

    # -- Arms (bare skin) --
    arm_y = torso_y + 1
    arm_len = 10
    if pose == "death" and frame >= 2:
        d.rectangle([tcx - torso_w // 2 - 4, arm_y + 3, tcx - torso_w // 2, arm_y + 6],
                     fill=DIVER_SKIN, outline=DIVER_OUTLINE)
        d.rectangle([tcx + torso_w // 2, arm_y + 3, tcx + torso_w // 2 + 4, arm_y + 6],
                     fill=DIVER_SKIN, outline=DIVER_OUTLINE)
    else:
        # Left arm
        la_end_y = arm_y + arm_len + ao[0]
        d.line([tcx - torso_w // 2, arm_y, tcx - torso_w // 2 - 2, la_end_y],
               fill=DIVER_SKIN, width=2)
        d.point([tcx - torso_w // 2 - 2, la_end_y], fill=DIVER_SKIN_SHADOW)
        # Right arm
        ra_end_y = arm_y + arm_len + ao[1]
        d.line([tcx + torso_w // 2, arm_y, tcx + torso_w // 2 + 2, ra_end_y],
               fill=DIVER_SKIN, width=2)
        d.point([tcx + torso_w // 2 + 2, ra_end_y], fill=DIVER_SKIN_SHADOW)

    # -- Legs (ripped blue jeans) --
    leg_w = 4
    if pose == "death" and frame >= 3:
        d.rectangle([cx - 5, hip_y, cx + 5, hip_y + 3], fill=DIVER_JEANS)
    else:
        # Left leg
        ll_x = cx + lo[0]
        d.rectangle([ll_x - leg_w // 2 - 1, hip_y, ll_x + leg_w // 2, foot_y],
                    fill=DIVER_JEANS, outline=DIVER_OUTLINE)
        # Rip detail (skin showing through)
        rip_y = hip_y + (foot_y - hip_y) // 2
        d.rectangle([ll_x - 1, rip_y, ll_x + 1, rip_y + 2], fill=DIVER_JEANS_RIP)
        # Right leg
        rl_x = cx + lo[1]
        d.rectangle([rl_x - leg_w // 2, hip_y, rl_x + leg_w // 2 + 1, foot_y],
                    fill=DIVER_JEANS, outline=DIVER_OUTLINE)
        # Rip on right leg too
        rip_y2 = hip_y + (foot_y - hip_y) * 2 // 3
        d.rectangle([rl_x - 1, rip_y2, rl_x + 1, rip_y2 + 1], fill=DIVER_JEANS_RIP)

        # Sneakers (white with dark sole)
        d.rectangle([ll_x - leg_w // 2 - 1, foot_y - 2, ll_x + leg_w // 2 + 1, foot_y + 1],
                    fill=DIVER_SNEAKER)
        d.rectangle([ll_x - leg_w // 2 - 1, foot_y, ll_x + leg_w // 2 + 1, foot_y + 1],
                    fill=DIVER_SNEAKER_SOLE)
        d.rectangle([rl_x - leg_w // 2 - 1, foot_y - 2, rl_x + leg_w // 2 + 1, foot_y + 1],
                    fill=DIVER_SNEAKER)
        d.rectangle([rl_x - leg_w // 2 - 1, foot_y, rl_x + leg_w // 2 + 1, foot_y + 1],
                    fill=DIVER_SNEAKER_SOLE)

    # Hurt flash
    if pose == "hurt":
        d.rectangle([cx - 2, torso_y + 2, cx + 2, torso_y + 6],
                     fill=(255, 255, 255, 80))

    # Charge: motion lines behind diver
    if pose == "charge" and frame >= 1:
        for _ in range(3):
            dx = cx - lean - random.randint(3, 8)
            dy = torso_y + random.randint(-2, 8)
            d.line([dx, dy, dx - random.randint(2, 4), dy],
                   fill=(180, 180, 180, 100), width=1)


def create_stage_diver_sheets():
    """Generate stage diver sprite sheets."""
    fw, fh = 20, 42

    sheets = {
        "stage_diver_walk_sheet.png": ("walk", 6),
        "stage_diver_charge_sheet.png": ("charge", 4),
        "stage_diver_hurt_sheet.png": ("hurt", 2),
        "stage_diver_death_sheet.png": ("death", 4),
    }

    for name, (pose, nframes) in sheets.items():
        img = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))
        for f in range(nframes):
            draw_stage_diver_frame(img, f * fw, 0, fw, fh, pose, f)
        path = ENEMY_DIR / name
        img.save(path)
        print(f"  [OK] {name}")


# -- Main ---------------------------------------------------------------------


def main():
    print("Generating CBGB enemies (Level 04 -- Blondie Concert)...")

    print("\nBottle Thrower (palette-swap from shooter):")
    swap_explicit([
        ("shooter_skate_sheet.png", "bottle_thrower_walk_sheet.png"),
        ("shooter_shoot_skate_sheet.png", "bottle_thrower_attack_sheet.png"),
        ("shooter_hurt_sheet.png", "bottle_thrower_hurt_sheet.png"),
        ("shooter_death_sheet.png", "bottle_thrower_death_sheet.png"),
    ], remap_bottle_thrower)

    print("\nPogo Punk (palette-swap from shooter):")
    swap_explicit([
        ("shooter_skate_sheet.png", "pogo_punk_walk_sheet.png"),
        ("shooter_shoot_skate_sheet.png", "pogo_punk_attack_sheet.png"),
        ("shooter_hurt_sheet.png", "pogo_punk_hurt_sheet.png"),
        ("shooter_death_sheet.png", "pogo_punk_death_sheet.png"),
    ], remap_pogo_punk)

    print("\nBouncer (from scratch):")
    create_bouncer_sheets()

    print("\nStage Diver (from scratch):")
    create_stage_diver_sheets()

    print("\nDone! CBGB enemies generated.")


if __name__ == "__main__":
    main()
