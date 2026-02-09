"""
Blender sprite sheet renderer for Disco Cop.
Run from Blender command line:
    blender -b model.blend -P render_spritesheet.py -- --output ../assets/sprites/players/ --name player --frames 8 --size 64

Renders orthographic side-view frames with transparent background,
then composites them into a horizontal sprite sheet.
"""

import bpy
import sys
import os
import argparse
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None


def get_args():
    # Get args after "--"
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Render sprite sheet from Blender model")
    parser.add_argument("--output", type=str, required=True, help="Output directory")
    parser.add_argument("--name", type=str, required=True, help="Sprite name prefix")
    parser.add_argument("--frames", type=int, default=8, help="Number of frames to render")
    parser.add_argument("--size", type=int, default=64, help="Frame size in pixels (square)")
    parser.add_argument("--action", type=str, default="", help="Blender action/animation name")
    parser.add_argument("--start-frame", type=int, default=1, help="Start frame in animation")

    return parser.parse_args(argv)


def setup_camera(size):
    """Set up orthographic side-view camera."""
    cam = bpy.data.cameras.get("SpriteCamera")
    if not cam:
        cam = bpy.data.cameras.new("SpriteCamera")

    cam.type = 'ORTHO'
    cam.ortho_scale = 2.0  # Adjust based on model size

    cam_obj = bpy.data.objects.get("SpriteCameraObj")
    if not cam_obj:
        cam_obj = bpy.data.objects.new("SpriteCameraObj", cam)
        bpy.context.scene.collection.objects.link(cam_obj)

    # Side view (looking from +Y toward -Y)
    cam_obj.location = (0, 5, 0.5)
    cam_obj.rotation_euler = (1.5708, 0, 0)  # 90 degrees X rotation

    bpy.context.scene.camera = cam_obj
    return cam_obj


def setup_render(size):
    """Configure render settings for pixel art."""
    scene = bpy.context.scene
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    # Use EEVEE for speed
    scene.render.engine = 'BLENDER_EEVEE_NEXT'


def render_frames(args):
    """Render individual frames."""
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    frames = []

    for i in range(args.frames):
        frame_num = args.start_frame + i
        scene.frame_set(frame_num)

        frame_path = output_dir / f"{args.name}_frame_{i:03d}.png"
        scene.render.filepath = str(frame_path)
        bpy.ops.render.render(write_still=True)
        frames.append(frame_path)
        print(f"Rendered frame {i + 1}/{args.frames}: {frame_path}")

    return frames


def create_spritesheet(frames, args):
    """Combine frames into a horizontal sprite sheet."""
    if Image is None:
        print("WARNING: Pillow not installed. Skipping sprite sheet assembly.")
        print("Install with: pip install Pillow")
        return

    images = [Image.open(f) for f in frames]
    width = args.size * len(images)
    height = args.size

    sheet = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    for i, img in enumerate(images):
        sheet.paste(img, (i * args.size, 0))

    output_path = Path(args.output) / f"{args.name}_sheet.png"
    sheet.save(output_path)
    print(f"Sprite sheet saved: {output_path}")

    # Clean up individual frames
    for f in frames:
        os.remove(f)
    print("Cleaned up individual frames.")


def main():
    args = get_args()
    print(f"Rendering sprite sheet: {args.name}")
    print(f"  Frames: {args.frames}, Size: {args.size}x{args.size}")
    print(f"  Output: {args.output}")

    setup_camera(args.size)
    setup_render(args.size)
    frames = render_frames(args)
    create_spritesheet(frames, args)
    print("Done!")


if __name__ == "__main__":
    main()
