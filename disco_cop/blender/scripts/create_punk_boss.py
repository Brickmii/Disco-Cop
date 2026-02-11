#!/usr/bin/env python3
"""Generate Joey Ramone boss sprites for Disco Cop Level 04 (CBGB Punk Alley).

Joey Ramone (48x80/frame):
  Palette-swap from Disco King:
    - joey_ramone_idle_sheet  (192x80, 4f)
    - joey_ramone_hurt_sheet  (96x80, 2f)
    - joey_ramone_death_sheet (384x80, 8f)
  From-scratch attack sheets:
    - joey_ramone_mic_swing_sheet       (288x80, 6f)
    - joey_ramone_feedback_shriek_sheet (288x80, 6f)
    - joey_ramone_crowd_surf_sheet      (288x80, 6f)
    - joey_ramone_wall_of_sound_sheet   (288x80, 6f)
    - joey_ramone_blitzkrieg_bop_sheet  (288x80, 6f)

Usage:
    python create_punk_boss.py
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
BOSS_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "bosses"

random.seed(811)

FW, FH = 48, 80

# ── Effect colors (shared) ───────────────────────────────────────────────────

SOUND_RING = (180, 160, 255)
MOTION_BLUR = (100, 60, 160)
RAGE_RED = (200, 30, 30)
SPEED_LINE = (160, 150, 180)
ENERGY_SPARK = (255, 240, 100)
WAVE_LINE = (140, 120, 220)

# ── Joey Ramone palette ──────────────────────────────────────────────────────

JR_SKIN = (210, 190, 175)           # Pale skin
JR_SKIN_SHADOW = (175, 155, 140)
JR_HAIR = (10, 8, 8)                # Jet black straight hair
JR_HAIR_HIGHLIGHT = (30, 28, 30)
JR_JACKET = (20, 18, 16)            # Black leather jacket
JR_JACKET_LIGHT = (40, 36, 32)      # Jacket highlights
JR_SHIRT = (30, 25, 25)             # Dark Ramones t-shirt
JR_SHIRT_LOGO = (180, 170, 160)     # Faded logo print
JR_JEANS = (25, 30, 50)             # Dark blue ripped jeans
JR_JEANS_LIGHT = (40, 48, 70)
JR_JEANS_RIP = (60, 65, 85)         # Exposed thread at rip
JR_SNEAKERS = (35, 32, 30)          # Worn sneakers
JR_SUNGLASSES = (12, 10, 10)        # Round sunglasses
JR_SUNGLASSES_GLINT = (180, 190, 210)  # Chrome/silver glint
JR_OUTLINE = (8, 6, 6)

# ── Mic stand palette ────────────────────────────────────────────────────────

MIC_CHROME = (190, 195, 205)        # Chrome pole
MIC_CHROME_LIGHT = (220, 225, 235)
MIC_CHROME_DARK = (130, 135, 145)
MIC_HEAD = (60, 58, 55)             # Mic head (dark mesh)
MIC_HEAD_RING = (170, 175, 185)     # Ring around mic head


def remap_joey_ramone(r, g, b, a):
    """Disco King -> Joey Ramone: black leather, dark denim, pale skin."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 160:
        # Very light (disco suit highlights) -> black leather with chrome hints
        return (max(int(r * 0.15), 18), max(int(g * 0.15), 16), max(int(b * 0.15), 14), a)
    elif is_gray and brightness > 120:
        # Light body -> dark denim blue
        return (max(int(r * 0.2), 22), max(int(g * 0.25), 28), max(int(b * 0.4), 48), a)
    elif is_gray and brightness > 80:
        # Mid body -> black leather jacket
        return (max(int(r * 0.18), 18), max(int(g * 0.16), 15), max(int(b * 0.16), 14), a)
    elif brightness > 120 and r > b:
        # Warm tones (gold/skin) -> pale skin
        return (min(int(r * 0.95), 210), min(int(g * 0.85), 190), min(int(b * 0.8), 175), a)
    elif brightness > 80 and b > r:
        # Cool tones -> darker black
        return (max(int(r * 0.12), 10), max(int(g * 0.1), 8), max(int(b * 0.12), 10), a)
    elif brightness > 60:
        # Mid tones -> dark jacket/jeans mix
        return (max(int(r * 0.2), 20), max(int(g * 0.22), 22), max(int(b * 0.3), 35), a)
    elif brightness > 30:
        # Dark -> very dark with slight chrome/silver hint
        return (max(int(r * 0.25), 12), max(int(g * 0.25), 12), max(int(b * 0.28), 15), a)
    else:
        return (min(r + 2, 15), min(g + 2, 12), min(b + 2, 12), a)


