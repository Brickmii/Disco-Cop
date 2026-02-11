#!/usr/bin/env python3
"""Generate Sex Pistols Concert boss sprites for Disco Cop Level 03.

Two bosses: Johnny Rotten (frontman, guitar-based attacks) and
Sid Vicious (bassist, physical/melee attacks).

Johnny Rotten (48x80/frame):
  Palette-swap from Disco King:
    - johnny_rotten_idle_sheet  (192x80, 4f)
    - johnny_rotten_hurt_sheet  (96x80, 2f)
    - johnny_rotten_death_sheet (384x80, 8f)
  From-scratch attack sheets:
    - johnny_rotten_sweep_sheet    (288x80, 6f)
    - johnny_rotten_feedback_sheet (288x80, 6f)
    - johnny_rotten_pyro_sheet     (288x80, 6f)
    - johnny_rotten_chord_sheet    (192x80, 4f)
    - johnny_rotten_solo_sheet     (288x80, 6f)

Sid Vicious (48x80/frame):
  Palette-swap from Disco King:
    - sid_vicious_idle_sheet  (192x80, 4f)
    - sid_vicious_hurt_sheet  (96x80, 2f)
    - sid_vicious_death_sheet (384x80, 8f)
  From-scratch attack sheets:
    - sid_vicious_bass_swing_sheet  (288x80, 6f)
    - sid_vicious_chain_whip_sheet  (288x80, 6f)
    - sid_vicious_punk_spit_sheet   (192x80, 4f)
    - sid_vicious_stage_dive_sheet  (288x80, 6f)
    - sid_vicious_berserker_sheet   (288x80, 6f)

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

random.seed(707)

FW, FH = 48, 80

# ── Effect colors (shared) ───────────────────────────────────────────────────

SOUND_RING = (180, 160, 255)
FLAME_YELLOW = (255, 220, 50)
FLAME_ORANGE = (255, 150, 20)
FLAME_RED = (255, 60, 10)
PROJECTILE_GLOW = (255, 200, 100)
MOTION_BLUR = (100, 60, 160)
PUNK_GREEN = (60, 200, 60)
SPIT_GREEN = (120, 220, 40)
CHAIN_SILVER = (190, 195, 205)
CHAIN_DARK = (110, 115, 125)


# ══════════════════════════════════════════════════════════════════════════════
#  JOHNNY ROTTEN — Punk frontman, guitar attacks
# ══════════════════════════════════════════════════════════════════════════════

# Johnny Rotten palette
JR_SKIN = (200, 175, 155)
JR_SKIN_SHADOW = (165, 140, 120)
JR_HAIR = (200, 100, 30)       # Spiky orange hair
JR_HAIR_TIP = (240, 140, 50)
JR_SHIRT = (40, 35, 30)        # Ripped black shirt
JR_SHIRT_RIP = (80, 70, 60)
JR_JACKET = (35, 80, 35)       # Army-green jacket
JR_JACKET_LIGHT = (55, 110, 55)
JR_PANTS = (25, 25, 30)        # Black drainpipes
JR_PANTS_LIGHT = (40, 40, 48)
JR_BOOTS = (30, 25, 20)
JR_SAFETY_PIN = (200, 200, 210)
JR_OUTLINE = (15, 10, 12)

# Guitar palette (battered Fender)
JR_GUITAR_BODY = (180, 180, 185)    # White/cream Telecaster
JR_GUITAR_BODY_LIGHT = (210, 210, 215)
JR_GUITAR_BODY_DARK = (140, 140, 148)
JR_GUITAR_NECK = (160, 120, 70)
JR_GUITAR_NECK_DARK = (120, 85, 50)
JR_GUITAR_HEAD = (30, 25, 20)
JR_GUITAR_STRING = (200, 200, 210)
JR_GUITAR_PICKUP = (60, 55, 50)
JR_GUITAR_GOLD = (210, 180, 60)


def remap_johnny_rotten(r, g, b, a):
    """Disco King → Johnny Rotten: punk green/black, safety pins, sneering."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 160:
        # Very light (disco suit highlights) → army green jacket highlight
        return (max(int(r * 0.3), 45), min(int(g * 0.7), 110), max(int(b * 0.3), 40), a)
    elif is_gray and brightness > 120:
        # Light body → ripped black shirt
        return (max(int(r * 0.3), 35), max(int(g * 0.3), 30), max(int(b * 0.3), 32), a)
    elif is_gray and brightness > 80:
        # Mid body → dark green jacket
        return (max(int(r * 0.3), 30), min(int(g * 0.6), 75), max(int(b * 0.3), 30), a)
    elif brightness > 120 and r > b:
        # Warm tones (gold/skin) → pale punk skin
        return (min(int(r * 0.95), 200), min(int(g * 0.8), 170), min(int(b * 0.75), 150), a)
    elif brightness > 80 and b > r:
        # Cool tones → darker green
        return (max(int(r * 0.35), 25), min(int(g * 0.8), 100), max(int(b * 0.35), 30), a)
    elif brightness > 60:
        # Mid tones → olive drab
        return (max(int(r * 0.45), 40), min(int(g * 0.55), 65), max(int(b * 0.35), 28), a)
    elif brightness > 30:
        # Dark → very dark with green hint
        return (max(int(r * 0.3), 18), min(int(g * 0.4), 30), max(int(b * 0.3), 15), a)
    else:
        return (min(r + 3, 25), min(g + 5, 22), min(b + 3, 18), a)


