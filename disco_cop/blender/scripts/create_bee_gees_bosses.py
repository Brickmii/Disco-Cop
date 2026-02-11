#!/usr/bin/env python3
"""Generate Bee Gees boss sprites for Disco Cop Level 05 (Bee Gees Disco Floor).

Three brothers:
  Barry Gibb  — flyer boss, always airborne
  Robin Gibb  — ground fighter
  Maurice Gibb — invisible pop-up boss with guitar/lasers

Barry Gibb (48x80/frame):
  Palette-swap from Disco King:
    - barry_gibb_idle_sheet  (192x80, 4f)
    - barry_gibb_hurt_sheet  (96x80, 2f)
    - barry_gibb_death_sheet (384x80, 8f)
  From-scratch attack sheets:
    - barry_gibb_heat_seeker_sheet  (288x80, 6f)
    - barry_gibb_missile_rain_sheet (288x80, 6f)
    - barry_gibb_strobe_burst_sheet (288x80, 6f)

Robin Gibb (48x80/frame):
  Palette-swap from Disco King:
    - robin_gibb_idle_sheet  (192x80, 4f)
    - robin_gibb_hurt_sheet  (96x80, 2f)
    - robin_gibb_death_sheet (384x80, 8f)
  From-scratch attack sheets:
    - robin_gibb_spread_shot_sheet     (288x80, 6f)
    - robin_gibb_disco_stomp_sheet     (288x80, 6f)
    - robin_gibb_spinning_records_sheet (192x80, 4f)
    - robin_gibb_falsetto_wave_sheet   (288x80, 6f)

Maurice Gibb (48x80/frame):
  Palette-swap from Disco King:
    - maurice_gibb_idle_sheet  (192x80, 4f)
    - maurice_gibb_hurt_sheet  (96x80, 2f)
    - maurice_gibb_death_sheet (384x80, 8f)
  From-scratch attack sheets:
    - maurice_gibb_laser_sweep_sheet  (288x80, 6f)
    - maurice_gibb_laser_cross_sheet  (288x80, 6f)
    - maurice_gibb_laser_spiral_sheet (288x80, 6f)

Usage:
    python create_bee_gees_bosses.py
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
BOSS_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "bosses"

random.seed(817)

FW, FH = 48, 80

# -- Effect colors (shared) ---------------------------------------------------

SOUND_RING = (180, 160, 255)
MOTION_BLUR = (100, 60, 160)
ENERGY_SPARK = (255, 240, 100)
WAVE_LINE = (140, 120, 220)
HEAT_ORANGE = (255, 140, 30)
HEAT_RED = (255, 60, 20)
HEAT_YELLOW = (255, 220, 60)
MISSILE_GRAY = (160, 155, 150)
MISSILE_TIP = (200, 50, 30)
STROBE_WHITE = (255, 255, 255)
STROBE_DIM = (80, 70, 100)
SPREAD_CYAN = (60, 220, 240)
SPREAD_WHITE = (220, 240, 255)
STOMP_BROWN = (140, 100, 60)
STOMP_CRACK = (80, 60, 35)
RECORD_BLACK = (15, 12, 10)
RECORD_GROOVE = (35, 30, 28)
RECORD_LABEL = (180, 40, 40)
FALSETTO_PINK = (240, 180, 220)
FALSETTO_LIGHT = (255, 220, 245)
LASER_RED = (255, 40, 30)
LASER_ORANGE = (255, 120, 20)
LASER_GLOW = (255, 180, 100)
LASER_CORE = (255, 255, 240)


# ==============================================================================
#  BARRY GIBB -- Flyer boss, always airborne
# ==============================================================================

# Barry Gibb palette
BG_SKIN = (200, 165, 135)
BG_SKIN_SHADOW = (170, 135, 105)
BG_BEARD = (120, 80, 40)
BG_BEARD_DARK = (90, 55, 25)
BG_HAIR = (100, 65, 35)
BG_HAIR_HIGHLIGHT = (130, 90, 50)
BG_SHIRT = (230, 225, 220)          # Open white shirt
BG_CHEST = (200, 165, 135)          # Visible chest
BG_PANTS = (220, 215, 210)          # Tight white flares
BG_PANTS_SHADOW = (190, 185, 180)
BG_GOLD_CHAIN = (220, 190, 60)
BG_MEDALLION = (240, 210, 80)
BG_SHOES = (210, 205, 200)          # White platform shoes
BG_OUTLINE = (12, 8, 6)


def remap_barry_gibb(r, g, b, a):
    """Disco King -> Barry Gibb: open white shirt, gold chain, brown beard."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 160:
        # Very light (disco suit highlights) -> white shirt/pants
        return (min(int(brightness * 0.95), 230),
                min(int(brightness * 0.93), 225),
                min(int(brightness * 0.91), 220), a)
    elif is_gray and brightness > 120:
        # Light body -> skin tones (chest visible through open shirt)
        return (min(int(brightness * 0.85), 200),
                min(int(brightness * 0.70), 165),
                min(int(brightness * 0.58), 135), a)
    elif is_gray and brightness > 80:
        # Mid body -> brown beard/hair
        return (min(int(brightness * 0.65), 120),
                min(int(brightness * 0.42), 80),
                min(int(brightness * 0.25), 40), a)
    elif brightness > 120 and r > b:
        # Warm tones (gold/skin) -> gold chain accents
        return (min(int(r * 0.95), 220),
                min(int(g * 0.85), 190),
                max(int(b * 0.4), 55), a)
    elif brightness > 80 and b > r:
        # Cool tones -> lighter white with warm cast
        return (min(int(brightness * 0.9), 210),
                min(int(brightness * 0.85), 200),
                min(int(brightness * 0.82), 195), a)
    elif brightness > 60:
        # Mid tones -> skin shadow
        return (min(int(r * 0.85), 170),
                min(int(g * 0.7), 135),
                min(int(b * 0.55), 105), a)
    elif brightness > 30:
        # Dark -> keep dark with warm tint
        return (max(int(r * 0.4), 20),
                max(int(g * 0.3), 15),
                max(int(b * 0.2), 10), a)
    else:
        return (min(r + 5, 18), min(g + 3, 12), min(b + 2, 8), a)


