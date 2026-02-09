"""
Create the Flyer enemy model in Blender 5.0+.

Run via:
    blender -b -P create_flyer_model.py

Produces flyer.blend in the same directory as this script.
Character: DJ on a flying turntable/DJ booth — hovering setup with
a small figure perched on top operating the decks. Drops music note
bombs. 24x24 pixel frame.

Uses Blender 5.0 layered action API (pose_bone.keyframe_insert).
"""

import bpy
import math
import os
from mathutils import Vector, Euler

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clear_scene():
    """Remove all default objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def make_material(name, r, g, b):
    """Create a simple flat-color material."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
        bsdf.inputs["Roughness"].default_value = 1.0
        bsdf.inputs["Metallic"].default_value = 0.0
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.0
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.0
    return mat


def assign_material(obj, mat):
    """Assign a material to an object."""
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def set_smooth(obj, smooth=False):
    """Set flat or smooth shading."""
    for poly in obj.data.polygons:
        poly.use_smooth = smooth


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

def create_materials():
    """Create all character materials and return as dict."""
    mats = {}
    mats['skin'] = make_material('Skin', 0.45, 0.28, 0.15)
    mats['headphones'] = make_material('Headphones', 0.12, 0.12, 0.12)
    mats['hoodie'] = make_material('Hoodie', 0.10, 0.60, 0.80)        # cyan hoodie
    mats['deck_top'] = make_material('DeckTop', 0.20, 0.20, 0.22)     # dark grey
    mats['deck_body'] = make_material('DeckBody', 0.10, 0.10, 0.12)   # near-black
    mats['vinyl'] = make_material('Vinyl', 0.05, 0.05, 0.05)          # black records
    mats['glow'] = make_material('Glow', 0.90, 0.20, 0.90)            # magenta glow
    mats['hover_ring'] = make_material('HoverRing', 0.20, 0.80, 0.95) # cyan ring
    return mats


# ---------------------------------------------------------------------------
# Mesh Creation
# ---------------------------------------------------------------------------

# 24x24 pixel frame. Render script uses ortho_scale=2.0.
# Visible area: 2.0 BU wide x 2.0 BU tall (square).
# Character should fit in ~1.6 BU wide x 1.6 BU tall, centered.
#
# Layout (bottom up):
#   Hover ring/glow:  z = 0.10 - 0.20
#   DJ deck body:     z = 0.20 - 0.45
#   Deck surface:     z = 0.45 - 0.50
#   Vinyl records:    z = 0.51
#   DJ torso:         z = 0.50 - 0.80
#   DJ head:          z = 0.80 - 1.05
#   Headphones:       z = 0.92

