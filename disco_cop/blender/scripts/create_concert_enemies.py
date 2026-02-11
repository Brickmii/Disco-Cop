#!/usr/bin/env python3
"""Generate Led Zeppelin Concert enemy sprites for Disco Cop Level 03.

Palette-swap enemies (from shooter sheets, 20x40/frame):
  - Groupie: hot pink/magenta concert fan
  - Pyro Tech: orange/red hazmat fire crew

From-scratch enemies:
  - Roadie (30x55/frame): dark crew shirt, jeans, big build
  - Speaker Stack (30x50/frame): Marshall-style amp cabinet

Usage:
    python create_concert_enemies.py
"""

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
ENEMY_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "enemies"

random.seed(303)

# ── Palette-swap remap functions ──────────────────────────────────────────────


def remap_groupie(r, g, b, a):
    """Shooter → Groupie: hot pink/magenta concert fan outfit."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 130:
        # Light body → hot pink top
        return (min(int(r * 1.3), 240), max(int(g * 0.4), 40), min(int(b * 1.1), 180), a)
    elif is_gray and brightness > 80:
        # Mid body → magenta/purple skirt
        return (min(int(r * 1.1), 200), max(int(g * 0.3), 30), min(int(b * 1.3), 210), a)
    elif brightness > 100 and r > g:
        # Warm accents → neon pink highlights
        return (min(int(r * 1.4), 255), max(int(g * 0.3), 50), min(int(b * 1.2), 200), a)
    elif brightness > 50:
        # Mid tones → warm skin tone
        return (min(int(r * 1.2), 200), min(int(g * 0.9), 150), max(int(b * 0.7), 80), a)
    else:
        # Dark (outlines, hair) → keep dark with slight pink
        return (min(r + 15, 80), g, min(b + 10, 60), a)


def remap_pyrotech(r, g, b, a):
    """Shooter → Pyro Tech: orange/red hazmat fire crew."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 130:
        # Light body → bright orange hazmat
        return (min(int(r * 1.4), 255), min(int(g * 0.8), 160), max(int(b * 0.2), 10), a)
    elif is_gray and brightness > 80:
        # Mid body → darker orange/red
        return (min(int(r * 1.3), 220), max(int(g * 0.5), 60), max(int(b * 0.2), 10), a)
    elif brightness > 100 and r > g:
        # Warm accents → yellow safety stripes
        return (min(int(r * 1.3), 255), min(int(g * 1.2), 230), max(int(b * 0.3), 20), a)
    elif brightness > 50:
        # Mid tones → red-tinted skin
        return (min(int(r * 1.3), 210), min(int(g * 0.8), 130), max(int(b * 0.5), 50), a)
    else:
        # Dark (outlines) → deep red-brown
        return (min(r + 20, 90), min(g + 5, 40), b, a)


def swap_sheets(src_names, prefix, remap_fn):
    """Apply remap function to source sheets, save with new prefix."""
    for src_name in src_names:
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

        base = src_name.split("_", 1)[1]  # Remove first word
        dst_name = f"{prefix}_{base}"
        dst_path = ENEMY_DIR / dst_name
        Image.fromarray(px.astype(np.uint8), "RGBA").save(dst_path)
        print(f"  [OK] {dst_name}")


# ── From-scratch enemies ─────────────────────────────────────────────────────

# Roadie palette
ROADIE_SKIN = (180, 140, 110)
ROADIE_SKIN_SHADOW = (150, 115, 85)
ROADIE_SHIRT = (30, 30, 35)
ROADIE_SHIRT_LIGHT = (50, 50, 55)
ROADIE_JEANS = (50, 55, 80)
ROADIE_JEANS_DARK = (35, 40, 60)
ROADIE_BOOTS = (40, 30, 25)
ROADIE_HAIR = (50, 35, 20)
ROADIE_OUTLINE = (20, 15, 10)

# Speaker Stack palette
SPEAKER_BLACK = (25, 25, 30)
SPEAKER_DARK = (40, 40, 45)
SPEAKER_GRILLE = (60, 60, 65)
SPEAKER_GRILLE_LIGHT = (80, 80, 85)
SPEAKER_CHROME = (180, 185, 195)
SPEAKER_CHROME_LIGHT = (220, 225, 235)
SPEAKER_GOLD = (200, 170, 50)
SPEAKER_GOLD_LIGHT = (240, 210, 80)
SPEAKER_CONE = (45, 45, 50)
SPEAKER_CONE_CENTER = (35, 35, 40)


