#!/usr/bin/env python3
"""Generate Debbie Harry boss sprites for Disco Cop Level 04 (Blondie Concert at CBGB).

Debbie Harry (48x80/frame):
  Palette-swap from Disco King:
    - debbie_harry_idle_sheet  (192x80, 4f)
    - debbie_harry_hurt_sheet  (96x80, 2f)
    - debbie_harry_death_sheet (384x80, 8f)
  From-scratch attack sheets:
    - debbie_harry_heart_of_glass_sheet (288x80, 6f)
    - debbie_harry_call_me_sheet        (288x80, 6f)
    - debbie_harry_one_way_sheet        (288x80, 6f)
    - debbie_harry_rapture_sheet        (288x80, 6f)
    - debbie_harry_atomic_sheet         (288x80, 6f)

Usage:
    python create_cbgb_boss.py
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
BOSS_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "bosses"

random.seed(816)

FW, FH = 48, 80

# -- Effect colors (shared) ---------------------------------------------------

SOUND_RING = (180, 160, 255)
MOTION_BLUR = (100, 60, 160)
SPEED_LINE = (160, 150, 180)
ENERGY_SPARK = (255, 240, 100)
WAVE_LINE = (140, 120, 220)
GLASS_CYAN = (160, 230, 255)
GLASS_WHITE = (230, 245, 255)
FLASH_WHITE = (255, 255, 240)
TELEPORT_GLOW = (220, 200, 255)

# -- Debbie Harry palette ------------------------------------------------------

DH_SKIN = (225, 200, 185)
DH_SKIN_SHADOW = (190, 165, 150)
DH_HAIR = (240, 230, 180)            # Platinum blonde
DH_HAIR_HIGHLIGHT = (255, 245, 210)
DH_HAIR_DARK = (200, 190, 140)
DH_OUTFIT = (20, 18, 22)             # Black dress/top
DH_OUTFIT_LIGHT = (45, 42, 48)       # Sheen on black fabric
DH_STRIPE = (220, 215, 210)          # White stripes/accents
DH_LIPS = (200, 50, 50)              # Red lips
DH_EYES = (60, 90, 120)              # Blue-gray eyes
DH_EYELINER = (15, 12, 18)           # Dark eyeliner
DH_BOOTS = (25, 22, 28)              # Black boots
DH_BOOTS_HEEL = (40, 36, 42)         # Boot heel highlight
DH_OUTLINE = (10, 8, 10)

# -- Mic palette (handheld, no stand) -----------------------------------------

MIC_CHROME = (190, 195, 205)
MIC_CHROME_LIGHT = (220, 225, 235)
MIC_CHROME_DARK = (130, 135, 145)
MIC_HEAD = (60, 58, 55)
MIC_HEAD_RING = (170, 175, 185)


def remap_debbie_harry(r, g, b, a):
    """Disco King -> Debbie Harry: platinum blonde, black outfit, pale skin, red lips."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 160:
        # Very light (disco suit highlights) -> platinum blonde hair / white accents
        blend = brightness / 255.0
        rr = int(200 + blend * 55)
        gg = int(190 + blend * 55)
        bb = int(140 + blend * 70)
        return (min(rr, 255), min(gg, 245), min(bb, 210), a)
    elif is_gray and brightness > 120:
        # Light-mid grays -> black outfit with slight sheen
        return (max(int(brightness * 0.15), 18),
                max(int(brightness * 0.14), 16),
                max(int(brightness * 0.17), 20), a)
    elif is_gray and brightness > 80:
        # Mid grays -> pale skin tones
        return (min(int(brightness * 1.6), 225),
                min(int(brightness * 1.4), 200),
                min(int(brightness * 1.3), 185), a)
    elif brightness > 120 and r > b:
        # Warm tones (gold/skin) -> blonde hair with warm cast
        return (min(int(r * 1.05), 240),
                min(int(g * 1.02), 230),
                max(int(b * 0.75), 140), a)
    elif brightness > 80 and b > r:
        # Cool tones -> black outfit
        return (max(int(r * 0.12), 18),
                max(int(g * 0.1), 16),
                max(int(b * 0.14), 20), a)
    elif brightness > 60:
        # Mid tones -> skin shadow / outfit mix
        if r > g:
            # Warmer mid -> red lip accent
            return (min(int(r * 1.8), 200),
                    max(int(g * 0.4), 45),
                    max(int(b * 0.4), 45), a)
        else:
            # Cooler mid -> dark outfit
            return (max(int(r * 0.18), 18),
                    max(int(g * 0.16), 16),
                    max(int(b * 0.2), 20), a)
    elif brightness > 30:
        # Dark -> very dark with slight warm tint
        return (min(int(r * 0.3) + 6, 30),
                min(int(g * 0.25) + 4, 25),
                min(int(b * 0.25) + 4, 28), a)
    else:
        return (min(r + 3, 15), min(g + 2, 12), min(b + 3, 14), a)


