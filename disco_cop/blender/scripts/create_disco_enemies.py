#!/usr/bin/env python3
"""Generate Bee Gees Disco Floor enemy sprites for Disco Cop Level 05.

Palette-swap enemy (from shooter sheets, 20x40/frame):
  - Disco Dancer: gold/white sparkly disco outfit, bell bottoms, afro

From-scratch enemies:
  - Floor Bouncer (26x48/frame): black suit, bow tie, earpiece, wide build
  - Mirror Ball (24x24/frame): faceted disco ball sphere with chain

Usage:
    python create_disco_enemies.py
"""

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
ENEMY_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "enemies"

random.seed(813)

# ── Palette-swap remap functions ──────────────────────────────────────────────


def remap_disco_dancer(r, g, b, a):
    """Shooter → Disco Dancer: gold/white sparkle outfit, bell bottoms, dark skin."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 130:
        # Light body → gold/white sparkle top
        gold_r = min(int(r * 1.3), 255)
        gold_g = min(int(g * 1.1), 220)
        gold_b = max(int(b * 0.3), 30)
        # Sparkle variation based on pixel position hash
        sparkle = ((r * 7 + g * 13 + b * 3) % 40)
        if sparkle < 10:
            # Bright white sparkle highlight
            return (min(gold_r + 30, 255), min(gold_g + 35, 255), min(gold_b + 60, 200), a)
        return (gold_r, gold_g, gold_b, a)
    elif is_gray and brightness > 80:
        # Mid body → white bell-bottom pants
        return (min(int(r * 1.1) + 60, 245), min(int(g * 1.1) + 55, 240),
                min(int(b * 1.1) + 50, 235), a)
    elif brightness > 100 and r > g:
        # Warm accents → dark skin with gold highlight
        return (min(int(r * 0.6), 120), min(int(g * 0.5), 90),
                max(int(b * 0.4), 50), a)
    elif brightness > 50:
        # Mid tones → dark skin tone
        return (min(int(r * 0.7), 130), min(int(g * 0.55), 95),
                max(int(b * 0.45), 55), a)
    else:
        # Dark (outlines, hair) → keep dark with slight gold tint
        return (min(r + 12, 70), min(g + 8, 55), b, a)


def swap_explicit(mappings, remap_fn):
    """Apply remap function to source sheets with explicit src->dst name mapping.

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

# Floor Bouncer palette (26x48)
BOUNCER_SKIN = (165, 125, 95)
BOUNCER_SKIN_SHADOW = (135, 100, 75)
BOUNCER_SUIT = (25, 25, 30)
BOUNCER_SUIT_LIGHT = (45, 45, 55)
BOUNCER_SHIRT = (230, 230, 235)
BOUNCER_SHIRT_SHADOW = (200, 200, 210)
BOUNCER_BOWTIE = (160, 30, 30)
BOUNCER_BOWTIE_KNOT = (130, 20, 20)
BOUNCER_PANTS = (28, 28, 33)
BOUNCER_PANTS_CREASE = (40, 40, 48)
BOUNCER_SHOES = (20, 18, 15)
BOUNCER_SHOES_SHINE = (60, 55, 50)
BOUNCER_HAIR = (30, 25, 20)
BOUNCER_EARPIECE = (180, 185, 195)
BOUNCER_OUTLINE = (15, 12, 10)

# Mirror Ball palette (24x24)
MIRROR_BODY = (180, 185, 195)
MIRROR_BODY_DARK = (140, 145, 155)
MIRROR_HIGHLIGHT = (240, 245, 255)
MIRROR_FACET_DARK = (120, 125, 135)
MIRROR_FACET_MID = (160, 165, 175)
MIRROR_CHAIN = (160, 165, 170)
MIRROR_CHAIN_LIGHT = (200, 205, 215)
MIRROR_BEAM = (255, 240, 100)
MIRROR_BEAM_WHITE = (255, 255, 220)
MIRROR_CRACK = (80, 85, 95)


# ── Floor Bouncer (26x48) ────────────────────────────────────────────────────


