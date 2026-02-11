#!/usr/bin/env python3
"""Generate Bee Gees Disco Floor parallax backgrounds for Disco Cop Level 05.

Creates 3 parallax layers at 640x360:
  - parallax_disco_floor_sky.png  (far)  -- dark venue ceiling, spinning mirror ball
                                            with faceted surface, colored light beams,
                                            spotlights, sparkle reflections, rafters
  - parallax_disco_floor_mid.png  (mid)  -- speaker stacks, DJ booth silhouette,
                                            VIP rope posts with velvet rope,
                                            neon "DISCO" sign with glow
  - parallax_disco_floor_near.png (near) -- illuminated dance floor tiles,
                                            disco fog/haze, scattered cups/bottles

Usage:
    python create_disco_floor_parallax.py
"""

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "environment"

W, H = 640, 360
random.seed(815)

# ── Ceiling / sky palette ──
CEILING_TOP = (8, 5, 15)
CEILING_BOT = (18, 12, 30)
RAFTER_DARK = (12, 8, 20)
RAFTER_LIGHT = (22, 16, 35)
RAFTER_BOLT = (60, 55, 70)

# ── Mirror ball ──
BALL_SILVER = (180, 185, 195)
BALL_HIGHLIGHT = (240, 245, 255)
BALL_DARK_FACET = (100, 105, 115)
BALL_FRAME = (70, 72, 80)

# ── Light beams & spots ──
BEAM_PINK = (255, 100, 150)
BEAM_BLUE = (100, 150, 255)
BEAM_GOLD = (255, 220, 100)
BEAM_WHITE = (240, 240, 255)
SPARKLE_WHITE = (250, 250, 255)
SPARKLE_GOLD = (255, 230, 140)

# ── Speakers ──
SPEAKER_BLACK = (15, 15, 18)
SPEAKER_BODY = (22, 22, 26)
SPEAKER_CONE = (30, 30, 35)
SPEAKER_DUST_CAP = (20, 20, 24)
SPEAKER_CHROME = (160, 165, 175)
SPEAKER_CHROME_DARK = (110, 112, 120)

# ── DJ booth ──
DJ_BOOTH_DARK = (25, 20, 30)
DJ_BOOTH_MID = (35, 28, 42)
DJ_BOOTH_PANEL = (30, 25, 36)
DJ_SILHOUETTE = (18, 14, 22)
LED_RED = (255, 40, 40)
LED_GREEN = (40, 255, 60)
LED_BLUE = (60, 80, 255)
LED_AMBER = (255, 180, 40)
TURNTABLE_DARK = (20, 18, 24)
TURNTABLE_PLATTER = (40, 38, 45)
TURNTABLE_LABEL = (180, 50, 50)

# ── VIP ropes ──
ROPE_POST_GOLD = (200, 170, 60)
ROPE_POST_HIGHLIGHT = (230, 200, 90)
ROPE_POST_DARK = (150, 125, 40)
VELVET_RED = (160, 30, 40)
VELVET_HIGHLIGHT = (190, 50, 60)
VELVET_DARK = (120, 20, 30)

# ── Neon sign ──
NEON_MAGENTA = (255, 50, 200)
NEON_CYAN = (50, 220, 255)
NEON_YELLOW = (255, 240, 50)
NEON_GLOW_MAGENTA = (200, 30, 160)

# ── Floor tiles ──
TILE_PURPLE = (140, 40, 160)
TILE_PURPLE_BRIGHT = (170, 60, 190)
TILE_CYAN = (40, 130, 160)
TILE_CYAN_BRIGHT = (60, 160, 190)
TILE_MAGENTA = (160, 40, 100)
TILE_MAGENTA_BRIGHT = (190, 60, 130)
TILE_BLUE = (50, 50, 180)
TILE_BLUE_BRIGHT = (70, 70, 210)
TILE_WHITE_CENTER = (220, 220, 235)

# ── Fog ──
FOG_COLOR = (200, 200, 210)

# ── Scattered debris ──
CUP_RED = (180, 30, 30)
CUP_RED_DARK = (140, 20, 20)
GLASS_CLEAR = (180, 190, 200)
GLASS_HIGHLIGHT = (220, 225, 240)
BOTTLE_DARK = (30, 80, 40)
BOTTLE_LABEL = (200, 195, 180)
STRAW_PINK = (220, 100, 130)


