#!/usr/bin/env python3
"""Generate Jimmy Page boss sprites for Disco Cop Level 03.

Palette-swap from Disco King (48x80/frame):
  - jimmy_page_idle_sheet  (192x80, 4f)
  - jimmy_page_hurt_sheet  (96x80, 2f)
  - jimmy_page_death_sheet (384x80, 8f)

From-scratch attack sheets (48x80/frame):
  - jimmy_page_sweep_sheet    (288x80, 6f) — guitar swing L to R
  - jimmy_page_feedback_sheet (288x80, 6f) — guitar raised, sound rings
  - jimmy_page_pyro_sheet     (288x80, 6f) — flames rising around him
  - jimmy_page_chord_sheet    (192x80, 4f) — strum pose, projectile launch
  - jimmy_page_solo_sheet     (288x80, 6f) — fast strumming, motion blur

Usage:
    python create_concert_boss.py
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
BOSS_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "bosses"

random.seed(606)

# ── Palette-swap ──────────────────────────────────────────────────────────────

def remap_jimmy_page(r, g, b, a):
    """Disco King → Jimmy Page: purple/black rocker outfit, wild hair."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 160:
        # Very light (disco suit highlights) → dark leather jacket highlight
        return (max(int(r * 0.4), 50), max(int(g * 0.35), 40), min(int(b * 0.6), 80), a)
    elif is_gray and brightness > 120:
        # Light body → deep purple shirt
        return (min(int(r * 0.7), 120), max(int(g * 0.3), 25), min(int(b * 1.2), 160), a)
    elif is_gray and brightness > 80:
        # Mid body → black leather
        return (max(int(r * 0.35), 30), max(int(g * 0.3), 25), max(int(b * 0.4), 40), a)
    elif brightness > 120 and r > b:
        # Warm tones (gold/skin) → pale skin with purple tint
        return (min(int(r * 0.9), 190), min(int(g * 0.7), 150), min(int(b * 0.8), 140), a)
    elif brightness > 80 and b > r:
        # Cool tones → deeper purple/blue
        return (max(int(r * 0.5), 40), max(int(g * 0.3), 20), min(int(b * 1.3), 200), a)
    elif brightness > 60:
        # Mid tones → dark purplish
        return (max(int(r * 0.5), 45), max(int(g * 0.35), 30), min(int(b * 0.8), 100), a)
    elif brightness > 30:
        # Dark → very dark with purple hint
        return (max(int(r * 0.4), 20), max(int(g * 0.3), 15), min(int(b * 0.6), 50), a)
    else:
        # Very dark (outlines) → pure dark
        return (min(r + 5, 30), min(g + 3, 20), min(b + 8, 40), a)


def swap_boss_sheets():
    """Palette-swap Disco King sheets to Jimmy Page."""
    mappings = [
        ("disco_king_idle_sheet.png", "jimmy_page_idle_sheet.png"),
        ("disco_king_hurt_sheet.png", "jimmy_page_hurt_sheet.png"),
        ("disco_king_death_sheet.png", "jimmy_page_death_sheet.png"),
    ]
    for src_name, dst_name in mappings:
        src_path = BOSS_DIR / src_name
        if not src_path.exists():
            print(f"  [SKIP] {src_name} — not found")
            continue

        img = Image.open(src_path).convert("RGBA")
        px = np.array(img)
        h, w, _ = px.shape
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[y, x]
                px[y, x] = remap_jimmy_page(int(r), int(g), int(b), int(a))

        dst_path = BOSS_DIR / dst_name
        Image.fromarray(px.astype(np.uint8), "RGBA").save(dst_path)
        print(f"  [OK] {dst_name}")


# ── From-scratch attack sheets ────────────────────────────────────────────────

# Jimmy Page palette
JP_SKIN = (195, 170, 150)
JP_SKIN_SHADOW = (160, 135, 115)
JP_HAIR = (30, 20, 15)
JP_HAIR_HIGHLIGHT = (60, 45, 35)
JP_JACKET = (25, 22, 30)
JP_JACKET_LIGHT = (45, 40, 55)
JP_SHIRT = (80, 30, 120)
JP_SHIRT_LIGHT = (110, 50, 155)
JP_PANTS = (20, 18, 25)
JP_PANTS_LIGHT = (35, 30, 42)
JP_BOOTS = (30, 25, 20)
JP_OUTLINE = (15, 10, 12)