def draw_bouncer_frame(img, x_off, y_off, fw, fh, pose="stand", frame=0):
    """Draw a single floor bouncer frame at given offset. 26x48."""
    d = ImageDraw.Draw(img)
    cx = x_off + fw // 2
    head_y = y_off + 3
    torso_y = y_off + 14
    hip_y = y_off + 30
    foot_y = y_off + fh - 4

    # Pose offsets
    if pose == "walk":
        leg_offsets = [(-2, 2), (2, -2), (-1, 1), (1, -1)]
        lo = leg_offsets[frame % 4]
        arm_swing = [(-2, 2), (2, -2), (-1, 1), (1, -1)]
        ao = arm_swing[frame % 4]
    elif pose == "attack":
        # Heavy overhead swing
        lo = (0, 0)
        swing_phase = [0, -6, -3, 4][frame % 4]
        ao = (swing_phase, swing_phase // 2)
    elif pose == "hurt":
        lo = (0, 0)
        ao = (3, -3) if frame == 0 else (-3, 3)
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

    # ── Head (slightly blocky — clean cut) ──
    head_w, head_h = 9, 10
    d.ellipse([cx - head_w // 2, head_y, cx + head_w // 2, head_y + head_h],
              fill=BOUNCER_SKIN, outline=BOUNCER_OUTLINE)
    # Short cropped hair (flat top)
    d.rectangle([cx - head_w // 2 + 1, head_y, cx + head_w // 2 - 1, head_y + 3],
                fill=BOUNCER_HAIR)
    # Stern eyes
    d.point([cx - 2, head_y + 5], fill=BOUNCER_OUTLINE)
    d.point([cx + 2, head_y + 5], fill=BOUNCER_OUTLINE)
    # Mouth (straight line — no-nonsense)
    d.line([cx - 1, head_y + 7, cx + 1, head_y + 7], fill=BOUNCER_OUTLINE, width=1)
    # Earpiece (right ear)
    d.point([cx + head_w // 2, head_y + 4], fill=BOUNCER_EARPIECE)
    d.point([cx + head_w // 2, head_y + 5], fill=BOUNCER_EARPIECE)
    # Earpiece wire down neck
    if pose != "death" or frame < 2:
        d.line([cx + head_w // 2, head_y + 5, cx + head_w // 2 - 1, head_y + head_h + 1],
               fill=BOUNCER_EARPIECE, width=1)

    # ── Neck (thick) ──
    neck_y = head_y + head_h
    d.rectangle([cx - 3, neck_y, cx + 3, neck_y + 2], fill=BOUNCER_SKIN)

    # ── Torso (wide — big build, suit jacket) ──
    torso_w = 14
    d.rectangle([cx - torso_w // 2, torso_y, cx + torso_w // 2, hip_y],
                fill=BOUNCER_SUIT, outline=BOUNCER_OUTLINE)
    # Wide shoulders (epaulettes)
    d.rectangle([cx - torso_w // 2 - 1, torso_y, cx - torso_w // 2 + 1, torso_y + 3],
                fill=BOUNCER_SUIT_LIGHT)
    d.rectangle([cx + torso_w // 2 - 1, torso_y, cx + torso_w // 2 + 1, torso_y + 3],
                fill=BOUNCER_SUIT_LIGHT)
    # White dress shirt visible at center
    d.rectangle([cx - 2, torso_y + 1, cx + 2, hip_y - 2],
                fill=BOUNCER_SHIRT)
    d.line([cx, torso_y + 2, cx, hip_y - 3], fill=BOUNCER_SHIRT_SHADOW, width=1)
    # Bow tie
    d.rectangle([cx - 3, torso_y + 1, cx - 1, torso_y + 3], fill=BOUNCER_BOWTIE)
    d.rectangle([cx + 1, torso_y + 1, cx + 3, torso_y + 3], fill=BOUNCER_BOWTIE)
    d.point([cx, torso_y + 2], fill=BOUNCER_BOWTIE_KNOT)
    # Suit lapel lines
    d.line([cx - 3, torso_y + 1, cx - 5, torso_y + 8], fill=BOUNCER_SUIT_LIGHT, width=1)
    d.line([cx + 3, torso_y + 1, cx + 5, torso_y + 8], fill=BOUNCER_SUIT_LIGHT, width=1)
    # Jacket button
    d.point([cx, torso_y + 10], fill=BOUNCER_SUIT_LIGHT)

    # ── Arms (suit sleeves) ──
    arm_y = torso_y + 2
    arm_len = 13
    if pose == "death" and frame >= 2:
        # Arms flop to sides
        d.rectangle([cx - torso_w // 2 - 5, arm_y + 4, cx - torso_w // 2, arm_y + 8],
                     fill=BOUNCER_SUIT, outline=BOUNCER_OUTLINE)
        d.rectangle([cx + torso_w // 2, arm_y + 4, cx + torso_w // 2 + 5, arm_y + 8],
                     fill=BOUNCER_SUIT, outline=BOUNCER_OUTLINE)
    elif pose == "attack":
        # Heavy swing — both arms involved
        swing_phase = frame % 4
        if swing_phase == 0:
            # Wind up — arms back
            la_end_y = arm_y + arm_len - 4
            ra_end_y = arm_y + arm_len - 4
            d.line([cx - torso_w // 2, arm_y, cx - torso_w // 2 - 4, la_end_y],
                   fill=BOUNCER_SUIT, width=3)
            d.line([cx + torso_w // 2, arm_y, cx + torso_w // 2 + 4, ra_end_y],
                   fill=BOUNCER_SUIT, width=3)
        elif swing_phase == 1:
            # Arms raised overhead
            la_end_y = arm_y - 5
            ra_end_y = arm_y - 5
            d.line([cx - torso_w // 2, arm_y, cx - 3, la_end_y],
                   fill=BOUNCER_SUIT, width=3)
            d.line([cx + torso_w // 2, arm_y, cx + 3, ra_end_y],
                   fill=BOUNCER_SUIT, width=3)
            # Clasped fists above
            d.rectangle([cx - 3, la_end_y - 2, cx + 3, la_end_y + 1],
                         fill=BOUNCER_SKIN)
        elif swing_phase == 2:
            # Slamming down — arms forward
            la_end_y = arm_y + arm_len + 3
            ra_end_y = arm_y + arm_len + 3
            d.line([cx - torso_w // 2, arm_y, cx - torso_w // 2 + 2, la_end_y],
                   fill=BOUNCER_SUIT, width=3)
            d.line([cx + torso_w // 2, arm_y, cx + torso_w // 2 - 2, ra_end_y],
                   fill=BOUNCER_SUIT, width=3)
            # Fists at bottom
            d.rectangle([cx - 4, la_end_y - 1, cx + 4, la_end_y + 2],
                         fill=BOUNCER_SKIN)
        else:
            # Recovery
            la_end_y = arm_y + arm_len
            ra_end_y = arm_y + arm_len
            d.line([cx - torso_w // 2, arm_y, cx - torso_w // 2 - 3, la_end_y],
                   fill=BOUNCER_SUIT, width=3)
            d.line([cx + torso_w // 2, arm_y, cx + torso_w // 2 + 3, ra_end_y],
                   fill=BOUNCER_SUIT, width=3)
            d.rectangle([cx - torso_w // 2 - 5, la_end_y - 1,
                          cx - torso_w // 2 - 2, la_end_y + 2], fill=BOUNCER_SKIN)
            d.rectangle([cx + torso_w // 2 + 2, ra_end_y - 1,
                          cx + torso_w // 2 + 5, ra_end_y + 2], fill=BOUNCER_SKIN)
    else:
        # Normal arms (standing guard or walking)
        la_end_y = arm_y + arm_len + ao[0]
        d.line([cx - torso_w // 2, arm_y, cx - torso_w // 2 - 3, la_end_y],
               fill=BOUNCER_SUIT, width=3)
        # Fist (hands clasped in front or at sides)
        d.rectangle([cx - torso_w // 2 - 5, la_end_y - 1,
                      cx - torso_w // 2 - 2, la_end_y + 2], fill=BOUNCER_SKIN)
        ra_end_y = arm_y + arm_len + ao[1]
        d.line([cx + torso_w // 2, arm_y, cx + torso_w // 2 + 3, ra_end_y],
               fill=BOUNCER_SUIT, width=3)
        d.rectangle([cx + torso_w // 2 + 2, ra_end_y - 1,
                      cx + torso_w // 2 + 5, ra_end_y + 2], fill=BOUNCER_SKIN)

    # ── Legs (dress pants) ──
    leg_w = 5
    if pose == "death" and frame >= 3:
        d.rectangle([cx - 7, hip_y, cx + 7, hip_y + 4], fill=BOUNCER_PANTS)
    else:
        # Left leg
        ll_x = cx - 4 + lo[0]
        d.rectangle([ll_x - leg_w // 2, hip_y, ll_x + leg_w // 2, foot_y],
                    fill=BOUNCER_PANTS, outline=BOUNCER_OUTLINE)
        # Crease line
        d.line([ll_x, hip_y + 2, ll_x, foot_y - 2], fill=BOUNCER_PANTS_CREASE, width=1)
        # Right leg
        rl_x = cx + 4 + lo[1]
        d.rectangle([rl_x - leg_w // 2, hip_y, rl_x + leg_w // 2, foot_y],
                    fill=BOUNCER_PANTS, outline=BOUNCER_OUTLINE)
        d.line([rl_x, hip_y + 2, rl_x, foot_y - 2], fill=BOUNCER_PANTS_CREASE, width=1)

        # Dress shoes (polished)
        d.rectangle([ll_x - leg_w // 2 - 1, foot_y - 2, ll_x + leg_w // 2 + 1, foot_y + 1],
                    fill=BOUNCER_SHOES)
        d.point([ll_x + 1, foot_y - 1], fill=BOUNCER_SHOES_SHINE)
        d.rectangle([rl_x - leg_w // 2 - 1, foot_y - 2, rl_x + leg_w // 2 + 1, foot_y + 1],
                    fill=BOUNCER_SHOES)
        d.point([rl_x + 1, foot_y - 1], fill=BOUNCER_SHOES_SHINE)

    # Hurt flash
    if pose == "hurt":
        d.rectangle([cx - 3, torso_y + 3, cx + 3, torso_y + 8],
                     fill=(255, 255, 255, 80))


def create_floor_bouncer_sheets():
    """Generate floor bouncer sprite sheets."""
    fw, fh = 26, 48

    sheets = {
        "floor_bouncer_walk_sheet.png": ("walk", 4),
        "floor_bouncer_attack_sheet.png": ("attack", 4),
        "floor_bouncer_hurt_sheet.png": ("hurt", 2),
        "floor_bouncer_death_sheet.png": ("death", 4),
    }

    for name, (pose, nframes) in sheets.items():
        img = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))
        for f in range(nframes):
            draw_bouncer_frame(img, f * fw, 0, fw, fh, pose, f)
        path = ENEMY_DIR / name
        img.save(path)
        print(f"  [OK] {name}")


# ── Mirror Ball (24x24) ──────────────────────────────────────────────────────


def draw_mirror_facets(d, cx, cy, radius, rotation=0):
    """Draw faceted mirror ball surface with rotating highlights.

    rotation: 0-3 shifts highlight pattern for animation.
    """
    # Draw base sphere
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              fill=MIRROR_BODY, outline=MIRROR_FACET_DARK)

    # Facet grid — horizontal bands
    for row in range(-radius + 2, radius, 3):
        y = cy + row
        # Width of sphere at this row (circular cross-section)
        row_dist = abs(row) / max(radius, 1)
        if row_dist > 0.9:
            continue
        half_w = int(radius * (1.0 - row_dist * row_dist) ** 0.5)

        for col_off in range(-half_w + 1, half_w, 3):
            fx = cx + col_off + ((rotation * 1) % 3)
            fy = y
            # Check bounds inside sphere
            dx = fx - cx
            dy = fy - cy
            if dx * dx + dy * dy > radius * radius:
                continue

            # Facet shading based on position and rotation
            facet_id = (fx * 7 + fy * 13 + rotation * 5) % 12
            if facet_id < 2:
                color = MIRROR_HIGHLIGHT
            elif facet_id < 5:
                color = MIRROR_BODY
            elif facet_id < 8:
                color = MIRROR_FACET_MID
            else:
                color = MIRROR_FACET_DARK

            # Draw small facet square
            d.rectangle([fx - 1, fy - 1, fx + 1, fy + 1], fill=color)

    # Specular highlight (shifts with rotation)
    spec_x = cx - 2 + (rotation % 3)
    spec_y = cy - 3 + (rotation % 2)
    d.rectangle([spec_x, spec_y, spec_x + 2, spec_y + 1], fill=MIRROR_HIGHLIGHT)
    d.point([spec_x + 1, spec_y - 1], fill=(255, 255, 255))


def draw_mirror_chain(d, cx, top_y, length=4):
    """Draw chain links hanging from above to the ball."""
    for i in range(length):
        link_y = top_y + i * 2
        if i % 2 == 0:
            d.rectangle([cx - 1, link_y, cx, link_y + 1], fill=MIRROR_CHAIN)
        else:
            d.rectangle([cx, link_y, cx + 1, link_y + 1], fill=MIRROR_CHAIN_LIGHT)


def draw_mirror_ball_frame(img, x_off, y_off, fw, fh, pose="spin", frame=0):
    """Draw a single mirror ball frame at given offset. 24x24."""
    d = ImageDraw.Draw(img)
    cx = x_off + fw // 2
    cy = y_off + fh // 2 + 2  # Slightly lower to leave room for chain
    radius = 8

    if pose == "walk":
        # Spinning rotation — facets shift each frame
        draw_mirror_chain(d, cx, y_off + 1, length=3)
        draw_mirror_facets(d, cx, cy, radius, rotation=frame)

        # Gentle bob up/down
        bob = [0, -1, 0, 1][frame % 4]
        if bob != 0:
            # Redraw with vertical offset
            # Clear and redraw (simple approach: just offset cy)
            pass  # bob already baked into visual via frame variation

    elif pose == "attack":
        # Light burst — radial beams emanate outward
        draw_mirror_chain(d, cx, y_off + 1, length=3)
        draw_mirror_facets(d, cx, cy, radius, rotation=frame)

        # Light beams radiating outward
        beam_count = 4 + frame * 2  # More beams as attack progresses
        beam_len = 3 + frame * 2
        import math
        for i in range(beam_count):
            angle = (i * 2 * math.pi / beam_count) + (frame * 0.3)
            bx1 = int(cx + (radius + 1) * math.cos(angle))
            by1 = int(cy + (radius + 1) * math.sin(angle))
            bx2 = int(cx + (radius + beam_len) * math.cos(angle))
            by2 = int(cy + (radius + beam_len) * math.sin(angle))
            beam_color = MIRROR_BEAM if i % 2 == 0 else MIRROR_BEAM_WHITE
            d.line([bx1, by1, bx2, by2], fill=beam_color, width=1)

        # Bright flash halo on frames 2-3
        if frame >= 2:
            halo_r = radius + 2
            d.arc([cx - halo_r, cy - halo_r, cx + halo_r, cy + halo_r],
                  0, 360, fill=MIRROR_BEAM, width=1)

    elif pose == "hurt":
        draw_mirror_chain(d, cx, y_off + 1, length=3)
        draw_mirror_facets(d, cx, cy, radius, rotation=0)

        # Hurt flash overlay
        flash_alpha = 140 if frame == 0 else 70
        d.ellipse([cx - radius + 1, cy - radius + 1, cx + radius - 1, cy + radius - 1],
                  fill=(255, 255, 255, flash_alpha))
        # Redraw a few dark facets on top so it still reads as a ball
        for dx, dy in [(-3, -2), (2, 3), (-1, 4), (4, -1)]:
            fx = cx + dx
            fy = cy + dy
            if (fx - cx) ** 2 + (fy - cy) ** 2 < radius * radius:
                d.point([fx, fy], fill=MIRROR_FACET_DARK)

    elif pose == "death":
        # Shatter into fragments
        if frame == 0:
            # Still intact but cracking
            draw_mirror_chain(d, cx, y_off + 1, length=3)
            draw_mirror_facets(d, cx, cy, radius, rotation=0)
            # Crack lines
            d.line([cx - 3, cy - 4, cx + 4, cy + 3], fill=MIRROR_CRACK, width=1)
            d.line([cx + 2, cy - 5, cx - 3, cy + 4], fill=MIRROR_CRACK, width=1)

        elif frame == 1:
            # Cracking more, pieces starting to separate
            draw_mirror_chain(d, cx, y_off + 1, length=2)  # Chain shortening
            # Draw fragmented sphere with gaps
            draw_mirror_facets(d, cx, cy, radius, rotation=1)
            # Multiple crack lines
            d.line([cx - radius, cy, cx + radius, cy], fill=MIRROR_CRACK, width=1)
            d.line([cx, cy - radius, cx, cy + radius], fill=MIRROR_CRACK, width=1)
            d.line([cx - 4, cy - 5, cx + 5, cy + 4], fill=MIRROR_CRACK, width=1)

        elif frame == 2:
            # Breaking apart — chunks flying
            draw_mirror_chain(d, cx, y_off + 1, length=1)
            # Top-left chunk
            d.rectangle([cx - 7, cy - 6, cx - 3, cy - 2], fill=MIRROR_BODY)
            d.point([cx - 5, cy - 4], fill=MIRROR_HIGHLIGHT)
            # Top-right chunk
            d.rectangle([cx + 3, cy - 7, cx + 7, cy - 3], fill=MIRROR_FACET_MID)
            d.point([cx + 5, cy - 5], fill=MIRROR_HIGHLIGHT)
            # Bottom-left chunk
            d.rectangle([cx - 8, cy + 2, cx - 4, cy + 6], fill=MIRROR_FACET_DARK)
            d.point([cx - 6, cy + 4], fill=MIRROR_BODY)
            # Bottom-right chunk
            d.rectangle([cx + 2, cy + 3, cx + 6, cy + 7], fill=MIRROR_BODY_DARK)
            d.point([cx + 4, cy + 5], fill=MIRROR_HIGHLIGHT)
            # Center debris
            d.point([cx, cy], fill=MIRROR_FACET_MID)
            d.point([cx - 1, cy + 1], fill=MIRROR_FACET_DARK)

        else:
            # Fully shattered — scattered tiny fragments falling
            # Dangling chain end
            d.point([cx, y_off + 2], fill=MIRROR_CHAIN)
            d.point([cx, y_off + 3], fill=MIRROR_CHAIN_LIGHT)
            # Small scattered shards
            shard_positions = [
                (cx - 8, cy - 4), (cx + 6, cy - 6),
                (cx - 5, cy + 5), (cx + 7, cy + 4),
                (cx - 2, cy + 7), (cx + 3, cy - 2),
                (cx, cy + 3), (cx - 6, cy),
            ]
            shard_colors = [MIRROR_BODY, MIRROR_HIGHLIGHT, MIRROR_FACET_MID,
                            MIRROR_FACET_DARK, MIRROR_BODY_DARK, MIRROR_HIGHLIGHT,
                            MIRROR_FACET_MID, MIRROR_BODY]
            for (sx, sy), sc in zip(shard_positions, shard_colors):
                d.point([sx, sy], fill=sc)
                # Some shards are 2px
                if random.random() > 0.5:
                    d.point([sx + 1, sy], fill=sc)

    else:
        # Default standing/idle
        draw_mirror_chain(d, cx, y_off + 1, length=3)
        draw_mirror_facets(d, cx, cy, radius, rotation=0)


def create_mirror_ball_sheets():
    """Generate mirror ball sprite sheets."""
    fw, fh = 24, 24

    sheets = {
        "mirror_ball_walk_sheet.png": ("walk", 4),
        "mirror_ball_attack_sheet.png": ("attack", 4),
        "mirror_ball_hurt_sheet.png": ("hurt", 2),
        "mirror_ball_death_sheet.png": ("death", 4),
    }

    for name, (pose, nframes) in sheets.items():
        img = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))
        for f in range(nframes):
            draw_mirror_ball_frame(img, f * fw, 0, fw, fh, pose, f)
        path = ENEMY_DIR / name
        img.save(path)
        print(f"  [OK] {name}")


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    print("Generating Disco Floor enemies (Level 05 — Bee Gees Disco Floor)...")

    print("\nDisco Dancer (palette-swap from shooter):")
    swap_explicit([
        ("shooter_skate_sheet.png", "disco_dancer_walk_sheet.png"),
        ("shooter_shoot_skate_sheet.png", "disco_dancer_attack_sheet.png"),
        ("shooter_hurt_sheet.png", "disco_dancer_hurt_sheet.png"),
        ("shooter_death_sheet.png", "disco_dancer_death_sheet.png"),
    ], remap_disco_dancer)

    print("\nFloor Bouncer (from scratch):")
    create_floor_bouncer_sheets()

    print("\nMirror Ball (from scratch):")
    create_mirror_ball_sheets()

    print("\nDone! Disco Floor enemies generated.")


if __name__ == "__main__":
    main()