def draw_barry_body(d, cx, cy, pose_data=None):
    """Draw Barry Gibb's body (floating). Returns attachment points dict."""
    p = pose_data or {}
    head_tilt = p.get("head_tilt", 0)
    torso_lean = p.get("torso_lean", 0)
    l_arm_angle = p.get("l_arm_angle", -25)
    r_arm_angle = p.get("r_arm_angle", 25)
    float_bob = p.get("float_bob", 0)

    # Floating means legs dangle; shift everything up a bit
    base_cy = cy + float_bob
    hip_y = base_cy + 12
    foot_y = base_cy + 32
    leg_spread = p.get("leg_spread", 4)

    # Legs (tight white flares -- dangling, slight outward flare at bottom)
    ll_x = cx - leg_spread + torso_lean
    d.line([cx - 3 + torso_lean, hip_y, ll_x - 2, foot_y], fill=BG_PANTS_SHADOW, width=5)
    d.line([cx - 3 + torso_lean, hip_y, ll_x - 2, foot_y], fill=BG_PANTS, width=3)
    # Flare at bottom
    d.line([ll_x - 2, foot_y - 3, ll_x - 4, foot_y + 1], fill=BG_PANTS, width=2)
    d.line([ll_x - 2, foot_y - 3, ll_x + 1, foot_y + 1], fill=BG_PANTS, width=2)
    d.rectangle([ll_x - 5, foot_y, ll_x + 2, foot_y + 3], fill=BG_SHOES)

    rl_x = cx + leg_spread + torso_lean
    d.line([cx + 3 + torso_lean, hip_y, rl_x + 2, foot_y], fill=BG_PANTS_SHADOW, width=5)
    d.line([cx + 3 + torso_lean, hip_y, rl_x + 2, foot_y], fill=BG_PANTS, width=3)
    d.line([rl_x + 2, foot_y - 3, rl_x + 4, foot_y + 1], fill=BG_PANTS, width=2)
    d.line([rl_x + 2, foot_y - 3, rl_x - 1, foot_y + 1], fill=BG_PANTS, width=2)
    d.rectangle([rl_x - 2, foot_y, rl_x + 5, foot_y + 3], fill=BG_SHOES)

    # Torso (open white shirt, chest visible)
    torso_top = base_cy - 8
    torso_cx = cx + torso_lean
    d.rectangle([torso_cx - 10, torso_top, torso_cx + 10, hip_y], fill=BG_SHIRT)
    # Exposed chest (open shirt V)
    for vy in range(torso_top + 1, torso_top + 14):
        v_half = max(1, int((vy - torso_top) * 0.45))
        d.line([torso_cx - v_half, vy, torso_cx + v_half, vy], fill=BG_CHEST)
    # Shirt collar points
    d.line([torso_cx - 10, torso_top, torso_cx - 6, torso_top - 2], fill=BG_SHIRT)
    d.line([torso_cx + 10, torso_top, torso_cx + 6, torso_top - 2], fill=BG_SHIRT)

    # Gold chain with medallion
    chain_y = torso_top + 4
    for chain_x in range(torso_cx - 5, torso_cx + 6):
        sag = int(abs(chain_x - torso_cx) * 0.4)
        d.point([chain_x, chain_y + sag], fill=BG_GOLD_CHAIN)
    # Medallion at center of chain sag
    med_y = chain_y + 3
    d.ellipse([torso_cx - 2, med_y, torso_cx + 2, med_y + 4], fill=BG_MEDALLION)
    d.point([torso_cx, med_y + 2], fill=BG_GOLD_CHAIN)

    # Arms
    arm_len = 18
    shoulder_y = torso_top + 3

    la_rad = math.radians(l_arm_angle)
    la_ex = torso_cx - 10 + int(arm_len * math.sin(la_rad))
    la_ey = shoulder_y + int(arm_len * math.cos(la_rad))
    d.line([torso_cx - 10, shoulder_y, la_ex, la_ey], fill=BG_SHIRT, width=4)
    d.ellipse([la_ex - 2, la_ey - 2, la_ex + 2, la_ey + 2], fill=BG_SKIN)

    ra_rad = math.radians(r_arm_angle)
    ra_ex = torso_cx + 10 + int(arm_len * math.sin(ra_rad))
    ra_ey = shoulder_y + int(arm_len * math.cos(ra_rad))
    d.line([torso_cx + 10, shoulder_y, ra_ex, ra_ey], fill=BG_SHIRT, width=4)
    d.ellipse([ra_ex - 2, ra_ey - 2, ra_ex + 2, ra_ey + 2], fill=BG_SKIN)

    # Head
    head_cx = torso_cx + head_tilt
    head_cy = torso_top - 10
    head_w, head_h = 9, 12
    d.ellipse([head_cx - head_w // 2, head_cy - head_h // 2,
               head_cx + head_w // 2, head_cy + head_h // 2],
              fill=BG_SKIN, outline=BG_OUTLINE)

    # Eyes
    d.point([head_cx - 2, head_cy - 1], fill=BG_OUTLINE)
    d.point([head_cx + 2, head_cy - 1], fill=BG_OUTLINE)
    # Mouth
    d.line([head_cx - 1, head_cy + 2, head_cx + 1, head_cy + 2], fill=BG_OUTLINE)

    # Big beard (fills lower face and extends below chin)
    beard_top = head_cy + 1
    beard_bottom = head_cy + head_h // 2 + 6
    for by in range(beard_top, beard_bottom):
        t = (by - beard_top) / max(1, beard_bottom - beard_top)
        half_w = max(1, int(5 * (1 - t * 0.4)))
        for bx in range(head_cx - half_w, head_cx + half_w + 1):
            if 0 <= bx < FW * 10 and 0 <= by < FH:
                c = BG_BEARD if random.random() > 0.3 else BG_BEARD_DARK
                d.point([bx, by], fill=c)

    # Wavy brown hair (long, feathered 70s style)
    hair_top = head_cy - head_h // 2
    for hair_x in range(-5, 6):
        base_x = head_cx + hair_x
        hair_len = random.randint(14, 22)
        if abs(hair_x) >= 4:
            hair_len += random.randint(2, 5)
        for j in range(hair_len):
            hy = hair_top + j
            wave = int(math.sin(j * 0.5 + hair_x * 0.7) * 1.5)
            hx = base_x + wave
            if 0 <= hy < FH:
                c = BG_HAIR if j < hair_len * 0.6 else BG_HAIR_HIGHLIGHT
                d.point([hx, hy], fill=c)
                if abs(hair_x) <= 2 and j < 3:
                    d.point([hx + 1, hy], fill=c)

    return {
        "l_hand": (la_ex, la_ey),
        "r_hand": (ra_ex, ra_ey),
        "torso_cx": torso_cx,
        "shoulder_y": shoulder_y,
        "head_cx": head_cx,
        "head_cy": head_cy,
    }


# ==============================================================================
#  ROBIN GIBB -- Ground fighter, thinner build
# ==============================================================================

# Robin Gibb palette
RG_SKIN = (210, 180, 155)
RG_SKIN_SHADOW = (175, 145, 120)
RG_HAIR = (60, 40, 25)
RG_HAIR_HIGHLIGHT = (85, 60, 40)
RG_SUIT = (100, 70, 45)
RG_SUIT_LIGHT = (120, 85, 55)
RG_SUIT_DARK = (75, 50, 30)
RG_SCARF = (220, 210, 185)          # Cream/ivory scarf
RG_SHIRT = (210, 200, 180)          # Cream shirt
RG_SHOES = (70, 45, 25)             # Brown leather shoes
RG_OUTLINE = (10, 8, 6)


def remap_robin_gibb(r, g, b, a):
    """Disco King -> Robin Gibb: brown suit, cream shirt, scarf at neck."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 160:
        # Very light (disco suit highlights) -> cream shirt/scarf
        return (min(int(brightness * 0.90), 220),
                min(int(brightness * 0.87), 210),
                min(int(brightness * 0.77), 185), a)
    elif is_gray and brightness > 120:
        # Light body -> brown suit lighter
        return (min(int(brightness * 0.55), 120),
                min(int(brightness * 0.40), 85),
                min(int(brightness * 0.28), 55), a)
    elif is_gray and brightness > 80:
        # Mid body -> brown suit main
        return (min(int(brightness * 0.55), 100),
                min(int(brightness * 0.38), 70),
                min(int(brightness * 0.24), 45), a)
    elif brightness > 120 and r > b:
        # Warm tones -> skin
        return (min(int(r * 0.95), 210),
                min(int(g * 0.82), 180),
                min(int(b * 0.72), 155), a)
    elif brightness > 80 and b > r:
        # Cool tones -> suit dark
        return (min(int(brightness * 0.45), 75),
                min(int(brightness * 0.30), 50),
                min(int(brightness * 0.18), 30), a)
    elif brightness > 60:
        # Mid tones -> skin shadow
        return (min(int(r * 0.82), 175),
                min(int(g * 0.68), 145),
                min(int(b * 0.56), 120), a)
    elif brightness > 30:
        # Dark -> dark brown
        return (max(int(r * 0.35), 18),
                max(int(g * 0.25), 12),
                max(int(b * 0.15), 8), a)
    else:
        return (min(r + 3, 15), min(g + 2, 10), min(b + 1, 8), a)


def draw_robin_body(d, cx, cy, pose_data=None):
    """Draw Robin Gibb's body (thinner, dapper). Returns attachment points."""
    p = pose_data or {}
    head_tilt = p.get("head_tilt", 0)
    torso_lean = p.get("torso_lean", 0)
    l_arm_angle = p.get("l_arm_angle", -25)
    r_arm_angle = p.get("r_arm_angle", 25)

    hip_y = cy + 14
    foot_y = cy + 34
    leg_spread = p.get("leg_spread", 4)

    # Legs (brown suit trousers -- thinner than Barry)
    ll_x = cx - leg_spread + torso_lean
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=RG_SUIT_DARK, width=4)
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=RG_SUIT, width=2)
    d.rectangle([ll_x - 3, foot_y - 2, ll_x + 3, foot_y + 2], fill=RG_SHOES)

    rl_x = cx + leg_spread + torso_lean
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=RG_SUIT_DARK, width=4)
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=RG_SUIT, width=2)
    d.rectangle([rl_x - 3, foot_y - 2, rl_x + 3, foot_y + 2], fill=RG_SHOES)

    # Torso (brown suit jacket, slightly narrower)
    torso_top = cy - 8
    torso_cx = cx + torso_lean
    d.rectangle([torso_cx - 9, torso_top, torso_cx + 9, hip_y], fill=RG_SUIT)
    # Cream shirt visible at center
    d.rectangle([torso_cx - 4, torso_top + 1, torso_cx + 4, torso_top + 10], fill=RG_SHIRT)
    # Suit lapels
    d.line([torso_cx - 9, torso_top, torso_cx - 4, torso_top + 7],
           fill=RG_SUIT_LIGHT, width=1)
    d.line([torso_cx + 9, torso_top, torso_cx + 4, torso_top + 7],
           fill=RG_SUIT_LIGHT, width=1)
    # Scarf at neck (draped, cream/ivory)
    scarf_y = torso_top - 1
    d.line([torso_cx - 5, scarf_y, torso_cx + 5, scarf_y], fill=RG_SCARF, width=2)
    # Scarf tails hang down center
    d.line([torso_cx - 1, scarf_y, torso_cx - 2, scarf_y + 8], fill=RG_SCARF, width=1)
    d.line([torso_cx + 1, scarf_y, torso_cx + 2, scarf_y + 8], fill=RG_SCARF, width=1)

    # Arms (suit sleeves)
    arm_len = 17
    shoulder_y = torso_top + 3

    la_rad = math.radians(l_arm_angle)
    la_ex = torso_cx - 9 + int(arm_len * math.sin(la_rad))
    la_ey = shoulder_y + int(arm_len * math.cos(la_rad))
    d.line([torso_cx - 9, shoulder_y, la_ex, la_ey], fill=RG_SUIT, width=3)
    d.ellipse([la_ex - 2, la_ey - 2, la_ex + 2, la_ey + 2], fill=RG_SKIN)

    ra_rad = math.radians(r_arm_angle)
    ra_ex = torso_cx + 9 + int(arm_len * math.sin(ra_rad))
    ra_ey = shoulder_y + int(arm_len * math.cos(ra_rad))
    d.line([torso_cx + 9, shoulder_y, ra_ex, ra_ey], fill=RG_SUIT, width=3)
    d.ellipse([ra_ex - 2, ra_ey - 2, ra_ex + 2, ra_ey + 2], fill=RG_SKIN)

    # Head (slightly narrower face)
    head_cx = torso_cx + head_tilt
    head_cy = torso_top - 10
    head_w, head_h = 8, 11
    d.ellipse([head_cx - head_w // 2, head_cy - head_h // 2,
               head_cx + head_w // 2, head_cy + head_h // 2],
              fill=RG_SKIN, outline=RG_OUTLINE)

    # Eyes
    d.point([head_cx - 2, head_cy - 1], fill=RG_OUTLINE)
    d.point([head_cx + 2, head_cy - 1], fill=RG_OUTLINE)
    # Mouth
    mouth_open = p.get("mouth_open", False)
    if mouth_open:
        d.ellipse([head_cx - 2, head_cy + 2, head_cx + 2, head_cy + 4], fill=RG_OUTLINE)
    else:
        d.line([head_cx - 1, head_cy + 3, head_cx + 1, head_cy + 3], fill=RG_OUTLINE)

    # Wavy dark brown hair (feathered, parted, 70s style)
    hair_top = head_cy - head_h // 2
    for hair_x in range(-4, 5):
        base_x = head_cx + hair_x
        hair_len = random.randint(10, 16)
        if abs(hair_x) >= 3:
            hair_len += random.randint(2, 4)
        for j in range(hair_len):
            hy = hair_top + j
            wave = int(math.sin(j * 0.6 + hair_x * 0.8) * 1.0)
            hx = base_x + wave
            if 0 <= hy < FH:
                c = RG_HAIR if j < hair_len * 0.65 else RG_HAIR_HIGHLIGHT
                d.point([hx, hy], fill=c)

    return {
        "l_hand": (la_ex, la_ey),
        "r_hand": (ra_ex, ra_ey),
        "torso_cx": torso_cx,
        "shoulder_y": shoulder_y,
        "head_cx": head_cx,
        "head_cy": head_cy,
        "foot_y": foot_y,
    }


# ==============================================================================
#  MAURICE GIBB -- Invisible pop-up boss with guitar
# ==============================================================================

# Maurice Gibb palette
MG_SKIN = (195, 160, 130)
MG_SKIN_SHADOW = (160, 125, 95)
MG_BEARD = (90, 60, 35)
MG_BEARD_HIGHLIGHT = (110, 75, 45)
MG_HAIR = (80, 55, 30)
MG_GLASSES_LENS = (200, 140, 40)      # Amber tint
MG_GLASSES_FRAME = (60, 55, 50)
MG_DENIM = (70, 85, 120)              # Denim jacket
MG_DENIM_LIGHT = (90, 105, 140)
MG_DENIM_DARK = (50, 65, 95)
MG_SHIRT = (30, 28, 25)               # Dark shirt underneath
MG_PANTS = (40, 50, 70)               # Dark denim
MG_PANTS_LIGHT = (55, 65, 85)
MG_SHOES = (45, 35, 25)
MG_OUTLINE = (10, 8, 6)

# Guitar palette
MG_GUITAR_BODY = (140, 70, 30)
MG_GUITAR_BODY_LIGHT = (170, 95, 45)
MG_GUITAR_BODY_DARK = (105, 50, 20)
MG_GUITAR_NECK = (120, 90, 50)
MG_GUITAR_NECK_DARK = (90, 65, 35)
MG_GUITAR_HEAD = (35, 28, 20)
MG_GUITAR_STRING = (200, 200, 210)
MG_GUITAR_PICKUP = (55, 50, 45)


def remap_maurice_gibb(r, g, b, a):
    """Disco King -> Maurice Gibb: denim jacket, amber glasses, guitar accent."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 160:
        # Very light (disco suit highlights) -> denim jacket light
        return (min(int(brightness * 0.42), 90),
                min(int(brightness * 0.48), 105),
                min(int(brightness * 0.62), 140), a)
    elif is_gray and brightness > 120:
        # Light body -> denim main
        return (min(int(brightness * 0.35), 70),
                min(int(brightness * 0.42), 85),
                min(int(brightness * 0.58), 120), a)
    elif is_gray and brightness > 80:
        # Mid body -> denim dark
        return (min(int(brightness * 0.30), 50),
                min(int(brightness * 0.38), 65),
                min(int(brightness * 0.52), 95), a)
    elif brightness > 120 and r > b:
        # Warm tones (gold/skin) -> amber glasses accent / skin
        return (min(int(r * 0.88), 195),
                min(int(g * 0.72), 160),
                min(int(b * 0.60), 130), a)
    elif brightness > 80 and b > r:
        # Cool tones -> dark denim pants
        return (max(int(r * 0.30), 40),
                max(int(g * 0.35), 50),
                max(int(b * 0.50), 70), a)
    elif brightness > 60:
        # Mid tones -> skin shadow
        return (min(int(r * 0.78), 160),
                min(int(g * 0.62), 125),
                min(int(b * 0.48), 95), a)
    elif brightness > 30:
        # Dark -> very dark shirt
        return (max(int(r * 0.25), 15),
                max(int(g * 0.22), 14),
                max(int(b * 0.20), 12), a)
    else:
        return (min(r + 3, 15), min(g + 3, 12), min(b + 2, 10), a)


def draw_maurice_body(d, cx, cy, pose_data=None):
    """Draw Maurice Gibb's body. Returns attachment points dict."""
    p = pose_data or {}
    head_tilt = p.get("head_tilt", 0)
    torso_lean = p.get("torso_lean", 0)
    l_arm_angle = p.get("l_arm_angle", -25)
    r_arm_angle = p.get("r_arm_angle", 25)

    hip_y = cy + 14
    foot_y = cy + 34
    leg_spread = p.get("leg_spread", 5)

    # Legs (dark denim)
    ll_x = cx - leg_spread + torso_lean
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=MG_PANTS, width=4)
    d.line([cx - 3 + torso_lean, hip_y, ll_x, foot_y], fill=MG_PANTS_LIGHT, width=2)
    d.rectangle([ll_x - 3, foot_y - 2, ll_x + 3, foot_y + 2], fill=MG_SHOES)

    rl_x = cx + leg_spread + torso_lean
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=MG_PANTS, width=4)
    d.line([cx + 3 + torso_lean, hip_y, rl_x, foot_y], fill=MG_PANTS_LIGHT, width=2)
    d.rectangle([rl_x - 3, foot_y - 2, rl_x + 3, foot_y + 2], fill=MG_SHOES)

    # Torso (denim jacket over dark shirt)
    torso_top = cy - 8
    torso_cx = cx + torso_lean
    d.rectangle([torso_cx - 10, torso_top, torso_cx + 10, hip_y], fill=MG_DENIM)
    # Dark shirt visible at center
    d.rectangle([torso_cx - 4, torso_top + 2, torso_cx + 4, torso_top + 10], fill=MG_SHIRT)
    # Denim jacket details -- lapels and shoulder seams
    d.line([torso_cx - 10, torso_top, torso_cx - 4, torso_top + 7],
           fill=MG_DENIM_LIGHT, width=1)
    d.line([torso_cx + 10, torso_top, torso_cx + 4, torso_top + 7],
           fill=MG_DENIM_LIGHT, width=1)
    # Collar
    d.line([torso_cx - 10, torso_top, torso_cx - 8, torso_top - 2], fill=MG_DENIM_LIGHT)
    d.line([torso_cx + 10, torso_top, torso_cx + 8, torso_top - 2], fill=MG_DENIM_LIGHT)
    # Jacket pocket hint
    d.rectangle([torso_cx - 8, hip_y - 4, torso_cx - 4, hip_y - 1], outline=MG_DENIM_DARK)

    # Arms (denim sleeves)
    arm_len = 18
    shoulder_y = torso_top + 3

    la_rad = math.radians(l_arm_angle)
    la_ex = torso_cx - 10 + int(arm_len * math.sin(la_rad))
    la_ey = shoulder_y + int(arm_len * math.cos(la_rad))
    d.line([torso_cx - 10, shoulder_y, la_ex, la_ey], fill=MG_DENIM, width=4)
    d.ellipse([la_ex - 2, la_ey - 2, la_ex + 2, la_ey + 2], fill=MG_SKIN)

    ra_rad = math.radians(r_arm_angle)
    ra_ex = torso_cx + 10 + int(arm_len * math.sin(ra_rad))
    ra_ey = shoulder_y + int(arm_len * math.cos(ra_rad))
    d.line([torso_cx + 10, shoulder_y, ra_ex, ra_ey], fill=MG_DENIM, width=4)
    d.ellipse([ra_ex - 2, ra_ey - 2, ra_ex + 2, ra_ey + 2], fill=MG_SKIN)

    # Head
    head_cx = torso_cx + head_tilt
    head_cy = torso_top - 10
    head_w, head_h = 9, 12
    d.ellipse([head_cx - head_w // 2, head_cy - head_h // 2,
               head_cx + head_w // 2, head_cy + head_h // 2],
              fill=MG_SKIN, outline=MG_OUTLINE)

    # Amber tinted round glasses
    # Left lens
    d.ellipse([head_cx - 5, head_cy - 2, head_cx - 1, head_cy + 2],
              fill=MG_GLASSES_LENS, outline=MG_GLASSES_FRAME)
    # Right lens
    d.ellipse([head_cx + 1, head_cy - 2, head_cx + 5, head_cy + 2],
              fill=MG_GLASSES_LENS, outline=MG_GLASSES_FRAME)
    # Bridge
    d.line([head_cx - 1, head_cy, head_cx + 1, head_cy], fill=MG_GLASSES_FRAME)

    # Mouth
    d.line([head_cx - 1, head_cy + 3, head_cx + 1, head_cy + 3], fill=MG_OUTLINE)

    # Shorter beard (less full than Barry)
    beard_top = head_cy + 2
    beard_bottom = head_cy + head_h // 2 + 3
    for by in range(beard_top, beard_bottom):
        t = (by - beard_top) / max(1, beard_bottom - beard_top)
        half_w = max(1, int(4 * (1 - t * 0.5)))
        for bx in range(head_cx - half_w, head_cx + half_w + 1):
            if 0 <= bx < FW * 10 and 0 <= by < FH:
                c = MG_BEARD if random.random() > 0.35 else MG_BEARD_HIGHLIGHT
                d.point([bx, by], fill=c)

    # Wavy medium brown hair
    hair_top = head_cy - head_h // 2
    for hair_x in range(-4, 5):
        base_x = head_cx + hair_x
        hair_len = random.randint(12, 18)
        if abs(hair_x) >= 3:
            hair_len += random.randint(1, 4)
        for j in range(hair_len):
            hy = hair_top + j
            wave = int(math.sin(j * 0.55 + hair_x * 0.6) * 1.2)
            hx = base_x + wave
            if 0 <= hy < FH:
                c = MG_HAIR if j < hair_len * 0.7 else MG_BEARD_HIGHLIGHT
                d.point([hx, hy], fill=c)

    return {
        "l_hand": (la_ex, la_ey),
        "r_hand": (ra_ex, ra_ey),
        "torso_cx": torso_cx,
        "shoulder_y": shoulder_y,
        "head_cx": head_cx,
        "head_cy": head_cy,
    }


def draw_mg_guitar(d, x, y, angle_deg=0):
    """Draw Maurice Gibb's guitar (warm-toned acoustic/semi-hollow body)."""
    body_w, body_h = 13, 10
    neck_len = 17
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    # Body (elliptical)
    for dy in range(-body_h // 2, body_h // 2 + 1):
        for dx in range(-body_w // 2, body_w // 2 + 1):
            if (dx / (body_w / 2.0)) ** 2 + (dy / (body_h / 2.0)) ** 2 <= 1:
                rx = x + int(dx * cos_a - dy * sin_a)
                ry = y + int(dx * sin_a + dy * cos_a)
                dist = math.sqrt(dx * dx + dy * dy)
                max_r = math.sqrt((body_w / 2) ** 2 + (body_h / 2) ** 2)
                t = dist / max_r
                if t < 0.4:
                    c = MG_GUITAR_BODY_LIGHT
                elif t < 0.7:
                    c = MG_GUITAR_BODY
                else:
                    c = MG_GUITAR_BODY_DARK
                d.point([rx, ry], fill=c)

    # Pickup
    d.rectangle([x - 2, y - 1, x + 2, y + 1], fill=MG_GUITAR_PICKUP)

    # Neck
    for i in range(neck_len):
        nx = x + int((-body_w // 2 - i) * cos_a)
        ny = y + int((-body_w // 2 - i) * sin_a)
        d.rectangle([nx - 1, ny - 1, nx + 1, ny + 1], fill=MG_GUITAR_NECK)
        if i % 5 == 0:
            d.point([nx, ny], fill=MG_GUITAR_NECK_DARK)

    # Headstock
    hx = x + int((-body_w // 2 - neck_len) * cos_a)
    hy = y + int((-body_w // 2 - neck_len) * sin_a)
    d.rectangle([hx - 3, hy - 3, hx + 3, hy + 3], fill=MG_GUITAR_HEAD)

    # Strings
    bx = x + int(4 * cos_a)
    by = y + int(4 * sin_a)
    d.line([bx, by, hx, hy], fill=MG_GUITAR_STRING, width=1)

    return (hx, hy)  # Return guitar head position for laser origin


# ==============================================================================
#  Shared drawing helpers
# ==============================================================================

def draw_sound_rings(d, cx, cy, num_rings, max_radius, alpha_base=180):
    """Draw expanding sound wave rings."""
    for i in range(num_rings):
        t = (i + 1) / num_rings
        r = int(max_radius * t)
        alpha = max(20, int(alpha_base * (1 - t)))
        color = (*SOUND_RING[:3], alpha)
        d.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], outline=color, width=1)


def draw_heat_trail(d, x1, y1, x2, y2, frame_t):
    """Draw a wavy heat-seeking projectile trail (orange/red wavy line)."""
    steps = 20
    for i in range(steps):
        t = i / steps
        bx = int(x1 + (x2 - x1) * t)
        by = int(y1 + (y2 - y1) * t)
        # Wavy offset
        wave = int(math.sin(t * 8 + frame_t * 3) * 3)
        by += wave
        alpha = max(40, int(200 * (1 - t * 0.5)))
        if t < 0.3:
            c = HEAT_RED
        elif t < 0.6:
            c = HEAT_ORANGE
        else:
            c = HEAT_YELLOW
        d.rectangle([bx - 1, by - 1, bx + 1, by + 1], fill=(*c, alpha))


# ==============================================================================
#  BARRY GIBB -- Attack sheets (from scratch)
# ==============================================================================

def barry_heat_seeker_sheet():
    """Points forward, 2-3 heat-seeking projectile trails (wavy lines) -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 - 2  # Floating higher

        bob = int(math.sin(f * 0.8) * 2)
        pose = {"torso_lean": 2, "head_tilt": 1,
                "l_arm_angle": -15, "r_arm_angle": -50 - f * 3,
                "leg_spread": 4, "float_bob": bob}
        pts = draw_barry_body(d, cx, cy, pose)

        # Heat-seeking projectile trails emanating from right hand
        rh = pts["r_hand"]
        num_trails = min(2 + f // 2, 3)
        for trail in range(num_trails):
            # Each trail curves differently
            spread = (trail - 1) * 8
            trail_end_x = rh[0] + 6 + f * 4
            trail_end_y = rh[1] + spread - f * 2
            if f >= 1:
                trail_start_x = rh[0] + 3
                trail_start_y = rh[1] + spread // 2
                draw_heat_trail(d, trail_start_x, trail_start_y,
                                min(trail_end_x, x_off + FW - 2),
                                max(2, min(trail_end_y, FH - 2)), f)

        # Glow at hand on early frames
        if f < 3:
            glow_r = 4 - f
            for gy in range(rh[1] - glow_r, rh[1] + glow_r + 1):
                for gx in range(rh[0] - glow_r, rh[0] + glow_r + 1):
                    dist = math.sqrt((gx - rh[0]) ** 2 + (gy - rh[1]) ** 2)
                    if dist <= glow_r and 0 <= gx < img.width and 0 <= gy < FH:
                        alpha = int(180 * (1 - dist / glow_r))
                        r0, g0, b0, a0 = img.getpixel((gx, gy))
                        if a0 == 0:
                            img.putpixel((gx, gy), (*HEAT_ORANGE, alpha))

    path = BOSS_DIR / "barry_gibb_heat_seeker_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def barry_missile_rain_sheet():
    """Arms raised, projectiles rain down from above -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 - 6  # Hovers high in frame

        bob = int(math.sin(f * 0.7) * 2)
        pose = {"torso_lean": 0, "head_tilt": 0,
                "l_arm_angle": -75 - f * 2, "r_arm_angle": -75 - f * 2,
                "leg_spread": 3, "float_bob": bob}
        draw_barry_body(d, cx, cy, pose)

        # Missiles raining from top of frame
        if f >= 1:
            num_missiles = f + 1
            for m in range(num_missiles):
                # Stagger positions across the frame
                mx = x_off + 5 + int((FW - 10) * (m + 0.5) / num_missiles)
                # Missiles fall further each frame
                fall_progress = (f - 1 + m * 0.3) / nf
                my = int(fall_progress * FH * 0.9)
                if 0 <= my < FH and x_off <= mx < x_off + FW:
                    # Missile body (small downward arrow)
                    d.rectangle([mx - 1, my - 3, mx + 1, my + 2], fill=MISSILE_GRAY)
                    # Red nose cone
                    d.rectangle([mx - 1, my + 2, mx + 1, my + 4], fill=MISSILE_TIP)
                    # Exhaust trail above
                    trail_len = min(8, my)
                    for ty in range(trail_len):
                        trail_y = my - 3 - ty
                        if trail_y >= 0:
                            alpha = max(20, 120 - ty * 15)
                            d.point([mx + random.randint(-1, 1), trail_y],
                                    fill=(*HEAT_ORANGE[:3], alpha))

        # Energy glow around raised hands on later frames
        if f >= 3:
            for _ in range(f * 2):
                sx = cx + random.randint(-6, 6)
                sy = cy - 20 + random.randint(-5, 5)
                if x_off <= sx < x_off + FW and 0 <= sy < FH:
                    d.point([sx, sy], fill=(*ENERGY_SPARK, 150))

    path = BOSS_DIR / "barry_gibb_missile_rain_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def barry_strobe_burst_sheet():
    """Arms spread wide, strobing flash effect -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 - 2

        bob = int(math.sin(f * 0.9) * 2)
        # Arms spread wide
        spread_prog = min(f / 3.0, 1.0)
        pose = {"torso_lean": 0, "head_tilt": 0,
                "l_arm_angle": int(-20 - 50 * spread_prog),
                "r_arm_angle": int(20 + 50 * spread_prog),
                "leg_spread": 5, "float_bob": bob}
        draw_barry_body(d, cx, cy, pose)

        # Alternating bright/dark frames with radial light rays
        is_bright = (f % 2 == 0)
        if f >= 2:
            if is_bright:
                # Radial light rays from center
                num_rays = 8 + f * 2
                for ray in range(num_rays):
                    angle = (ray / num_rays) * 2 * math.pi
                    ray_len = 12 + f * 4
                    ex = cx + int(ray_len * math.cos(angle))
                    ey = cy + int(ray_len * math.sin(angle) * 0.6)
                    alpha = max(60, 200 - f * 15)
                    d.line([cx, cy, ex, ey], fill=(*STROBE_WHITE, alpha), width=1)

                # White flash overlay on bright frames
                flash_r = 8 + f * 3
                for fy in range(cy - flash_r, cy + flash_r + 1):
                    for fx in range(cx - flash_r, cx + flash_r + 1):
                        dist = math.sqrt((fx - cx) ** 2 + (fy - cy) ** 2)
                        if dist <= flash_r and 0 <= fx < img.width and 0 <= fy < FH:
                            alpha = int(120 * (1 - dist / flash_r))
                            r0, g0, b0, a0 = img.getpixel((fx, fy))
                            if a0 > 0:
                                img.putpixel((fx, fy), (min(r0 + alpha, 255),
                                                         min(g0 + alpha, 255),
                                                         min(b0 + alpha, 255), a0))
                            elif alpha > 30:
                                img.putpixel((fx, fy), (*STROBE_WHITE, alpha))
            else:
                # Dim frames -- darker tint over body
                for dy in range(-20, 25):
                    for dx in range(-15, 16):
                        px_x = cx + dx
                        px_y = cy + dy
                        if 0 <= px_x < img.width and 0 <= px_y < FH:
                            r0, g0, b0, a0 = img.getpixel((px_x, px_y))
                            if a0 > 0:
                                img.putpixel((px_x, px_y),
                                             (max(r0 - 40, 0), max(g0 - 40, 0),
                                              max(b0 - 30, 0), a0))

    path = BOSS_DIR / "barry_gibb_strobe_burst_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


# ==============================================================================
#  ROBIN GIBB -- Attack sheets (from scratch)
# ==============================================================================

def robin_spread_shot_sheet():
    """Fan-shaped spread of 5 projectiles from hand -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        # Arm extends forward, then fires
        pose = {"torso_lean": [0, 1, 2, 2, 1, 0][f],
                "head_tilt": [0, 0, 1, 1, 0, 0][f],
                "l_arm_angle": -20,
                "r_arm_angle": [-10, -30, -45, -45, -40, -35][f],
                "leg_spread": 6}
        pts = draw_robin_body(d, cx, cy, pose)
        rh = pts["r_hand"]

        # Charge-up glow at hand (frames 0-1)
        if f <= 1:
            glow_r = 3 + f * 2
            d.ellipse([rh[0] - glow_r, rh[1] - glow_r,
                       rh[0] + glow_r, rh[1] + glow_r],
                      fill=(*SPREAD_CYAN[:3], 80 + f * 40))

        # Spread shot projectiles (frames 2-5)
        if f >= 2:
            num_shots = 5
            base_angle = -40  # degrees, fan centered around forward
            for s in range(num_shots):
                shot_angle = math.radians(base_angle + s * 20)
                proj_dist = (f - 1) * 7
                px = rh[0] + int(proj_dist * math.cos(shot_angle))
                py = rh[1] + int(proj_dist * math.sin(shot_angle))
                if x_off <= px < x_off + FW and 0 <= py < FH:
                    # Projectile dot
                    pr = 2
                    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=SPREAD_CYAN)
                    d.point([px, py], fill=SPREAD_WHITE)
                    # Trail line back toward hand
                    trail_dist = max(0, proj_dist - 5)
                    tx = rh[0] + int(trail_dist * math.cos(shot_angle))
                    ty = rh[1] + int(trail_dist * math.sin(shot_angle))
                    d.line([tx, ty, px, py], fill=(*SPREAD_CYAN, 100), width=1)

    path = BOSS_DIR / "robin_gibb_spread_shot_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def robin_disco_stomp_sheet():
    """Leg raises high then stomps down, shockwave rings expand -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        # Raise leg (0-2), stomp (3), shockwave (4-5)
        leg_raise = [0, -6, -14, -2, 0, 0][f]
        pose = {"torso_lean": [0, -2, -3, 2, 0, 0][f],
                "head_tilt": [0, -1, -1, 1, 0, 0][f],
                "l_arm_angle": [-20, -30, -40, -10, -20, -20][f],
                "r_arm_angle": [20, 30, 40, 10, 20, 20][f],
                "leg_spread": [5, 3, 2, 8, 6, 5][f]}
        pts = draw_robin_body(d, cx, cy, pose)

        # Draw the stomping leg separately for raise effect
        if f in (1, 2):
            # Right leg raised high (override the normal leg)
            stomp_foot_y = pts["foot_y"] + leg_raise
            d.line([cx + 3 + pose["torso_lean"], cy + 14,
                    cx + 6, stomp_foot_y], fill=RG_SUIT, width=4)
            d.rectangle([cx + 3, stomp_foot_y - 2, cx + 9, stomp_foot_y + 2], fill=RG_SHOES)

        # Impact frame
        if f == 3:
            # Ground crack lines
            foot_x = cx + 4
            foot_ground = cy + 34
            for crack in range(5):
                angle = math.radians(-150 + crack * 30)
                crack_len = random.randint(6, 14)
                ex = foot_x + int(crack_len * math.cos(angle))
                ey = foot_ground + int(crack_len * math.sin(angle) * 0.3)
                d.line([foot_x, foot_ground, ex, ey], fill=STOMP_CRACK, width=1)

        # Shockwave rings (frames 3-5)
        if f >= 3:
            wave_f = f - 3
            num_rings = wave_f + 1
            for ring in range(num_rings):
                ring_r = 6 + (wave_f * 8) + ring * 5
                ring_alpha = max(30, 180 - wave_f * 50 - ring * 30)
                d.ellipse([cx - ring_r, cy + 32 - ring_r // 4,
                           cx + ring_r, cy + 32 + ring_r // 4],
                          outline=(*STOMP_BROWN, ring_alpha), width=1)
            # Debris particles
            for _ in range(3 + wave_f * 2):
                dx = cx + random.randint(-ring_r, ring_r)
                dy = cy + 30 + random.randint(-4, 4)
                if x_off <= dx < x_off + FW and 0 <= dy < FH:
                    d.point([dx, dy], fill=STOMP_BROWN)

    path = BOSS_DIR / "robin_gibb_disco_stomp_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def robin_spinning_records_sheet():
    """Throws vinyl records as projectiles -- 4 frames."""
    nf = 4
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        # Throwing motion
        pose = {"torso_lean": [-1, 2, 4, 2][f],
                "head_tilt": [0, 1, 2, 1][f],
                "l_arm_angle": -20,
                "r_arm_angle": [-40, 10, 45, 35][f],
                "leg_spread": 5}
        pts = draw_robin_body(d, cx, cy, pose)
        rh = pts["r_hand"]

        # Record in hand on frame 0
        if f == 0:
            draw_vinyl_record(d, rh[0], rh[1], 5)

        # Flying records (frames 1-3)
        if f >= 1:
            num_records = min(f, 3)
            for rec in range(num_records):
                rec_dist = (f - rec * 0.3) * 10
                rx = rh[0] + int(rec_dist)
                ry = rh[1] - 3 + rec * 6 - f * 2
                if x_off <= rx - 4 and rx + 4 < x_off + FW and 0 <= ry < FH:
                    draw_vinyl_record(d, rx, ry, 4)
                    # Spin lines (rotation indicator)
                    spin_angle = f * 45 + rec * 30
                    sa = math.radians(spin_angle)
                    d.line([rx + int(2 * math.cos(sa)), ry + int(2 * math.sin(sa)),
                            rx - int(2 * math.cos(sa)), ry - int(2 * math.sin(sa))],
                           fill=RECORD_GROOVE, width=1)

    path = BOSS_DIR / "robin_gibb_spinning_records_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def draw_vinyl_record(d, cx, cy, radius):
    """Draw a small vinyl record at given position."""
    # Outer disc
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=RECORD_BLACK)
    # Groove ring
    if radius >= 3:
        d.ellipse([cx - radius + 1, cy - radius + 1, cx + radius - 1, cy + radius - 1],
                  outline=RECORD_GROOVE)
    # Center label
    label_r = max(1, radius // 2)
    d.ellipse([cx - label_r, cy - label_r, cx + label_r, cy + label_r], fill=RECORD_LABEL)
    # Center hole
    d.point([cx, cy], fill=RECORD_BLACK)


def robin_falsetto_wave_sheet():
    """Head tilted back, mouth open, horizontal sound waves emanate forward -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        # Head tilted back, singing pose
        pose = {"torso_lean": [-1, -1, 0, 0, 0, 0][f],
                "head_tilt": [-2, -3, -2, -1, 0, 0][f],
                "l_arm_angle": -15,
                "r_arm_angle": [15, 20, 25, 25, 20, 15][f],
                "leg_spread": 5,
                "mouth_open": True}
        pts = draw_robin_body(d, cx, cy, pose)

        # Falsetto sound waves -- sine waves moving rightward
        if f >= 1:
            head_x = pts["head_cx"]
            head_y = pts["head_cy"]
            num_waves = f + 1
            for w in range(num_waves):
                wave_start_x = head_x + 6 + w * 5
                wave_alpha = max(30, 200 - w * 35 - f * 10)
                # Draw sine wave segment
                for px in range(10 + f * 2):
                    wx = wave_start_x + px
                    if wx >= x_off + FW:
                        break
                    wave_amp = 4 + w
                    wy = head_y + int(wave_amp * math.sin(px * 0.5 + w * 1.5 + f * 0.8))
                    if 0 <= wy < FH and x_off <= wx < x_off + FW:
                        if w < 2:
                            c = FALSETTO_LIGHT
                        else:
                            c = FALSETTO_PINK
                        d.point([wx, wy], fill=(*c, wave_alpha))
                        # Thicker center waves
                        if w < 2 and 0 <= wy + 1 < FH:
                            d.point([wx, wy + 1], fill=(*c, wave_alpha // 2))

        # Subtle vibration on body at high intensity
        if f >= 4:
            for _ in range(4):
                vx = cx + random.randint(-10, 10)
                vy = cy + random.randint(-15, 10)
                if x_off <= vx < x_off + FW and 0 <= vy < FH:
                    r0, g0, b0, a0 = img.getpixel((vx, vy))
                    if a0 > 0:
                        img.putpixel((vx, vy), (min(r0 + 20, 255), min(g0 + 10, 255),
                                                  min(b0 + 25, 255), a0))

    path = BOSS_DIR / "robin_gibb_falsetto_wave_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


# ==============================================================================
#  MAURICE GIBB -- Attack sheets (from scratch)
# ==============================================================================

def draw_laser_beam(d, x1, y1, x2, y2, width=3):
    """Draw a glowing laser beam between two points."""
    # Core beam
    d.line([x1, y1, x2, y2], fill=LASER_CORE, width=1)
    # Inner glow
    for offset in range(-1, 2):
        if offset == 0:
            continue
        d.line([x1, y1 + offset, x2, y2 + offset], fill=LASER_RED, width=1)
    # Outer glow
    if width >= 3:
        for offset in [-2, 2]:
            d.line([x1, y1 + offset, x2, y2 + offset],
                   fill=(*LASER_GLOW, 80), width=1)


def maurice_laser_sweep_sheet():
    """Horizontal laser beam sweeps across frame from guitar neck -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        # Guitar held, slight lean forward
        pose = {"torso_lean": [0, 1, 2, 2, 1, 0][f],
                "head_tilt": [0, 0, 1, 1, 0, 0][f],
                "l_arm_angle": [-30, -35, -40, -40, -35, -30][f],
                "r_arm_angle": [15, 10, 5, 5, 10, 15][f],
                "leg_spread": 6}
        pts = draw_maurice_body(d, cx, cy, pose)

        # Guitar slung at torso
        guitar_x = pts["l_hand"][0]
        guitar_y = pts["l_hand"][1]
        guitar_head = draw_mg_guitar(d, guitar_x + 2, guitar_y - 2, -20 + f * 3)

        # Laser beam from guitar neck, sweeping angle changes per frame
        if f >= 1:
            laser_origin_x = guitar_head[0]
            laser_origin_y = guitar_head[1]
            # Sweep angle: starts high, sweeps down
            sweep_angle = math.radians(-30 + f * 15)
            laser_len = 35 + f * 5
            laser_end_x = laser_origin_x + int(laser_len * math.cos(sweep_angle))
            laser_end_y = laser_origin_y + int(laser_len * math.sin(sweep_angle))
            # Clamp to frame bounds
            laser_end_x = max(x_off, min(laser_end_x, x_off + FW - 1))
            laser_end_y = max(0, min(laser_end_y, FH - 1))
            draw_laser_beam(d, laser_origin_x, laser_origin_y,
                            laser_end_x, laser_end_y, 3)
            # Glow at origin
            glow_r = 3
            d.ellipse([laser_origin_x - glow_r, laser_origin_y - glow_r,
                       laser_origin_x + glow_r, laser_origin_y + glow_r],
                      fill=(*LASER_ORANGE, 120))

    path = BOSS_DIR / "maurice_gibb_laser_sweep_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def maurice_laser_cross_sheet():
    """Two laser beams cross in an X pattern, rotating -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        pose = {"torso_lean": 0, "head_tilt": 0,
                "l_arm_angle": -40 - f * 3, "r_arm_angle": 40 + f * 3,
                "leg_spread": 7}
        pts = draw_maurice_body(d, cx, cy, pose)

        # Guitar held upward, both hands
        guitar_head = draw_mg_guitar(d, cx - 2, cy - 5, -60 + f * 5)

        # Two crossing laser beams rotating around guitar head
        if f >= 1:
            origin_x, origin_y = guitar_head
            base_angle = f * 18  # Rotation per frame
            laser_len = 25 + f * 4

            for beam in range(2):
                angle = math.radians(base_angle + beam * 90)
                # Each beam goes both directions from origin (forming an X)
                for direction in [-1, 1]:
                    end_x = origin_x + int(direction * laser_len * math.cos(angle))
                    end_y = origin_y + int(direction * laser_len * math.sin(angle))
                    end_x = max(x_off, min(end_x, x_off + FW - 1))
                    end_y = max(0, min(end_y, FH - 1))
                    draw_laser_beam(d, origin_x, origin_y, end_x, end_y, 2)

            # Bright intersection glow
            glow_r = 3 + f // 2
            for gy in range(origin_y - glow_r, origin_y + glow_r + 1):
                for gx in range(origin_x - glow_r, origin_x + glow_r + 1):
                    dist = math.sqrt((gx - origin_x) ** 2 + (gy - origin_y) ** 2)
                    if dist <= glow_r and 0 <= gx < img.width and 0 <= gy < FH:
                        alpha = int(200 * (1 - dist / glow_r))
                        r0, g0, b0, a0 = img.getpixel((gx, gy))
                        if a0 == 0:
                            img.putpixel((gx, gy), (*LASER_CORE, alpha))
                        else:
                            img.putpixel((gx, gy), (min(r0 + alpha // 2, 255),
                                                     min(g0 + alpha // 3, 255),
                                                     min(b0 + alpha // 4, 255), a0))

    path = BOSS_DIR / "maurice_gibb_laser_cross_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def maurice_laser_spiral_sheet():
    """Spiral pattern of laser dots/lines rotating outward from guitar -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        pose = {"torso_lean": [0, 0, 1, 1, 0, 0][f],
                "head_tilt": [0, -1, -1, 0, 1, 0][f],
                "l_arm_angle": [-35, -40, -50, -55, -50, -40][f],
                "r_arm_angle": [20, 15, 10, 5, 10, 15][f],
                "leg_spread": 6}
        pts = draw_maurice_body(d, cx, cy, pose)

        # Guitar raised slightly
        guitar_head = draw_mg_guitar(d, pts["l_hand"][0] + 2,
                                     pts["l_hand"][1] - 3, -35 + f * 4)

        # Spiral laser dots expanding outward
        if f >= 1:
            origin_x, origin_y = guitar_head
            num_arms = 3  # 3-arm spiral
            dots_per_arm = 4 + f * 2
            max_spiral_r = 8 + f * 5

            for arm in range(num_arms):
                arm_offset = (arm / num_arms) * 2 * math.pi
                for dot in range(dots_per_arm):
                    t = (dot + 1) / dots_per_arm
                    # Spiral: angle increases with distance
                    spiral_angle = arm_offset + t * 3.0 + f * 0.8
                    spiral_r = t * max_spiral_r
                    dx = origin_x + int(spiral_r * math.cos(spiral_angle))
                    dy = origin_y + int(spiral_r * math.sin(spiral_angle))

                    if x_off <= dx < x_off + FW and 0 <= dy < FH:
                        alpha = max(40, int(220 * (1 - t * 0.5)))
                        # Laser dot
                        if t < 0.4:
                            c = LASER_CORE
                        elif t < 0.7:
                            c = LASER_RED
                        else:
                            c = LASER_ORANGE
                        d.rectangle([dx - 1, dy - 1, dx + 1, dy + 1],
                                    fill=(*c[:3], alpha))
                        # Connect adjacent dots with lines on later frames
                        if dot > 0 and f >= 3:
                            prev_t = dot / dots_per_arm
                            prev_angle = arm_offset + prev_t * 3.0 + f * 0.8
                            prev_r = prev_t * max_spiral_r
                            prev_x = origin_x + int(prev_r * math.cos(prev_angle))
                            prev_y = origin_y + int(prev_r * math.sin(prev_angle))
                            if (x_off <= prev_x < x_off + FW and
                                    0 <= prev_y < FH):
                                d.line([prev_x, prev_y, dx, dy],
                                       fill=(*LASER_GLOW, alpha // 2), width=1)

            # Center glow
            glow_alpha = min(200, 80 + f * 25)
            d.ellipse([origin_x - 2, origin_y - 2, origin_x + 2, origin_y + 2],
                      fill=(*LASER_CORE, glow_alpha))

    path = BOSS_DIR / "maurice_gibb_laser_spiral_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


# ==============================================================================
#  Palette-swap helpers
# ==============================================================================

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
                r, g, b, a_val = px[y, x]
                px[y, x] = remap_fn(int(r), int(g), int(b), int(a_val))

        dst_path = BOSS_DIR / dst_name
        Image.fromarray(px.astype(np.uint8), "RGBA").save(dst_path)
        print(f"  [OK] {dst_name}")


# ==============================================================================
#  Main
# ==============================================================================

def main():
    print("Generating Bee Gees boss sprites (Level 05 — Bee Gees Disco Floor)...")

    print("\n=== Barry Gibb (flyer) ===")
    print("Palette-swap (from Disco King):")
    swap_boss_sheets(remap_barry_gibb, "barry_gibb")
    print("From-scratch attacks:")
    barry_heat_seeker_sheet()
    barry_missile_rain_sheet()
    barry_strobe_burst_sheet()

    print("\n=== Robin Gibb (ground fighter) ===")
    print("Palette-swap (from Disco King):")
    swap_boss_sheets(remap_robin_gibb, "robin_gibb")
    print("From-scratch attacks:")
    robin_spread_shot_sheet()
    robin_disco_stomp_sheet()
    robin_spinning_records_sheet()
    robin_falsetto_wave_sheet()

    print("\n=== Maurice Gibb (invisible pop-up) ===")
    print("Palette-swap (from Disco King):")
    swap_boss_sheets(remap_maurice_gibb, "maurice_gibb")
    print("From-scratch attacks:")
    maurice_laser_sweep_sheet()
    maurice_laser_cross_sheet()
    maurice_laser_spiral_sheet()

    print("\nDone! 19 Bee Gees boss sprites generated.")


if __name__ == "__main__":
    main()