def create_body_meshes(mats):
    """Create all body part meshes and return them as a dict."""
    parts = {}

    # --- HOVER RING (glowing ring under the deck) ---
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.40, minor_radius=0.04,
        major_segments=16, minor_segments=6,
        location=(0, 0, 0.15))
    hover_ring = bpy.context.active_object
    hover_ring.name = 'HoverRing'
    assign_material(hover_ring, mats['hover_ring'])
    set_smooth(hover_ring, True)
    parts['hover_ring'] = hover_ring

    # --- GLOW DISC (flat disc under deck for glow effect) ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.35, depth=0.03,
        location=(0, 0, 0.12))
    glow_disc = bpy.context.active_object
    glow_disc.name = 'GlowDisc'
    assign_material(glow_disc, mats['glow'])
    parts['glow_disc'] = glow_disc

    # --- DECK BODY (the main DJ booth box) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.32))
    deck_body = bpy.context.active_object
    deck_body.name = 'DeckBody'
    deck_body.scale = (0.60, 0.40, 0.20)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(deck_body, mats['deck_body'])
    parts['deck_body'] = deck_body

    # --- DECK TOP (surface of the booth) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.44))
    deck_top = bpy.context.active_object
    deck_top.name = 'DeckTop'
    deck_top.scale = (0.64, 0.44, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(deck_top, mats['deck_top'])
    parts['deck_top'] = deck_top

    # --- LEFT VINYL RECORD ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.12, depth=0.02,
        location=(0, 0.14, 0.47))
    vinyl_l = bpy.context.active_object
    vinyl_l.name = 'Vinyl.L'
    assign_material(vinyl_l, mats['vinyl'])
    parts['vinyl_l'] = vinyl_l

    # --- RIGHT VINYL RECORD ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.12, depth=0.02,
        location=(0, -0.14, 0.47))
    vinyl_r = bpy.context.active_object
    vinyl_r.name = 'Vinyl.R'
    assign_material(vinyl_r, mats['vinyl'])
    parts['vinyl_r'] = vinyl_r

    # --- DJ HEAD ---
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=6, radius=0.14,
        location=(0, 0, 0.92))
    head = bpy.context.active_object
    head.name = 'Head'
    assign_material(head, mats['skin'])
    set_smooth(head, True)
    parts['head'] = head

    # --- HEADPHONES ---
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.15, minor_radius=0.03,
        major_segments=12, minor_segments=4,
        location=(0, 0, 0.94))
    headphones = bpy.context.active_object
    headphones.name = 'Headphones'
    headphones.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_material(headphones, mats['headphones'])
    parts['headphones'] = headphones

    # --- DJ TORSO (small, hunched over decks) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.68))
    torso = bpy.context.active_object
    torso.name = 'Torso'
    torso.scale = (0.22, 0.20, 0.20)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(torso, mats['hoodie'])
    parts['torso'] = torso

    # --- LEFT ARM (reaching toward deck) ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6, radius=0.05, depth=0.20,
        location=(0.05, 0.14, 0.58))
    arm_l = bpy.context.active_object
    arm_l.name = 'Arm.L'
    arm_l.rotation_euler = (0, math.radians(30), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_material(arm_l, mats['hoodie'])
    parts['arm_l'] = arm_l

    # --- RIGHT ARM (reaching toward deck) ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6, radius=0.05, depth=0.20,
        location=(0.05, -0.14, 0.58))
    arm_r = bpy.context.active_object
    arm_r.name = 'Arm.R'
    arm_r.rotation_euler = (0, math.radians(30), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_material(arm_r, mats['hoodie'])
    parts['arm_r'] = arm_r

    return parts


# ---------------------------------------------------------------------------
# Armature — simpler than humanoid, mostly for bob/tilt/attack motion
# ---------------------------------------------------------------------------

def create_armature():
    """Create the flyer armature."""
    bpy.ops.object.armature_add(location=(0, 0, 0))
    armature_obj = bpy.context.active_object
    armature_obj.name = 'Armature'
    armature_obj.data.name = 'ArmatureData'

    bpy.ops.object.mode_set(mode='EDIT')
    arm = armature_obj.data

    # Remove default bone
    for bone in arm.edit_bones:
        arm.edit_bones.remove(bone)

    # --- Root (controls whole assembly position) ---
    root = arm.edit_bones.new('root')
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.15)

    # --- Deck (the DJ booth — tilt for movement) ---
    deck = arm.edit_bones.new('deck')
    deck.head = (0, 0, 0.20)
    deck.tail = (0, 0, 0.46)
    deck.parent = root

    # --- Body (DJ upper body) ---
    body = arm.edit_bones.new('body')
    body.head = (0, 0, 0.50)
    body.tail = (0, 0, 0.78)
    body.parent = deck

    # --- Head ---
    head_bone = arm.edit_bones.new('head')
    head_bone.head = (0, 0, 0.78)
    head_bone.tail = (0, 0, 1.05)
    head_bone.parent = body
    head_bone.use_connect = True

    # --- Left arm ---
    arm_l = arm.edit_bones.new('arm.L')
    arm_l.head = (0, 0.10, 0.68)
    arm_l.tail = (0.05, 0.14, 0.50)
    arm_l.parent = body

    # --- Right arm ---
    arm_r = arm.edit_bones.new('arm.R')
    arm_r.head = (0, -0.10, 0.68)
    arm_r.tail = (0.05, -0.14, 0.50)
    arm_r.parent = body

    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj


# ---------------------------------------------------------------------------
# Parenting (mesh -> armature)
# ---------------------------------------------------------------------------

MESH_BONE_MAP = {
    'HoverRing': 'root',
    'GlowDisc': 'root',
    'DeckBody': 'deck',
    'DeckTop': 'deck',
    'Vinyl.L': 'deck',
    'Vinyl.R': 'deck',
    'Torso': 'body',
    'Head': 'head',
    'Headphones': 'head',
    'Arm.L': 'arm.L',
    'Arm.R': 'arm.R',
}