def draw_jr_body(d, cx, cy, pose_data=None):
    """Draw Johnny Rotten's body. Returns key points for guitar attachment."""
    p = pose_data or {}
    head_tilt = p.get("head_tilt", 0)
    torso_lean = p.get("torso_lean", 0)
    l_arm_angle = p.get("l_arm_angle", -30)
    r_arm_angle = p.get("r_arm_angle", 30)

    hip_y = cy + 14
    foot_y = cy + 34
    leg_spread = p.get("leg_spread", 5)

    # Legs (black drainpipes)
    ll_x = cx - leg_spread + torso_lean
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=JR_PANTS, width=4)
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=JR_PANTS_LIGHT, width=2)
    d.rectangle([ll_x - 3, foot_y - 2, ll_x + 3, foot_y + 2], fill=JR_BOOTS)

    rl_x = cx + leg_spread + torso_lean
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=JR_PANTS, width=4)
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=JR_PANTS_LIGHT, width=2)
    d.rectangle([rl_x - 3, foot_y - 2, rl_x + 3, foot_y + 2], fill=JR_BOOTS)

    # Torso
    torso_top = cy - 8
    torso_cx = cx + torso_lean
    d.rectangle([torso_cx - 10, torso_top, torso_cx + 10, hip_y], fill=JR_JACKET)
    # Ripped shirt underneath
    d.rectangle([torso_cx - 5, torso_top + 3, torso_cx + 5, torso_top + 12], fill=JR_SHIRT)
    # Shirt rip holes
    d.point([torso_cx - 2, torso_top + 6], fill=JR_SHIRT_RIP)
    d.point([torso_cx + 3, torso_top + 8], fill=JR_SHIRT_RIP)
    # Jacket lapels
    d.line([torso_cx - 10, torso_top, torso_cx - 5, torso_top + 8],
           fill=JR_JACKET_LIGHT, width=1)
    d.line([torso_cx + 10, torso_top, torso_cx + 5, torso_top + 8],
           fill=JR_JACKET_LIGHT, width=1)
    # Safety pins on jacket
    d.line([torso_cx - 8, torso_top + 4, torso_cx - 6, torso_top + 2], fill=JR_SAFETY_PIN)
    d.line([torso_cx + 7, torso_top + 6, torso_cx + 9, torso_top + 4], fill=JR_SAFETY_PIN)

    # Arms
    arm_len = 18
    shoulder_y = torso_top + 3

    la_rad = math.radians(l_arm_angle)
    la_ex = torso_cx - 10 + int(arm_len * math.sin(la_rad))
    la_ey = shoulder_y + int(arm_len * math.cos(la_rad))
    d.line([torso_cx - 10, shoulder_y, la_ex, la_ey], fill=JR_JACKET, width=4)
    d.ellipse([la_ex - 2, la_ey - 2, la_ex + 2, la_ey + 2], fill=JR_SKIN)

    ra_rad = math.radians(r_arm_angle)
    ra_ex = torso_cx + 10 + int(arm_len * math.sin(ra_rad))
    ra_ey = shoulder_y + int(arm_len * math.cos(ra_rad))
    d.line([torso_cx + 10, shoulder_y, ra_ex, ra_ey], fill=JR_JACKET, width=4)
    d.ellipse([ra_ex - 2, ra_ey - 2, ra_ex + 2, ra_ey + 2], fill=JR_SKIN)

    # Head
    head_cx = torso_cx + head_tilt
    head_cy = torso_top - 10
    head_w, head_h = 9, 12
    d.ellipse([head_cx - head_w // 2, head_cy - head_h // 2,
               head_cx + head_w // 2, head_cy + head_h // 2],
              fill=JR_SKIN, outline=JR_OUTLINE)
    # Sneering eyes
    d.line([head_cx - 3, head_cy - 1, head_cx - 1, head_cy - 1], fill=JR_OUTLINE)
    d.line([head_cx + 1, head_cy - 1, head_cx + 3, head_cy - 1], fill=JR_OUTLINE)
    # Sneering mouth
    d.line([head_cx - 2, head_cy + 2, head_cx + 2, head_cy + 3], fill=JR_OUTLINE)

    # Spiky orange hair (upward spikes)
    for spike_x in range(-4, 5, 2):
        spike_h = random.randint(6, 12)
        base_x = head_cx + spike_x
        tip_x = base_x + random.randint(-2, 2)
        tip_y = head_cy - head_h // 2 - spike_h
        for j in range(spike_h):
            t = j / spike_h
            hx = int(base_x + (tip_x - base_x) * t)
            hy = head_cy - head_h // 2 - j
            if 0 <= hy < FH:
                c = JR_HAIR if t < 0.5 else JR_HAIR_TIP
                d.point([hx, hy], fill=c)
                if t < 0.3:
                    d.point([hx + 1, hy], fill=c)

    return {
        "l_hand": (la_ex, la_ey),
        "r_hand": (ra_ex, ra_ey),
        "torso_cx": torso_cx,
        "shoulder_y": shoulder_y,
    }


def draw_jr_guitar(d, x, y, angle_deg=0):
    """Draw Johnny Rotten's battered Telecaster."""
    body_w, body_h = 14, 10
    neck_len = 18
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    for dy in range(-body_h // 2, body_h // 2 + 1):
        for dx in range(-body_w // 2, body_w // 2 + 1):
            if (dx / (body_w / 2.0)) ** 2 + (dy / (body_h / 2.0)) ** 2 <= 1:
                rx = x + int(dx * cos_a - dy * sin_a)
                ry = y + int(dx * sin_a + dy * cos_a)
                dist = math.sqrt(dx * dx + dy * dy)
                max_r = math.sqrt((body_w / 2) ** 2 + (body_h / 2) ** 2)
                t = dist / max_r
                if t < 0.4:
                    c = JR_GUITAR_BODY_LIGHT
                elif t < 0.7:
                    c = JR_GUITAR_BODY
                else:
                    c = JR_GUITAR_BODY_DARK
                d.point([rx, ry], fill=c)

    for offset in [-2, 3]:
        px = x + int(offset * cos_a)
        py = y + int(offset * sin_a)
        d.rectangle([px - 2, py - 1, px + 2, py + 1], fill=JR_GUITAR_PICKUP)

    d.point([x + int(5 * cos_a), y + int(5 * sin_a)], fill=JR_GUITAR_GOLD)

    for i in range(neck_len):
        nx = x + int((-body_w // 2 - i) * cos_a)
        ny = y + int((-body_w // 2 - i) * sin_a)
        d.rectangle([nx - 1, ny - 1, nx + 1, ny + 1], fill=JR_GUITAR_NECK)
        if i % 5 == 0:
            d.point([nx, ny], fill=JR_GUITAR_NECK_DARK)

    hx = x + int((-body_w // 2 - neck_len) * cos_a)
    hy = y + int((-body_w // 2 - neck_len) * sin_a)
    d.rectangle([hx - 3, hy - 3, hx + 3, hy + 3], fill=JR_GUITAR_HEAD)
    for peg_off in [-2, 0, 2]:
        d.point([hx - 4, hy + peg_off], fill=JR_GUITAR_GOLD)
        d.point([hx + 4, hy + peg_off], fill=JR_GUITAR_GOLD)

    bx = x + int(5 * cos_a)
    by = y + int(5 * sin_a)
    d.line([bx, by, hx, hy], fill=JR_GUITAR_STRING, width=1)


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
        colors = [FLAME_RED, FLAME_ORANGE, FLAME_YELLOW]
        for j in range(flame_h):
            t = j / flame_h
            c = colors[min(int(t * 3), 2)]
            py = base_y - j
            px = fx + random.randint(-1, 1)
            d.point([px, py], fill=c)
        d.point([fx, fy], fill=FLAME_YELLOW)


def jr_sweep_sheet():
    """Guitar swing L to R — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        cx = f * FW + FW // 2
        cy = FH // 2 + 5
        guitar_angle = -60 + f * 24
        lean = int((f - 2.5) * 2)
        pose = {"torso_lean": lean, "head_tilt": lean // 2,
                "l_arm_angle": -40 + f * 8, "r_arm_angle": -20 + f * 15,
                "leg_spread": 6 + abs(f - 3)}
        pts = draw_jr_body(d, cx, cy, pose)
        draw_jr_guitar(d, pts["r_hand"][0], pts["r_hand"][1], guitar_angle)
        if f >= 3:
            for tx in range(pts["r_hand"][0] - 10, pts["r_hand"][0] + 10):
                for ty in range(pts["r_hand"][1] - 5, pts["r_hand"][1] + 5):
                    if 0 <= tx < img.width and 0 <= ty < FH:
                        r0, g0, b0, a0 = img.getpixel((tx, ty))
                        if a0 == 0:
                            img.putpixel((tx, ty), (*MOTION_BLUR, 30 + (f - 3) * 15))
    path = BOSS_DIR / "johnny_rotten_sweep_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def jr_feedback_sheet():
    """Guitar raised, sound rings expanding — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        cx = f * FW + FW // 2
        cy = FH // 2 + 5
        pose = {"torso_lean": -2, "head_tilt": -1,
                "l_arm_angle": -70 - f * 3, "r_arm_angle": -60 - f * 3, "leg_spread": 7}
        draw_jr_body(d, cx, cy, pose)
        gx, gy = cx, cy - 28 - f
        draw_jr_guitar(d, gx, gy, -80 + f * 5)
        if f >= 1:
            draw_sound_rings(d, gx, gy, f, 8 + f * 6)
        if f >= 3:
            for _ in range(f * 2):
                vx = cx + random.randint(-15, 15)
                vy = cy + random.randint(-20, 20)
                if 0 <= vx < img.width and 0 <= vy < FH:
                    r0, g0, b0, a0 = img.getpixel((vx, vy))
                    if a0 > 0:
                        img.putpixel((vx, vy), (min(r0 + 30, 255), min(g0 + 20, 255),
                                                  min(b0 + 50, 255), a0))
    path = BOSS_DIR / "johnny_rotten_feedback_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def jr_pyro_sheet():
    """Flames rising around him — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5
        pose = {"torso_lean": 0, "head_tilt": 0,
                "l_arm_angle": -45 + f * 5, "r_arm_angle": 45 - f * 5, "leg_spread": 8}
        draw_jr_body(d, cx, cy, pose)
        draw_jr_guitar(d, cx + 12, cy + 8, 30)
        flame_intensity = (f + 1) / nf
        flame_height = 15 + f * 8
        for fxo in [-15, -8, 0, 8, 15]:
            draw_flames(d, cx + fxo, cy + 34, flame_height, 3, flame_intensity)
        if f >= 2:
            for hy in range(0, cy - 10):
                for hx in range(x_off + 5, x_off + FW - 5):
                    if 0 <= hx < img.width and 0 <= hy < FH:
                        r0, g0, b0, a0 = img.getpixel((hx, hy))
                        if a0 > 0:
                            warm = min(f * 8, 40)
                            img.putpixel((hx, hy), (min(r0 + warm, 255), g0,
                                                      max(b0 - warm // 2, 0), a0))
    path = BOSS_DIR / "johnny_rotten_pyro_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def jr_chord_sheet():
    """Strum pose, projectile launch — 4 frames."""
    nf = 4
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5
        strum_offset = [0, -2, 2, 0][f]
        pose = {"torso_lean": 2, "head_tilt": 1,
                "l_arm_angle": -20 + strum_offset * 3, "r_arm_angle": 10 + strum_offset * 5,
                "leg_spread": 5}
        draw_jr_body(d, cx, cy, pose)
        gx, gy = cx + 5, cy + 2
        draw_jr_guitar(d, gx, gy, 15 + strum_offset * 3)
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
        if f >= 2:
            proj_dist = (f - 1) * 12
            proj_x = cx + 15 + proj_dist
            proj_y = cy - 5
            if proj_x < x_off + FW:
                pr = 4
                d.ellipse([proj_x - pr, proj_y - pr, proj_x + pr, proj_y + pr],
                          fill=PUNK_GREEN)
                d.ellipse([proj_x - pr - 2, proj_y - pr - 2,
                          proj_x + pr + 2, proj_y + pr + 2],
                          outline=(*SOUND_RING[:3], 120))
    path = BOSS_DIR / "johnny_rotten_chord_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def jr_solo_sheet():
    """Fast strumming, motion blur — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5
        phase = math.sin(f * math.pi * 0.8)
        pose = {"torso_lean": int(phase * 3), "head_tilt": int(phase * 2),
                "l_arm_angle": -25 + int(phase * 10), "r_arm_angle": 15 + int(phase * 15),
                "leg_spread": 6}
        draw_jr_body(d, cx, cy, pose)
        gx = cx + 4 + int(phase * 2)
        gy = cy + 1
        draw_jr_guitar(d, gx, gy, 12 + int(phase * 8))
        for _ in range(8 + f * 2):
            bx = gx + random.randint(-8, 8)
            by = gy + random.randint(-5, 5)
            if 0 <= bx < img.width and 0 <= by < FH:
                r0, g0, b0, a0 = img.getpixel((bx, by))
                if a0 == 0:
                    img.putpixel((bx, by), (*MOTION_BLUR, 40 + random.randint(0, 40)))
                else:
                    img.putpixel((bx, by), (min(r0 + 20, 255), min(g0 + 10, 255),
                                              min(b0 + 30, 255), a0))
        for _ in range(4):
            angle = random.uniform(-0.5, 0.5) + math.pi * (0.5 if phase > 0 else -0.5)
            line_len = random.randint(8, 18)
            sx = gx + int(6 * math.cos(angle))
            sy = gy + int(3 * math.sin(angle))
            ex = sx + int(line_len * math.cos(angle))
            ey = sy + int(line_len * math.sin(angle))
            d.line([sx, sy, ex, ey], fill=(*SOUND_RING[:3], 100), width=1)
        if f >= 2:
            for _ in range(f):
                sx = cx + random.randint(-18, 18)
                sy = cy + random.randint(-25, 15)
                if x_off <= sx < x_off + FW and 0 <= sy < FH:
                    d.point([sx, sy], fill=PUNK_GREEN)
    path = BOSS_DIR / "johnny_rotten_solo_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


# ══════════════════════════════════════════════════════════════════════════════
#  SID VICIOUS — Punk bassist, physical attacks
# ══════════════════════════════════════════════════════════════════════════════

# Sid Vicious palette
SV_SKIN = (195, 165, 145)
SV_SKIN_SHADOW = (160, 130, 110)
SV_HAIR = (15, 12, 10)         # Black spiky hair
SV_HAIR_TIP = (35, 28, 22)
SV_CHEST = (195, 165, 145)     # Shirtless
SV_VEST = (25, 20, 18)         # Black leather vest (open)
SV_VEST_LIGHT = (45, 38, 32)
SV_PANTS = (25, 22, 28)        # Black leather pants
SV_PANTS_LIGHT = (40, 35, 45)
SV_BOOTS = (30, 25, 20)
SV_CHAIN = (190, 195, 205)     # Padlock necklace chain
SV_PADLOCK = (200, 200, 210)
SV_OUTLINE = (15, 10, 12)

# P-Bass palette
SV_BASS_BODY = (180, 160, 130)     # Natural wood Fender P-Bass
SV_BASS_BODY_LIGHT = (210, 190, 155)
SV_BASS_BODY_DARK = (130, 115, 90)
SV_BASS_NECK = (150, 110, 65)
SV_BASS_NECK_DARK = (115, 80, 45)
SV_BASS_HEAD = (30, 25, 20)
SV_BASS_STRING = (200, 200, 210)
SV_BASS_PICKUP = (55, 50, 45)


def remap_sid_vicious(r, g, b, a):
    """Disco King → Sid Vicious: shirtless, leather vest, chains, spiky black hair."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 160:
        # Very light (disco suit) → exposed skin
        return (min(int(brightness * 0.8), 195), min(int(brightness * 0.65), 165),
                min(int(brightness * 0.55), 145), a)
    elif is_gray and brightness > 120:
        # Light body → leather vest dark
        return (max(int(r * 0.2), 22), max(int(g * 0.18), 18), max(int(b * 0.18), 16), a)
    elif is_gray and brightness > 80:
        # Mid body → vest/leather
        return (max(int(r * 0.25), 25), max(int(g * 0.22), 20), max(int(b * 0.25), 22), a)
    elif brightness > 120 and r > b:
        # Warm tones → pale punk skin
        return (min(int(r * 0.9), 195), min(int(g * 0.75), 160), min(int(b * 0.7), 140), a)
    elif brightness > 80 and b > r:
        # Cool tones → darker leather
        return (max(int(r * 0.25), 20), max(int(g * 0.2), 15), max(int(b * 0.3), 25), a)
    elif brightness > 60:
        # Mid → skin shadow
        return (min(int(r * 0.75), 160), min(int(g * 0.6), 130), min(int(b * 0.5), 110), a)
    elif brightness > 30:
        # Dark → very dark
        return (max(int(r * 0.3), 15), max(int(g * 0.25), 12), max(int(b * 0.25), 10), a)
    else:
        return (min(r + 2, 20), min(g + 2, 15), min(b + 2, 12), a)


def draw_sv_body(d, cx, cy, pose_data=None):
    """Draw Sid Vicious's body. Shirtless w/ open leather vest, chain necklace."""
    p = pose_data or {}
    head_tilt = p.get("head_tilt", 0)
    torso_lean = p.get("torso_lean", 0)
    l_arm_angle = p.get("l_arm_angle", -30)
    r_arm_angle = p.get("r_arm_angle", 30)

    hip_y = cy + 14
    foot_y = cy + 34
    leg_spread = p.get("leg_spread", 5)

    # Legs (black leather)
    ll_x = cx - leg_spread + torso_lean
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=SV_PANTS, width=4)
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=SV_PANTS_LIGHT, width=2)
    d.rectangle([ll_x - 3, foot_y - 2, ll_x + 3, foot_y + 2], fill=SV_BOOTS)

    rl_x = cx + leg_spread + torso_lean
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=SV_PANTS, width=4)
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=SV_PANTS_LIGHT, width=2)
    d.rectangle([rl_x - 3, foot_y - 2, rl_x + 3, foot_y + 2], fill=SV_BOOTS)

    # Torso (shirtless w/ open vest)
    torso_top = cy - 8
    torso_cx = cx + torso_lean
    # Skin torso
    d.rectangle([torso_cx - 8, torso_top, torso_cx + 8, hip_y], fill=SV_CHEST)
    d.rectangle([torso_cx - 4, torso_top + 2, torso_cx + 4, torso_top + 8],
                fill=SV_SKIN_SHADOW)  # Abs hint
    # Vest sides
    d.rectangle([torso_cx - 10, torso_top, torso_cx - 7, hip_y], fill=SV_VEST)
    d.rectangle([torso_cx + 7, torso_top, torso_cx + 10, hip_y], fill=SV_VEST)
    # Vest collar
    d.line([torso_cx - 10, torso_top, torso_cx - 7, torso_top + 5], fill=SV_VEST_LIGHT)
    d.line([torso_cx + 10, torso_top, torso_cx + 7, torso_top + 5], fill=SV_VEST_LIGHT)

    # Chain necklace with padlock
    chain_y = torso_top + 1
    for chain_x in range(torso_cx - 5, torso_cx + 6):
        sag = int(abs(chain_x - torso_cx) * 0.3)
        d.point([chain_x, chain_y + sag], fill=SV_CHAIN)
    # Padlock at center
    d.rectangle([torso_cx - 1, chain_y + 1, torso_cx + 1, chain_y + 4], fill=SV_PADLOCK)

    # Arms (bare skin + vest straps)
    arm_len = 18
    shoulder_y = torso_top + 3

    la_rad = math.radians(l_arm_angle)
    la_ex = torso_cx - 10 + int(arm_len * math.sin(la_rad))
    la_ey = shoulder_y + int(arm_len * math.cos(la_rad))
    d.line([torso_cx - 10, shoulder_y, la_ex, la_ey], fill=SV_SKIN, width=4)
    d.ellipse([la_ex - 2, la_ey - 2, la_ex + 2, la_ey + 2], fill=SV_SKIN)

    ra_rad = math.radians(r_arm_angle)
    ra_ex = torso_cx + 10 + int(arm_len * math.sin(ra_rad))
    ra_ey = shoulder_y + int(arm_len * math.cos(ra_rad))
    d.line([torso_cx + 10, shoulder_y, ra_ex, ra_ey], fill=SV_SKIN, width=4)
    d.ellipse([ra_ex - 2, ra_ey - 2, ra_ex + 2, ra_ey + 2], fill=SV_SKIN)

    # Head
    head_cx = torso_cx + head_tilt
    head_cy = torso_top - 10
    head_w, head_h = 9, 12
    d.ellipse([head_cx - head_w // 2, head_cy - head_h // 2,
               head_cx + head_w // 2, head_cy + head_h // 2],
              fill=SV_SKIN, outline=SV_OUTLINE)
    # Angry eyes
    d.line([head_cx - 3, head_cy - 2, head_cx - 1, head_cy - 1], fill=SV_OUTLINE)
    d.line([head_cx + 1, head_cy - 1, head_cx + 3, head_cy - 2], fill=SV_OUTLINE)
    # Snarl
    d.line([head_cx - 2, head_cy + 2, head_cx, head_cy + 3], fill=SV_OUTLINE)
    d.line([head_cx, head_cy + 3, head_cx + 2, head_cy + 2], fill=SV_OUTLINE)

    # Spiky black hair (shorter, more vertical than JR)
    for spike_x in range(-3, 4, 2):
        spike_h = random.randint(5, 10)
        base_x = head_cx + spike_x
        for j in range(spike_h):
            t = j / spike_h
            hy = head_cy - head_h // 2 - j
            if 0 <= hy < FH:
                c = SV_HAIR if t < 0.6 else SV_HAIR_TIP
                d.point([base_x, hy], fill=c)

    return {
        "l_hand": (la_ex, la_ey),
        "r_hand": (ra_ex, ra_ey),
        "torso_cx": torso_cx,
        "shoulder_y": shoulder_y,
    }


def draw_sv_bass(d, x, y, angle_deg=0):
    """Draw Sid's Fender P-Bass."""
    body_w, body_h = 12, 9
    neck_len = 20
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    for dy in range(-body_h // 2, body_h // 2 + 1):
        for dx in range(-body_w // 2, body_w // 2 + 1):
            if (dx / (body_w / 2.0)) ** 2 + (dy / (body_h / 2.0)) ** 2 <= 1:
                rx = x + int(dx * cos_a - dy * sin_a)
                ry = y + int(dx * sin_a + dy * cos_a)
                dist = math.sqrt(dx * dx + dy * dy)
                max_r = math.sqrt((body_w / 2) ** 2 + (body_h / 2) ** 2)
                t = dist / max_r
                if t < 0.4:
                    c = SV_BASS_BODY_LIGHT
                elif t < 0.7:
                    c = SV_BASS_BODY
                else:
                    c = SV_BASS_BODY_DARK
                d.point([rx, ry], fill=c)

    d.rectangle([x - 2, y - 1, x + 2, y + 1], fill=SV_BASS_PICKUP)
    for i in range(neck_len):
        nx = x + int((-body_w // 2 - i) * cos_a)
        ny = y + int((-body_w // 2 - i) * sin_a)
        d.rectangle([nx - 1, ny - 1, nx + 1, ny + 1], fill=SV_BASS_NECK)
        if i % 6 == 0:
            d.point([nx, ny], fill=SV_BASS_NECK_DARK)

    hx = x + int((-body_w // 2 - neck_len) * cos_a)
    hy = y + int((-body_w // 2 - neck_len) * sin_a)
    d.rectangle([hx - 3, hy - 3, hx + 3, hy + 3], fill=SV_BASS_HEAD)
    bx = x + int(4 * cos_a)
    by = y + int(4 * sin_a)
    d.line([bx, by, hx, hy], fill=SV_BASS_STRING, width=1)


def draw_chain(d, x1, y1, x2, y2, segments=8):
    """Draw a chain between two points with sagging links."""
    for i in range(segments + 1):
        t = i / segments
        mx = int(x1 + (x2 - x1) * t)
        sag = int(10 * math.sin(t * math.pi))
        my = int(y1 + (y2 - y1) * t) + sag
        c = CHAIN_SILVER if i % 2 == 0 else CHAIN_DARK
        d.rectangle([mx - 1, my - 1, mx + 1, my + 1], fill=c)


def sv_bass_swing_sheet():
    """Bass guitar swing L to R — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        cx = f * FW + FW // 2
        cy = FH // 2 + 5
        bass_angle = -70 + f * 28
        lean = int((f - 2.5) * 3)
        pose = {"torso_lean": lean, "head_tilt": lean // 2,
                "l_arm_angle": -50 + f * 10, "r_arm_angle": -30 + f * 18,
                "leg_spread": 7 + abs(f - 3)}
        pts = draw_sv_body(d, cx, cy, pose)
        draw_sv_bass(d, pts["r_hand"][0], pts["r_hand"][1], bass_angle)
        if f >= 3:
            for tx in range(pts["r_hand"][0] - 12, pts["r_hand"][0] + 12):
                for ty in range(pts["r_hand"][1] - 6, pts["r_hand"][1] + 6):
                    if 0 <= tx < img.width and 0 <= ty < FH:
                        r0, g0, b0, a0 = img.getpixel((tx, ty))
                        if a0 == 0:
                            img.putpixel((tx, ty), (*MOTION_BLUR, 25 + (f - 3) * 20))
    path = BOSS_DIR / "sid_vicious_bass_swing_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def sv_chain_whip_sheet():
    """Chain whip attack — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        cx = f * FW + FW // 2
        cy = FH // 2 + 5
        # Windup then throw
        arm_angle = [-60, -80, -40, 20, 50, 40][f]
        pose = {"torso_lean": [-2, -3, 0, 3, 4, 2][f],
                "head_tilt": [0, -1, 0, 2, 2, 1][f],
                "l_arm_angle": arm_angle,
                "r_arm_angle": [20, 15, 10, -10, -20, -10][f],
                "leg_spread": 6}
        pts = draw_sv_body(d, cx, cy, pose)
        # Chain extends from left hand
        lh = pts["l_hand"]
        chain_ext = [3, 5, 12, 20, 22, 18][f]
        chain_end_x = lh[0] - chain_ext
        chain_end_y = lh[1] + chain_ext // 2
        draw_chain(d, lh[0], lh[1], chain_end_x, chain_end_y, 6 + f)
        # Chain tip flash on frames 3-4
        if 3 <= f <= 4:
            d.ellipse([chain_end_x - 3, chain_end_y - 3,
                      chain_end_x + 3, chain_end_y + 3],
                      fill=(255, 255, 255, 150))
        # Bass slung on back
        draw_sv_bass(d, cx + 8, cy + 5, 80)
    path = BOSS_DIR / "sid_vicious_chain_whip_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def sv_punk_spit_sheet():
    """Punk spit projectile — 4 frames."""
    nf = 4
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5
        pose = {"torso_lean": [0, 2, 3, 1][f], "head_tilt": [0, 3, 4, 2][f],
                "l_arm_angle": -20, "r_arm_angle": 15, "leg_spread": 5}
        draw_sv_body(d, cx, cy, pose)
        draw_sv_bass(d, cx + 8, cy + 5, 25)
        # Spit projectile
        if f >= 1:
            spit_dist = f * 8
            spit_x = cx + 8 + spit_dist
            spit_y = cy - 18
            if spit_x < x_off + FW:
                d.ellipse([spit_x - 2, spit_y - 2, spit_x + 2, spit_y + 2],
                          fill=SPIT_GREEN)
                # Trail
                if f >= 2:
                    d.line([spit_x - 4, spit_y, spit_x - 1, spit_y],
                           fill=(*SPIT_GREEN, 120))
    path = BOSS_DIR / "sid_vicious_punk_spit_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def sv_stage_dive_sheet():
    """Stage dive charge — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        cx = f * FW + FW // 2
        cy = FH // 2 + 5
        # Crouch → leap → airborne → impact
        crouch = [0, -3, -6, -4, -1, 2][f]
        lean = [0, 3, 8, 10, 8, 4][f]
        pose = {"torso_lean": lean, "head_tilt": lean // 2,
                "l_arm_angle": [-20, -40, -60, -50, -30, -20][f],
                "r_arm_angle": [20, 40, 60, 50, 30, 20][f],
                "leg_spread": [5, 3, 8, 10, 8, 5][f]}
        draw_sv_body(d, cx, cy + crouch, pose)
        draw_sv_bass(d, cx + 8, cy + crouch + 5, 25 + lean * 2)
        # Impact shockwave on frame 5
        if f == 5:
            for ring_r in range(5, 20, 4):
                d.ellipse([cx - ring_r, cy + 30 - ring_r // 3,
                          cx + ring_r, cy + 30 + ring_r // 3],
                          outline=(255, 255, 200, 100))
        # Speed lines during dive (frames 2-4)
        if 2 <= f <= 4:
            for _ in range(3):
                sx = cx - 15 + random.randint(-5, 5)
                sy = cy + crouch + random.randint(-10, 10)
                d.line([sx, sy, sx - random.randint(5, 15), sy],
                       fill=(*MOTION_BLUR, 80), width=1)
    path = BOSS_DIR / "sid_vicious_stage_dive_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def sv_berserker_sheet():
    """Berserker rage — rapid alternating swings — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5
        phase = math.sin(f * math.pi * 0.7)
        pose = {"torso_lean": int(phase * 4), "head_tilt": int(phase * 3),
                "l_arm_angle": -40 + int(phase * 25),
                "r_arm_angle": 40 - int(phase * 25),
                "leg_spread": 8}
        pts = draw_sv_body(d, cx, cy, pose)
        # Bass swinging wildly
        bass_angle = int(phase * 50)
        draw_sv_bass(d, pts["r_hand"][0], pts["r_hand"][1], bass_angle)
        # Rage aura (red glow)
        for _ in range(6 + f * 2):
            rx = cx + random.randint(-16, 16)
            ry = cy + random.randint(-25, 25)
            if x_off <= rx < x_off + FW and 0 <= ry < FH:
                r0, g0, b0, a0 = img.getpixel((rx, ry))
                if a0 > 0:
                    img.putpixel((rx, ry), (min(r0 + 40, 255), max(g0 - 10, 0),
                                              max(b0 - 10, 0), a0))
                else:
                    img.putpixel((rx, ry), (180, 30, 30, 30 + random.randint(0, 30)))
        # Motion blur streaks
        for _ in range(3):
            sx = cx + random.randint(-12, 12)
            sy = cy + random.randint(-15, 15)
            d.line([sx, sy, sx + int(phase * 8), sy], fill=(*MOTION_BLUR, 60), width=1)
    path = BOSS_DIR / "sid_vicious_berserker_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


# ══════════════════════════════════════════════════════════════════════════════
#  Palette-swap helpers
# ══════════════════════════════════════════════════════════════════════════════

def swap_boss_sheets(remap_fn, prefix):
    """Palette-swap Disco King sheets to a new boss."""
    mappings = [
        ("disco_king_idle_sheet.png", f"{prefix}_idle_sheet.png"),
        ("disco_king_hurt_sheet.png", f"{prefix}_hurt_sheet.png"),
        ("disco_king_death_sheet.png", f"{prefix}_death_sheet.png"),
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
                px[y, x] = remap_fn(int(r), int(g), int(b), int(a))

        dst_path = BOSS_DIR / dst_name
        Image.fromarray(px.astype(np.uint8), "RGBA").save(dst_path)
        print(f"  [OK] {dst_name}")


# ══════════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("Generating Sex Pistols Concert boss sprites...")

    # ── Johnny Rotten ──
    print("\nJohnny Rotten — palette-swap (from Disco King):")
    swap_boss_sheets(remap_johnny_rotten, "johnny_rotten")

    print("\nJohnny Rotten — from-scratch attacks:")
    jr_sweep_sheet()
    jr_feedback_sheet()
    jr_pyro_sheet()
    jr_chord_sheet()
    jr_solo_sheet()

    # ── Sid Vicious ──
    print("\nSid Vicious — palette-swap (from Disco King):")
    swap_boss_sheets(remap_sid_vicious, "sid_vicious")

    print("\nSid Vicious — from-scratch attacks:")
    sv_bass_swing_sheet()
    sv_chain_whip_sheet()
    sv_punk_spit_sheet()
    sv_stage_dive_sheet()
    sv_berserker_sheet()

    print("\nDone! 16 Sex Pistols boss sprites generated (8 each).")


if __name__ == "__main__":
    main()
