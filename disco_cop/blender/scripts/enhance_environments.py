#!/usr/bin/env python3
"""Post-process enhancement for Disco Cop level environments.

Pushes visual identity harder per zone:
  - L1 Rink: More neon glow, disco ball reflections, purple/pink saturation
  - L2 Venice Beach: Warmer golden light, orange sunset vibes, haze
  - L3 Concert: Stage lighting bloom, red/amber theatrical glow
  - L4 Punk Alley: Gritty high-contrast, graffiti splatter overlay, green tint
  - L5 Disco Floor: Maximum mirror ball sparkle, chromatic light beams, fog

Usage:
    python enhance_environments.py
"""

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
ENV_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "sprites" / "environment"

random.seed(888)


def boost_channel(px, channel, factor):
    """Boost a specific color channel (0=R, 1=G, 2=B)."""
    result = px.copy().astype(np.float32)
    result[:, :, channel] = np.clip(result[:, :, channel] * factor, 0, 255)
    return result.astype(np.uint8)


def add_glow_points(img, color, count=50, radius_range=(3, 12), alpha_range=(15, 50)):
    """Add random glow spots across the image."""
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.size
    for _ in range(count):
        cx = random.randint(0, w - 1)
        cy = random.randint(0, h - 1)
        r = random.randint(radius_range[0], radius_range[1])
        a = random.randint(alpha_range[0], alpha_range[1])
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=(color[0], color[1], color[2], a))
    return img


def add_scan_lines(img, spacing=3, alpha=20):
    """Add subtle horizontal scan lines for retro feel."""
    px = np.array(img)
    h, w = px.shape[:2]
    for y in range(0, h, spacing):
        if y < h:
            px[y, :, 0] = np.clip(px[y, :, 0].astype(int) - alpha, 0, 255)
            px[y, :, 1] = np.clip(px[y, :, 1].astype(int) - alpha, 0, 255)
            px[y, :, 2] = np.clip(px[y, :, 2].astype(int) - alpha, 0, 255)
    return Image.fromarray(px)


def add_vignette(img, strength=0.3):
    """Add a subtle dark vignette to the edges."""
    px = np.array(img).astype(np.float32)
    h, w = px.shape[:2]
    cy, cx = h / 2.0, w / 2.0
    max_dist = (cx**2 + cy**2)**0.5

    for y in range(h):
        for x in range(w):
            dist = ((x - cx)**2 + (y - cy)**2)**0.5 / max_dist
            darken = max(0, 1.0 - dist * strength)
            px[y, x, :3] *= darken

    return Image.fromarray(np.clip(px, 0, 255).astype(np.uint8))


def add_color_overlay(img, color, alpha=0.08):
    """Add a subtle color wash over the entire image."""
    px = np.array(img).astype(np.float32)
    overlay = np.array(color, dtype=np.float32)
    px[:, :, :3] = px[:, :, :3] * (1 - alpha) + overlay * alpha * 255
    return Image.fromarray(np.clip(px, 0, 255).astype(np.uint8))


def add_sparkle_field(img, count=80, colors=None):
    """Add scattered sparkle pixels."""
    if colors is None:
        colors = [(255, 255, 255), (255, 240, 100), (200, 220, 255)]
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.size
    for _ in range(count):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        c = random.choice(colors)
        size = random.choice([0, 0, 0, 1])  # Mostly single pixels
        a = random.randint(120, 255)
        if size == 0:
            d.point([x, y], fill=(c[0], c[1], c[2], a))
        else:
            d.rectangle([x, y, x + 1, y + 1], fill=(c[0], c[1], c[2], a))
    return img


def add_graffiti_splatter(img, count=15):
    """Add small graffiti-style paint splatters for punk aesthetic."""
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.size
    punk_colors = [
        (255, 50, 50),    # Red
        (50, 255, 50),    # Green
        (255, 255, 50),   # Yellow
        (255, 50, 255),   # Magenta
        (255, 140, 0),    # Orange
    ]
    for _ in range(count):
        cx = random.randint(20, w - 20)
        cy = random.randint(h // 3, h - 10)
        color = random.choice(punk_colors)
        r = random.randint(2, 6)
        a = random.randint(30, 70)
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=(color[0], color[1], color[2], a))
        # Splatter drops
        for _ in range(random.randint(2, 5)):
            dx = random.randint(-8, 8)
            dy = random.randint(-8, 8)
            d.point([cx + dx, cy + dy], fill=(color[0], color[1], color[2], a + 20))
    return img


def enhance_layer(filepath, transforms):
    """Apply a list of transform functions to an image."""
    if not filepath.exists():
        print(f"  [SKIP] {filepath.name}")
        return
    img = Image.open(filepath).convert("RGBA")
    for fn in transforms:
        img = fn(img)
    img.save(filepath)
    print(f"  [OK] {filepath.name}")


