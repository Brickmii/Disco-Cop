"""
Blender sprite sheet renderer for Disco Cop.
Run from Blender command line:
    blender -b model.blend -P render_spritesheet.py -- --output ../assets/sprites/players/ --name player_idle --frames 4 --size 48 --action idle

Non-square frames (e.g. 24x48 player):
    blender -b model.blend -P render_spritesheet.py -- --output ../assets/sprites/players/ --name player_idle --frames 4 --width 24 --height 48 --action idle

Batch mode (renders all entries from a JSON manifest):
    blender -b model.blend -P render_spritesheet.py -- --batch manifest.json

Renders orthographic side-view frames with transparent background,
then composites them into a horizontal sprite sheet.
"""

import bpy
import sys
import os
import json
import argparse
import site
from pathlib import Path

# Blender doesn't include user site-packages by default
_user_site = site.getusersitepackages()
if _user_site not in sys.path:
    sys.path.append(_user_site)

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
    parser.add_argument("--output", type=str, help="Output directory")
    parser.add_argument("--name", type=str, help="Sprite name prefix")
    parser.add_argument("--frames", type=int, default=8, help="Number of frames to render")
    parser.add_argument("--size", type=int, default=0, help="Frame size in pixels (square, overrides width/height)")
    parser.add_argument("--width", type=int, default=0, help="Frame width in pixels")
    parser.add_argument("--height", type=int, default=0, help="Frame height in pixels")
    parser.add_argument("--action", type=str, default="", help="Blender action/animation name")
    parser.add_argument("--start-frame", type=int, default=1, help="Start frame in animation")
    parser.add_argument("--ortho-scale", type=float, default=0.0, help="Camera orthographic scale (auto-calculated if 0)")
    parser.add_argument("--batch", type=str, default="", help="Path to JSON batch manifest file")

    return parser.parse_args(argv)


def resolve_dimensions(args):
    """Resolve frame width and height from args. Returns (width, height)."""
    if args.size > 0:
        return args.size, args.size
    w = args.width if args.width > 0 else 64
    h = args.height if args.height > 0 else 64
    return w, h


def setup_camera(width, height, ortho_scale=0.0):
    """Set up orthographic side-view camera."""
    cam = bpy.data.cameras.get("SpriteCamera")
    if not cam:
        cam = bpy.data.cameras.new("SpriteCamera")

    cam.type = 'ORTHO'

    # Auto-calculate ortho_scale from the taller dimension if not specified
    if ortho_scale > 0.0:
        cam.ortho_scale = ortho_scale
    else:
        # Scale so 1 Blender unit ≈ 1 pixel at render size
        # Default: fit the frame height into the camera view
        cam.ortho_scale = max(width, height) / max(width, height) * 2.0

    cam_obj = bpy.data.objects.get("SpriteCameraObj")
    if not cam_obj:
        cam_obj = bpy.data.objects.new("SpriteCameraObj", cam)
        bpy.context.scene.collection.objects.link(cam_obj)

    # Front view from -Y: character faces +X which appears as RIGHT on screen
    cam_z = height / max(width, height) * cam.ortho_scale * 0.5
    cam_obj.location = (0, -10, cam_z)
    cam_obj.rotation_euler = (1.5708, 0, 0)  # 90° X rotation

    bpy.context.scene.camera = cam_obj
    return cam_obj


def setup_render(width, height):
    """Configure render settings for pixel art."""
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    # Use EEVEE for speed (Blender 5.0 renamed EEVEE_NEXT back to EEVEE)
    if 'BLENDER_EEVEE' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]:
        scene.render.engine = 'BLENDER_EEVEE'
    else:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'


def set_action(action_name):
    """Set the active action on the armature."""
    if not action_name:
        return

    # Find armature
    armature = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break

    if armature is None:
        print(f"WARNING: No armature found, cannot set action '{action_name}'")
        return

    # Find and set the action
    action = bpy.data.actions.get(action_name)
    if action is None:
        print(f"WARNING: Action '{action_name}' not found. Available actions:")
        for a in bpy.data.actions:
            print(f"  - {a.name}")
        return

    if armature.animation_data is None:
        armature.animation_data_create()
    armature.animation_data.action = action
    print(f"Set action: {action_name}")