def draw_joey_body(d, cx, cy, pose_data=None):
    """Draw Joey Ramone's body. Returns key points for mic stand attachment."""
    p = pose_data or {}
    head_tilt = p.get("head_tilt", 0)
    torso_lean = p.get("torso_lean", 0)
    l_arm_angle = p.get("l_arm_angle", -30)
    r_arm_angle = p.get("r_arm_angle", 30)

    hip_y = cy + 14
    foot_y = cy + 34
    leg_spread = p.get("leg_spread", 5)

    # Legs (ripped dark blue jeans)
    ll_x = cx - leg_spread + torso_lean
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=JR_JEANS, width=4)
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=JR_JEANS_LIGHT, width=2)
    # Rip on left knee
    rip_y = hip_y + (foot_y - hip_y) // 2
    d.point([ll_x, rip_y], fill=JR_JEANS_RIP)
    d.point([ll_x - 1, rip_y + 1], fill=JR_JEANS_RIP)
    d.rectangle([ll_x - 3, foot_y - 2, ll_x + 3, foot_y + 2], fill=JR_SNEAKERS)

    rl_x = cx + leg_spread + torso_lean
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=JR_JEANS, width=4)
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=JR_JEANS_LIGHT, width=2)
    # Rip on right knee
    rip_y2 = hip_y + (foot_y - hip_y) * 2 // 3
    d.point([rl_x + 1, rip_y2], fill=JR_JEANS_RIP)
    d.point([rl_x, rip_y2 + 1], fill=JR_JEANS_RIP)
    d.rectangle([rl_x - 3, foot_y - 2, rl_x + 3, foot_y + 2], fill=JR_SNEAKERS)

    # Torso (leather jacket over Ramones tee)
    torso_top = cy - 8
    torso_cx = cx + torso_lean
    # Jacket body
    d.rectangle([torso_cx - 10, torso_top, torso_cx + 10, hip_y], fill=JR_JACKET)
    # Ramones t-shirt visible underneath (open jacket center)
    d.rectangle([torso_cx - 5, torso_top + 2, torso_cx + 5, torso_top + 12], fill=JR_SHIRT)
    # Faded logo on shirt (tiny horizontal lines)
    d.line([torso_cx - 3, torso_top + 5, torso_cx + 3, torso_top + 5], fill=JR_SHIRT_LOGO)
    d.line([torso_cx - 2, torso_top + 7, torso_cx + 2, torso_top + 7], fill=JR_SHIRT_LOGO)
    # Jacket lapels
    d.line([torso_cx - 10, torso_top, torso_cx - 5, torso_top + 8],
           fill=JR_JACKET_LIGHT, width=1)
    d.line([torso_cx + 10, torso_top, torso_cx + 5, torso_top + 8],
           fill=JR_JACKET_LIGHT, width=1)
    # Jacket collar
    d.line([torso_cx - 10, torso_top, torso_cx - 8, torso_top - 2], fill=JR_JACKET_LIGHT)
    d.line([torso_cx + 10, torso_top, torso_cx + 8, torso_top - 2], fill=JR_JACKET_LIGHT)

    # Arms (jacket sleeves)
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
    # Round sunglasses (two small circles)
    d.ellipse([head_cx - 4, head_cy - 2, head_cx - 1, head_cy + 1], fill=JR_SUNGLASSES)
    d.ellipse([head_cx + 1, head_cy - 2, head_cx + 4, head_cy + 1], fill=JR_SUNGLASSES)
    # Chrome glint on sunglasses
    d.point([head_cx - 3, head_cy - 1], fill=JR_SUNGLASSES_GLINT)
    d.point([head_cx + 2, head_cy - 1], fill=JR_SUNGLASSES_GLINT)
    # Mouth (neutral/open depends on pose)
    mouth_open = p.get("mouth_open", False)
    if mouth_open:
        d.rectangle([head_cx - 2, head_cy + 3, head_cx + 2, head_cy + 5], fill=JR_OUTLINE)
    else:
        d.line([head_cx - 2, head_cy + 3, head_cx + 2, head_cy + 3], fill=JR_OUTLINE)

    # Long straight black hair (hanging down past shoulders, not spiky)
    hair_top = head_cy - head_h // 2
    for hair_x in range(-5, 6):
        base_x = head_cx + hair_x
        # Hair starts at top of head and hangs straight down
        hair_len = random.randint(18, 26)
        # Outer strands are longer
        if abs(hair_x) >= 4:
            hair_len += random.randint(3, 6)
        for j in range(hair_len):
            hy = hair_top + j
            # Slight sway for natural look
            sway = int(math.sin(j * 0.3 + hair_x * 0.5) * 0.5)
            hx = base_x + sway
            if 0 <= hy < FH:
                c = JR_HAIR if j < hair_len * 0.7 else JR_HAIR_HIGHLIGHT
                d.point([hx, hy], fill=c)

    return {
        "l_hand": (la_ex, la_ey),
        "r_hand": (ra_ex, ra_ey),
        "torso_cx": torso_cx,
        "shoulder_y": shoulder_y,
    }