def draw_debbie_body(d, cx, cy, pose_data=None):
    """Draw Debbie Harry's body. Returns key attachment points."""
    p = pose_data or {}
    head_tilt = p.get("head_tilt", 0)
    torso_lean = p.get("torso_lean", 0)
    l_arm_angle = p.get("l_arm_angle", -25)
    r_arm_angle = p.get("r_arm_angle", 25)

    hip_y = cy + 12
    foot_y = cy + 34
    leg_spread = p.get("leg_spread", 4)

    # -- Legs (slim, black tights / boots) --
    ll_x = cx - leg_spread + torso_lean
    d.line([cx - 2 + torso_lean, hip_y, ll_x, foot_y], fill=DH_OUTFIT, width=3)
    # Slim highlight along leg
    d.line([cx - 2 + torso_lean, hip_y + 2, ll_x, foot_y - 4],
           fill=DH_OUTFIT_LIGHT, width=1)
    # Boot
    d.rectangle([ll_x - 3, foot_y - 3, ll_x + 3, foot_y + 2], fill=DH_BOOTS)
    d.line([ll_x - 2, foot_y + 2, ll_x + 2, foot_y + 2], fill=DH_BOOTS_HEEL)

    rl_x = cx + leg_spread + torso_lean
    d.line([cx + 2 + torso_lean, hip_y, rl_x, foot_y], fill=DH_OUTFIT, width=3)
    d.line([cx + 2 + torso_lean, hip_y + 2, rl_x, foot_y - 4],
           fill=DH_OUTFIT_LIGHT, width=1)
    d.rectangle([rl_x - 3, foot_y - 3, rl_x + 3, foot_y + 2], fill=DH_BOOTS)
    d.line([rl_x - 2, foot_y + 2, rl_x + 2, foot_y + 2], fill=DH_BOOTS_HEEL)

    # -- Torso (black top with white stripe accents) --
    torso_top = cy - 10
    torso_cx = cx + torso_lean
    # Main body (slightly narrower / slimmer than Joey)
    d.rectangle([torso_cx - 9, torso_top, torso_cx + 9, hip_y], fill=DH_OUTFIT)
    # Horizontal white stripes across the top
    d.line([torso_cx - 8, torso_top + 3, torso_cx + 8, torso_top + 3],
           fill=DH_STRIPE, width=1)
    d.line([torso_cx - 7, torso_top + 6, torso_cx + 7, torso_top + 6],
           fill=DH_STRIPE, width=1)
    d.line([torso_cx - 8, torso_top + 9, torso_cx + 8, torso_top + 9],
           fill=DH_STRIPE, width=1)
    # Slight fabric sheen
    d.line([torso_cx - 9, torso_top, torso_cx - 9, hip_y],
           fill=DH_OUTFIT_LIGHT, width=1)
    d.line([torso_cx + 9, torso_top, torso_cx + 9, hip_y],
           fill=DH_OUTFIT_LIGHT, width=1)
    # Neckline / collarbone area (skin showing)
    d.rectangle([torso_cx - 5, torso_top - 1, torso_cx + 5, torso_top + 1],
                fill=DH_SKIN)
    d.point([torso_cx - 4, torso_top], fill=DH_SKIN_SHADOW)
    d.point([torso_cx + 4, torso_top], fill=DH_SKIN_SHADOW)

    # -- Arms (slim, skin-toned upper arm, black sleeve on forearm) --
    arm_len = 17
    shoulder_y = torso_top + 3

    la_rad = math.radians(l_arm_angle)
    la_mid_x = torso_cx - 9 + int((arm_len // 2) * math.sin(la_rad))
    la_mid_y = shoulder_y + int((arm_len // 2) * math.cos(la_rad))
    la_ex = torso_cx - 9 + int(arm_len * math.sin(la_rad))
    la_ey = shoulder_y + int(arm_len * math.cos(la_rad))
    # Upper arm (skin)
    d.line([torso_cx - 9, shoulder_y, la_mid_x, la_mid_y], fill=DH_SKIN, width=3)
    # Forearm (black)
    d.line([la_mid_x, la_mid_y, la_ex, la_ey], fill=DH_OUTFIT, width=3)
    # Hand
    d.ellipse([la_ex - 2, la_ey - 2, la_ex + 2, la_ey + 2], fill=DH_SKIN)

    ra_rad = math.radians(r_arm_angle)
    ra_mid_x = torso_cx + 9 + int((arm_len // 2) * math.sin(ra_rad))
    ra_mid_y = shoulder_y + int((arm_len // 2) * math.cos(ra_rad))
    ra_ex = torso_cx + 9 + int(arm_len * math.sin(ra_rad))
    ra_ey = shoulder_y + int(arm_len * math.cos(ra_rad))
    d.line([torso_cx + 9, shoulder_y, ra_mid_x, ra_mid_y], fill=DH_SKIN, width=3)
    d.line([ra_mid_x, ra_mid_y, ra_ex, ra_ey], fill=DH_OUTFIT, width=3)
    d.ellipse([ra_ex - 2, ra_ey - 2, ra_ex + 2, ra_ey + 2], fill=DH_SKIN)

    # -- Head --
    head_cx = torso_cx + head_tilt
    head_cy = torso_top - 10
    head_w, head_h = 9, 11
    d.ellipse([head_cx - head_w // 2, head_cy - head_h // 2,
               head_cx + head_w // 2, head_cy + head_h // 2],
              fill=DH_SKIN, outline=DH_OUTLINE)
    # Eyes (blue-gray with heavy eyeliner)
    d.rectangle([head_cx - 4, head_cy - 2, head_cx - 2, head_cy], fill=DH_EYES)
    d.rectangle([head_cx + 2, head_cy - 2, head_cx + 4, head_cy], fill=DH_EYES)
    # Eyeliner (thick dark line above each eye)
    d.line([head_cx - 5, head_cy - 3, head_cx - 1, head_cy - 3], fill=DH_EYELINER)
    d.line([head_cx + 1, head_cy - 3, head_cx + 5, head_cy - 3], fill=DH_EYELINER)
    # Red lips
    mouth_open = p.get("mouth_open", False)
    if mouth_open:
        d.rectangle([head_cx - 2, head_cy + 3, head_cx + 2, head_cy + 5], fill=DH_LIPS)
        # Teeth hint
        d.line([head_cx - 1, head_cy + 3, head_cx + 1, head_cy + 3],
               fill=DH_STRIPE)
    else:
        d.line([head_cx - 2, head_cy + 3, head_cx + 2, head_cy + 3], fill=DH_LIPS)
        d.point([head_cx - 1, head_cy + 4], fill=DH_LIPS)
        d.point([head_cx + 1, head_cy + 4], fill=DH_LIPS)

    # -- Hair (short/choppy platinum blonde, iconic Blondie style) --
    hair_top = head_cy - head_h // 2 - 2
    # Top swept bangs / fringe
    for hair_x in range(-6, 7):
        base_x = head_cx + hair_x
        # Short choppy lengths
        if abs(hair_x) <= 2:
            # Center top — shorter bangs
            hair_len = random.randint(6, 10)
        elif abs(hair_x) <= 4:
            # Mid — medium bangs
            hair_len = random.randint(8, 14)
        else:
            # Sides — slightly longer, feathered
            hair_len = random.randint(12, 18)
        for j in range(hair_len):
            hy = hair_top + j
            # Choppy texture: slight random offset
            sway = int(math.sin(j * 0.4 + hair_x * 0.7) * 0.8)
            hx = base_x + sway
            if 0 <= hy < FH:
                if j < 3:
                    c = DH_HAIR_HIGHLIGHT
                elif j < hair_len * 0.6:
                    c = DH_HAIR
                else:
                    c = DH_HAIR_DARK
                d.point([hx, hy], fill=c)
    # Volumetric top (extra highlight pixels on crown)
    for tx in range(-4, 5):
        d.point([head_cx + tx, hair_top], fill=DH_HAIR_HIGHLIGHT)
        d.point([head_cx + tx, hair_top + 1], fill=DH_HAIR)

    return {
        "l_hand": (la_ex, la_ey),
        "r_hand": (ra_ex, ra_ey),
        "torso_cx": torso_cx,
        "shoulder_y": shoulder_y,
        "head_cx": head_cx,
        "head_cy": head_cy,
    }


def draw_handheld_mic(d, x, y, angle_deg=0):
    """Draw a handheld microphone (no stand, smaller than Joey's)."""
    handle_len = 10
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    # Handle
    for i in range(handle_len):
        px = x + int(i * sin_a)
        py = y - int(i * cos_a)
        c = MIC_CHROME if i % 3 < 2 else MIC_CHROME_LIGHT
        d.rectangle([px - 1, py, px, py], fill=c)

    # Mic head at top
    mic_x = x + int(handle_len * sin_a)
    mic_y = y - int(handle_len * cos_a)
    d.ellipse([mic_x - 2, mic_y - 3, mic_x + 2, mic_y + 2], fill=MIC_HEAD,
              outline=MIC_HEAD_RING)
    # Mesh dots
    d.point([mic_x - 1, mic_y - 1], fill=MIC_CHROME_DARK)
    d.point([mic_x + 1, mic_y], fill=MIC_CHROME_DARK)

    return (mic_x, mic_y)


def draw_glass_shard(d, x, y, size, alpha=200):
    """Draw a diamond-shaped glass shard (translucent cyan/white)."""
    half = max(1, size // 2)
    # Diamond shape via lines
    color = (*GLASS_CYAN[:3], alpha)
    highlight = (*GLASS_WHITE[:3], min(alpha + 30, 255))
    d.polygon([(x, y - half), (x + half, y), (x, y + half), (x - half, y)],
              fill=color, outline=highlight)
    # Central bright spot
    d.point([x, y], fill=highlight)


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


# ==============================================================================
#  Attack sheets -- from scratch
# ==============================================================================

def dh_heart_of_glass_sheet():
    """Arm extended, 3 glass shards spread outward from hand -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        cx = f * FW + FW // 2
        cy = FH // 2 + 5
        # Body leans forward progressively
        lean = 1 + f * 2
        pose = {"torso_lean": lean, "head_tilt": lean // 2,
                "l_arm_angle": -20 - f * 2, "r_arm_angle": -60 + f * 5,
                "leg_spread": 5 + f, "mouth_open": f >= 3}
        pts = draw_debbie_body(d, cx, cy, pose)
        # Mic in left hand (held casually at side)
        draw_handheld_mic(d, pts["l_hand"][0], pts["l_hand"][1], -20)
        # Glass shards emanate from right hand
        hand_x, hand_y = pts["r_hand"]
        if f >= 1:
            # 3 shards spreading in a fan pattern
            for s in range(3):
                # Spread angle: upper, middle, lower
                spread_angle = (-25 + s * 25) * math.pi / 180.0
                dist = 4 + (f - 1) * 6 + s * 2
                shard_x = hand_x + int(dist * math.cos(spread_angle))
                shard_y = hand_y + int(dist * math.sin(spread_angle))
                x_off = f * FW
                if x_off <= shard_x < x_off + FW and 0 <= shard_y < FH:
                    shard_size = 3 + f // 2
                    shard_alpha = max(80, 220 - f * 20)
                    draw_glass_shard(d, shard_x, shard_y, shard_size, shard_alpha)
            # Trailing sparkle dust behind shards
            for _ in range(f * 2):
                sx = hand_x + random.randint(0, max(1, f * 5))
                sy = hand_y + random.randint(-10, 10)
                x_off = f * FW
                if x_off <= sx < x_off + FW and 0 <= sy < FH:
                    d.point([sx, sy], fill=(*GLASS_WHITE[:3], 60 + random.randint(0, 40)))
    path = BOSS_DIR / "debbie_harry_heart_of_glass_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def dh_call_me_sheet():
    """Mic held high, radial burst rings expand from mic head -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        cx = f * FW + FW // 2
        cy = FH // 2 + 5
        # Power stance: legs spread, arms raising mic overhead
        pose = {"torso_lean": 0, "head_tilt": 0,
                "l_arm_angle": -40 - f * 8, "r_arm_angle": -40 - f * 8,
                "leg_spread": 8 + f, "mouth_open": True}
        pts = draw_debbie_body(d, cx, cy, pose)
        # Mic held high with right hand (above head on later frames)
        mic_angle = -70 - f * 5
        mic_x = pts["r_hand"][0]
        mic_y = pts["r_hand"][1]
        mic_top = draw_handheld_mic(d, mic_x, mic_y, mic_angle)
        # Radial burst rings expanding from mic head
        if f >= 1:
            ring_cx, ring_cy = mic_top
            num_rings = 1 + f
            max_r = 5 + f * 8
            for i in range(num_rings):
                t = (i + 1) / num_rings
                r = int(max_r * t)
                alpha = max(25, int(200 * (1 - t)))
                # Concentric circles (true circles for radial burst)
                color = (*SOUND_RING[:3], alpha)
                d.ellipse([ring_cx - r, ring_cy - r, ring_cx + r, ring_cy + r],
                          outline=color, width=1)
            # Bright flash at mic head on peak frames
            if f >= 3:
                glow_r = 2 + (f - 3) * 2
                d.ellipse([ring_cx - glow_r, ring_cy - glow_r,
                           ring_cx + glow_r, ring_cy + glow_r],
                          fill=(*FLASH_WHITE[:3], 60 + f * 15))
        # Energy particles around body during later frames
        if f >= 3:
            x_off = f * FW
            for _ in range(f * 2):
                px = cx + random.randint(-14, 14)
                py = cy + random.randint(-22, 18)
                if x_off <= px < x_off + FW and 0 <= py < FH:
                    d.point([px, py], fill=ENERGY_SPARK)
    path = BOSS_DIR / "debbie_harry_call_me_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def dh_one_way_sheet():
    """Charging forward, arm pointing ahead, speed lines behind -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        cx = f * FW + FW // 2
        cy = FH // 2 + 5
        # Aggressive forward lean increasing each frame
        lean = 2 + f * 3
        # Right arm pointing forward, left arm trailing back
        pose = {"torso_lean": lean, "head_tilt": lean // 3,
                "l_arm_angle": 30 + f * 8,
                "r_arm_angle": -70 + f * 3,
                "leg_spread": 4 + f * 2,
                "mouth_open": f >= 2}
        pts = draw_debbie_body(d, cx, cy, pose)
        # Mic in right hand pointing forward like a weapon
        draw_handheld_mic(d, pts["r_hand"][0], pts["r_hand"][1], 60 + lean)
        # Speed lines behind her (increasing density)
        if f >= 1:
            x_off = f * FW
            num_lines = 3 + f * 2
            for _ in range(num_lines):
                sx = cx - 10 - random.randint(0, 8)
                sy = cy + random.randint(-18, 18)
                line_len = random.randint(6, 14 + f * 2)
                ex = sx - line_len
                if x_off <= ex and sx < x_off + FW and 0 <= sy < FH:
                    alpha = 50 + f * 15
                    d.line([sx, sy, ex, sy], fill=(*SPEED_LINE, min(alpha, 200)), width=1)
            # Motion blur trailing the body
            if f >= 3:
                for _ in range(f * 3):
                    bx = cx - random.randint(8, 18)
                    by = cy + random.randint(-15, 15)
                    if x_off <= bx < x_off + FW and 0 <= by < FH:
                        d.point([bx, by], fill=(*MOTION_BLUR, 30 + f * 10))
    path = BOSS_DIR / "debbie_harry_one_way_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def dh_rapture_sheet():
    """Arms spread wide, horizontal wave emanates forward -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5
        # Trance-like pose: arms spreading wider each frame
        arm_spread = 50 + f * 10
        pose = {"torso_lean": 0, "head_tilt": 0,
                "l_arm_angle": -arm_spread, "r_arm_angle": arm_spread,
                "leg_spread": 5, "mouth_open": f >= 2}
        pts = draw_debbie_body(d, cx, cy, pose)
        # Mic dangling loosely from right hand
        draw_handheld_mic(d, pts["r_hand"][0], pts["r_hand"][1], 10)
        # Horizontal wave: vertical lines moving rightward
        if f >= 1:
            num_waves = 2 + f * 3
            for w in range(num_waves):
                wave_dist = 6 + w * 3
                wave_x = cx + wave_dist
                if wave_x < x_off + FW:
                    wave_top = cy - 12 - f * 2
                    wave_bot = cy + 12 + f * 2
                    alpha = max(20, 180 - w * 15)
                    # Wave line color: mystical purple-blue
                    wave_color = (160, 120, 240, alpha)
                    d.line([wave_x, wave_top, wave_x, wave_bot],
                           fill=wave_color, width=1)
                    # Wavy distortion: offset alternating pixels
                    if w % 2 == 0:
                        third = (wave_bot - wave_top) // 3
                        d.point([wave_x + 1, wave_top + third], fill=wave_color)
                        d.point([wave_x - 1, wave_top + 2 * third], fill=wave_color)
            # Mystical glow around hands
            for hand_pos in [pts["l_hand"], pts["r_hand"]]:
                hx, hy = hand_pos
                if x_off <= hx < x_off + FW and 0 <= hy < FH:
                    glow_r = 2 + f
                    d.ellipse([hx - glow_r, hy - glow_r,
                               hx + glow_r, hy + glow_r],
                              fill=(*TELEPORT_GLOW[:3], 30 + f * 10))
        # Ambient particles during trance
        if f >= 2:
            for _ in range(f * 2):
                px = cx + random.randint(-16, 16)
                py = cy + random.randint(-25, 20)
                if x_off <= px < x_off + FW and 0 <= py < FH:
                    d.point([px, py], fill=(*WAVE_LINE, 40 + random.randint(0, 40)))
    path = BOSS_DIR / "debbie_harry_rapture_sheet.png"
    img.save(path)
    print(f"  [OK] {path.name}")


def dh_atomic_sheet():
    """Teleport flash: fade out -> bright flash -> reappear with explosion -- 6 frames."""
    nf = 6
    img = Image.new("RGBA", (FW * nf, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Reappear offset (shifted right and slightly up from original position)
    reappear_shift_x = 8
    reappear_shift_y = -3

    for f in range(nf):
        x_off = f * FW
        cx = x_off + FW // 2
        cy = FH // 2 + 5

        if f <= 1:
            # Frames 0-1: body fading / dissolving
            pose = {"torso_lean": 0, "head_tilt": 0,
                    "l_arm_angle": -30 + f * 10, "r_arm_angle": 30 - f * 10,
                    "leg_spread": 5}
            draw_debbie_body(d, cx, cy, pose)
            draw_handheld_mic(d, cx - 7, cy + 2, -15)
            # Dissolve effect: scatter pixels outward with fading
            dissolve_intensity = (f + 1) * 12
            for _ in range(dissolve_intensity):
                dx = cx + random.randint(-14, 14)
                dy = cy + random.randint(-22, 22)
                if x_off <= dx < x_off + FW and 0 <= dy < FH:
                    r0, g0, b0, a0 = img.getpixel((dx, dy))
                    if a0 > 0:
                        # Fade alpha and shift color toward white
                        new_a = max(0, a0 - 40 - f * 50)
                        new_r = min(r0 + 40 + f * 30, 255)
                        new_g = min(g0 + 35 + f * 25, 255)
                        new_b = min(b0 + 50 + f * 35, 255)
                        img.putpixel((dx, dy), (new_r, new_g, new_b, new_a))
            # Scatter particles flying outward
            for _ in range(8 + f * 10):
                px = cx + random.randint(-18, 18)
                py = cy + random.randint(-26, 26)
                if x_off <= px < x_off + FW and 0 <= py < FH:
                    d.point([px, py], fill=(*TELEPORT_GLOW[:3], 40 + f * 30))

        elif f <= 3:
            # Frames 2-3: bright flash at original position
            flash_intensity = 200 if f == 2 else 140
            # Central bright glow
            for ring_r in range(2, 20, 2):
                alpha = max(15, flash_intensity - ring_r * 10)
                d.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
                          fill=(*FLASH_WHITE[:3], alpha))
            # Radial burst lines from center
            num_rays = 8 + (f - 2) * 4
            for i in range(num_rays):
                angle = (2 * math.pi * i) / num_rays
                ray_len = random.randint(10, 22)
                rx = cx + int(ray_len * math.cos(angle))
                ry = cy + int(ray_len * math.sin(angle))
                alpha = max(40, flash_intensity - 30)
                if x_off <= rx < x_off + FW and 0 <= ry < FH:
                    d.line([cx, cy, rx, ry],
                           fill=(*FLASH_WHITE[:3], alpha), width=1)
            # Scatter sparks
            for _ in range(15):
                sx = cx + random.randint(-20, 20)
                sy = cy + random.randint(-25, 25)
                if x_off <= sx < x_off + FW and 0 <= sy < FH:
                    spark_color = random.choice([ENERGY_SPARK, GLASS_WHITE,
                                                 TELEPORT_GLOW])
                    d.point([sx, sy], fill=(*spark_color[:3], 120 + random.randint(0, 80)))

        else:
            # Frames 4-5: reappearing at shifted position with explosive particles
            new_cx = cx + reappear_shift_x
            new_cy = cy + reappear_shift_y
            reappear_alpha_mult = 0.6 if f == 4 else 1.0
            pose = {"torso_lean": -2 + (f - 4) * 2, "head_tilt": 0,
                    "l_arm_angle": -50 + (f - 4) * 20,
                    "r_arm_angle": 50 - (f - 4) * 20,
                    "leg_spread": 7 - (f - 4) * 2}
            draw_debbie_body(d, new_cx, new_cy, pose)
            draw_handheld_mic(d, new_cx - 7, new_cy + 2, -15)
            # Fade-in effect on frame 4
            if f == 4:
                for dy in range(FH):
                    for dx in range(x_off, x_off + FW):
                        if 0 <= dx < img.width:
                            r0, g0, b0, a0 = img.getpixel((dx, dy))
                            if a0 > 0:
                                img.putpixel((dx, dy), (min(r0 + 20, 255),
                                                          min(g0 + 15, 255),
                                                          min(b0 + 25, 255),
                                                          int(a0 * reappear_alpha_mult)))
            # Explosive particle spread around reappear location
            num_particles = 20 if f == 4 else 10
            for _ in range(num_particles):
                px = new_cx + random.randint(-18, 18)
                py = new_cy + random.randint(-24, 24)
                if x_off <= px < x_off + FW and 0 <= py < FH:
                    # Mix of sparkles and teleport glow
                    if random.random() < 0.5:
                        d.point([px, py], fill=(*ENERGY_SPARK[:3],
                                                  80 + random.randint(0, 80)))
                    else:
                        d.point([px, py], fill=(*TELEPORT_GLOW[:3],
                                                  60 + random.randint(0, 60)))
            # Small flash remnant at original position
            if f == 4:
                orig_cx = cx
                for ring_r in range(2, 8, 2):
                    alpha = max(10, 60 - ring_r * 8)
                    d.ellipse([orig_cx - ring_r, cy - ring_r,
                               orig_cx + ring_r, cy + ring_r],
                              fill=(*TELEPORT_GLOW[:3], alpha))

    path = BOSS_DIR / "debbie_harry_atomic_sheet.png"
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
            print(f"  [SKIP] {src_name} -- not found")
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


# ==============================================================================
#  Main
# ==============================================================================

def main():
    print("Generating Debbie Harry boss sprites (Level 04 -- Blondie Concert at CBGB)...")

    # -- Palette-swap from Disco King --
    print("\nDebbie Harry -- palette-swap (from Disco King):")
    swap_boss_sheets(remap_debbie_harry, "debbie_harry")

    # -- From-scratch attack sheets --
    print("\nDebbie Harry -- from-scratch attacks:")
    dh_heart_of_glass_sheet()
    dh_call_me_sheet()
    dh_one_way_sheet()
    dh_rapture_sheet()
    dh_atomic_sheet()

    print("\nDone! 8 Debbie Harry boss sprites generated.")


if __name__ == "__main__":
    main()