# Les Paul guitar palette
GUITAR_BODY = (140, 40, 20)       # Cherry sunburst
GUITAR_BODY_LIGHT = (180, 70, 30)
GUITAR_BODY_DARK = (90, 25, 12)
GUITAR_NECK = (160, 120, 70)
GUITAR_NECK_DARK = (120, 85, 50)
GUITAR_HEAD = (30, 25, 20)
GUITAR_STRING = (200, 200, 210)
GUITAR_PICKUP = (60, 55, 50)
GUITAR_GOLD = (210, 180, 60)

# Effect colors
SOUND_RING = (180, 160, 255)
FLAME_YELLOW = (255, 220, 50)
FLAME_ORANGE = (255, 150, 20)
FLAME_RED = (255, 60, 10)
PROJECTILE_GLOW = (255, 200, 100)
MOTION_BLUR = (100, 60, 160)

FW, FH = 48, 80


def draw_jp_body(d, cx, cy, pose_data=None):
    """Draw Jimmy Page's body (no guitar). Returns key points for guitar attachment."""
    p = pose_data or {}
    head_tilt = p.get("head_tilt", 0)
    torso_lean = p.get("torso_lean", 0)
    l_arm_angle = p.get("l_arm_angle", -30)
    r_arm_angle = p.get("r_arm_angle", 30)

    # ── Legs ──
    hip_y = cy + 14
    foot_y = cy + 34
    leg_spread = p.get("leg_spread", 5)

    # Left leg
    ll_x = cx - leg_spread + torso_lean
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=JP_PANTS, width=4)
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=JP_PANTS_LIGHT, width=2)
    # Boot
    d.rectangle([ll_x - 3, foot_y - 2, ll_x + 3, foot_y + 2], fill=JP_BOOTS)

    # Right leg
    rl_x = cx + leg_spread + torso_lean
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=JP_PANTS, width=4)
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=JP_PANTS_LIGHT, width=2)
    # Boot
    d.rectangle([rl_x - 3, foot_y - 2, rl_x + 3, foot_y + 2], fill=JP_BOOTS)

    # ── Torso ──
    torso_top = cy - 8
    torso_cx = cx + torso_lean
    # Jacket (wider silhouette)
    d.rectangle([torso_cx - 10, torso_top, torso_cx + 10, hip_y], fill=JP_JACKET)
    # Shirt V-neck
    d.polygon([(torso_cx - 4, torso_top + 2), (torso_cx + 4, torso_top + 2),
               (torso_cx, torso_top + 10)], fill=JP_SHIRT)
    # Jacket lapels
    d.line([torso_cx - 10, torso_top, torso_cx - 4, torso_top + 8],
           fill=JP_JACKET_LIGHT, width=1)
    d.line([torso_cx + 10, torso_top, torso_cx + 4, torso_top + 8],
           fill=JP_JACKET_LIGHT, width=1)

    # ── Arms ──
    arm_len = 18
    shoulder_y = torso_top + 3

    # Left arm
    la_rad = math.radians(l_arm_angle)
    la_ex = torso_cx - 10 + int(arm_len * math.sin(la_rad))
    la_ey = shoulder_y + int(arm_len * math.cos(la_rad))
    d.line([torso_cx - 10, shoulder_y, la_ex, la_ey], fill=JP_JACKET, width=4)
    # Hand
    d.ellipse([la_ex - 2, la_ey - 2, la_ex + 2, la_ey + 2], fill=JP_SKIN)

    # Right arm
    ra_rad = math.radians(r_arm_angle)
    ra_ex = torso_cx + 10 + int(arm_len * math.sin(ra_rad))
    ra_ey = shoulder_y + int(arm_len * math.cos(ra_rad))
    d.line([torso_cx + 10, shoulder_y, ra_ex, ra_ey], fill=JP_JACKET, width=4)
    # Hand
    d.ellipse([ra_ex - 2, ra_ey - 2, ra_ex + 2, ra_ey + 2], fill=JP_SKIN)

    # ── Head ──
    head_cx = torso_cx + head_tilt
    head_cy = torso_top - 10
    head_w, head_h = 9, 12
    d.ellipse([head_cx - head_w // 2, head_cy - head_h // 2,
               head_cx + head_w // 2, head_cy + head_h // 2],
              fill=JP_SKIN, outline=JP_OUTLINE)
    # Eyes
    d.point([head_cx - 2, head_cy - 1], fill=JP_OUTLINE)
    d.point([head_cx + 2, head_cy - 1], fill=JP_OUTLINE)
    # Mouth
    d.point([head_cx, head_cy + 2], fill=JP_SKIN_SHADOW)

    # ── Wild curly hair ──
    for angle in range(0, 360, 20):
        rad = math.radians(angle)
        hair_len = random.randint(6, 12)
        for j in range(hair_len):
            t = j / hair_len
            hx = head_cx + int((head_w // 2 + j) * math.cos(rad) * (0.8 + 0.4 * math.sin(j)))
            hy = head_cy - head_h // 2 + int((head_h // 2 + j) * math.sin(rad) * 0.6) - 2
            if abs(hx - head_cx) < FW // 2 and 0 <= hy < FH:
                c = JP_HAIR if t < 0.6 else JP_HAIR_HIGHLIGHT
                d.point([hx, hy], fill=c)

    return {
        "l_hand": (la_ex, la_ey),
        "r_hand": (ra_ex, ra_ey),
        "torso_cx": torso_cx,
        "shoulder_y": shoulder_y,
    }


def draw_les_paul(d, x, y, angle_deg=0, scale=1.0):
    """Draw a Les Paul guitar at position with rotation."""
    # Simplified guitar: body ellipse + neck rectangle + headstock
    body_w = int(14 * scale)
    body_h = int(10 * scale)
    neck_len = int(18 * scale)

    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    # Guitar body (ellipse approximation with rotated rect)
    for dy in range(-body_h // 2, body_h // 2 + 1):
        for dx in range(-body_w // 2, body_w // 2 + 1):
            if (dx / (body_w / 2.0)) ** 2 + (dy / (body_h / 2.0)) ** 2 <= 1:
                rx = x + int(dx * cos_a - dy * sin_a)
                ry = y + int(dx * sin_a + dy * cos_a)
                dist = math.sqrt(dx * dx + dy * dy)
                max_r = math.sqrt((body_w / 2) ** 2 + (body_h / 2) ** 2)
                t = dist / max_r
                if t < 0.4:
                    c = GUITAR_BODY_LIGHT
                elif t < 0.7:
                    c = GUITAR_BODY
                else:
                    c = GUITAR_BODY_DARK
                d.point([rx, ry], fill=c)

    # Pickups
    for offset in [-2, 3]:
        px = x + int(offset * cos_a)
        py = y + int(offset * sin_a)
        d.rectangle([px - 2, py - 1, px + 2, py + 1], fill=GUITAR_PICKUP)

    # Bridge/tailpiece
    d.point([x + int(5 * cos_a), y + int(5 * sin_a)], fill=GUITAR_GOLD)

    # Neck
    for i in range(neck_len):
        nx = x + int((-body_w // 2 - i) * cos_a)
        ny = y + int((-body_w // 2 - i) * sin_a)
        d.rectangle([nx - 1, ny - 1, nx + 1, ny + 1], fill=GUITAR_NECK)
        # Fret dots
        if i % 5 == 0:
            d.point([nx, ny], fill=GUITAR_NECK_DARK)

    # Headstock
    hx = x + int((-body_w // 2 - neck_len) * cos_a)
    hy = y + int((-body_w // 2 - neck_len) * sin_a)
    d.rectangle([hx - 3, hy - 3, hx + 3, hy + 3], fill=GUITAR_HEAD)
    # Tuning pegs
    for peg_off in [-2, 0, 2]:
        d.point([hx - 4, hy + peg_off], fill=GUITAR_GOLD)
        d.point([hx + 4, hy + peg_off], fill=GUITAR_GOLD)

    # Strings (thin lines from bridge to headstock)
    bx = x + int(5 * cos_a)
    by = y + int(5 * sin_a)
    d.line([bx, by, hx, hy], fill=GUITAR_STRING, width=1)


def draw_sound_rings(d, cx, cy, num_rings, max_radius, alpha_base=180):
    """Draw expanding sound wave rings."""
    for i in range(num_rings):
        t = (i + 1) / num_rings
        r = int(max_radius * t)
        alpha = max(20, int(alpha_base * (1 - t)))
        color = (*SOUND_RING[:3], alpha)
        d.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], outline=color, width=1)


def draw_flames(d, cx, base_y, height, width, intensity=1.0):
    """Draw rising flame effect."""
    for _ in range(int(12 * intensity)):
        fx = cx + random.randint(-width, width)
        flame_h = random.randint(int(height * 0.3), height)
        fy = base_y - flame_h
        # Flame tongue
        colors = [FLAME_RED, FLAME_ORANGE, FLAME_YELLOW]
        for j in range(flame_h):
            t = j / flame_h
            c = colors[min(int(t * 3), 2)]
            py = base_y - j
            px = fx + random.randint(-1, 1)
            d.point([px, py], fill=c)
        # Tip
        d.point([fx, fy], fill=FLAME_YELLOW)


def create_sweep_sheet():
    """Guitar swing L to R — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        # Guitar angle sweeps from left (-60) to right (+60)
        guitar_angle = -60 + f * 24

        # Body pose: leaning into swing
        lean = int((f - 2.5) * 2)
        pose = {
            "torso_lean": lean,
            "head_tilt": lean // 2,
            "l_arm_angle": -40 + f * 8,
            "r_arm_angle": -20 + f * 15,
            "leg_spread": 6 + abs(f - 3),
        }

        pts = draw_jp_body(d, cx, cy, pose)
        # Guitar follows right hand
        gx = pts["r_hand"][0]
        gy = pts["r_hand"][1]
        draw_les_paul(d, gx, gy, guitar_angle)

        # Motion trail for later frames
        if f >= 3:
            trail_alpha = 60 + (f - 3) * 30
            for tx in range(gx - 10, gx + 10):
                for ty in range(gy - 5, gy + 5):
                    if 0 <= tx < img.width and 0 <= ty < FH:
                        r0, g0, b0, a0 = img.getpixel((tx, ty))
                        if a0 == 0:
                            img.putpixel((tx, ty), (*MOTION_BLUR, trail_alpha // 2))

    path = BOSS_DIR / "jimmy_page_sweep_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def create_feedback_sheet():
    """Guitar raised, sound rings expanding — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        # Guitar raised overhead, body leaning back
        pose = {
            "torso_lean": -2,
            "head_tilt": -1,
            "l_arm_angle": -70 - f * 3,
            "r_arm_angle": -60 - f * 3,
            "leg_spread": 7,
        }

        pts = draw_jp_body(d, cx, cy, pose)

        # Guitar above head, angled up
        gx = cx
        gy = cy - 28 - f
        draw_les_paul(d, gx, gy, -80 + f * 5)

        # Sound rings emanating from guitar
        if f >= 1:
            draw_sound_rings(d, gx, gy, f, 8 + f * 6)

        # Vibration on body
        if f >= 3:
            for _ in range(f * 2):
                vx = cx + random.randint(-15, 15)
                vy = cy + random.randint(-20, 20)
                if 0 <= vx < img.width and 0 <= vy < FH:
                    r0, g0, b0, a0 = img.getpixel((vx, vy))
                    if a0 > 0:
                        img.putpixel((vx, vy), (min(r0 + 30, 255), min(g0 + 20, 255),
                                                  min(b0 + 50, 255), a0))

    path = BOSS_DIR / "jimmy_page_feedback_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def create_pyro_sheet():
    """Flames rising around him — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        # Power stance, arms spread
        pose = {
            "torso_lean": 0,
            "head_tilt": 0,
            "l_arm_angle": -45 + f * 5,
            "r_arm_angle": 45 - f * 5,
            "leg_spread": 8,
        }

        draw_jp_body(d, cx, cy, pose)

        # Guitar slung at side
        draw_les_paul(d, cx + 12, cy + 8, 30)

        # Flames rising from ground, increasing intensity
        flame_intensity = (f + 1) / nf
        flame_height = 15 + f * 8
        for flame_x_off in [-15, -8, 0, 8, 15]:
            draw_flames(d, cx + flame_x_off, cy + 34, flame_height,
                       3, flame_intensity)

        # Heat haze effect (subtle shift) on upper pixels
        if f >= 2:
            for hy in range(0, cy - 10):
                for hx in range(x_off + 5, x_off + FW - 5):
                    if 0 <= hx < img.width and 0 <= hy < FH:
                        r0, g0, b0, a0 = img.getpixel((hx, hy))
                        if a0 > 0:
                            warm = min(f * 8, 40)
                            img.putpixel((hx, hy), (min(r0 + warm, 255), g0,
                                                      max(b0 - warm // 2, 0), a0))

    path = BOSS_DIR / "jimmy_page_pyro_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def create_chord_sheet():
    """Strum pose, projectile launch — 4 frames."""
    nf = 4
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        # Strumming stance
        strum_offset = [0, -2, 2, 0][f]
        pose = {
            "torso_lean": 2,
            "head_tilt": 1,
            "l_arm_angle": -20 + strum_offset * 3,
            "r_arm_angle": 10 + strum_offset * 5,
            "leg_spread": 5,
        }

        pts = draw_jp_body(d, cx, cy, pose)

        # Guitar in playing position
        gx = cx + 5
        gy = cy + 2
        draw_les_paul(d, gx, gy, 15 + strum_offset * 3)

        # Strum flash on frame 1
        if f == 1:
            for sx in range(gx - 6, gx + 6):
                for sy in range(gy - 4, gy + 4):
                    if 0 <= sx < img.width and 0 <= sy < FH:
                        dist = math.sqrt((sx - gx) ** 2 + (sy - gy) ** 2)
                        if dist < 6:
                            alpha = int(150 * (1 - dist / 6))
                            r0, g0, b0, a0 = img.getpixel((sx, sy))
                            img.putpixel((sx, sy), (min(r0 + alpha, 255),
                                                     min(g0 + alpha, 255),
                                                     min(b0 + alpha // 2, 255),
                                                     max(a0, alpha)))

        # Projectile (note/energy ball) launching on frames 2-3
        if f >= 2:
            proj_dist = (f - 1) * 12
            proj_x = cx + 15 + proj_dist
            proj_y = cy - 5
            if proj_x < x_off + FW:
                # Energy ball
                pr = 4
                d.ellipse([proj_x - pr, proj_y - pr, proj_x + pr, proj_y + pr],
                          fill=PROJECTILE_GLOW)
                # Glow
                d.ellipse([proj_x - pr - 2, proj_y - pr - 2,
                          proj_x + pr + 2, proj_y + pr + 2],
                          outline=(*SOUND_RING[:3], 120))
                # Musical note hint (small flag)
                d.line([proj_x + 2, proj_y - 3, proj_x + 2, proj_y + 1], fill=(255, 255, 200))
                d.line([proj_x + 2, proj_y - 3, proj_x + 5, proj_y - 1], fill=(255, 255, 200))

    path = BOSS_DIR / "jimmy_page_chord_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def create_solo_sheet():
    """Fast strumming, motion blur — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        # Frantic pose, alternating hand positions
        strum_phase = math.sin(f * math.pi * 0.8)
        pose = {
            "torso_lean": int(strum_phase * 3),
            "head_tilt": int(strum_phase * 2),
            "l_arm_angle": -25 + int(strum_phase * 10),
            "r_arm_angle": 15 + int(strum_phase * 15),
            "leg_spread": 6,
        }

        draw_jp_body(d, cx, cy, pose)

        # Guitar in playing position, slight angle variation
        gx = cx + 4 + int(strum_phase * 2)
        gy = cy + 1
        draw_les_paul(d, gx, gy, 12 + int(strum_phase * 8))

        # Motion blur on strumming hand area
        blur_cx = gx
        blur_cy = gy
        for _ in range(8 + f * 2):
            bx = blur_cx + random.randint(-8, 8)
            by = blur_cy + random.randint(-5, 5)
            if 0 <= bx < img.width and 0 <= by < FH:
                r0, g0, b0, a0 = img.getpixel((bx, by))
                if a0 == 0:
                    img.putpixel((bx, by), (*MOTION_BLUR, 40 + random.randint(0, 40)))
                else:
                    img.putpixel((bx, by), (min(r0 + 20, 255), min(g0 + 10, 255),
                                              min(b0 + 30, 255), a0))

        # Speed lines radiating from guitar
        for _ in range(4):
            angle = random.uniform(-0.5, 0.5) + math.pi * (0.5 if strum_phase > 0 else -0.5)
            line_len = random.randint(8, 18)
            sx = gx + int(6 * math.cos(angle))
            sy = gy + int(3 * math.sin(angle))
            ex = sx + int(line_len * math.cos(angle))
            ey = sy + int(line_len * math.sin(angle))
            d.line([sx, sy, ex, ey], fill=(*SOUND_RING[:3], 100), width=1)

        # Energy sparks
        if f >= 2:
            for _ in range(f):
                sx = cx + random.randint(-18, 18)
                sy = cy + random.randint(-25, 15)
                if x_off <= sx < x_off + FW and 0 <= sy < FH:
                    d.point([sx, sy], fill=PROJECTILE_GLOW)

    path = BOSS_DIR / "jimmy_page_solo_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    print("Generating Jimmy Page boss sprites...")

    # Palette-swaps from Disco King
    print("\nPalette-swap sheets (from Disco King):")
    swap_boss_sheets()

    # From-scratch attack sheets
    print("\nFrom-scratch attack sheets:")
    create_sweep_sheet()
    create_feedback_sheet()
    create_pyro_sheet()
    create_chord_sheet()
    create_solo_sheet()

    print("\nDone! 8 Jimmy Page boss sprites generated.")


if __name__ == "__main__":
    main()