def parent_meshes_to_armature(parts, armature_obj):
    """Parent each mesh part to the armature with a single vertex group."""
    for mesh_name, bone_name in MESH_BONE_MAP.items():
        obj = bpy.data.objects.get(mesh_name)
        if obj is None:
            print(f"WARNING: Could not find mesh '{mesh_name}' for parenting")
            continue

        vg = obj.vertex_groups.new(name=bone_name)
        vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')

        obj.parent = armature_obj
        mod = obj.modifiers.new(name='Armature', type='ARMATURE')
        mod.object = armature_obj


# ---------------------------------------------------------------------------
# Animations (Blender 5.0 compatible)
# ---------------------------------------------------------------------------

def setup_pose_mode(armature_obj):
    bpy.context.view_layer.objects.active = armature_obj
    armature_obj.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    for pbone in armature_obj.pose.bones:
        pbone.rotation_mode = 'XYZ'


def reset_pose(armature_obj):
    for pbone in armature_obj.pose.bones:
        pbone.location = (0, 0, 0)
        pbone.rotation_euler = (0, 0, 0)
        pbone.scale = (1, 1, 1)


def start_action(armature_obj, name):
    action = bpy.data.actions.new(name=name)
    action.use_fake_user = True
    if armature_obj.animation_data is None:
        armature_obj.animation_data_create()
    armature_obj.animation_data.action = action
    return action


def pose_and_key_loc(armature_obj, bone_name, frame, loc):
    armature_obj.pose.bones[bone_name].location = loc
    armature_obj.pose.bones[bone_name].keyframe_insert(data_path='location', frame=frame)


def pose_and_key_rot(armature_obj, bone_name, frame, rot):
    armature_obj.pose.bones[bone_name].rotation_euler = rot
    armature_obj.pose.bones[bone_name].keyframe_insert(data_path='rotation_euler', frame=frame)


def create_animations(armature_obj):
    """Create all 4 animation actions."""
    setup_pose_mode(armature_obj)

    create_fly_action(armature_obj)
    create_attack_action(armature_obj)
    create_hurt_action(armature_obj)
    create_death_action(armature_obj)

    bpy.ops.object.mode_set(mode='OBJECT')


