#!/usr/bin/env python3
"""Generate Player 2 palette-swapped sprites for Disco Cop co-op.

Takes existing P1 sprite sheets and remaps colors:
  P1 (gray suit, dark brown afro) → P2 (cyan-tinted suit, blonde afro)

Usage:
    python create_p2_sprites.py

Output: disco_cop/assets/sprites/players/player_*_p2_sheet.png
"""

from pathlib import Path

import numpy as np
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
SPRITES_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "players"

ANIMATIONS = ["idle", "run", "jump", "fall", "double_jump", "hurt"]


def remap_pixel(r: int, g: int, b: int, a: int) -> tuple:
    """Remap a single pixel from P1 palette to P2 palette."""
    if a < 10:
        return (r, g, b, a)

    # Detect color category based on channel relationships
    is_gray = abs(r - g) < 15 and abs(g - b) < 15
    is_brown = r > g > b and (r - b) > 8
    brightness = (r + g + b) / 3.0

    if is_gray and brightness > 140:
        # Bright gray (suit/body) → cyan tint
        # Shift: reduce red, keep green, boost blue
        nr = max(int(r * 0.55), 0)
        ng = min(int(g * 1.05), 255)
        nb = min(int(b * 1.3), 255)
        return (nr, ng, nb, a)

    elif is_gray and brightness > 50:
        # Mid-gray (shading on suit) → darker cyan tint
        nr = max(int(r * 0.6), 0)
        ng = min(int(g * 1.0), 255)
        nb = min(int(b * 1.2), 255)
        return (nr, ng, nb, a)

    elif is_brown and brightness > 30:
        # Brown (afro) → blonde/platinum
        # Boost all channels, especially R and G
        factor = 2.8
        nr = min(int(r * factor), 240)
        ng = min(int(g * factor), 220)
        nb = min(int(b * factor * 0.9), 180)
        return (nr, ng, nb, a)

    elif is_brown and brightness <= 30:
        # Very dark brown (afro shadow) → darker blonde
        factor = 2.2
        nr = min(int(r * factor), 180)
        ng = min(int(g * factor), 160)
        nb = min(int(b * factor * 0.8), 120)
        return (nr, ng, nb, a)

    else:
        # Black (outlines), skin tones, etc. — keep as-is
        return (r, g, b, a)


def swap_palette(src_path: Path, dst_path: Path):
    """Load a sprite sheet, remap all pixels, save."""
    img = Image.open(src_path).convert("RGBA")
    pixels = np.array(img)

    h, w, _ = pixels.shape
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[y, x]
            pixels[y, x] = remap_pixel(int(r), int(g), int(b), int(a))

    out = Image.fromarray(pixels.astype(np.uint8), "RGBA")
    out.save(dst_path)


def main():
    print(f"Generating P2 palette swaps from: {SPRITES_DIR}")

    for anim in ANIMATIONS:
        src = SPRITES_DIR / f"player_{anim}_sheet.png"
        dst = SPRITES_DIR / f"player_{anim}_p2_sheet.png"

        if not src.exists():
            print(f"  [SKIP] {src.name} — not found")
            continue

        swap_palette(src, dst)
        print(f"  [OK] {dst.name}")

    print(f"\nDone! {len(ANIMATIONS)} P2 sprite sheets generated.")


if __name__ == "__main__":
    main()