def draw_mic_stand(d, x, y, angle_deg=0):
    """Draw Joey Ramone's mic stand weapon (chrome pole with mic head)."""
    pole_len = 22
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    # Chrome pole
    for i in range(pole_len):
        px = x + int(i * sin_a)
        py = y - int(i * cos_a)
        # Shading along pole length
        if i % 4 < 2:
            c = MIC_CHROME
        else:
            c = MIC_CHROME_LIGHT
        d.rectangle([px - 1, py, px + 1, py], fill=c)
        # Dark edge
        d.point([px - 1, py], fill=MIC_CHROME_DARK)

    # Mic head at top
    mic_x = x + int(pole_len * sin_a)
    mic_y = y - int(pole_len * cos_a)
    # Ring
    d.ellipse([mic_x - 3, mic_y - 3, mic_x + 3, mic_y + 3], fill=MIC_HEAD,
              outline=MIC_HEAD_RING)
    # Mesh dots on mic head
    d.point([mic_x - 1, mic_y - 1], fill=MIC_CHROME_DARK)
    d.point([mic_x + 1, mic_y], fill=MIC_CHROME_DARK)
    d.point([mic_x, mic_y + 1], fill=MIC_CHROME_DARK)

    return (mic_x, mic_y)


def draw_sound_rings(d, cx, cy, num_rings, max_radius, alpha_base=180):
    """Draw expanding sound wave rings."""
    for i in range(num_rings):
        t = (i + 1) / num_rings
        r = int(max_radius * t)
        alpha = max(20, int(alpha_base * (1 - t)))
        color = (*SOUND_RING[:3], alpha)
        d.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], outline=color, width=1)


def draw_speed_lines(d, cx, cy, count, direction, length_range=(8, 18)):
    """Draw speed lines for motion effects."""
    for _ in range(count):
        sx = cx + random.randint(-12, 12)
        sy = cy + random.randint(-15, 15)
        line_len = random.randint(length_range[0], length_range[1])
        ex = sx + int(line_len * direction)
        d.line([sx, sy, ex, sy], fill=(*SPEED_LINE, 80), width=1)


def draw_rage_aura(img, cx, cy, x_off, intensity):
    """Draw red rage aura around character."""
    for _ in range(int(6 * intensity)):
        rx = cx + random.randint(-16, 16)
        ry = cy + random.randint(-25, 25)
        if x_off <= rx < x_off + FW and 0 <= ry < FH:
            r0, g0, b0, a0 = img.getpixel((rx, ry))
            if a0 > 0:
                img.putpixel((rx, ry), (min(r0 + 40, 255), max(g0 - 10, 0),
                                          max(b0 - 10, 0), a0))
            else:
                img.putpixel((rx, ry), (180, 30, 30, 30 + random.randint(0, 30)))


# ══════════════════════════════════════════════════════════════════════════════
#  Attack sheets — from scratch
# ══════════════════════════════════════════════════════════════════════════════