def create_fly_action(armature_obj):
    """Hovering idle — gentle bob and tilt. Frames 1-4, looping."""
    reset_pose(armature_obj)
    action = start_action(armature_obj, 'fly')
    r = math.radians

    # Frame 1: neutral, slight tilt
    pose_and_key_loc(armature_obj, 'root', 1, (0, 0, 0))
    pose_and_key_rot(armature_obj, 'deck', 1, (r(2), 0, 0))
    pose_and_key_rot(armature_obj, 'body', 1, (r(5), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 1, (r(-3), 0, r(5)))
    pose_and_key_rot(armature_obj, 'arm.L', 1, (r(5), 0, 0))
    pose_and_key_rot(armature_obj, 'arm.R', 1, (r(-5), 0, 0))

    # Frame 2: bob up
    pose_and_key_loc(armature_obj, 'root', 2, (0, 0, 0.04))
    pose_and_key_rot(armature_obj, 'deck', 2, (r(-2), 0, r(3)))
    pose_and_key_rot(armature_obj, 'body', 2, (r(8), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 2, (r(-5), 0, r(-5)))
    pose_and_key_rot(armature_obj, 'arm.L', 2, (r(-5), 0, 0))
    pose_and_key_rot(armature_obj, 'arm.R', 2, (r(5), 0, 0))

    # Frame 3: neutral, opposite tilt
    pose_and_key_loc(armature_obj, 'root', 3, (0, 0, 0))
    pose_and_key_rot(armature_obj, 'deck', 3, (r(-2), 0, 0))
    pose_and_key_rot(armature_obj, 'body', 3, (r(5), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 3, (r(-3), 0, r(5)))
    pose_and_key_rot(armature_obj, 'arm.L', 3, (r(5), 0, 0))
    pose_and_key_rot(armature_obj, 'arm.R', 3, (r(-5), 0, 0))

    # Frame 4: bob down
    pose_and_key_loc(armature_obj, 'root', 4, (0, 0, -0.03))
    pose_and_key_rot(armature_obj, 'deck', 4, (r(2), 0, r(-3)))
    pose_and_key_rot(armature_obj, 'body', 4, (r(3), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 4, (r(-2), 0, r(-5)))
    pose_and_key_rot(armature_obj, 'arm.L', 4, (r(-5), 0, 0))
    pose_and_key_rot(armature_obj, 'arm.R', 4, (r(5), 0, 0))


def create_attack_action(armature_obj):
    """Swoop/drop attack — deck tilts forward aggressively. Frames 1-3."""
    reset_pose(armature_obj)
    action = start_action(armature_obj, 'attack')
    r = math.radians

    # Frame 1: wind up — pull back, tilt up
    pose_and_key_loc(armature_obj, 'root', 1, (0, 0, 0.05))
    pose_and_key_rot(armature_obj, 'deck', 1, (r(-15), 0, 0))
    pose_and_key_rot(armature_obj, 'body', 1, (r(-10), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 1, (r(10), 0, 0))
    pose_and_key_rot(armature_obj, 'arm.L', 1, (r(-15), 0, 0))
    pose_and_key_rot(armature_obj, 'arm.R', 1, (r(-15), 0, 0))

    # Frame 2: dive — deck tilts sharply forward
    pose_and_key_loc(armature_obj, 'root', 2, (0.03, 0, -0.05))
    pose_and_key_rot(armature_obj, 'deck', 2, (r(25), 0, 0))
    pose_and_key_rot(armature_obj, 'body', 2, (r(15), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 2, (r(5), 0, 0))
    pose_and_key_rot(armature_obj, 'arm.L', 2, (r(20), 0, 0))
    pose_and_key_rot(armature_obj, 'arm.R', 2, (r(20), 0, 0))

    # Frame 3: recovery — pulling back up
    pose_and_key_loc(armature_obj, 'root', 3, (0, 0, 0.02))
    pose_and_key_rot(armature_obj, 'deck', 3, (r(5), 0, 0))
    pose_and_key_rot(armature_obj, 'body', 3, (r(5), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 3, (r(-3), 0, 0))
    pose_and_key_rot(armature_obj, 'arm.L', 3, (r(5), 0, 0))
    pose_and_key_rot(armature_obj, 'arm.R', 3, (r(5), 0, 0))


def create_hurt_action(armature_obj):
    """Recoil — whole setup jolts. Frames 1-2."""
    reset_pose(armature_obj)
    action = start_action(armature_obj, 'hurt')
    r = math.radians

    # Frame 1: jolt back and tilt
    pose_and_key_loc(armature_obj, 'root', 1, (-0.04, 0, 0.03))
    pose_and_key_rot(armature_obj, 'deck', 1, (r(-12), 0, r(8)))
    pose_and_key_rot(armature_obj, 'body', 1, (r(-15), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 1, (r(-10), 0, r(-10)))
    pose_and_key_rot(armature_obj, 'arm.L', 1, (r(-20), 0, r(-15)))
    pose_and_key_rot(armature_obj, 'arm.R', 1, (r(-20), 0, r(15)))

    # Frame 2: stabilizing
    pose_and_key_loc(armature_obj, 'root', 2, (-0.02, 0, 0.01))
    pose_and_key_rot(armature_obj, 'deck', 2, (r(-5), 0, r(3)))
    pose_and_key_rot(armature_obj, 'body', 2, (r(-8), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 2, (r(-5), 0, r(-5)))
    pose_and_key_rot(armature_obj, 'arm.L', 2, (r(-10), 0, r(-8)))
    pose_and_key_rot(armature_obj, 'arm.R', 2, (r(-10), 0, r(8)))


def create_death_action(armature_obj):
    """Losing control and crashing. Frames 1-4."""
    reset_pose(armature_obj)
    action = start_action(armature_obj, 'death')
    r = math.radians

    # Frame 1: spark/hit — jolt
    pose_and_key_loc(armature_obj, 'root', 1, (0, 0, 0.02))
    pose_and_key_rot(armature_obj, 'deck', 1, (r(-10), 0, r(15)))
    pose_and_key_rot(armature_obj, 'body', 1, (r(-20), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 1, (r(-15), 0, r(-10)))
    pose_and_key_rot(armature_obj, 'arm.L', 1, (r(-25), 0, r(-20)))
    pose_and_key_rot(armature_obj, 'arm.R', 1, (r(-25), 0, r(20)))

    # Frame 2: spinning out
    pose_and_key_loc(armature_obj, 'root', 2, (-0.03, 0, -0.05))
    pose_and_key_rot(armature_obj, 'deck', 2, (r(10), 0, r(-20)))
    pose_and_key_rot(armature_obj, 'body', 2, (r(-30), 0, r(10)))
    pose_and_key_rot(armature_obj, 'head', 2, (r(-20), 0, r(15)))
    pose_and_key_rot(armature_obj, 'arm.L', 2, (r(-40), 0, r(-30)))
    pose_and_key_rot(armature_obj, 'arm.R', 2, (r(-40), 0, r(30)))

    # Frame 3: falling — tilted heavily
    pose_and_key_loc(armature_obj, 'root', 3, (-0.05, 0, -0.15))
    pose_and_key_rot(armature_obj, 'deck', 3, (r(25), 0, r(-30)))
    pose_and_key_rot(armature_obj, 'body', 3, (r(-40), 0, r(15)))
    pose_and_key_rot(armature_obj, 'head', 3, (r(-25), 0, r(20)))
    pose_and_key_rot(armature_obj, 'arm.L', 3, (r(-50), 0, r(-35)))
    pose_and_key_rot(armature_obj, 'arm.R', 3, (r(-50), 0, r(35)))

    # Frame 4: crashed — deck flipped, on ground
    pose_and_key_loc(armature_obj, 'root', 4, (-0.06, 0, -0.30))
    pose_and_key_rot(armature_obj, 'deck', 4, (r(45), 0, r(-40)))
    pose_and_key_rot(armature_obj, 'body', 4, (r(-50), 0, r(20)))
    pose_and_key_rot(armature_obj, 'head', 4, (r(-30), 0, r(25)))
    pose_and_key_rot(armature_obj, 'arm.L', 4, (r(-60), 0, r(-40)))
    pose_and_key_rot(armature_obj, 'arm.R', 4, (r(-60), 0, r(40)))


# ---------------------------------------------------------------------------
# Scene & Camera Setup
# ---------------------------------------------------------------------------

def setup_scene():
    """Configure scene for sprite rendering."""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 4
    scene.render.fps = 10

    # Sun light for flat look
    bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))
    sun = bpy.context.active_object
    sun.name = 'SpriteLight'
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(30), math.radians(10), math.radians(20))

    # Fill light
    bpy.ops.object.light_add(type='SUN', location=(-2, 2, 3))
    fill = bpy.context.active_object
    fill.name = 'FillLight'
    fill.data.energy = 1.5
    fill.rotation_euler = (math.radians(50), math.radians(-30), math.radians(-20))

    # World
    world = bpy.data.worlds.get('World')
    if world is None:
        world = bpy.data.worlds.new('World')
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0, 0, 0, 1)
        bg.inputs['Strength'].default_value = 0.0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Creating Flyer Enemy Model (DJ on Flying Turntable)")
    print("=" * 60)

    clear_scene()
    mats = create_materials()
    parts = create_body_meshes(mats)
    armature_obj = create_armature()
    parent_meshes_to_armature(parts, armature_obj)
    create_animations(armature_obj)
    setup_scene()

    # Set fly as default action
    bpy.context.view_layer.objects.active = armature_obj
    fly_action = bpy.data.actions.get('fly')
    if fly_action:
        armature_obj.animation_data.action = fly_action

    # Save
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blend_path = os.path.join(script_dir, 'flyer.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"\nSaved: {blend_path}")

    # Summary
    print(f"\nMeshes: {len([o for o in bpy.data.objects if o.type == 'MESH'])}")
    print(f"Bones: {len(armature_obj.data.bones)}")
    print(f"Actions: {len(bpy.data.actions)}")
    for act in bpy.data.actions:
        print(f"  {act.name}")
    print("\nDone!")


if __name__ == '__main__':
    main()