def create_sky_layer():
    """Far: dark venue ceiling with spinning mirror ball, light beams, spots, sparkles."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    # ── Dark ceiling gradient ──
    for y in range(H):
        t = y / H
        r = int(CEILING_TOP[0] * (1 - t) + CEILING_BOT[0] * t)
        g = int(CEILING_TOP[1] * (1 - t) + CEILING_BOT[1] * t)
        b = int(CEILING_TOP[2] * (1 - t) + CEILING_BOT[2] * t)
        d.line([0, y, W - 1, y], fill=(r, g, b, 255))

    # ── Ceiling rafters / structural beams ──
    for rx in range(0, W, 80):
        # Vertical beam
        d.rectangle([rx, 0, rx + 4, 60], fill=RAFTER_DARK)
        d.line([rx, 0, rx, 60], fill=RAFTER_LIGHT)
        # Bolt dots at joints
        d.point([rx + 2, 15], fill=RAFTER_BOLT)
        d.point([rx + 2, 45], fill=RAFTER_BOLT)
    # Horizontal beam across top
    d.rectangle([0, 55, W - 1, 62], fill=RAFTER_DARK)
    d.line([0, 56, W - 1, 56], fill=RAFTER_LIGHT)
    d.line([0, 61, W - 1, 61], fill=RAFTER_LIGHT)

    # ── Colored spotlights from ceiling edges ──
    # Each spotlight is a cone of colored light fading downward
    spotlight_defs = [
        (40, 0, BEAM_PINK, 0.5, 35),       # left edge, pink
        (160, 0, BEAM_BLUE, 0.45, 30),      # left-center, blue
        (480, 0, BEAM_GOLD, 0.5, 32),       # right-center, gold
        (600, 0, BEAM_PINK, 0.4, 28),       # right edge, pink
        (100, 0, BEAM_GOLD, 0.35, 25),      # extra
        (540, 0, BEAM_BLUE, 0.42, 30),      # extra
    ]
    for sx, sy, color, intensity, spread_rate in spotlight_defs:
        # Draw cone from top toward bottom
        for dist in range(1, 200):
            t = dist / 200.0
            alpha = max(2, int(intensity * 30 * (1 - t)))
            cone_y = sy + dist
            half_spread = int(dist * spread_rate)
            if cone_y >= H:
                break
            for lx in range(sx - half_spread, sx + half_spread + 1):
                if 0 <= lx < W:
                    # Fade at edges of cone
                    edge_dist = abs(lx - sx) / max(half_spread, 1)
                    edge_fade = max(0.0, 1.0 - edge_dist)
                    a = int(alpha * edge_fade)
                    if a < 1:
                        continue
                    r0, g0, b0, _ = img.getpixel((lx, cone_y))
                    nr = min(r0 + int(color[0] * a / 255), 255)
                    ng = min(g0 + int(color[1] * a / 255), 255)
                    nb = min(b0 + int(color[2] * a / 255), 255)
                    img.putpixel((lx, cone_y), (nr, ng, nb, 255))

    # ── Light beam radials from mirror ball (draw BEFORE ball so ball sits on top) ──
    ball_cx, ball_cy = W // 2, 55
    beam_colors = [BEAM_PINK, BEAM_BLUE, BEAM_GOLD, BEAM_WHITE, BEAM_PINK, BEAM_BLUE]
    num_beams = 18
    for i in range(num_beams):
        angle = (i * 360 / num_beams) + random.uniform(-5, 5)
        rad = math.radians(angle)
        color = beam_colors[i % len(beam_colors)]
        beam_len = random.randint(120, 220)
        # Draw beam as a series of points with decreasing alpha
        for dist in range(25, beam_len):
            t = (dist - 25) / (beam_len - 25)
            alpha = max(2, int(22 * (1 - t * t)))
            px = int(ball_cx + dist * math.cos(rad))
            py = int(ball_cy + dist * math.sin(rad))
            if 0 <= px < W and 0 <= py < H:
                r0, g0, b0, _ = img.getpixel((px, py))
                nr = min(r0 + int(color[0] * alpha / 255), 255)
                ng = min(g0 + int(color[1] * alpha / 255), 255)
                nb = min(b0 + int(color[2] * alpha / 255), 255)
                img.putpixel((px, py), (nr, ng, nb, 255))
            # Slight width: one pixel on each side for thicker beams near center
            if dist < 80:
                for offset in [-1, 1]:
                    ox = int(ball_cx + dist * math.cos(rad) + offset * math.sin(rad))
                    oy = int(ball_cy + dist * math.sin(rad) - offset * math.cos(rad))
                    if 0 <= ox < W and 0 <= oy < H:
                        r0, g0, b0, _ = img.getpixel((ox, oy))
                        a2 = alpha // 2
                        nr = min(r0 + int(color[0] * a2 / 255), 255)
                        ng = min(g0 + int(color[1] * a2 / 255), 255)
                        nb = min(b0 + int(color[2] * a2 / 255), 255)
                        img.putpixel((ox, oy), (nr, ng, nb, 255))

    # ── Mirror ball (center-top) ──
    ball_r = 20
    # Hanging wire/chain
    d.line([ball_cx, 0, ball_cx, ball_cy - ball_r], fill=BALL_FRAME, width=1)
    # Ball base circle (dark)
    d.ellipse([ball_cx - ball_r, ball_cy - ball_r,
               ball_cx + ball_r, ball_cy + ball_r], fill=BALL_DARK_FACET)
    # Faceted surface: grid of small rectangles mapped onto sphere
    facet_size = 4
    for fy in range(-ball_r + 1, ball_r, facet_size):
        for fx in range(-ball_r + 1, ball_r, facet_size):
            # Check if this facet is within the sphere
            dist_sq = fx * fx + fy * fy
            if dist_sq > ball_r * ball_r:
                continue
            # Sphere shading: brighter toward upper-left (light source)
            norm_x = fx / ball_r
            norm_y = fy / ball_r
            # Simple diffuse: light from upper-left
            light = max(0.0, -0.5 * norm_x - 0.6 * norm_y + 0.3)
            # Alternating brightness pattern for facets
            facet_row = (fy + ball_r) // facet_size
            facet_col = (fx + ball_r) // facet_size
            is_bright = (facet_row + facet_col) % 2 == 0
            if is_bright:
                base = BALL_SILVER
            else:
                base = BALL_DARK_FACET
            # Apply sphere lighting
            brightness = 0.4 + 0.6 * light
            r = min(int(base[0] * brightness), 255)
            g = min(int(base[1] * brightness), 255)
            b = min(int(base[2] * brightness), 255)
            # Specular highlight on some facets
            if light > 0.7 and is_bright:
                r = min(r + 60, 255)
                g = min(g + 60, 255)
                b = min(b + 65, 255)
            px1 = ball_cx + fx
            py1 = ball_cy + fy
            px2 = min(ball_cx + fx + facet_size - 1, ball_cx + ball_r)
            py2 = min(ball_cy + fy + facet_size - 1, ball_cy + ball_r)
            d.rectangle([px1, py1, px2, py2], fill=(r, g, b, 255))
    # Re-clip to sphere shape by clearing pixels outside radius
    for yy in range(ball_cy - ball_r - 1, ball_cy + ball_r + 2):
        for xx in range(ball_cx - ball_r - 1, ball_cx + ball_r + 2):
            if 0 <= xx < W and 0 <= yy < H:
                dx = xx - ball_cx
                dy = yy - ball_cy
                if dx * dx + dy * dy > ball_r * ball_r:
                    continue  # outside handled by original background
    # Bright specular spot
    spec_x = ball_cx - 6
    spec_y = ball_cy - 7
    d.rectangle([spec_x, spec_y, spec_x + 3, spec_y + 3], fill=BALL_HIGHLIGHT)
    d.point([spec_x + 1, spec_y - 1], fill=BALL_HIGHLIGHT)

    # ── Mirror ball glow halo ──
    for ring in range(1, 12):
        alpha = max(3, 35 - ring * 3)
        for angle in range(0, 360, 2):
            rad = math.radians(angle)
            px = ball_cx + int((ball_r + ring * 2.5) * math.cos(rad))
            py = ball_cy + int((ball_r + ring * 2.5) * math.sin(rad))
            if 0 <= px < W and 0 <= py < H:
                r0, g0, b0, _ = img.getpixel((px, py))
                nr = min(r0 + alpha, 255)
                ng = min(g0 + alpha, 255)
                nb = min(b0 + alpha + 2, 255)
                img.putpixel((px, py), (nr, ng, min(nb, 255), 255))

    # ── Sparkle / star field (mirror ball reflections scattered everywhere) ──
    for _ in range(250):
        sx = random.randint(0, W - 1)
        sy = random.randint(0, H - 1)
        bright = random.randint(140, 255)
        sparkle_c = random.choice([SPARKLE_WHITE, SPARKLE_GOLD])
        r0, g0, b0, _ = img.getpixel((sx, sy))
        blend = random.uniform(0.3, 0.7)
        nr = min(int(r0 * (1 - blend) + sparkle_c[0] * blend), 255)
        ng = min(int(g0 * (1 - blend) + sparkle_c[1] * blend), 255)
        nb = min(int(b0 * (1 - blend) + sparkle_c[2] * blend), 255)
        img.putpixel((sx, sy), (nr, ng, nb, 255))
        # Some sparkles get a small cross pattern
        if random.random() < 0.15:
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ax, ay = sx + ox, sy + oy
                if 0 <= ax < W and 0 <= ay < H:
                    r0, g0, b0, _ = img.getpixel((ax, ay))
                    a2 = int(bright * 0.3)
                    nr = min(r0 + a2, 255)
                    ng = min(g0 + a2, 255)
                    nb = min(b0 + a2, 255)
                    img.putpixel((ax, ay), (nr, ng, nb, 255))

    # ── Spotlight fixture shapes at ceiling edges ──
    fixture_positions = [40, 160, 480, 540, 600]
    for fx in fixture_positions:
        # Small housing rectangle
        d.rectangle([fx - 5, 0, fx + 5, 6], fill=(40, 38, 48))
        d.rectangle([fx - 3, 6, fx + 3, 10], fill=(55, 52, 62))
        # Lens glow dot
        d.point([fx, 10], fill=(200, 200, 210))

    out = OUTPUT_DIR / "parallax_disco_floor_sky.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def draw_speaker_stack(d, x, y_bottom, count=3):
    """Draw a stack of speakers at position x, sitting on y_bottom."""
    cab_w = 40
    cab_h = 32
    for i in range(count):
        cy = y_bottom - (i + 1) * cab_h
        # Cabinet body
        d.rectangle([x, cy, x + cab_w, cy + cab_h], fill=SPEAKER_BLACK)
        d.rectangle([x + 1, cy + 1, x + cab_w - 1, cy + cab_h - 1],
                     fill=SPEAKER_BODY)
        # Chrome trim at edges
        d.line([x, cy, x + cab_w, cy], fill=SPEAKER_CHROME, width=1)
        d.line([x, cy + cab_h, x + cab_w, cy + cab_h], fill=SPEAKER_CHROME_DARK)
        d.line([x, cy, x, cy + cab_h], fill=SPEAKER_CHROME_DARK)
        d.line([x + cab_w, cy, x + cab_w, cy + cab_h], fill=SPEAKER_CHROME_DARK)
        # Speaker cone (large circle)
        cone_cx = x + cab_w // 2
        cone_cy = cy + cab_h // 2
        cone_r = 11
        d.ellipse([cone_cx - cone_r, cone_cy - cone_r,
                    cone_cx + cone_r, cone_cy + cone_r],
                   fill=SPEAKER_CONE, outline=SPEAKER_BLACK)
        # Inner cone ring
        inner_r = 7
        d.ellipse([cone_cx - inner_r, cone_cy - inner_r,
                    cone_cx + inner_r, cone_cy + inner_r],
                   fill=SPEAKER_BLACK, outline=SPEAKER_CONE)
        # Dust cap (center circle)
        cap_r = 3
        d.ellipse([cone_cx - cap_r, cone_cy - cap_r,
                    cone_cx + cap_r, cone_cy + cap_r],
                   fill=SPEAKER_DUST_CAP)
        # Corner bolts
        for bx, by in [(x + 3, cy + 3), (x + cab_w - 3, cy + 3),
                        (x + 3, cy + cab_h - 3), (x + cab_w - 3, cy + cab_h - 3)]:
            d.point([bx, by], fill=SPEAKER_CHROME)


def draw_rope_post(d, x, y_bottom, height=35):
    """Draw a brass/gold VIP stanchion post."""
    post_w = 5
    # Base plate
    d.rectangle([x - 4, y_bottom - 3, x + post_w + 3, y_bottom],
                fill=ROPE_POST_DARK)
    d.ellipse([x - 3, y_bottom - 5, x + post_w + 2, y_bottom - 1],
              fill=ROPE_POST_GOLD)
    # Pole
    d.rectangle([x, y_bottom - height, x + post_w - 1, y_bottom - 3],
                fill=ROPE_POST_GOLD)
    # Highlight stripe along pole
    d.line([x + 1, y_bottom - height + 2, x + 1, y_bottom - 5],
           fill=ROPE_POST_HIGHLIGHT)
    # Top finial (ball)
    top_y = y_bottom - height
    d.ellipse([x - 1, top_y - 5, x + post_w, top_y + 1],
              fill=ROPE_POST_HIGHLIGHT)
    d.point([x + 1, top_y - 3], fill=(255, 240, 140))  # glint


def draw_velvet_rope(d, x1, x2, y, sag=8):
    """Draw a velvet rope (catenary curve) between two x positions at height y."""
    mid_x = (x1 + x2) / 2.0
    half_span = (x2 - x1) / 2.0
    for px in range(x1, x2 + 1):
        # Catenary approximation: y = sag * (((x-mid)/half_span)^2)
        t = (px - mid_x) / half_span if half_span > 0 else 0
        rope_y = int(y + sag * t * t)
        # Draw rope thickness (3 pixels tall)
        for ry in range(rope_y - 1, rope_y + 2):
            if 0 <= px < W and 0 <= ry < H:
                if ry == rope_y - 1:
                    d.point([px, ry], fill=VELVET_HIGHLIGHT)
                elif ry == rope_y:
                    d.point([px, ry], fill=VELVET_RED)
                else:
                    d.point([px, ry], fill=VELVET_DARK)
    # Tassel/attachment points at ends
    for ex in [x1, x2]:
        d.rectangle([ex, y - 2, ex + 2, y + 3], fill=ROPE_POST_GOLD)


def create_mid_layer():
    """Mid: speaker stacks, DJ booth, VIP rope posts, neon DISCO sign."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    ground_y = 300

    # ── Speaker stacks (left side) ──
    draw_speaker_stack(d, 10, ground_y, count=3)
    draw_speaker_stack(d, 55, ground_y, count=2)

    # ── Speaker stacks (right side) ──
    draw_speaker_stack(d, 585, ground_y, count=3)
    draw_speaker_stack(d, 540, ground_y, count=2)

    # ── DJ booth (center-back) ──
    booth_x = 250
    booth_w = 140
    booth_y = ground_y - 55  # elevated platform
    booth_h = 55

    # Platform / stage riser
    d.rectangle([booth_x - 10, booth_y + booth_h - 8,
                 booth_x + booth_w + 10, ground_y], fill=(20, 16, 25))
    # Platform front face
    d.rectangle([booth_x - 10, ground_y - 8,
                 booth_x + booth_w + 10, ground_y], fill=(28, 22, 34))
    # Platform edge highlight
    d.line([booth_x - 10, ground_y - 8, booth_x + booth_w + 10, ground_y - 8],
           fill=(45, 38, 55))

    # Booth desk/console
    d.rectangle([booth_x, booth_y + 10, booth_x + booth_w, booth_y + booth_h],
                fill=DJ_BOOTH_DARK)
    d.rectangle([booth_x + 2, booth_y + 12, booth_x + booth_w - 2, booth_y + booth_h - 2],
                fill=DJ_BOOTH_MID)
    # Front panel with equipment
    d.rectangle([booth_x + 5, booth_y + booth_h - 18,
                 booth_x + booth_w - 5, booth_y + booth_h - 3],
                fill=DJ_BOOTH_PANEL)

    # LED dots on front panel
    led_colors = [LED_RED, LED_GREEN, LED_BLUE, LED_AMBER, LED_RED,
                  LED_GREEN, LED_BLUE, LED_AMBER, LED_RED, LED_GREEN]
    for i, lc in enumerate(led_colors):
        lx = booth_x + 12 + i * 12
        ly = booth_y + booth_h - 12
        d.point([lx, ly], fill=lc)
        d.point([lx, ly + 4], fill=random.choice(led_colors))
    # Second row of LEDs (mixer level indicators)
    for i in range(14):
        lx = booth_x + 10 + i * 9
        ly = booth_y + booth_h - 7
        # VU-meter style: green at bottom, red at top
        bar_height = random.randint(1, 5)
        for bh in range(bar_height):
            bc = LED_GREEN if bh < 3 else (LED_AMBER if bh < 4 else LED_RED)
            if booth_y + booth_h - 7 - bh > booth_y + booth_h - 18:
                d.point([lx, ly - bh], fill=bc)

    # Turntables (two circles on desk surface)
    for tt_offset in [25, 95]:
        tt_cx = booth_x + tt_offset
        tt_cy = booth_y + 28
        tt_r = 14
        # Platter
        d.ellipse([tt_cx - tt_r, tt_cy - tt_r, tt_cx + tt_r, tt_cy + tt_r],
                   fill=TURNTABLE_DARK)
        d.ellipse([tt_cx - tt_r + 2, tt_cy - tt_r + 2,
                    tt_cx + tt_r - 2, tt_cy + tt_r - 2],
                   fill=TURNTABLE_PLATTER)
        # Record grooves (concentric rings)
        for gr in range(3, tt_r - 2, 2):
            d.ellipse([tt_cx - gr, tt_cy - gr, tt_cx + gr, tt_cy + gr],
                       outline=TURNTABLE_DARK)
        # Center label
        label_r = 4
        d.ellipse([tt_cx - label_r, tt_cy - label_r,
                    tt_cx + label_r, tt_cy + label_r],
                   fill=TURNTABLE_LABEL)
        # Spindle dot
        d.point([tt_cx, tt_cy], fill=(60, 60, 65))
        # Tonearm (line from edge)
        arm_x = tt_cx + tt_r - 2
        arm_y = tt_cy - tt_r + 2
        d.line([arm_x, arm_y, arm_x + 8, arm_y - 6], fill=SPEAKER_CHROME, width=1)
        d.line([arm_x + 8, arm_y - 6, arm_x + 10, arm_y - 4],
               fill=SPEAKER_CHROME, width=1)

    # Mixer between turntables (center section)
    mixer_x = booth_x + 50
    mixer_y = booth_y + 18
    d.rectangle([mixer_x, mixer_y, mixer_x + 40, mixer_y + 25],
                fill=(32, 28, 38))
    # Fader slots
    for fi in range(5):
        fx = mixer_x + 5 + fi * 7
        d.line([fx, mixer_y + 4, fx, mixer_y + 20], fill=(45, 40, 52))
        # Fader knob
        fk_y = mixer_y + random.randint(6, 16)
        d.rectangle([fx - 1, fk_y, fx + 1, fk_y + 3], fill=SPEAKER_CHROME)

    # DJ silhouette figure (behind booth)
    dj_cx = booth_x + booth_w // 2
    dj_head_y = booth_y - 10
    # Head (circle)
    d.ellipse([dj_cx - 6, dj_head_y - 10, dj_cx + 6, dj_head_y + 2],
              fill=DJ_SILHOUETTE)
    # Headphones arc
    d.arc([dj_cx - 8, dj_head_y - 12, dj_cx + 8, dj_head_y + 2],
          start=200, end=340, fill=(40, 36, 48), width=2)
    # Headphone ear pads
    d.rectangle([dj_cx - 9, dj_head_y - 5, dj_cx - 7, dj_head_y + 1],
                fill=(45, 40, 50))
    d.rectangle([dj_cx + 7, dj_head_y - 5, dj_cx + 9, dj_head_y + 1],
                fill=(45, 40, 50))
    # Torso
    d.polygon([(dj_cx - 10, dj_head_y + 2), (dj_cx + 10, dj_head_y + 2),
               (dj_cx + 14, booth_y + 12), (dj_cx - 14, booth_y + 12)],
              fill=DJ_SILHOUETTE)
    # Arms reaching toward turntables
    d.line([dj_cx - 10, dj_head_y + 8, dj_cx - 25, booth_y + 20],
           fill=DJ_SILHOUETTE, width=3)
    d.line([dj_cx + 10, dj_head_y + 8, dj_cx + 25, booth_y + 20],
           fill=DJ_SILHOUETTE, width=3)

    # ── VIP rope posts and ropes ──
    # Left side group
    rope_posts_left = [120, 170, 220]
    post_top_y = ground_y - 35
    for px in rope_posts_left:
        draw_rope_post(d, px, ground_y, height=35)
    # Ropes between left posts
    for i in range(len(rope_posts_left) - 1):
        x1 = rope_posts_left[i] + 3
        x2 = rope_posts_left[i + 1] + 2
        draw_velvet_rope(d, x1, x2, post_top_y, sag=6)

    # Right side group
    rope_posts_right = [420, 470, 520]
    for px in rope_posts_right:
        draw_rope_post(d, px, ground_y, height=35)
    for i in range(len(rope_posts_right) - 1):
        x1 = rope_posts_right[i] + 3
        x2 = rope_posts_right[i + 1] + 2
        draw_velvet_rope(d, x1, x2, post_top_y, sag=6)

    # ── Neon "DISCO" sign (above DJ booth) ──
    sign_x = 275
    sign_y = 170
    letter_w = 16
    letter_h = 22
    letter_gap = 3
    sign_colors = [NEON_MAGENTA, NEON_CYAN, NEON_YELLOW, NEON_MAGENTA, NEON_CYAN]
    # Background panel (dark)
    total_w = 5 * letter_w + 4 * letter_gap
    d.rectangle([sign_x - 5, sign_y - 5, sign_x + total_w + 5, sign_y + letter_h + 5],
                fill=(15, 10, 20, 200))

    # Draw each letter as block shapes
    letters_data = []  # store (x, y, w, h, color) for glow pass
    for i, letter in enumerate("DISCO"):
        lx = sign_x + i * (letter_w + letter_gap)
        color = sign_colors[i]
        letters_data.append((lx, sign_y, letter_w, letter_h, color))

        # Simple block-letter shapes
        if letter == "D":
            d.rectangle([lx, sign_y, lx + 3, sign_y + letter_h], fill=color)
            d.rectangle([lx + 3, sign_y, lx + letter_w - 3, sign_y + 3], fill=color)
            d.rectangle([lx + 3, sign_y + letter_h - 3, lx + letter_w - 3,
                         sign_y + letter_h], fill=color)
            d.rectangle([lx + letter_w - 3, sign_y + 3, lx + letter_w,
                         sign_y + letter_h - 3], fill=color)
        elif letter == "I":
            d.rectangle([lx + 2, sign_y, lx + letter_w - 2, sign_y + 3], fill=color)
            d.rectangle([lx + letter_w // 2 - 2, sign_y + 3,
                         lx + letter_w // 2 + 2, sign_y + letter_h - 3], fill=color)
            d.rectangle([lx + 2, sign_y + letter_h - 3, lx + letter_w - 2,
                         sign_y + letter_h], fill=color)
        elif letter == "S":
            d.rectangle([lx, sign_y, lx + letter_w, sign_y + 3], fill=color)
            d.rectangle([lx, sign_y + 3, lx + 3, sign_y + letter_h // 2], fill=color)
            d.rectangle([lx, sign_y + letter_h // 2 - 2, lx + letter_w,
                         sign_y + letter_h // 2 + 1], fill=color)
            d.rectangle([lx + letter_w - 3, sign_y + letter_h // 2 + 1,
                         lx + letter_w, sign_y + letter_h - 3], fill=color)
            d.rectangle([lx, sign_y + letter_h - 3, lx + letter_w,
                         sign_y + letter_h], fill=color)
        elif letter == "C":
            d.rectangle([lx, sign_y, lx + letter_w, sign_y + 3], fill=color)
            d.rectangle([lx, sign_y, lx + 3, sign_y + letter_h], fill=color)
            d.rectangle([lx, sign_y + letter_h - 3, lx + letter_w,
                         sign_y + letter_h], fill=color)
        elif letter == "O":
            d.rectangle([lx, sign_y, lx + letter_w, sign_y + 3], fill=color)
            d.rectangle([lx, sign_y, lx + 3, sign_y + letter_h], fill=color)
            d.rectangle([lx + letter_w - 3, sign_y, lx + letter_w,
                         sign_y + letter_h], fill=color)
            d.rectangle([lx, sign_y + letter_h - 3, lx + letter_w,
                         sign_y + letter_h], fill=color)

    # Glow effect around neon letters
    glow_radius = 6
    for lx, ly, lw, lh, color in letters_data:
        for gx in range(lx - glow_radius, lx + lw + glow_radius):
            for gy in range(ly - glow_radius, ly + lh + glow_radius):
                if 0 <= gx < W and 0 <= gy < H:
                    r0, g0, b0, a0 = img.getpixel((gx, gy))
                    # Distance to nearest letter edge
                    dx = max(lx - gx, 0, gx - (lx + lw))
                    dy = max(ly - gy, 0, gy - (ly + lh))
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < glow_radius and dist > 0:
                        intensity = (1.0 - dist / glow_radius) * 0.3
                        if a0 > 0:
                            nr = min(int(r0 + color[0] * intensity), 255)
                            ng = min(int(g0 + color[1] * intensity), 255)
                            nb = min(int(b0 + color[2] * intensity), 255)
                            img.putpixel((gx, gy), (nr, ng, nb, a0))
                        else:
                            nr = int(color[0] * intensity * 0.5)
                            ng = int(color[1] * intensity * 0.5)
                            nb = int(color[2] * intensity * 0.5)
                            na = int(255 * intensity * 0.4)
                            if na > 0:
                                img.putpixel((gx, gy), (nr, ng, nb, na))

    out = OUTPUT_DIR / "parallax_disco_floor_mid.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def create_near_layer():
    """Near: illuminated dance floor tiles, disco fog/haze, cups and bottles."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    ground_y = 310

    # ── Illuminated dance floor tiles ──
    tile_colors = [
        (TILE_PURPLE, TILE_PURPLE_BRIGHT),
        (TILE_CYAN, TILE_CYAN_BRIGHT),
        (TILE_MAGENTA, TILE_MAGENTA_BRIGHT),
        (TILE_BLUE, TILE_BLUE_BRIGHT),
    ]
    tile_w = 25
    tile_h = 14  # foreshortened perspective
    tile_start_y = ground_y
    tile_rows = 4

    for row in range(tile_rows):
        for col in range(W // tile_w + 1):
            tx = col * tile_w
            ty = tile_start_y + row * tile_h
            if ty + tile_h > H:
                break
            # Alternating color pattern
            color_idx = (row + col) % len(tile_colors)
            base_color, bright_color = tile_colors[color_idx]

            # Tile body
            d.rectangle([tx + 1, ty + 1, tx + tile_w - 1, ty + tile_h - 1],
                        fill=base_color)
            # Tile border (darker gap between tiles)
            d.rectangle([tx, ty, tx + tile_w, ty], fill=(10, 10, 12, 200))
            d.rectangle([tx, ty, tx, ty + tile_h], fill=(10, 10, 12, 200))

            # Glowing center highlight
            cx = tx + tile_w // 2
            cy = ty + tile_h // 2
            glow_r = min(tile_w, tile_h) // 3
            for gy in range(cy - glow_r, cy + glow_r + 1):
                for gx in range(cx - glow_r, cx + glow_r + 1):
                    if 0 <= gx < W and 0 <= gy < H:
                        dx = gx - cx
                        dy = gy - cy
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist < glow_r:
                            t = 1.0 - dist / glow_r
                            r0, g0, b0, a0 = img.getpixel((gx, gy))
                            if a0 > 0:
                                blend = t * 0.5
                                nr = min(int(r0 * (1 - blend) +
                                             TILE_WHITE_CENTER[0] * blend), 255)
                                ng = min(int(g0 * (1 - blend) +
                                             TILE_WHITE_CENTER[1] * blend), 255)
                                nb = min(int(b0 * (1 - blend) +
                                             TILE_WHITE_CENTER[2] * blend), 255)
                                img.putpixel((gx, gy), (nr, ng, nb, a0))

    # ── Floor edge line at ground_y (chrome/metal strip) ──
    d.rectangle([0, ground_y - 1, W - 1, ground_y + 1], fill=(80, 82, 90, 220))
    d.line([0, ground_y - 1, W - 1, ground_y - 1], fill=(120, 122, 130, 200))

    # ── Disco fog / haze at ground level ──
    fog_y_start = ground_y - 15
    fog_y_end = ground_y + 20
    for fy in range(fog_y_start, min(fog_y_end, H)):
        # Varying density: thickest near ground_y, fading above and below
        dist_from_center = abs(fy - ground_y) / 20.0
        base_alpha = int(50 * (1.0 - dist_from_center))
        if base_alpha < 2:
            continue
        for fx in range(0, W):
            # Perlin-ish noise approximation: use sin waves at different frequencies
            noise = (math.sin(fx * 0.02 + fy * 0.1) * 0.3 +
                     math.sin(fx * 0.05 - fy * 0.03) * 0.2 +
                     math.sin(fx * 0.01 + fy * 0.07) * 0.5)
            noise = (noise + 1.0) / 2.0  # normalize to 0..1
            alpha = int(base_alpha * noise)
            if alpha < 2:
                continue
            r0, g0, b0, a0 = img.getpixel((fx, fy))
            if a0 > 0:
                blend = alpha / 255.0
                nr = min(int(r0 * (1 - blend) + FOG_COLOR[0] * blend), 255)
                ng = min(int(g0 * (1 - blend) + FOG_COLOR[1] * blend), 255)
                nb = min(int(b0 * (1 - blend) + FOG_COLOR[2] * blend), 255)
                img.putpixel((fx, fy), (nr, ng, nb, a0))
            else:
                img.putpixel((fx, fy), (FOG_COLOR[0], FOG_COLOR[1], FOG_COLOR[2],
                                         alpha))

    # ── Thicker fog wisps (a few drifting clouds of haze) ──
    for _ in range(8):
        wisp_cx = random.randint(40, W - 40)
        wisp_cy = random.randint(ground_y - 8, ground_y + 10)
        wisp_w = random.randint(50, 130)
        wisp_h = random.randint(6, 14)
        for wx in range(wisp_cx - wisp_w // 2, wisp_cx + wisp_w // 2):
            if 0 <= wx < W:
                for wy in range(wisp_cy - wisp_h // 2, wisp_cy + wisp_h // 2):
                    if 0 <= wy < H:
                        dx = (wx - wisp_cx) / (wisp_w / 2)
                        dy = (wy - wisp_cy) / (wisp_h / 2)
                        dist = dx * dx + dy * dy
                        if dist < 1.0 and random.random() < (1 - dist) * 0.5:
                            alpha = int(40 * (1 - dist))
                            r0, g0, b0, a0 = img.getpixel((wx, wy))
                            if a0 > 0:
                                blend = alpha / 255.0
                                nr = min(int(r0 * (1 - blend) +
                                             FOG_COLOR[0] * blend), 255)
                                ng = min(int(g0 * (1 - blend) +
                                             FOG_COLOR[1] * blend), 255)
                                nb = min(int(b0 * (1 - blend) +
                                             FOG_COLOR[2] * blend), 255)
                                img.putpixel((wx, wy), (nr, ng, nb, a0))
                            else:
                                img.putpixel((wx, wy),
                                             (FOG_COLOR[0], FOG_COLOR[1],
                                              FOG_COLOR[2], alpha))

    # ── Scattered cups / bottles / cocktail glasses on the floor ──
    # Red solo cups
    for _ in range(10):
        cx = random.randint(20, W - 20)
        cy = random.randint(ground_y + 8, H - 8)
        # Cup body (small trapezoid)
        cup_h = random.randint(6, 9)
        cup_top_w = 4
        cup_bot_w = 3
        d.polygon([(cx - cup_bot_w // 2, cy + cup_h),
                    (cx + cup_bot_w // 2, cy + cup_h),
                    (cx + cup_top_w // 2, cy),
                    (cx - cup_top_w // 2, cy)],
                   fill=CUP_RED)
        # Rim highlight
        d.line([cx - cup_top_w // 2, cy, cx + cup_top_w // 2, cy],
               fill=CUP_RED_DARK)
        # Some are tipped over
        if random.random() < 0.3:
            # Spill puddle
            d.ellipse([cx + 3, cy + cup_h - 2, cx + 10, cy + cup_h + 1],
                      fill=(120, 80, 30, 80))

    # Cocktail glasses (triangular shape)
    for _ in range(5):
        gx = random.randint(30, W - 30)
        gy = random.randint(ground_y + 5, H - 10)
        glass_h = random.randint(7, 10)
        # V-shaped glass
        d.polygon([(gx - 4, gy), (gx + 4, gy), (gx, gy + glass_h - 3)],
                   fill=GLASS_CLEAR)
        # Stem
        d.line([gx, gy + glass_h - 3, gx, gy + glass_h], fill=GLASS_CLEAR)
        # Base
        d.line([gx - 2, gy + glass_h, gx + 2, gy + glass_h], fill=GLASS_CLEAR)
        # Glass highlight
        d.point([gx - 2, gy + 1], fill=GLASS_HIGHLIGHT)
        # Tiny olive/cherry
        if random.random() < 0.5:
            d.point([gx, gy + 2], fill=(180, 50, 50))

    # Beer bottles
    for _ in range(6):
        bx = random.randint(15, W - 15)
        by = random.randint(ground_y + 4, H - 10)
        bottle_h = random.randint(8, 11)
        # Body
        d.rectangle([bx, by + 3, bx + 3, by + bottle_h], fill=BOTTLE_DARK)
        # Neck
        d.rectangle([bx + 1, by, bx + 2, by + 3], fill=BOTTLE_DARK)
        # Label
        d.rectangle([bx, by + 5, bx + 3, by + 8], fill=BOTTLE_LABEL)
        # Highlight glint
        d.point([bx, by + 4], fill=(100, 180, 110))
        # Cap
        d.point([bx + 1, by], fill=(200, 170, 50))

    # Cocktail straws scattered
    for _ in range(8):
        sx = random.randint(10, W - 10)
        sy = random.randint(ground_y + 3, H - 5)
        angle = random.uniform(-0.4, 0.4)
        straw_len = random.randint(8, 14)
        ex = sx + int(straw_len * math.cos(angle))
        ey = sy + int(straw_len * math.sin(angle))
        color = random.choice([STRAW_PINK, (255, 255, 100), (100, 200, 255)])
        d.line([sx, sy, ex, ey], fill=color, width=1)

    # ── Confetti/glitter scattered on floor ──
    for _ in range(40):
        cx = random.randint(0, W - 1)
        cy = random.randint(ground_y + 2, H - 2)
        confetti_c = random.choice([
            (255, 100, 150), (100, 200, 255), (255, 220, 50),
            (200, 100, 255), (100, 255, 150), (255, 150, 50),
        ])
        shape = random.choice(["dot", "rect"])
        if shape == "dot":
            d.point([cx, cy], fill=confetti_c)
        else:
            d.rectangle([cx, cy, cx + 1, cy + 1], fill=confetti_c)

    out = OUTPUT_DIR / "parallax_disco_floor_near.png"
    img.save(out)
    print(f"  [OK] {out.name}")


def main():
    print("Generating Bee Gees Disco Floor parallax layers...")
    create_sky_layer()
    create_mid_layer()
    create_near_layer()
    print("Done!")


if __name__ == "__main__":
    main()
