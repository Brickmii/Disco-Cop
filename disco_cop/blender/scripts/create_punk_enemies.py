#!/usr/bin/env python3
"""Generate CBGB Punk Alley enemy sprites for Disco Cop Level 04.

Palette-swap enemy (from shooter sheets, 20x40/frame):
  - Spray Painter: cyan/teal graffiti artist

From-scratch enemies:
  - Punk Rocker (20x45/frame): green mohawk, ripped band tee, plaid pants
  - Mohawk Diver (20x42/frame): red mohawk, sleeveless vest, aggressive lean
  - Biker (35x55/frame): leather jacket, helmet/bandana, chains, big build

Usage:
    python create_punk_enemies.py
"""

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
ENEMY_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "enemies"

random.seed(808)

# ── Palette-swap remap functions ──────────────────────────────────────────────


def remap_spray_painter(r, g, b, a):
    """Shooter → Spray Painter: cyan shirt, dark denim, teal accents."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 130:
        # Light body → bright cyan shirt
        return (max(int(r * 0.3), 20), min(int(g * 1.3), 230), min(int(b * 1.4), 240), a)
    elif is_gray and brightness > 80:
        # Mid body → dark denim blue jeans
        return (max(int(r * 0.4), 30), max(int(g * 0.5), 45), min(int(b * 1.2), 140), a)
    elif brightness > 100 and r > g:
        # Warm accents → spray paint splatter (magenta/pink)
        return (min(int(r * 1.3), 255), max(int(g * 0.3), 40), min(int(b * 1.4), 220), a)
    elif brightness > 50:
        # Mid tones → teal-tinted skin shadow
        return (min(int(r * 0.9), 160), min(int(g * 1.1), 170), min(int(b * 1.0), 140), a)
    else:
        # Dark (outlines, hair) → keep dark with slight teal
        return (r, min(g + 10, 55), min(b + 15, 70), a)


def swap_explicit(mappings, remap_fn):
    """Apply remap function to source sheets with explicit src→dst name mapping.

    mappings: list of (src_name, dst_name) tuples.
    """
    for src_name, dst_name in mappings:
        src_path = ENEMY_DIR / src_name
        if not src_path.exists():
            print(f"  [SKIP] {src_name} — not found")
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


# ── From-scratch enemies ─────────────────────────────────────────────────────

# Punk Rocker palette (20x45)
PUNK_SKIN = (210, 175, 145)
PUNK_SKIN_SHADOW = (175, 140, 110)
PUNK_MOHAWK = (50, 200, 50)
PUNK_MOHAWK_TIP = (80, 255, 80)
PUNK_SHIRT = (25, 25, 25)
PUNK_SHIRT_PRINT = (200, 60, 60)
PUNK_PANTS = (160, 40, 40)
PUNK_PANTS_PLAID = (50, 50, 50)
PUNK_BOOTS = (30, 25, 25)
PUNK_BOOTS_SOLE = (50, 45, 40)
PUNK_OUTLINE = (15, 10, 10)

# Mohawk Diver palette (20x42)
DIVER_SKIN = (195, 160, 130)
DIVER_SKIN_SHADOW = (160, 125, 95)
DIVER_MOHAWK = (200, 35, 35)
DIVER_MOHAWK_TIP = (255, 60, 60)
DIVER_VEST = (60, 65, 90)
DIVER_VEST_DARK = (40, 45, 65)
DIVER_JEANS = (70, 75, 100)
DIVER_JEANS_RIP = (140, 130, 110)
DIVER_BOOTS = (35, 30, 25)
DIVER_OUTLINE = (15, 10, 10)

# Biker palette (35x55)
BIKER_SKIN = (175, 135, 105)
BIKER_SKIN_SHADOW = (140, 105, 80)
BIKER_LEATHER = (30, 25, 20)
BIKER_LEATHER_LIGHT = (55, 45, 35)
BIKER_HELMET = (40, 40, 45)
BIKER_HELMET_VISOR = (80, 85, 100)
BIKER_JEANS = (45, 50, 70)
BIKER_JEANS_DARK = (30, 35, 50)
BIKER_BOOTS = (35, 25, 20)
BIKER_CHAIN = (190, 195, 205)
BIKER_CHAIN_LIGHT = (225, 230, 240)
BIKER_OUTLINE = (15, 10, 8)


# ── Punk Rocker (20x45) ──────────────────────────────────────────────────────


def draw_punk_rocker_frame(img, x_off, y_off, fw, fh, pose="stand", frame=0):
    """Draw a single punk rocker frame at given offset. 20x45."""
    d = ImageDraw.Draw(img)
    cx = x_off + fw // 2
    head_y = y_off + 5
    torso_y = y_off + 18
    hip_y = y_off + 30
    foot_y = y_off + fh - 3

    # Pose offsets
    if pose == "walk":
        leg_offsets = [(-2, 2), (2, -2), (-1, 1), (1, -1), (-2, 2), (2, -2)]
        lo = leg_offsets[frame % 6]
        arm_swing = [(-2, 2), (2, -2), (-1, 1), (1, -1), (-2, 2), (2, -2)]
        ao = arm_swing[frame % 6]
    elif pose == "attack":
        # Punch / swing
        lo = (0, 0)
        punch_ext = [0, 4, 6, 3][frame % 4]
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

    # ── Mohawk (tall green spikes above head) ──
    if pose != "death" or frame < 3:
        spike_base_y = head_y - 1
        for sx in range(-2, 3):
            spike_x = cx + sx * 2
            spike_h = random.randint(5, 8) if sx % 2 == 0 else random.randint(3, 5)
            d.line([spike_x, spike_base_y, spike_x, spike_base_y - spike_h],
                   fill=PUNK_MOHAWK, width=2)
            d.point([spike_x, spike_base_y - spike_h], fill=PUNK_MOHAWK_TIP)

    # ── Head (ellipse) ──
    head_w, head_h = 7, 8
    d.ellipse([cx - head_w // 2, head_y, cx + head_w // 2, head_y + head_h],
              fill=PUNK_SKIN, outline=PUNK_OUTLINE)
    # Eyes
    d.point([cx - 2, head_y + 4], fill=PUNK_OUTLINE)
    d.point([cx + 1, head_y + 4], fill=PUNK_OUTLINE)

    # ── Torso (black band tee) ──
    torso_w = 10
    d.rectangle([cx - torso_w // 2, torso_y, cx + torso_w // 2, hip_y],
                fill=PUNK_SHIRT, outline=PUNK_OUTLINE)
    # Band logo (small red rectangle on chest)
    d.rectangle([cx - 3, torso_y + 2, cx + 3, torso_y + 5], fill=PUNK_SHIRT_PRINT)
    # Ripped edges at bottom
    d.point([cx - 4, hip_y], fill=PUNK_SKIN_SHADOW)
    d.point([cx + 3, hip_y], fill=PUNK_SKIN_SHADOW)

    # ── Arms ──
    arm_y = torso_y + 2
    arm_len = 10
    if pose == "death" and frame >= 2:
        d.rectangle([cx - torso_w // 2 - 4, arm_y + 4, cx - torso_w // 2, arm_y + 7],
                     fill=PUNK_SKIN, outline=PUNK_OUTLINE)
        d.rectangle([cx + torso_w // 2, arm_y + 4, cx + torso_w // 2 + 4, arm_y + 7],
                     fill=PUNK_SKIN, outline=PUNK_OUTLINE)
    else:
        # Left arm
        la_end_y = arm_y + arm_len + ao[0]
        d.line([cx - torso_w // 2, arm_y, cx - torso_w // 2 - 2, la_end_y],
               fill=PUNK_SKIN, width=2)
        # Right arm
        ra_end_y = arm_y + arm_len + ao[1]
        d.line([cx + torso_w // 2, arm_y, cx + torso_w // 2 + 2, ra_end_y],
               fill=PUNK_SKIN, width=2)

    # ── Legs (red/black plaid pants) ──
    leg_w = 4
    if pose == "death" and frame >= 3:
        d.rectangle([cx - 5, hip_y, cx + 5, hip_y + 3], fill=PUNK_PANTS)
    else:
        # Left leg
        ll_x = cx - 3 + lo[0]
        d.rectangle([ll_x - leg_w // 2, hip_y, ll_x + leg_w // 2, foot_y],
                    fill=PUNK_PANTS, outline=PUNK_OUTLINE)
        # Plaid cross-hatch
        for py in range(hip_y + 2, foot_y, 4):
            d.point([ll_x, py], fill=PUNK_PANTS_PLAID)
        # Right leg
        rl_x = cx + 3 + lo[1]
        d.rectangle([rl_x - leg_w // 2, hip_y, rl_x + leg_w // 2, foot_y],
                    fill=PUNK_PANTS, outline=PUNK_OUTLINE)
        for py in range(hip_y + 2, foot_y, 4):
            d.point([rl_x, py], fill=PUNK_PANTS_PLAID)

        # Combat boots
        d.rectangle([ll_x - leg_w // 2 - 1, foot_y - 2, ll_x + leg_w // 2 + 1, foot_y + 1],
                    fill=PUNK_BOOTS)
        d.rectangle([ll_x - leg_w // 2, foot_y - 1, ll_x + leg_w // 2, foot_y],
                    fill=PUNK_BOOTS_SOLE)
        d.rectangle([rl_x - leg_w // 2 - 1, foot_y - 2, rl_x + leg_w // 2 + 1, foot_y + 1],
                    fill=PUNK_BOOTS)
        d.rectangle([rl_x - leg_w // 2, foot_y - 1, rl_x + leg_w // 2, foot_y],
                    fill=PUNK_BOOTS_SOLE)

    # Hurt flash
    if pose == "hurt":
        d.rectangle([cx - 2, torso_y + 2, cx + 2, torso_y + 6],
                     fill=(255, 255, 255, 80))


def create_punk_rocker_sheets():
    """Generate punk rocker sprite sheets."""
    fw, fh = 20, 45

    sheets = {
        "punk_rocker_walk_sheet.png": ("walk", 6),
        "punk_rocker_attack_sheet.png": ("attack", 4),
        "punk_rocker_hurt_sheet.png": ("hurt", 2),
        "punk_rocker_death_sheet.png": ("death", 4),
    }

    for name, (pose, nframes) in sheets.items():
        img = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))
        for f in range(nframes):
            draw_punk_rocker_frame(img, f * fw, 0, fw, fh, pose, f)
        path = ENEMY_DIR / name
        img.save(path)
        print(f"  [OK] {name}")


# ── Mohawk Diver (20x42) ─────────────────────────────────────────────────────


def draw_mohawk_diver_frame(img, x_off, y_off, fw, fh, pose="stand", frame=0):
    """Draw a single mohawk diver frame at given offset. 20x42."""
    d = ImageDraw.Draw(img)
    cx = x_off + fw // 2
    head_y = y_off + 5
    torso_y = y_off + 17
    hip_y = y_off + 28
    foot_y = y_off + fh - 3

    # Forward lean for charge
    lean = 0
    if pose == "charge":
        lean = [2, 3, 4, 3][frame % 4]

    # Pose offsets
    if pose == "walk":
        leg_offsets = [(-2, 2), (2, -2), (-1, 1), (1, -1), (-2, 2), (2, -2)]
        lo = leg_offsets[frame % 6]
        arm_swing = [(-2, 2), (2, -2), (-1, 1), (1, -1), (-2, 2), (2, -2)]
        ao = arm_swing[frame % 6]
    elif pose == "charge":
        # Aggressive running
        lo = [(-3, 3), (3, -3), (-4, 4), (4, -4)][frame % 4]
        ao = [(-3, 3), (3, -3), (-4, 4), (4, -4)][frame % 4]
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

    # Adjust for lean
    head_x_shift = lean
    torso_x_shift = lean // 2

    # ── Mohawk (tall red spikes) ──
    if pose != "death" or frame < 3:
        spike_base_y = head_y - 1
        for sx in range(-2, 3):
            spike_x = cx + head_x_shift + sx * 2
            spike_h = random.randint(6, 10) if sx % 2 == 0 else random.randint(4, 7)
            d.line([spike_x, spike_base_y, spike_x, spike_base_y - spike_h],
                   fill=DIVER_MOHAWK, width=2)
            d.point([spike_x, spike_base_y - spike_h], fill=DIVER_MOHAWK_TIP)

    # ── Head (ellipse) ──
    head_w, head_h = 7, 8
    hcx = cx + head_x_shift
    d.ellipse([hcx - head_w // 2, head_y, hcx + head_w // 2, head_y + head_h],
              fill=DIVER_SKIN, outline=DIVER_OUTLINE)
    # Aggressive eyes
    d.point([hcx - 2, head_y + 4], fill=DIVER_OUTLINE)
    d.point([hcx + 1, head_y + 4], fill=DIVER_OUTLINE)
    # Scowl line
    d.line([hcx - 1, head_y + 6, hcx + 1, head_y + 6], fill=DIVER_OUTLINE, width=1)

    # ── Torso (sleeveless denim vest, bare arms visible) ──
    torso_w = 9
    tcx = cx + torso_x_shift
    d.rectangle([tcx - torso_w // 2, torso_y, tcx + torso_w // 2, hip_y],
                fill=DIVER_VEST, outline=DIVER_OUTLINE)
    # Vest lapel detail
    d.line([tcx, torso_y, tcx, torso_y + 5], fill=DIVER_VEST_DARK, width=1)
    # Button/stud dots
    d.point([tcx - 1, torso_y + 3], fill=BIKER_CHAIN)
    d.point([tcx + 1, torso_y + 3], fill=BIKER_CHAIN)

    # ── Arms (bare skin — sleeveless) ──
    arm_y = torso_y + 1
    arm_len = 10
    if pose == "death" and frame >= 2:
        d.rectangle([tcx - torso_w // 2 - 4, arm_y + 3, tcx - torso_w // 2, arm_y + 6],
                     fill=DIVER_SKIN, outline=DIVER_OUTLINE)
        d.rectangle([tcx + torso_w // 2, arm_y + 3, tcx + torso_w // 2 + 4, arm_y + 6],
                     fill=DIVER_SKIN, outline=DIVER_OUTLINE)
    else:
        # Left arm (bare skin)
        la_end_y = arm_y + arm_len + ao[0]
        d.line([tcx - torso_w // 2, arm_y, tcx - torso_w // 2 - 2, la_end_y],
               fill=DIVER_SKIN, width=2)
        d.point([tcx - torso_w // 2 - 2, la_end_y], fill=DIVER_SKIN_SHADOW)
        # Right arm
        ra_end_y = arm_y + arm_len + ao[1]
        d.line([tcx + torso_w // 2, arm_y, tcx + torso_w // 2 + 2, ra_end_y],
               fill=DIVER_SKIN, width=2)
        d.point([tcx + torso_w // 2 + 2, ra_end_y], fill=DIVER_SKIN_SHADOW)

    # ── Legs (ripped jeans) ──
    leg_w = 4
    if pose == "death" and frame >= 3:
        d.rectangle([cx - 5, hip_y, cx + 5, hip_y + 3], fill=DIVER_JEANS)
    else:
        # Left leg
        ll_x = cx + lo[0]
        d.rectangle([ll_x - leg_w // 2 - 1, hip_y, ll_x + leg_w // 2, foot_y],
                    fill=DIVER_JEANS, outline=DIVER_OUTLINE)
        # Rip detail (skin showing through)
        rip_y = hip_y + (foot_y - hip_y) * 2 // 3
        d.rectangle([ll_x - 1, rip_y, ll_x + 1, rip_y + 2], fill=DIVER_JEANS_RIP)
        # Right leg
        rl_x = cx + lo[1]
        d.rectangle([rl_x - leg_w // 2, hip_y, rl_x + leg_w // 2 + 1, foot_y],
                    fill=DIVER_JEANS, outline=DIVER_OUTLINE)

        # Boots
        d.rectangle([ll_x - leg_w // 2 - 1, foot_y - 2, ll_x + leg_w // 2 + 1, foot_y + 1],
                    fill=DIVER_BOOTS)
        d.rectangle([rl_x - leg_w // 2 - 1, foot_y - 2, rl_x + leg_w // 2 + 1, foot_y + 1],
                    fill=DIVER_BOOTS)

    # Hurt flash
    if pose == "hurt":
        d.rectangle([cx - 2, torso_y + 2, cx + 2, torso_y + 6],
                     fill=(255, 255, 255, 80))


def create_mohawk_diver_sheets():
    """Generate mohawk diver sprite sheets."""
    fw, fh = 20, 42

    sheets = {
        "mohawk_diver_walk_sheet.png": ("walk", 6),
        "mohawk_diver_charge_sheet.png": ("charge", 4),
        "mohawk_diver_hurt_sheet.png": ("hurt", 2),
        "mohawk_diver_death_sheet.png": ("death", 4),
    }

    for name, (pose, nframes) in sheets.items():
        img = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))
        for f in range(nframes):
            draw_mohawk_diver_frame(img, f * fw, 0, fw, fh, pose, f)
        path = ENEMY_DIR / name
        img.save(path)
        print(f"  [OK] {name}")


# ── Biker (35x55) ────────────────────────────────────────────────────────────


def draw_biker_frame(img, x_off, y_off, fw, fh, pose="stand", frame=0):
    """Draw a single biker frame at given offset. 35x55."""
    d = ImageDraw.Draw(img)
    cx = x_off + fw // 2
    head_y = y_off + 3
    torso_y = y_off + 16
    hip_y = y_off + 34
    foot_y = y_off + fh - 4

    # Pose offsets
    if pose == "walk":
        leg_offsets = [(-3, 3), (3, -3), (-2, 2), (2, -2)]
        lo = leg_offsets[frame % 4]
        arm_swing = [(-2, 2), (2, -2), (-1, 1), (1, -1)]
        ao = arm_swing[frame % 4]
    elif pose == "charge":
        # Heavy forward rush
        lo = [(-4, 4), (4, -4), (-3, 3), (3, -3)][frame % 4]
        ao = [(-4, 4), (4, -4), (-3, 3), (3, -3)][frame % 4]
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

    # ── Head with helmet/bandana ──
    head_w, head_h = 9, 10
    d.ellipse([cx - head_w // 2, head_y, cx + head_w // 2, head_y + head_h],
              fill=BIKER_SKIN, outline=BIKER_OUTLINE)
    # Helmet dome (upper half of head)
    d.arc([cx - head_w // 2 - 1, head_y - 1, cx + head_w // 2 + 1, head_y + head_h],
          180, 360, fill=BIKER_HELMET, width=3)
    # Visor strip
    d.rectangle([cx - head_w // 2, head_y + 3, cx + head_w // 2, head_y + 5],
                fill=BIKER_HELMET_VISOR)
    # Eyes behind visor
    d.point([cx - 2, head_y + 4], fill=(220, 220, 220))
    d.point([cx + 2, head_y + 4], fill=(220, 220, 220))

    # ── Torso (wide leather jacket — big build) ──
    torso_w = 16
    d.rectangle([cx - torso_w // 2, torso_y, cx + torso_w // 2, hip_y],
                fill=BIKER_LEATHER, outline=BIKER_OUTLINE)
    # Jacket lapel highlights
    d.line([cx - 2, torso_y, cx - 2, torso_y + 8], fill=BIKER_LEATHER_LIGHT, width=1)
    d.line([cx + 2, torso_y, cx + 2, torso_y + 8], fill=BIKER_LEATHER_LIGHT, width=1)
    # Zipper center line
    d.line([cx, torso_y + 2, cx, hip_y - 2], fill=BIKER_CHAIN, width=1)

    # ── Chain detail across chest ──
    chain_y = torso_y + 6
    for chain_x in range(cx - torso_w // 2 + 3, cx + torso_w // 2 - 2, 3):
        c = BIKER_CHAIN if (chain_x % 2 == 0) else BIKER_CHAIN_LIGHT
        d.point([chain_x, chain_y], fill=c)
        d.point([chain_x + 1, chain_y + 1], fill=c)

    # ── Arms (leather sleeves) ──
    arm_y = torso_y + 2
    arm_len = 14
    if pose == "death" and frame >= 2:
        d.rectangle([cx - torso_w // 2 - 5, arm_y + 4, cx - torso_w // 2, arm_y + 8],
                     fill=BIKER_LEATHER, outline=BIKER_OUTLINE)
        d.rectangle([cx + torso_w // 2, arm_y + 4, cx + torso_w // 2 + 5, arm_y + 8],
                     fill=BIKER_LEATHER, outline=BIKER_OUTLINE)
    else:
        # Left arm
        la_end_y = arm_y + arm_len + ao[0]
        d.line([cx - torso_w // 2, arm_y, cx - torso_w // 2 - 3, la_end_y],
               fill=BIKER_LEATHER, width=3)
        # Fist
        d.rectangle([cx - torso_w // 2 - 5, la_end_y - 1, cx - torso_w // 2 - 2, la_end_y + 2],
                     fill=BIKER_SKIN)
        # Right arm
        ra_end_y = arm_y + arm_len + ao[1]
        d.line([cx + torso_w // 2, arm_y, cx + torso_w // 2 + 3, ra_end_y],
               fill=BIKER_LEATHER, width=3)
        # Fist
        d.rectangle([cx + torso_w // 2 + 2, ra_end_y - 1, cx + torso_w // 2 + 5, ra_end_y + 2],
                     fill=BIKER_SKIN)

    # ── Legs (dark jeans, heavy boots) ──
    leg_w = 6
    if pose == "death" and frame >= 3:
        d.rectangle([cx - 7, hip_y, cx + 7, hip_y + 4], fill=BIKER_JEANS)
    else:
        # Left leg
        ll_x = cx - 5 + lo[0]
        d.rectangle([ll_x - leg_w // 2, hip_y, ll_x + leg_w // 2, foot_y],
                    fill=BIKER_JEANS, outline=BIKER_JEANS_DARK)
        # Right leg
        rl_x = cx + 5 + lo[1]
        d.rectangle([rl_x - leg_w // 2, hip_y, rl_x + leg_w // 2, foot_y],
                    fill=BIKER_JEANS, outline=BIKER_JEANS_DARK)

        # Heavy boots
        d.rectangle([ll_x - leg_w // 2 - 1, foot_y - 3, ll_x + leg_w // 2 + 1, foot_y + 1],
                    fill=BIKER_BOOTS)
        d.rectangle([rl_x - leg_w // 2 - 1, foot_y - 3, rl_x + leg_w // 2 + 1, foot_y + 1],
                    fill=BIKER_BOOTS)
        # Boot buckle/chain detail
        d.point([ll_x, foot_y - 2], fill=BIKER_CHAIN)
        d.point([rl_x, foot_y - 2], fill=BIKER_CHAIN)

    # Hurt flash
    if pose == "hurt":
        d.rectangle([cx - 3, torso_y + 3, cx + 3, torso_y + 8],
                     fill=(255, 255, 255, 80))

    # Charge: forward lean dust trail
    if pose == "charge" and frame >= 2:
        for _ in range(2):
            dx = cx - random.randint(4, 10)
            dy = foot_y + random.randint(-2, 1)
            d.point([dx, dy], fill=(160, 155, 140, 120))


def create_biker_sheets():
    """Generate biker sprite sheets."""
    fw, fh = 35, 55

    sheets = {
        "biker_walk_sheet.png": ("walk", 4),
        "biker_charge_sheet.png": ("charge", 4),
        "biker_hurt_sheet.png": ("hurt", 2),
        "biker_death_sheet.png": ("death", 4),
    }

    for name, (pose, nframes) in sheets.items():
        img = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))
        for f in range(nframes):
            draw_biker_frame(img, f * fw, 0, fw, fh, pose, f)
        path = ENEMY_DIR / name
        img.save(path)
        print(f"  [OK] {name}")


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    print("Generating CBGB Punk Alley enemy sprites...")

    # Palette-swap: Spray Painter (from shooter, explicit name mapping)
    print("\nSpray Painter (palette-swap from shooter):")
    swap_explicit([
        ("shooter_skate_sheet.png", "spray_painter_walk_sheet.png"),
        ("shooter_shoot_skate_sheet.png", "spray_painter_shoot_sheet.png"),
        ("shooter_hurt_sheet.png", "spray_painter_hurt_sheet.png"),
        ("shooter_death_sheet.png", "spray_painter_death_sheet.png"),
    ], remap_spray_painter)

    # From-scratch: Punk Rocker
    print("\nPunk Rocker (from scratch):")
    create_punk_rocker_sheets()

    # From-scratch: Mohawk Diver
    print("\nMohawk Diver (from scratch):")
    create_mohawk_diver_sheets()

    # From-scratch: Biker
    print("\nBiker (from scratch):")
    create_biker_sheets()

    print("\nDone! CBGB Punk Alley enemies generated.")


if __name__ == "__main__":
    main()