def jr_mic_swing_sheet():
    """Swings mic stand L to R like a weapon — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        cx = f * FW + FW // 2
        cy = FH // 2 + 5
        mic_angle = -60 + f * 24
        lean = int((f - 2.5) * 3)
        pose = {"torso_lean": lean, "head_tilt": lean // 2,
                "l_arm_angle": -50 + f * 10, "r_arm_angle": -30 + f * 18,
                "leg_spread": 7 + abs(f - 3)}
        pts = draw_joey_body(d, cx, cy, pose)
        draw_mic_stand(d, pts["r_hand"][0], pts["r_hand"][1], mic_angle)
        # Motion blur on later frames
        if f >= 3:
            for tx in range(pts["r_hand"][0] - 12, pts["r_hand"][0] + 12):
                for ty in range(pts["r_hand"][1] - 6, pts["r_hand"][1] + 6):
                    if 0 <= tx < img.width and 0 <= ty < FH:
                        r0, g0, b0, a0 = img.getpixel((tx, ty))
                        if a0 == 0:
                            img.putpixel((tx, ty), (*MOTION_BLUR, 25 + (f - 3) * 20))
    path = BOSS_DIR / "joey_ramone_mic_swing_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def jr_feedback_shriek_sheet():
    """Leans into mic, mouth open wide, sound rings expand — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        cx = f * FW + FW // 2
        cy = FH // 2 + 5
        pose = {"torso_lean": 3 + f, "head_tilt": 2 + f // 2,
                "l_arm_angle": -20, "r_arm_angle": -40 - f * 3,
                "leg_spread": 6, "mouth_open": True}
        pts = draw_joey_body(d, cx, cy, pose)
        # Mic stand held in front at mouth level
        mic_x = pts["r_hand"][0]
        mic_y = pts["r_hand"][1]
        mic_top = draw_mic_stand(d, mic_x, mic_y, -70 + f * 5)
        # Sound rings expanding outward from mic head
        if f >= 1:
            ring_cx = mic_top[0] + 5
            ring_cy = mic_top[1]
            num_rings = f + 1
            max_r = 6 + f * 7
            draw_sound_rings(d, ring_cx, ring_cy, num_rings, max_r)
        # Vibration on body (pixel shimmer) at higher intensity
        if f >= 3:
            for _ in range(f * 3):
                vx = cx + random.randint(-15, 15)
                vy = cy + random.randint(-20, 20)
                if 0 <= vx < img.width and 0 <= vy < FH:
                    r0, g0, b0, a0 = img.getpixel((vx, vy))
                    if a0 > 0:
                        img.putpixel((vx, vy), (min(r0 + 25, 255), min(g0 + 15, 255),
                                                  min(b0 + 45, 255), a0))
    path = BOSS_DIR / "joey_ramone_feedback_shriek_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def jr_crowd_surf_sheet():
    """Charges forward: crouch -> leap -> airborne -> landing — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        cx = f * FW + FW // 2
        cy = FH // 2 + 5
        # Crouch -> leap -> airborne -> landing
        crouch = [0, -4, -8, -6, -2, 3][f]
        lean = [0, 2, 6, 10, 8, 3][f]
        pose = {"torso_lean": lean, "head_tilt": lean // 2,
                "l_arm_angle": [-20, -40, -60, -70, -50, -25][f],
                "r_arm_angle": [20, 40, 60, 70, 50, 25][f],
                "leg_spread": [5, 3, 10, 12, 8, 5][f]}
        draw_joey_body(d, cx, cy + crouch, pose)
        # Mic held forward during jump
        mic_lean = [0, 10, 30, 40, 20, 5][f]
        draw_mic_stand(d, cx + lean + 5, cy + crouch + 5, mic_lean)
        # Speed lines during airborne frames (2-4)
        if 2 <= f <= 4:
            draw_speed_lines(d, cx, cy + crouch, 4, -1)
        # Impact shockwave on landing (frame 5)
        if f == 5:
            for ring_r in range(5, 20, 4):
                d.ellipse([cx - ring_r, cy + 30 - ring_r // 3,
                          cx + ring_r, cy + 30 + ring_r // 3],
                          outline=(255, 255, 200, 100))
    path = BOSS_DIR / "joey_ramone_crowd_surf_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def jr_wall_of_sound_sheet():
    """Power stance, horizontal sound wave lines emanating forward — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5
        # Power stance — arms spread, stable legs
        pose = {"torso_lean": 0, "head_tilt": 0,
                "l_arm_angle": -50 - f * 3, "r_arm_angle": 50 + f * 3,
                "leg_spread": 8}
        draw_joey_body(d, cx, cy, pose)
        # Mic stand planted center
        draw_mic_stand(d, cx, cy + 10, 0)
        # Horizontal sound wave lines emanating forward (increasing density)
        num_waves = 2 + f * 2
        for w in range(num_waves):
            wave_dist = 8 + w * 4
            wave_x = cx + wave_dist
            if wave_x < x_off + FW:
                wave_top = cy - 15 - f * 2
                wave_bot = cy + 15 + f * 2
                alpha = max(30, 160 - w * 20)
                d.line([wave_x, wave_top, wave_x, wave_bot],
                       fill=(*WAVE_LINE, alpha), width=1)
                # Slight wave distortion
                if w % 2 == 0:
                    d.point([wave_x + 1, wave_top + (wave_bot - wave_top) // 3],
                            fill=(*WAVE_LINE, alpha))
                    d.point([wave_x - 1, wave_top + 2 * (wave_bot - wave_top) // 3],
                            fill=(*WAVE_LINE, alpha))
        # Glow around body at higher frames
        if f >= 3:
            for _ in range(f * 2):
                gx = cx + random.randint(-12, 12)
                gy = cy + random.randint(-20, 15)
                if x_off <= gx < x_off + FW and 0 <= gy < FH:
                    r0, g0, b0, a0 = img.getpixel((gx, gy))
                    if a0 > 0:
                        img.putpixel((gx, gy), (min(r0 + 15, 255), min(g0 + 10, 255),
                                                  min(b0 + 35, 255), a0))
    path = BOSS_DIR / "joey_ramone_wall_of_sound_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def jr_blitzkrieg_bop_sheet():
    """Frantic bouncing, mic forward, energy sparks, rage aura — 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5
        # Frantic bouncing — rapid alternating leg positions
        phase = math.sin(f * math.pi * 0.8)
        bounce = int(phase * 4)
        pose = {"torso_lean": int(phase * 4), "head_tilt": int(phase * 3),
                "l_arm_angle": -30 + int(phase * 20),
                "r_arm_angle": 30 - int(phase * 20),
                "leg_spread": 6 + int(abs(phase) * 4)}
        draw_joey_body(d, cx, cy + bounce, pose)
        # Mic held forward aggressively
        mic_tilt = 20 + int(phase * 15)
        draw_mic_stand(d, cx + 6 + int(phase * 3), cy + bounce + 2, mic_tilt)
        # Motion blur streaks
        for _ in range(3 + f):
            sx = cx + random.randint(-12, 12)
            sy = cy + bounce + random.randint(-15, 15)
            d.line([sx, sy, sx + int(phase * 8), sy], fill=(*MOTION_BLUR, 60), width=1)
        # Energy sparks
        for _ in range(2 + f):
            sx = cx + random.randint(-18, 18)
            sy = cy + bounce + random.randint(-25, 20)
            if x_off <= sx < x_off + FW and 0 <= sy < FH:
                d.point([sx, sy], fill=ENERGY_SPARK)
        # Red rage aura on later frames
        if f >= 3:
            draw_rage_aura(img, cx, cy + bounce, x_off, (f - 2) / 2.0)
    path = BOSS_DIR / "joey_ramone_blitzkrieg_bop_sheet.png"
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
    print("Generating Joey Ramone boss sprites (Level 04 — CBGB Punk Alley)...")

    # ── Palette-swap from Disco King ──
    print("\nJoey Ramone — palette-swap (from Disco King):")
    swap_boss_sheets(remap_joey_ramone, "joey_ramone")

    # ── From-scratch attack sheets ──
    print("\nJoey Ramone — from-scratch attacks:")
    jr_mic_swing_sheet()
    jr_feedback_shriek_sheet()
    jr_crowd_surf_sheet()
    jr_wall_of_sound_sheet()
    jr_blitzkrieg_bop_sheet()

    print("\nDone! 8 Joey Ramone boss sprites generated.")


if __name__ == "__main__":
    main()