def main():
    print("Enhancing level environments...\n")

    # ── L1: Skating Rink ──────────────────────────────────────────────
    print("L1 Skating Rink (neon glow, disco reflections):")
    enhance_layer(ENV_DIR / "parallax_rink_ceiling.png", [
        lambda img: add_glow_points(img, (255, 105, 180), count=30, radius_range=(5, 15)),
        lambda img: add_glow_points(img, (0, 255, 255), count=20, radius_range=(4, 10)),
        lambda img: add_sparkle_field(img, count=60, colors=[(255, 255, 255), (255, 105, 180), (0, 255, 255)]),
        lambda img: add_color_overlay(img, (0.3, 0, 0.5), alpha=0.05),
    ])
    enhance_layer(ENV_DIR / "parallax_rink_mid.png", [
        lambda img: add_glow_points(img, (147, 112, 219), count=15, radius_range=(3, 8)),
        lambda img: add_scan_lines(img, spacing=4, alpha=10),
    ])
    enhance_layer(ENV_DIR / "parallax_rink_near.png", [
        lambda img: add_glow_points(img, (255, 215, 0), count=10, radius_range=(2, 6)),
    ])

    # ── L2: Venice Beach ──────────────────────────────────────────────
    print("\nL2 Venice Beach (golden sunset warmth):")
    enhance_layer(ENV_DIR / "parallax_venice_sky.png", [
        lambda img: add_color_overlay(img, (1.0, 0.6, 0.2), alpha=0.08),
        lambda img: add_glow_points(img, (255, 180, 80), count=15, radius_range=(10, 25)),
    ])
    enhance_layer(ENV_DIR / "parallax_venice_mid.png", [
        lambda img: add_color_overlay(img, (0.8, 0.5, 0.2), alpha=0.05),
        lambda img: add_glow_points(img, (255, 200, 100), count=8, radius_range=(3, 8)),
    ])
    enhance_layer(ENV_DIR / "parallax_venice_near.png", [
        lambda img: add_color_overlay(img, (0.6, 0.4, 0.1), alpha=0.04),
    ])

    # ── L3: Led Zeppelin Concert ──────────────────────────────────────
    print("\nL3 Concert (stage lighting bloom, amber glow):")
    enhance_layer(ENV_DIR / "parallax_concert_sky.png", [
        lambda img: add_glow_points(img, (255, 140, 0), count=25, radius_range=(8, 20)),
        lambda img: add_glow_points(img, (255, 50, 50), count=15, radius_range=(5, 15)),
        lambda img: add_sparkle_field(img, count=30, colors=[(255, 200, 100), (255, 255, 200)]),
    ])
    enhance_layer(ENV_DIR / "parallax_concert_mid.png", [
        lambda img: add_glow_points(img, (200, 100, 50), count=12, radius_range=(4, 10)),
        lambda img: add_scan_lines(img, spacing=5, alpha=8),
    ])
    enhance_layer(ENV_DIR / "parallax_concert_near.png", [
        lambda img: add_glow_points(img, (255, 180, 80), count=8, radius_range=(2, 6)),
    ])

    # ── L3/L4: Punk Alley ────────────────────────────────────────────
    print("\nL3/L4 Punk Alley (gritty, graffiti, high contrast):")
    enhance_layer(ENV_DIR / "parallax_punk_alley_sky.png", [
        lambda img: add_color_overlay(img, (0.1, 0.3, 0.1), alpha=0.06),
        lambda img: add_graffiti_splatter(img, count=8),
    ])
    enhance_layer(ENV_DIR / "parallax_punk_alley_mid.png", [
        lambda img: add_graffiti_splatter(img, count=12),
        lambda img: add_scan_lines(img, spacing=3, alpha=12),
    ])
    enhance_layer(ENV_DIR / "parallax_punk_alley_near.png", [
        lambda img: add_graffiti_splatter(img, count=6),
        lambda img: add_color_overlay(img, (0, 0.2, 0), alpha=0.04),
    ])

    # ── L5: Bee Gees Disco Floor ──────────────────────────────────────
    print("\nL5 Disco Floor (maximum sparkle, chromatic beams):")
    enhance_layer(ENV_DIR / "parallax_disco_floor_sky.png", [
        lambda img: add_glow_points(img, (255, 100, 150), count=30, radius_range=(6, 18)),
        lambda img: add_glow_points(img, (100, 150, 255), count=25, radius_range=(5, 15)),
        lambda img: add_glow_points(img, (255, 220, 100), count=20, radius_range=(4, 12)),
        lambda img: add_sparkle_field(img, count=120, colors=[
            (255, 255, 255), (255, 240, 100), (255, 200, 255),
            (200, 220, 255), (255, 150, 200),
        ]),
    ])
    enhance_layer(ENV_DIR / "parallax_disco_floor_mid.png", [
        lambda img: add_glow_points(img, (255, 105, 180), count=15, radius_range=(4, 10)),
        lambda img: add_sparkle_field(img, count=40, colors=[(255, 255, 255), (255, 240, 100)]),
        lambda img: add_scan_lines(img, spacing=4, alpha=8),
    ])
    enhance_layer(ENV_DIR / "parallax_disco_floor_near.png", [
        lambda img: add_sparkle_field(img, count=50, colors=[
            (255, 255, 255), (255, 240, 100), (200, 220, 255),
        ]),
        lambda img: add_glow_points(img, (255, 255, 255), count=10, radius_range=(2, 5), alpha_range=(20, 40)),
    ])

    print("\nDone! All level environments enhanced.")


if __name__ == "__main__":
    main()