def render_frames(output_dir, name, num_frames, start_frame, width, height):
    """Render individual frames."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    frames = []

    for i in range(num_frames):
        frame_num = start_frame + i
        scene.frame_set(frame_num)

        frame_path = output_dir / f"{name}_frame_{i:03d}.png"
        scene.render.filepath = str(frame_path)
        bpy.ops.render.render(write_still=True)
        frames.append(frame_path)
        print(f"Rendered frame {i + 1}/{num_frames}: {frame_path}")

    return frames


def create_spritesheet(frames, output_dir, name, width, height):
    """Combine frames into a horizontal sprite sheet."""
    if Image is None:
        print("WARNING: Pillow not installed. Skipping sprite sheet assembly.")
        print("Install with: pip install Pillow")
        return

    images = [Image.open(f) for f in frames]
    sheet_width = width * len(images)
    sheet_height = height

    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    for i, img in enumerate(images):
        # Resize frame if render size doesn't match target (shouldn't happen, but safety)
        if img.size != (width, height):
            img = img.resize((width, height), Image.NEAREST)
        sheet.paste(img, (i * width, 0))

    output_path = Path(output_dir) / f"{name}_sheet.png"
    sheet.save(output_path)
    print(f"Sprite sheet saved: {output_path}")

    # Clean up individual frames
    for f in frames:
        os.remove(f)
    print("Cleaned up individual frames.")


def render_single(args):
    """Render a single sprite sheet from CLI args."""
    width, height = resolve_dimensions(args)
    print(f"Rendering sprite sheet: {args.name}")
    print(f"  Frames: {args.frames}, Size: {width}x{height}")
    print(f"  Output: {args.output}")

    if args.action:
        set_action(args.action)

    setup_camera(width, height, args.ortho_scale)
    setup_render(width, height)
    frames = render_frames(args.output, args.name, args.frames, args.start_frame, width, height)
    create_spritesheet(frames, args.output, args.name, width, height)
    print("Done!")


def render_batch(manifest_path):
    """Render multiple sprite sheets from a JSON manifest.

    Manifest format:
    [
        {
            "output": "disco_cop/assets/sprites/players/",
            "name": "player_idle",
            "frames": 4,
            "width": 24,
            "height": 48,
            "action": "idle",
            "start_frame": 1,
            "ortho_scale": 0
        },
        ...
    ]
    """
    with open(manifest_path, 'r') as f:
        entries = json.load(f)

    print(f"Batch rendering {len(entries)} sprite sheets from {manifest_path}")

    for i, entry in enumerate(entries):
        width = entry.get("size", 0)
        height = entry.get("size", 0)
        if width == 0:
            width = entry.get("width", 64)
            height = entry.get("height", 64)

        name = entry["name"]
        output = entry["output"]
        num_frames = entry.get("frames", 8)
        action = entry.get("action", "")
        start_frame = entry.get("start_frame", 1)
        ortho_scale = entry.get("ortho_scale", 0.0)

        print(f"\n--- [{i + 1}/{len(entries)}] {name} ({width}x{height}, {num_frames} frames) ---")

        if action:
            set_action(action)

        setup_camera(width, height, ortho_scale)
        setup_render(width, height)
        frames = render_frames(output, name, num_frames, start_frame, width, height)
        create_spritesheet(frames, output, name, width, height)

    print(f"\nBatch complete: {len(entries)} sheets rendered.")


def main():
    args = get_args()

    if args.batch:
        render_batch(args.batch)
    else:
        if not args.output or not args.name:
            print("ERROR: --output and --name are required (or use --batch)")
            sys.exit(1)
        render_single(args)


if __name__ == "__main__":
    main()
