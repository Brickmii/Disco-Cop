"""
Create the Disco Cop player model in Blender 5.0+.

Run via:
    blender -b -P create_player_model.py

Produces player.blend in the same directory as this script.
Character: 70s Disco Cop with afro, sunglasses, magenta jacket,
gold badge, white bell-bottoms, platform boots.

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
    mats['skin'] = make_material('Skin', 0.45, 0.25, 0.15)
    mats['afro'] = make_material('Afro', 0.05, 0.03, 0.02)
    mats['sunglasses'] = make_material('Sunglasses', 0.02, 0.02, 0.02)
    mats['jacket'] = make_material('Jacket', 0.8, 0.1, 0.5)       # magenta
    mats['badge'] = make_material('Badge', 0.9, 0.75, 0.1)        # gold
    mats['pants'] = make_material('Pants', 0.9, 0.9, 0.9)         # white
    mats['boots'] = make_material('Boots', 0.12, 0.08, 0.05)      # dark brown
    mats['hands'] = make_material('Hands', 0.45, 0.25, 0.15)      # same as skin
    return mats


# ---------------------------------------------------------------------------
# Mesh Creation
# ---------------------------------------------------------------------------

# The character fits within a 24x48 pixel frame at ortho_scale 2.0.
# Visible area: ~2.0 BU wide x ~2.0 BU tall.
# Character ~1.75 BU tall, feet at z=0.
# Proportions (ground up):
#   Boots:  0.00 - 0.15
#   Legs:   0.15 - 0.70
#   Torso:  0.70 - 1.20
#   Head:   1.20 - 1.55
#   Afro:   1.40 - 1.75

def create_body_meshes(mats):
    """Create all body part meshes and return them as a dict."""
    parts = {}

    # --- HEAD ---
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8, radius=0.24,
        location=(0, 0, 1.38))
    head = bpy.context.active_object
    head.name = 'Head'
    assign_material(head, mats['skin'])
    set_smooth(head, True)
    parts['head'] = head

    # --- AFRO ---
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8, radius=0.35,
        location=(0, 0, 1.50))
    afro = bpy.context.active_object
    afro.name = 'Afro'
    assign_material(afro, mats['afro'])
    set_smooth(afro, True)
    parts['afro'] = afro

    # --- SUNGLASSES ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.15, 0, 1.40))
    glasses = bpy.context.active_object
    glasses.name = 'Sunglasses'
    glasses.scale = (0.12, 0.22, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(glasses, mats['sunglasses'])
    parts['sunglasses'] = glasses

    # --- TORSO ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.95))
    torso = bpy.context.active_object
    torso.name = 'Torso'
    torso.scale = (0.48, 0.35, 0.28)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(torso, mats['jacket'])
    parts['torso'] = torso

    # --- BADGE ---
    bpy.ops.mesh.primitive_plane_add(size=0.08, location=(0.50, 0.05, 1.0))
    badge = bpy.context.active_object
    badge.name = 'Badge'
    badge.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_material(badge, mats['badge'])
    parts['badge'] = badge

    # --- LEFT UPPER ARM ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.12, depth=0.30, location=(0, 0.33, 1.05))
    parts['upper_arm_l'] = bpy.context.active_object
    parts['upper_arm_l'].name = 'UpperArm.L'
    assign_material(parts['upper_arm_l'], mats['jacket'])

    # --- LEFT LOWER ARM ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.10, depth=0.25, location=(0, 0.33, 0.78))
    parts['lower_arm_l'] = bpy.context.active_object
    parts['lower_arm_l'].name = 'LowerArm.L'
    assign_material(parts['lower_arm_l'], mats['skin'])

    # --- LEFT HAND ---
    bpy.ops.mesh.primitive_cube_add(size=0.14, location=(0, 0.33, 0.63))
    parts['hand_l'] = bpy.context.active_object
    parts['hand_l'].name = 'Hand.L'
    assign_material(parts['hand_l'], mats['hands'])

    # --- RIGHT UPPER ARM ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.12, depth=0.30, location=(0, -0.33, 1.05))
    parts['upper_arm_r'] = bpy.context.active_object
    parts['upper_arm_r'].name = 'UpperArm.R'
    assign_material(parts['upper_arm_r'], mats['jacket'])

    # --- RIGHT LOWER ARM ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.10, depth=0.25, location=(0, -0.33, 0.78))
    parts['lower_arm_r'] = bpy.context.active_object
    parts['lower_arm_r'].name = 'LowerArm.R'
    assign_material(parts['lower_arm_r'], mats['skin'])

    # --- RIGHT HAND ---
    bpy.ops.mesh.primitive_cube_add(size=0.14, location=(0, -0.33, 0.63))
    parts['hand_r'] = bpy.context.active_object
    parts['hand_r'].name = 'Hand.R'
    assign_material(parts['hand_r'], mats['hands'])

    # --- LEFT UPPER LEG ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.14, depth=0.30, location=(0, 0.12, 0.52))
    parts['upper_leg_l'] = bpy.context.active_object
    parts['upper_leg_l'].name = 'UpperLeg.L'
    assign_material(parts['upper_leg_l'], mats['pants'])

    # --- LEFT LOWER LEG (bell-bottom flare) ---
    bpy.ops.mesh.primitive_cone_add(
        vertices=8, radius1=0.22, radius2=0.14, depth=0.30,
        location=(0, 0.12, 0.22))
    parts['lower_leg_l'] = bpy.context.active_object
    parts['lower_leg_l'].name = 'LowerLeg.L'
    assign_material(parts['lower_leg_l'], mats['pants'])

    # --- LEFT BOOT ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.03, 0.12, 0.06))
    parts['boot_l'] = bpy.context.active_object
    parts['boot_l'].name = 'Boot.L'
    parts['boot_l'].scale = (0.26, 0.10, 0.06)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(parts['boot_l'], mats['boots'])

    # --- RIGHT UPPER LEG ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.14, depth=0.30, location=(0, -0.12, 0.52))
    parts['upper_leg_r'] = bpy.context.active_object
    parts['upper_leg_r'].name = 'UpperLeg.R'
    assign_material(parts['upper_leg_r'], mats['pants'])

    # --- RIGHT LOWER LEG (bell-bottom flare) ---
    bpy.ops.mesh.primitive_cone_add(
        vertices=8, radius1=0.22, radius2=0.14, depth=0.30,
        location=(0, -0.12, 0.22))
    parts['lower_leg_r'] = bpy.context.active_object
    parts['lower_leg_r'].name = 'LowerLeg.R'
    assign_material(parts['lower_leg_r'], mats['pants'])

    # --- RIGHT BOOT ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.03, -0.12, 0.06))
    parts['boot_r'] = bpy.context.active_object
    parts['boot_r'].name = 'Boot.R'
    parts['boot_r'].scale = (0.26, 0.10, 0.06)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(parts['boot_r'], mats['boots'])

    return parts


# ---------------------------------------------------------------------------
# Armature
# ---------------------------------------------------------------------------

def create_armature():
    """Create the character armature and return the armature object."""
    bpy.ops.object.armature_add(location=(0, 0, 0))
    armature_obj = bpy.context.active_object
    armature_obj.name = 'Armature'
    armature_obj.data.name = 'ArmatureData'

    bpy.ops.object.mode_set(mode='EDIT')
    arm = armature_obj.data

    # Remove default bone
    for bone in arm.edit_bones:
        arm.edit_bones.remove(bone)

    # --- Root ---
    root = arm.edit_bones.new('root')
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.15)

    # --- Spine ---
    spine = arm.edit_bones.new('spine')
    spine.head = (0, 0, 0.70)
    spine.tail = (0, 0, 0.95)
    spine.parent = root

    # --- Chest ---
    chest = arm.edit_bones.new('chest')
    chest.head = (0, 0, 0.95)
    chest.tail = (0, 0, 1.20)
    chest.parent = spine
    chest.use_connect = True

    # --- Head ---
    head_bone = arm.edit_bones.new('head')
    head_bone.head = (0, 0, 1.20)
    head_bone.tail = (0, 0, 1.55)
    head_bone.parent = chest
    head_bone.use_connect = True

    # --- Left arm ---
    upper_arm_l = arm.edit_bones.new('upper_arm.L')
    upper_arm_l.head = (0, 0.30, 1.15)
    upper_arm_l.tail = (0, 0.33, 0.90)
    upper_arm_l.parent = chest

    lower_arm_l = arm.edit_bones.new('lower_arm.L')
    lower_arm_l.head = (0, 0.33, 0.90)
    lower_arm_l.tail = (0, 0.33, 0.63)
    lower_arm_l.parent = upper_arm_l
    lower_arm_l.use_connect = True

    # --- Right arm ---
    upper_arm_r = arm.edit_bones.new('upper_arm.R')
    upper_arm_r.head = (0, -0.30, 1.15)
    upper_arm_r.tail = (0, -0.33, 0.90)
    upper_arm_r.parent = chest

    lower_arm_r = arm.edit_bones.new('lower_arm.R')
    lower_arm_r.head = (0, -0.33, 0.90)
    lower_arm_r.tail = (0, -0.33, 0.63)
    lower_arm_r.parent = upper_arm_r
    lower_arm_r.use_connect = True

    # --- Left leg ---
    upper_leg_l = arm.edit_bones.new('upper_leg.L')
    upper_leg_l.head = (0, 0.12, 0.70)
    upper_leg_l.tail = (0, 0.12, 0.37)
    upper_leg_l.parent = root

    lower_leg_l = arm.edit_bones.new('lower_leg.L')
    lower_leg_l.head = (0, 0.12, 0.37)
    lower_leg_l.tail = (0, 0.12, 0.12)
    lower_leg_l.parent = upper_leg_l
    lower_leg_l.use_connect = True

    foot_l = arm.edit_bones.new('foot.L')
    foot_l.head = (0, 0.12, 0.12)
    foot_l.tail = (0.12, 0.12, 0.0)
    foot_l.parent = lower_leg_l
    foot_l.use_connect = True

    # --- Right leg ---
    upper_leg_r = arm.edit_bones.new('upper_leg.R')
    upper_leg_r.head = (0, -0.12, 0.70)
    upper_leg_r.tail = (0, -0.12, 0.37)
    upper_leg_r.parent = root

    lower_leg_r = arm.edit_bones.new('lower_leg.R')
    lower_leg_r.head = (0, -0.12, 0.37)
    lower_leg_r.tail = (0, -0.12, 0.12)
    lower_leg_r.parent = upper_leg_r
    lower_leg_r.use_connect = True

    foot_r = arm.edit_bones.new('foot.R')
    foot_r.head = (0, -0.12, 0.12)
    foot_r.tail = (0.12, -0.12, 0.0)
    foot_r.parent = lower_leg_r
    foot_r.use_connect = True

    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj


# ---------------------------------------------------------------------------
# Parenting (mesh -> armature)
# ---------------------------------------------------------------------------

MESH_BONE_MAP = {
    'Head': 'head',
    'Afro': 'head',
    'Sunglasses': 'head',
    'Torso': 'chest',
    'Badge': 'chest',
    'UpperArm.L': 'upper_arm.L',
    'LowerArm.L': 'lower_arm.L',
    'Hand.L': 'lower_arm.L',
    'UpperArm.R': 'upper_arm.R',
    'LowerArm.R': 'lower_arm.R',
    'Hand.R': 'lower_arm.R',
    'UpperLeg.L': 'upper_leg.L',
    'LowerLeg.L': 'lower_leg.L',
    'Boot.L': 'foot.L',
    'UpperLeg.R': 'upper_leg.R',
    'LowerLeg.R': 'lower_leg.R',
    'Boot.R': 'foot.R',
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
# Animations (Blender 5.0 compatible — uses pose_bone.keyframe_insert)
# ---------------------------------------------------------------------------

def setup_pose_mode(armature_obj):
    """Enter pose mode and set all bones to Euler rotation."""
    bpy.context.view_layer.objects.active = armature_obj
    armature_obj.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    for pbone in armature_obj.pose.bones:
        pbone.rotation_mode = 'XYZ'


def reset_pose(armature_obj):
    """Reset all pose bones to rest position."""
    for pbone in armature_obj.pose.bones:
        pbone.location = (0, 0, 0)
        pbone.rotation_euler = (0, 0, 0)
        pbone.scale = (1, 1, 1)


def start_action(armature_obj, name):
    """Create a new action, assign it to the armature, and return it."""
    action = bpy.data.actions.new(name=name)
    action.use_fake_user = True
    if armature_obj.animation_data is None:
        armature_obj.animation_data_create()
    armature_obj.animation_data.action = action
    return action


def key_bone_loc(armature_obj, bone_name, frame):
    """Insert location keyframe for a pose bone at current values."""
    pbone = armature_obj.pose.bones[bone_name]
    pbone.keyframe_insert(data_path='location', frame=frame)


def key_bone_rot(armature_obj, bone_name, frame):
    """Insert rotation_euler keyframe for a pose bone at current values."""
    pbone = armature_obj.pose.bones[bone_name]
    pbone.keyframe_insert(data_path='rotation_euler', frame=frame)


def set_bone_loc(armature_obj, bone_name, loc):
    """Set pose bone location."""
    armature_obj.pose.bones[bone_name].location = loc


def set_bone_rot(armature_obj, bone_name, rot):
    """Set pose bone rotation_euler (expects radians tuple)."""
    armature_obj.pose.bones[bone_name].rotation_euler = rot


def pose_and_key_loc(armature_obj, bone_name, frame, loc):
    """Set location and insert keyframe."""
    set_bone_loc(armature_obj, bone_name, loc)
    key_bone_loc(armature_obj, bone_name, frame)


def pose_and_key_rot(armature_obj, bone_name, frame, rot):
    """Set rotation and insert keyframe."""
    set_bone_rot(armature_obj, bone_name, rot)
    key_bone_rot(armature_obj, bone_name, frame)


def create_animations(armature_obj):
    """Create all 6 animation actions."""
    setup_pose_mode(armature_obj)

    create_idle_action(armature_obj)
    create_run_action(armature_obj)
    create_jump_action(armature_obj)
    create_fall_action(armature_obj)
    create_double_jump_action(armature_obj)
    create_hurt_action(armature_obj)

    bpy.ops.object.mode_set(mode='OBJECT')


def create_idle_action(armature_obj):
    """Subtle bobbing and arm sway. Frames 1-4, looping."""
    reset_pose(armature_obj)
    action = start_action(armature_obj, 'idle')
    r = math.radians

    # Frame 1: neutral
    pose_and_key_loc(armature_obj, 'root', 1, (0, 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.L', 1, (0, 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.R', 1, (0, 0, 0))
    pose_and_key_rot(armature_obj, 'chest', 1, (0, 0, 0))
    pose_and_key_rot(armature_obj, 'head', 1, (0, 0, 0))

    # Frame 2: bob down, arms sway forward
    pose_and_key_loc(armature_obj, 'root', 2, (0, 0, -0.02))
    pose_and_key_rot(armature_obj, 'upper_arm.L', 2, (r(5), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.R', 2, (r(-5), 0, 0))
    pose_and_key_rot(armature_obj, 'chest', 2, (r(2), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 2, (r(-2), 0, 0))

    # Frame 3: neutral
    pose_and_key_loc(armature_obj, 'root', 3, (0, 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.L', 3, (0, 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.R', 3, (0, 0, 0))
    pose_and_key_rot(armature_obj, 'chest', 3, (0, 0, 0))
    pose_and_key_rot(armature_obj, 'head', 3, (0, 0, 0))

    # Frame 4: bob up, arms sway back
    pose_and_key_loc(armature_obj, 'root', 4, (0, 0, 0.01))
    pose_and_key_rot(armature_obj, 'upper_arm.L', 4, (r(-5), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.R', 4, (r(5), 0, 0))
    pose_and_key_rot(armature_obj, 'chest', 4, (r(-2), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 4, (r(2), 0, 0))


def create_run_action(armature_obj):
    """Full run cycle. Frames 1-8."""
    reset_pose(armature_obj)
    action = start_action(armature_obj, 'run')
    r = math.radians

    # (upper_leg.L, lower_leg.L, upper_leg.R, lower_leg.R, upper_arm.L, upper_arm.R, root_z)
    frames = [
        (r(30),  r(-10), r(-30), r(-5),  r(-25), r(25),  0.00),
        (r(20),  r(-20), r(-20), r(-30), r(-20), r(20), -0.03),
        (r(0),   r(-5),  r(0),   r(-5),  r(0),   r(0),   0.00),
        (r(-20), r(-5),  r(20),  r(-20), r(20),  r(-20),  0.02),
        (r(-30), r(-5),  r(30),  r(-10), r(25),  r(-25),  0.00),
        (r(-20), r(-30), r(20),  r(-20), r(20),  r(-20), -0.03),
        (r(0),   r(-5),  r(0),   r(-5),  r(0),   r(0),   0.00),
        (r(20),  r(-20), r(-20), r(-5),  r(-20), r(20),   0.02),
    ]

    for i, (ul_l, ll_l, ul_r, ll_r, ua_l, ua_r, rz) in enumerate(frames):
        f = i + 1
        pose_and_key_rot(armature_obj, 'upper_leg.L', f, (ul_l, 0, 0))
        pose_and_key_rot(armature_obj, 'lower_leg.L', f, (ll_l, 0, 0))
        pose_and_key_rot(armature_obj, 'upper_leg.R', f, (ul_r, 0, 0))
        pose_and_key_rot(armature_obj, 'lower_leg.R', f, (ll_r, 0, 0))
        pose_and_key_rot(armature_obj, 'upper_arm.L', f, (ua_l, 0, 0))
        pose_and_key_rot(armature_obj, 'upper_arm.R', f, (ua_r, 0, 0))
        pose_and_key_loc(armature_obj, 'root', f, (0, 0, rz))
        pose_and_key_rot(armature_obj, 'chest', f, (r(5), 0, 0))


def create_jump_action(armature_obj):
    """Crouch to launch. Frames 1-2."""
    reset_pose(armature_obj)
    action = start_action(armature_obj, 'jump')
    r = math.radians

    # Frame 1: crouch
    pose_and_key_loc(armature_obj, 'root', 1, (0, 0, -0.08))
    pose_and_key_rot(armature_obj, 'upper_leg.L', 1, (r(30), 0, 0))
    pose_and_key_rot(armature_obj, 'lower_leg.L', 1, (r(-40), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_leg.R', 1, (r(30), 0, 0))
    pose_and_key_rot(armature_obj, 'lower_leg.R', 1, (r(-40), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.L', 1, (r(15), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.R', 1, (r(15), 0, 0))
    pose_and_key_rot(armature_obj, 'chest', 1, (r(10), 0, 0))

    # Frame 2: launch
    pose_and_key_loc(armature_obj, 'root', 2, (0, 0, 0.05))
    pose_and_key_rot(armature_obj, 'upper_leg.L', 2, (r(-15), 0, 0))
    pose_and_key_rot(armature_obj, 'lower_leg.L', 2, (r(-5), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_leg.R', 2, (r(-15), 0, 0))
    pose_and_key_rot(armature_obj, 'lower_leg.R', 2, (r(-5), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.L', 2, (r(-40), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.R', 2, (r(-40), 0, 0))
    pose_and_key_rot(armature_obj, 'chest', 2, (r(-5), 0, 0))


def create_fall_action(armature_obj):
    """Arms up, legs dangling. Frames 1-2."""
    reset_pose(armature_obj)
    action = start_action(armature_obj, 'fall')
    r = math.radians

    # Frame 1
    pose_and_key_loc(armature_obj, 'root', 1, (0, 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.L', 1, (r(-50), 0, r(-15)))
    pose_and_key_rot(armature_obj, 'upper_arm.R', 1, (r(-50), 0, r(15)))
    pose_and_key_rot(armature_obj, 'lower_arm.L', 1, (r(20), 0, 0))
    pose_and_key_rot(armature_obj, 'lower_arm.R', 1, (r(20), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_leg.L', 1, (r(10), 0, 0))
    pose_and_key_rot(armature_obj, 'lower_leg.L', 1, (r(-15), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_leg.R', 1, (r(15), 0, 0))
    pose_and_key_rot(armature_obj, 'lower_leg.R', 1, (r(-20), 0, 0))

    # Frame 2
    pose_and_key_loc(armature_obj, 'root', 2, (0, 0, -0.02))
    pose_and_key_rot(armature_obj, 'upper_arm.L', 2, (r(-55), 0, r(-20)))
    pose_and_key_rot(armature_obj, 'upper_arm.R', 2, (r(-55), 0, r(20)))
    pose_and_key_rot(armature_obj, 'lower_arm.L', 2, (r(25), 0, 0))
    pose_and_key_rot(armature_obj, 'lower_arm.R', 2, (r(25), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_leg.L', 2, (r(15), 0, 0))
    pose_and_key_rot(armature_obj, 'lower_leg.L', 2, (r(-20), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_leg.R', 2, (r(20), 0, 0))
    pose_and_key_rot(armature_obj, 'lower_leg.R', 2, (r(-25), 0, 0))


def create_double_jump_action(armature_obj):
    """Spin/flip. Frames 1-4."""
    reset_pose(armature_obj)
    action = start_action(armature_obj, 'double_jump')
    r = math.radians

    for i in range(4):
        f = i + 1
        spin = r(90 * i)
        pose_and_key_rot(armature_obj, 'root', f, (spin, 0, 0))
        pose_and_key_rot(armature_obj, 'upper_leg.L', f, (r(45), 0, 0))
        pose_and_key_rot(armature_obj, 'lower_leg.L', f, (r(-80), 0, 0))
        pose_and_key_rot(armature_obj, 'upper_leg.R', f, (r(45), 0, 0))
        pose_and_key_rot(armature_obj, 'lower_leg.R', f, (r(-80), 0, 0))
        pose_and_key_rot(armature_obj, 'upper_arm.L', f, (r(-30), 0, r(-30)))
        pose_and_key_rot(armature_obj, 'upper_arm.R', f, (r(-30), 0, r(30)))
        pose_and_key_rot(armature_obj, 'chest', f, (r(15), 0, 0))


def create_hurt_action(armature_obj):
    """Knockback recoil. Frames 1-2."""
    reset_pose(armature_obj)
    action = start_action(armature_obj, 'hurt')
    r = math.radians

    # Frame 1: impact
    pose_and_key_loc(armature_obj, 'root', 1, (-0.05, 0, 0))
    pose_and_key_rot(armature_obj, 'chest', 1, (r(-15), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 1, (r(-10), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.L', 1, (r(-30), 0, r(-20)))
    pose_and_key_rot(armature_obj, 'upper_arm.R', 1, (r(-30), 0, r(20)))
    pose_and_key_rot(armature_obj, 'upper_leg.L', 1, (r(10), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_leg.R', 1, (r(10), 0, 0))

    # Frame 2: recovery
    pose_and_key_loc(armature_obj, 'root', 2, (-0.03, 0, -0.02))
    pose_and_key_rot(armature_obj, 'chest', 2, (r(-8), 0, 0))
    pose_and_key_rot(armature_obj, 'head', 2, (r(-5), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_arm.L', 2, (r(-15), 0, r(-10)))
    pose_and_key_rot(armature_obj, 'upper_arm.R', 2, (r(-15), 0, r(10)))
    pose_and_key_rot(armature_obj, 'upper_leg.L', 2, (r(5), 0, 0))
    pose_and_key_rot(armature_obj, 'upper_leg.R', 2, (r(5), 0, 0))


# ---------------------------------------------------------------------------
# Scene & Camera Setup
# ---------------------------------------------------------------------------

def setup_scene():
    """Configure scene for sprite rendering."""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 8
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
    print("Creating Disco Cop Player Model")
    print("=" * 60)

    clear_scene()
    mats = create_materials()
    parts = create_body_meshes(mats)
    armature_obj = create_armature()
    parent_meshes_to_armature(parts, armature_obj)
    create_animations(armature_obj)
    setup_scene()

    # Set idle as default action
    bpy.context.view_layer.objects.active = armature_obj
    idle_action = bpy.data.actions.get('idle')
    if idle_action:
        armature_obj.animation_data.action = idle_action

    # Save
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blend_path = os.path.join(script_dir, 'player.blend')
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
