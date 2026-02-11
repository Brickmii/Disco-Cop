#!/usr/bin/env python3
"""Generate Venice Beach enemy sprites for Disco Cop Level 02.

Palette-swaps existing enemy sprite sheets to beach theme:
  - Grunt → Weightlifter Brute (tan skin, white tank top, red shorts)
  - Skating Grunt → Roller Skater (beach attire, bright colors)
  - Shooter → Beach Bum Shooter (Hawaiian shirt vibes, warm tones)
  - Flyer → Seagull (white/gray bird colors, yellow beak)

Usage:
    python create_venice_enemies.py
"""

from pathlib import Path

import numpy as np
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
ENEMY_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "enemies"


def remap_brute(r, g, b, a):
    """Grunt → Weightlifter Brute: warm tan skin, white tank top."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 130:
        # Light gray body → white tank top
        return (min(r + 60, 250), min(g + 55, 245), min(b + 50, 240), a)
    elif is_gray and brightness > 80:
        # Mid gray → tan skin
        return (min(int(r * 1.4), 210), min(int(g * 1.1), 170), min(int(b * 0.7), 120), a)
    elif brightness > 100 and r > g:
        # Warm tones → redder (shorts/accessories)
        return (min(int(r * 1.3), 220), max(int(g * 0.6), 40), max(int(b * 0.5), 30), a)
    elif brightness > 50:
        # Mid tones → warmer skin shadow
        return (min(int(r * 1.3), 180), min(int(g * 1.0), 140), max(int(b * 0.7), 60), a)
    else:
        # Dark (outlines, hair) → keep but warm slightly
        return (min(r + 10, 80), min(g + 5, 50), b, a)


def remap_skater(r, g, b, a):
    """Skating Grunt → Roller Skater: bright beach colors, orange/yellow."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 130:
        # Light body → bright orange tank
        return (min(int(r * 1.1), 255), min(int(g * 0.8), 180), max(int(b * 0.3), 20), a)
    elif is_gray and brightness > 80:
        # Mid body → yellow/gold shorts
        return (min(int(r * 1.4), 230), min(int(g * 1.3), 210), max(int(b * 0.4), 40), a)
    elif brightness > 100 and b > r:
        # Cool tones → warm flip (cyan skates → yellow wheels)
        return (min(int(b * 1.2), 240), min(int(g * 1.1), 220), max(int(r * 0.5), 30), a)
    elif brightness > 50:
        # Mid tones → tan skin
        return (min(int(r * 1.3), 200), min(int(g * 1.1), 160), max(int(b * 0.8), 80), a)
    else:
        return (min(r + 8, 70), min(g + 5, 45), b, a)


def remap_beach_shooter(r, g, b, a):
    """Shooter → Beach Bum: Hawaiian shirt (green/teal), khaki shorts."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if is_gray and brightness > 130:
        # Light body → teal Hawaiian shirt
        return (max(int(r * 0.4), 30), min(int(g * 1.2), 200), min(int(b * 1.1), 180), a)
    elif is_gray and brightness > 80:
        # Mid body → khaki/tan
        return (min(int(r * 1.2), 195), min(int(g * 1.15), 175), max(int(b * 0.8), 100), a)
    elif brightness > 100 and r > b:
        # Warm accent → flower pattern hint (pink)
        return (min(int(r * 1.2), 240), max(int(g * 0.6), 80), min(int(b * 1.1), 160), a)
    elif brightness > 50:
        # Mid tones → warm skin
        return (min(int(r * 1.2), 190), min(int(g * 1.0), 145), max(int(b * 0.7), 80), a)
    else:
        return (min(r + 5, 60), g, b, a)


def remap_seagull(r, g, b, a):
    """Flyer → Seagull: white/gray body, dark wingtips, yellow beak."""
    if a < 10:
        return (r, g, b, a)
    brightness = (r + g + b) / 3.0
    is_gray = abs(r - g) < 20 and abs(g - b) < 20

    if brightness > 140:
        # Light areas → bright white (bird body)
        boost = min(int(brightness * 0.3), 60)
        return (min(r + boost, 250), min(g + boost, 248), min(b + boost, 245), a)
    elif brightness > 90:
        # Mid areas → light gray (wings)
        return (min(int(brightness * 1.1), 200), min(int(brightness * 1.1), 198),
                min(int(brightness * 1.05), 195), a)
    elif brightness > 50:
        # Darker mid → gray-brown wingtips
        return (min(int(r * 0.8), 120), min(int(g * 0.8), 115), min(int(b * 0.85), 120), a)
    elif b > r and b > g:
        # Blue/cyan (original wing color) → yellow beak
        return (min(int(b * 2.0), 240), min(int(b * 1.6), 200), max(int(b * 0.3), 20), a)
    elif brightness > 20:
        # Dark accents → dark gray feather detail
        return (min(r + 20, 80), min(g + 20, 78), min(b + 20, 75), a)
    else:
        # Very dark (outlines) → keep
        return (r, g, b, a)


def swap_sheets(src_names, prefix, remap_fn):
    """Apply remap function to a list of source sheets, save with new prefix."""
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

        # Build output name: replace original prefix with new one
        # e.g., grunt_skate_sheet.png → brute_skate_sheet.png
        base = src_name.split("_", 1)[1]  # Remove first word
        dst_name = f"{prefix}_{base}"
        dst_path = ENEMY_DIR / dst_name
        Image.fromarray(px.astype(np.uint8), "RGBA").save(dst_path)
        print(f"  [OK] {dst_name}")


def main():
    print("Generating Venice Beach enemy sprites...")

    # Weightlifter Brute (from grunt)
    swap_sheets([
        "grunt_skate_sheet.png",
        "grunt_charge_sheet.png",
        "grunt_hurt_sheet.png",
        "grunt_death_sheet.png",
    ], "brute", remap_brute)

    # Roller Skater (from skating grunt — same source, different palette)
    swap_sheets([
        "grunt_skate_sheet.png",
        "grunt_charge_sheet.png",
        "grunt_hurt_sheet.png",
        "grunt_death_sheet.png",
    ], "skater", remap_skater)

    # Beach Bum Shooter (from shooter)
    swap_sheets([
        "shooter_skate_sheet.png",
        "shooter_shoot_skate_sheet.png",
        "shooter_hurt_sheet.png",
        "shooter_death_sheet.png",
    ], "beachbum", remap_beach_shooter)

    # Seagull (from flyer)
    swap_sheets([
        "flyer_fly_sheet.png",
        "flyer_attack_sheet.png",
        "flyer_hurt_sheet.png",
        "flyer_death_sheet.png",
    ], "seagull", remap_seagull)

    print("\nDone! Venice Beach enemies generated.")


if __name__ == "__main__":
    main()