def draw_roadie_frame(img, x_off, y_off, fw, fh, pose="stand", frame=0):
    """Draw a single roadie frame at given offset. 30x55."""
    d = ImageDraw.Draw(img)
    cx = x_off + fw // 2  # center x
    # Vertical offsets (from top of frame)
    head_y = y_off + 3
    torso_y = y_off + 16
    hip_y = y_off + 32
    foot_y = y_off + fh - 4

    # Walk/charge leg offsets
    if pose == "walk":
        leg_offsets = [(-3, 3), (3, -3), (-2, 2), (2, -2)]
        lo = leg_offsets[frame % 4]
        arm_swing = [(-2, 2), (2, -2), (-1, 1), (1, -1)]
        ao = arm_swing[frame % 4]
    elif pose == "charge":
        # Leaning forward, arms out
        lo = [(-4, 4), (4, -4), (-3, 3), (3, -3)][frame % 4]
        ao = [(-4, 3), (3, -4), (-3, 2), (2, -3)][frame % 4]
    elif pose == "hurt":
        lo = (0, 0)
        ao = (2, -2) if frame == 0 else (-2, 2)
    elif pose == "death":
        # Progressive collapse
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

    # ── Head (ellipse) ──
    head_w, head_h = 8, 10
    d.ellipse([cx - head_w // 2, head_y, cx + head_w // 2, head_y + head_h],
              fill=ROADIE_SKIN, outline=ROADIE_OUTLINE)
    # Hair (bandana/short hair)
    d.arc([cx - head_w // 2, head_y, cx + head_w // 2, head_y + head_h],
          180, 360, fill=ROADIE_HAIR, width=2)
    # Eyes
    d.point([cx - 2, head_y + 5], fill=ROADIE_OUTLINE)
    d.point([cx + 2, head_y + 5], fill=ROADIE_OUTLINE)

    # ── Torso (wide rectangle — big build) ──
    torso_w = 14
    d.rectangle([cx - torso_w // 2, torso_y, cx + torso_w // 2, hip_y],
                fill=ROADIE_SHIRT, outline=ROADIE_OUTLINE)
    # Shirt logo hint (small rectangle)
    d.rectangle([cx - 3, torso_y + 4, cx + 3, torso_y + 8], fill=ROADIE_SHIRT_LIGHT)

    # ── Arms ──
    arm_y = torso_y + 2
    arm_len = 12
    if pose == "death" and frame >= 2:
        # Arms flop
        d.rectangle([cx - torso_w // 2 - 5, arm_y + 4, cx - torso_w // 2, arm_y + 8],
                     fill=ROADIE_SKIN, outline=ROADIE_OUTLINE)
        d.rectangle([cx + torso_w // 2, arm_y + 4, cx + torso_w // 2 + 5, arm_y + 8],
                     fill=ROADIE_SKIN, outline=ROADIE_OUTLINE)
    else:
        # Left arm
        la_end_y = arm_y + arm_len + ao[0]
        d.line([cx - torso_w // 2, arm_y, cx - torso_w // 2 - 3, la_end_y],
               fill=ROADIE_SKIN, width=3)
        # Right arm
        ra_end_y = arm_y + arm_len + ao[1]
        d.line([cx + torso_w // 2, arm_y, cx + torso_w // 2 + 3, ra_end_y],
               fill=ROADIE_SKIN, width=3)
        # Hands (skin dots)
        d.rectangle([cx - torso_w // 2 - 4, la_end_y - 1, cx - torso_w // 2 - 2, la_end_y + 1],
                     fill=ROADIE_SKIN)
        d.rectangle([cx + torso_w // 2 + 2, ra_end_y - 1, cx + torso_w // 2 + 4, ra_end_y + 1],
                     fill=ROADIE_SKIN)

    # ── Legs (jeans) ──
    leg_w = 5
    if pose == "death" and frame >= 3:
        # Legs flat
        d.rectangle([cx - 6, hip_y, cx + 6, hip_y + 4], fill=ROADIE_JEANS)
    else:
        # Left leg
        ll_x = cx - 4 + (lo[0] if isinstance(lo, tuple) else lo)
        d.rectangle([ll_x - leg_w // 2, hip_y, ll_x + leg_w // 2, foot_y],
                    fill=ROADIE_JEANS, outline=ROADIE_JEANS_DARK)
        # Right leg
        rl_x = cx + 4 + (lo[1] if isinstance(lo, tuple) else 0)
        d.rectangle([rl_x - leg_w // 2, hip_y, rl_x + leg_w // 2, foot_y],
                    fill=ROADIE_JEANS, outline=ROADIE_JEANS_DARK)

        # Boots
        d.rectangle([ll_x - leg_w // 2 - 1, foot_y - 2, ll_x + leg_w // 2 + 1, foot_y + 1],
                    fill=ROADIE_BOOTS)
        d.rectangle([rl_x - leg_w // 2 - 1, foot_y - 2, rl_x + leg_w // 2 + 1, foot_y + 1],
                    fill=ROADIE_BOOTS)

    # Hurt flash
    if pose == "hurt":
        # Slight white overlay hint
        d.rectangle([cx - 2, torso_y + 2, cx + 2, torso_y + 6],
                     fill=(255, 255, 255, 80))


def create_roadie_sheets():
    """Generate roadie sprite sheets."""
    fw, fh = 30, 55

    sheets = {
        "roadie_walk_sheet.png": ("walk", 4),
        "roadie_charge_sheet.png": ("charge", 4),
        "roadie_hurt_sheet.png": ("hurt", 2),
        "roadie_death_sheet.png": ("death", 4),
    }

    for name, (pose, nframes) in sheets.items():
        img = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))
        for f in range(nframes):
            draw_roadie_frame(img, f * fw, 0, fw, fh, pose, f)
        path = ENEMY_DIR / name
        img.save(path)
        print(f"  [OK] {name}")


def draw_speaker_grille(d, x, y, w, h):
    """Draw speaker grille pattern (dotted grid)."""
    for gy in range(y + 1, y + h, 2):
        for gx in range(x + 1, x + w, 2):
            c = SPEAKER_GRILLE if (gx + gy) % 4 == 0 else SPEAKER_GRILLE_LIGHT
            d.point([gx, gy], fill=c)


def draw_speaker_cone(d, cx, cy, radius):
    """Draw a speaker cone circle."""
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              fill=SPEAKER_CONE, outline=SPEAKER_GRILLE)
    # Center dust cap
    r2 = max(radius // 3, 2)
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2],
              fill=SPEAKER_CONE_CENTER, outline=SPEAKER_DARK)


def draw_speaker_frame(img, x_off, y_off, fw, fh, pose="idle", frame=0):
    """Draw a single speaker stack frame. 30x50."""
    d = ImageDraw.Draw(img)

    # Vibration offset for idle
    vib_x = 0
    vib_y = 0
    if pose == "walk":
        vib_x = [0, 1, 0, -1][frame % 2]
    elif pose == "attack":
        vib_x = [-1, 1, -1, 1][frame % 4]
        vib_y = [-1, 0, 1, 0][frame % 4]

    bx = x_off + 2 + vib_x
    by = y_off + 2 + vib_y
    bw = fw - 4
    bh = fh - 4

    # ── Main cabinet body ──
    d.rectangle([bx, by, bx + bw, by + bh], fill=SPEAKER_BLACK, outline=SPEAKER_DARK)

    # ── Top section: logo area ──
    d.rectangle([bx + 2, by + 2, bx + bw - 2, by + 8], fill=SPEAKER_DARK)
    # Gold "MARSHALL" logo
    logo_y = by + 4
    for lx in range(bx + 6, bx + bw - 6, 2):
        d.point([lx, logo_y], fill=SPEAKER_GOLD)
        d.point([lx, logo_y - 1], fill=SPEAKER_GOLD_LIGHT)

    # ── Speaker cones (2x2 grid) ──
    cone_r = 4
    cx1 = bx + bw // 4
    cx2 = bx + 3 * bw // 4
    cy1 = by + 18
    cy2 = by + 32
    draw_speaker_cone(d, cx1, cy1, cone_r)
    draw_speaker_cone(d, cx2, cy1, cone_r)
    draw_speaker_cone(d, cx1, cy2, cone_r)
    draw_speaker_cone(d, cx2, cy2, cone_r)

    # ── Grille cloth around cones ──
    draw_speaker_grille(d, bx + 2, by + 10, bw - 4, bh - 14)

    # ── Chrome corners ──
    for corner_x, corner_y in [(bx + 1, by + 1), (bx + bw - 2, by + 1),
                                (bx + 1, by + bh - 2), (bx + bw - 2, by + bh - 2)]:
        d.rectangle([corner_x, corner_y, corner_x + 1, corner_y + 1], fill=SPEAKER_CHROME)

    # ── Chrome handle at top ──
    d.rectangle([bx + bw // 2 - 4, by, bx + bw // 2 + 4, by + 1], fill=SPEAKER_CHROME_LIGHT)

    # ── Attack: sound wave rings ──
    if pose == "attack" and frame >= 1:
        ring_cx = x_off + fw // 2
        ring_cy = y_off + fh // 2
        for ring in range(1, frame + 1):
            r = 8 + ring * 6
            alpha = max(60, 200 - ring * 50)
            d.arc([ring_cx - r, ring_cy - r, ring_cx + r, ring_cy + r],
                  0, 360, fill=(200, 200, 255, alpha), width=1)

    # ── Hurt: flash ──
    if pose == "hurt":
        flash_alpha = 120 if frame == 0 else 60
        d.rectangle([bx + 2, by + 2, bx + bw - 2, by + bh - 2],
                     fill=(255, 255, 255, flash_alpha))

    # ── Death: progressive break apart ──
    if pose == "death":
        if frame >= 1:
            # Crack lines
            d.line([bx + bw // 2, by, bx + bw // 2 + 3, by + bh], fill=SPEAKER_GRILLE, width=1)
        if frame >= 2:
            # More cracks, sparks
            d.line([bx + 4, by + bh // 3, bx + bw - 4, by + 2 * bh // 3],
                   fill=SPEAKER_GRILLE_LIGHT, width=1)
            # Spark pixels
            for _ in range(3):
                sx = bx + random.randint(2, bw - 2)
                sy = by + random.randint(2, bh - 2)
                d.point([sx, sy], fill=SPEAKER_GOLD_LIGHT)
        if frame >= 3:
            # Fading / darkening
            for fy in range(by + bh // 2, by + bh):
                for fx in range(bx, bx + bw):
                    if 0 <= fx < img.width and 0 <= fy < img.height:
                        pr, pg, pb, pa = img.getpixel((fx, fy))
                        if pa > 0:
                            img.putpixel((fx, fy), (pr // 2, pg // 2, pb // 2, pa))


def create_speaker_sheets():
    """Generate speaker stack sprite sheets."""
    fw, fh = 30, 50

    sheets = {
        "speaker_walk_sheet.png": ("walk", 2),
        "speaker_attack_sheet.png": ("attack", 4),
        "speaker_hurt_sheet.png": ("hurt", 2),
        "speaker_death_sheet.png": ("death", 4),
    }

    for name, (pose, nframes) in sheets.items():
        img = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))
        for f in range(nframes):
            draw_speaker_frame(img, f * fw, 0, fw, fh, pose, f)
        path = ENEMY_DIR / name
        img.save(path)
        print(f"  [OK] {name}")


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    print("Generating Led Zeppelin Concert enemy sprites...")

    # Palette-swap: Groupie (from shooter)
    print("\nGroupie (palette-swap from shooter):")
    swap_sheets([
        "shooter_skate_sheet.png",
        "shooter_shoot_skate_sheet.png",
        "shooter_hurt_sheet.png",
        "shooter_death_sheet.png",
    ], "groupie", remap_groupie)

    # Palette-swap: Pyro Tech (from shooter)
    print("\nPyro Tech (palette-swap from shooter):")
    swap_sheets([
        "shooter_skate_sheet.png",
        "shooter_shoot_skate_sheet.png",
        "shooter_hurt_sheet.png",
        "shooter_death_sheet.png",
    ], "pyrotech", remap_pyrotech)

    # From-scratch: Roadie
    print("\nRoadie (from scratch):")
    create_roadie_sheets()

    # From-scratch: Speaker Stack
    print("\nSpeaker Stack (from scratch):")
    create_speaker_sheets()

    print("\nDone! 16 concert enemy sprites generated.")


if __name__ == "__main__":
    main()
