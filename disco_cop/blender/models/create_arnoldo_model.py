"""
Create the Arnoldo boss model in Blender 5.0+.

Run via:
    blender -b -P create_arnoldo_model.py

Produces arnoldo.blend in the same directory as this script.
Character: Schwarzenegger-parody bodybuilder boss for Venice Beach (Level 02).
Massive V-taper torso, white tank top, red shorts, headband, sunglasses,
exposed muscular arms. Holds dumbbells. 48x80 pixel frame.

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
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def make_material(name, r, g, b):
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
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def set_smooth(obj, smooth=False):
    for poly in obj.data.polygons:
        poly.use_smooth = smooth


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

def create_materials():
    mats = {}
    mats['skin'] = make_material('Skin', 0.72, 0.52, 0.32)         # deep tan/bronze
    mats['tank_top'] = make_material('TankTop', 0.95, 0.95, 0.90)  # white tank
    mats['shorts'] = make_material('Shorts', 0.80, 0.12, 0.12)     # red gym shorts
    mats['headband'] = make_material('Headband', 0.85, 0.10, 0.10) # red headband
    mats['sunglasses'] = make_material('Sunglasses', 0.03, 0.03, 0.03)
    mats['hair'] = make_material('Hair', 0.20, 0.13, 0.08)         # dark brown flat-top
    mats['shoes'] = make_material('Shoes', 0.90, 0.90, 0.85)       # white sneakers
    mats['shoe_sole'] = make_material('ShoeSole', 0.25, 0.25, 0.25)
    mats['dumbbell_bar'] = make_material('DumbbellBar', 0.55, 0.55, 0.55)  # steel
    mats['dumbbell_weight'] = make_material('DumbbellWeight', 0.15, 0.15, 0.15)  # iron
    mats['hands'] = make_material('Hands', 0.72, 0.52, 0.32)
    return mats


# ---------------------------------------------------------------------------
# Mesh Creation
# ---------------------------------------------------------------------------

# 48x80 frame. ortho_scale=2.0.
# Visible: ~1.2 BU wide x 2.0 BU tall.
# Arnoldo is MASSIVE — fills the frame width.
#
# Proportions (ground up):
#   Shoes:       0.00 - 0.12
#   Shins:       0.10 - 0.40
#   Thighs:      0.40 - 0.70
#   Shorts:      0.50 - 0.72
#   Waist:       0.70
#   Tank/Torso:  0.70 - 1.15  (WIDE, V-taper)
#   Shoulders:   1.05 - 1.15  (very wide)
#   Upper arms:  0.85 - 1.12  (thick, exposed)
#   Forearms:    0.58 - 0.85
#   Hands:       0.52 - 0.58  (with dumbbells)
#   Neck:        1.12 - 1.20
#   Head:        1.18 - 1.45
#   Hair:        1.40 - 1.50  (flat-top)
#   Headband:    1.35 - 1.38
#   Sunglasses:  1.30

def create_body_meshes(mats):
    parts = {}

    # --- HEAD (big square jaw) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.32))
    head = bpy.context.active_object
    head.name = 'Head'
    head.scale = (0.20, 0.22, 0.18)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(head, mats['skin'])
    parts['head'] = head

    # --- HAIR (flat-top — flat cube on top of head) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.48))
    hair = bpy.context.active_object
    hair.name = 'Hair'
    hair.scale = (0.19, 0.21, 0.06)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(hair, mats['hair'])
    parts['hair'] = hair

    # --- HEADBAND (red band around forehead) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.38))
    headband = bpy.context.active_object
    headband.name = 'Headband'
    headband.scale = (0.22, 0.24, 0.03)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(headband, mats['headband'])
    parts['headband'] = headband

    # --- SUNGLASSES ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.16, 0, 1.32))
    glasses = bpy.context.active_object
    glasses.name = 'Sunglasses'
    glasses.scale = (0.06, 0.24, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(glasses, mats['sunglasses'])
    parts['sunglasses'] = glasses

    # --- NECK (thick) ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.12, depth=0.10, location=(0, 0, 1.17))
    neck = bpy.context.active_object
    neck.name = 'Neck'
    assign_material(neck, mats['skin'])
    parts['neck'] = neck

    # --- TORSO (massive V-taper: wide shoulders, narrow waist) ---
    # Upper torso (tank top, very wide)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.98))
    torso_upper = bpy.context.active_object
    torso_upper.name = 'TorsoUpper'
    torso_upper.scale = (0.28, 0.55, 0.18)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(torso_upper, mats['tank_top'])
    parts['torso_upper'] = torso_upper

    # Lower torso (waist, narrower)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.76))
    torso_lower = bpy.context.active_object
    torso_lower.name = 'TorsoLower'
    torso_lower.scale = (0.18, 0.38, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(torso_lower, mats['tank_top'])
    parts['torso_lower'] = torso_lower

    # --- SHORTS (red, above knees) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.62))
    shorts = bpy.context.active_object
    shorts.name = 'Shorts'
    shorts.scale = (0.16, 0.40, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(shorts, mats['shorts'])
    parts['shorts'] = shorts

    # --- LEFT UPPER ARM (thick, exposed skin — no sleeves) ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.14, depth=0.28, location=(0, 0.42, 1.00))
    parts['upper_arm_l'] = bpy.context.active_object
    parts['upper_arm_l'].name = 'UpperArm.L'
    assign_material(parts['upper_arm_l'], mats['skin'])

    # --- LEFT FOREARM ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.12, depth=0.26, location=(0, 0.42, 0.72))
    parts['lower_arm_l'] = bpy.context.active_object
    parts['lower_arm_l'].name = 'LowerArm.L'
    assign_material(parts['lower_arm_l'], mats['skin'])

    # --- LEFT HAND ---
    bpy.ops.mesh.primitive_cube_add(size=0.14, location=(0, 0.42, 0.55))
    parts['hand_l'] = bpy.context.active_object
    parts['hand_l'].name = 'Hand.L'
    assign_material(parts['hand_l'], mats['hands'])

    # --- LEFT DUMBBELL ---
    # Bar
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.025, depth=0.30,
        location=(0, 0.42, 0.50))
    dbell_bar_l = bpy.context.active_object
    dbell_bar_l.name = 'DumbbellBar.L'
    dbell_bar_l.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_material(dbell_bar_l, mats['dumbbell_bar'])
    parts['dbell_bar_l'] = dbell_bar_l

    # Weight plates (left side)
    for side, yoff in [(-0.14, 'DumbbellPlateA.L'), (0.14, 'DumbbellPlateB.L')]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=10, radius=0.08, depth=0.04,
            location=(0 + side, 0.42, 0.50))
        plate = bpy.context.active_object
        plate.name = yoff
        plate.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(plate, mats['dumbbell_weight'])
        parts[yoff.lower().replace('.', '_')] = plate

    # --- RIGHT UPPER ARM ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.14, depth=0.28, location=(0, -0.42, 1.00))
    parts['upper_arm_r'] = bpy.context.active_object
    parts['upper_arm_r'].name = 'UpperArm.R'
    assign_material(parts['upper_arm_r'], mats['skin'])

    # --- RIGHT FOREARM ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.12, depth=0.26, location=(0, -0.42, 0.72))
    parts['lower_arm_r'] = bpy.context.active_object
    parts['lower_arm_r'].name = 'LowerArm.R'
    assign_material(parts['lower_arm_r'], mats['skin'])

    # --- RIGHT HAND ---
    bpy.ops.mesh.primitive_cube_add(size=0.14, location=(0, -0.42, 0.55))
    parts['hand_r'] = bpy.context.active_object
    parts['hand_r'].name = 'Hand.R'
    assign_material(parts['hand_r'], mats['hands'])

    # --- RIGHT DUMBBELL ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.025, depth=0.30,
        location=(0, -0.42, 0.50))
    dbell_bar_r = bpy.context.active_object
    dbell_bar_r.name = 'DumbbellBar.R'
    dbell_bar_r.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_material(dbell_bar_r, mats['dumbbell_bar'])
    parts['dbell_bar_r'] = dbell_bar_r

    for side, yoff in [(-0.14, 'DumbbellPlateA.R'), (0.14, 'DumbbellPlateB.R')]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=10, radius=0.08, depth=0.04,
            location=(0 + side, -0.42, 0.50))
        plate = bpy.context.active_object
        plate.name = yoff
        plate.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        assign_material(plate, mats['dumbbell_weight'])
        parts[yoff.lower().replace('.', '_')] = plate

    # --- LEFT UPPER LEG ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.14, depth=0.24, location=(0, 0.16, 0.50))
    parts['upper_leg_l'] = bpy.context.active_object
    parts['upper_leg_l'].name = 'UpperLeg.L'
    assign_material(parts['upper_leg_l'], mats['skin'])

    # --- LEFT LOWER LEG ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.12, depth=0.26, location=(0, 0.16, 0.25))
    parts['lower_leg_l'] = bpy.context.active_object
    parts['lower_leg_l'].name = 'LowerLeg.L'
    assign_material(parts['lower_leg_l'], mats['skin'])

    # --- LEFT SHOE ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.03, 0.16, 0.08))
    parts['shoe_l'] = bpy.context.active_object
    parts['shoe_l'].name = 'Shoe.L'
    parts['shoe_l'].scale = (0.22, 0.12, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(parts['shoe_l'], mats['shoes'])

    # --- RIGHT UPPER LEG ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.14, depth=0.24, location=(0, -0.16, 0.50))
    parts['upper_leg_r'] = bpy.context.active_object
    parts['upper_leg_r'].name = 'UpperLeg.R'
    assign_material(parts['upper_leg_r'], mats['skin'])

    # --- RIGHT LOWER LEG ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.12, depth=0.26, location=(0, -0.16, 0.25))
    parts['lower_leg_r'] = bpy.context.active_object
    parts['lower_leg_r'].name = 'LowerLeg.R'
    assign_material(parts['lower_leg_r'], mats['skin'])

    # --- RIGHT SHOE ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.03, -0.16, 0.08))
    parts['shoe_r'] = bpy.context.active_object
    parts['shoe_r'].name = 'Shoe.R'
    parts['shoe_r'].scale = (0.22, 0.12, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(parts['shoe_r'], mats['shoes'])

    return parts


# ---------------------------------------------------------------------------
# Armature
# ---------------------------------------------------------------------------

def create_armature():
    bpy.ops.object.armature_add(location=(0, 0, 0))
    armature_obj = bpy.context.active_object
    armature_obj.name = 'Armature'
    armature_obj.data.name = 'ArmatureData'

    bpy.ops.object.mode_set(mode='EDIT')
    arm = armature_obj.data

    for bone in arm.edit_bones:
        arm.edit_bones.remove(bone)

    # --- Root ---
    root = arm.edit_bones.new('root')
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.15)

    # --- Spine ---
    spine = arm.edit_bones.new('spine')
    spine.head = (0, 0, 0.66)
    spine.tail = (0, 0, 0.86)
    spine.parent = root

    # --- Chest ---
    chest = arm.edit_bones.new('chest')
    chest.head = (0, 0, 0.86)
    chest.tail = (0, 0, 1.12)
    chest.parent = spine
    chest.use_connect = True

    # --- Head ---
    head_bone = arm.edit_bones.new('head')
    head_bone.head = (0, 0, 1.12)
    head_bone.tail = (0, 0, 1.50)
    head_bone.parent = chest
    head_bone.use_connect = True

    # --- Left arm ---
    upper_arm_l = arm.edit_bones.new('upper_arm.L')
    upper_arm_l.head = (0, 0.40, 1.10)
    upper_arm_l.tail = (0, 0.42, 0.86)
    upper_arm_l.parent = chest

    lower_arm_l = arm.edit_bones.new('lower_arm.L')
    lower_arm_l.head = (0, 0.42, 0.86)
    lower_arm_l.tail = (0, 0.42, 0.55)
    lower_arm_l.parent = upper_arm_l
    lower_arm_l.use_connect = True

    # --- Right arm ---
    upper_arm_r = arm.edit_bones.new('upper_arm.R')
    upper_arm_r.head = (0, -0.40, 1.10)
    upper_arm_r.tail = (0, -0.42, 0.86)
    upper_arm_r.parent = chest

    lower_arm_r = arm.edit_bones.new('lower_arm.R')
    lower_arm_r.head = (0, -0.42, 0.86)
    lower_arm_r.tail = (0, -0.42, 0.55)
    lower_arm_r.parent = upper_arm_r
    lower_arm_r.use_connect = True

    # --- Left leg ---
    upper_leg_l = arm.edit_bones.new('upper_leg.L')
    upper_leg_l.head = (0, 0.16, 0.66)
    upper_leg_l.tail = (0, 0.16, 0.38)
    upper_leg_l.parent = root

    lower_leg_l = arm.edit_bones.new('lower_leg.L')
    lower_leg_l.head = (0, 0.16, 0.38)
    lower_leg_l.tail = (0, 0.16, 0.12)
    lower_leg_l.parent = upper_leg_l
    lower_leg_l.use_connect = True

    foot_l = arm.edit_bones.new('foot.L')
    foot_l.head = (0, 0.16, 0.12)
    foot_l.tail = (0.12, 0.16, 0.0)
    foot_l.parent = lower_leg_l
    foot_l.use_connect = True

    # --- Right leg ---
    upper_leg_r = arm.edit_bones.new('upper_leg.R')
    upper_leg_r.head = (0, -0.16, 0.66)
    upper_leg_r.tail = (0, -0.16, 0.38)
    upper_leg_r.parent = root

    lower_leg_r = arm.edit_bones.new('lower_leg.R')
    lower_leg_r.head = (0, -0.16, 0.38)
    lower_leg_r.tail = (0, -0.16, 0.12)
    lower_leg_r.parent = upper_leg_r
    lower_leg_r.use_connect = True

    foot_r = arm.edit_bones.new('foot.R')
    foot_r.head = (0, -0.16, 0.12)
    foot_r.tail = (0.12, -0.16, 0.0)
    foot_r.parent = lower_leg_r
    foot_r.use_connect = True

    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj


# ---------------------------------------------------------------------------
# Parenting
# ---------------------------------------------------------------------------

MESH_BONE_MAP = {
    'Head': 'head',
    'Hair': 'head',
    'Headband': 'head',
    'Sunglasses': 'head',
    'Neck': 'chest',
    'TorsoUpper': 'chest',
    'TorsoLower': 'spine',
    'Shorts': 'spine',
    'UpperArm.L': 'upper_arm.L',
    'LowerArm.L': 'lower_arm.L',
    'Hand.L': 'lower_arm.L',
    'DumbbellBar.L': 'lower_arm.L',
    'DumbbellPlateA.L': 'lower_arm.L',
    'DumbbellPlateB.L': 'lower_arm.L',
    'UpperArm.R': 'upper_arm.R',
    'LowerArm.R': 'lower_arm.R',
    'Hand.R': 'lower_arm.R',
    'DumbbellBar.R': 'lower_arm.R',
    'DumbbellPlateA.R': 'lower_arm.R',
    'DumbbellPlateB.R': 'lower_arm.R',
    'UpperLeg.L': 'upper_leg.L',
    'LowerLeg.L': 'lower_leg.L',
    'Shoe.L': 'foot.L',
    'UpperLeg.R': 'upper_leg.R',
    'LowerLeg.R': 'lower_leg.R',
    'Shoe.R': 'foot.R',
}


def parent_meshes_to_armature(parts, armature_obj):
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
# Animations
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


def pkr(armature_obj, bone, frame, rot):
    """Pose and key rotation."""
    armature_obj.pose.bones[bone].rotation_euler = rot
    armature_obj.pose.bones[bone].keyframe_insert(data_path='rotation_euler', frame=frame)


def pkl(armature_obj, bone, frame, loc):
    """Pose and key location."""
    armature_obj.pose.bones[bone].location = loc
    armature_obj.pose.bones[bone].keyframe_insert(data_path='location', frame=frame)


def create_animations(armature_obj):
    setup_pose_mode(armature_obj)

    create_idle_action(armature_obj)
    create_flex_action(armature_obj)
    create_throw_action(armature_obj)
    create_sweep_action(armature_obj)
    create_hurt_action(armature_obj)
    create_death_action(armature_obj)

    bpy.ops.object.mode_set(mode='OBJECT')


def create_idle_action(armature_obj):
    """Bodybuilder posing — intimidating flex cycle. Frames 1-4, looping."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'idle')
    r = math.radians

    # Frame 1: front double bicep — classic pose
    pkl(armature_obj, 'root', 1, (0, 0, 0))
    pkr(armature_obj, 'spine', 1, (r(-5), 0, 0))
    pkr(armature_obj, 'chest', 1, (r(-8), 0, 0))
    pkr(armature_obj, 'head', 1, (r(5), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 1, (r(-90), 0, r(-20)))
    pkr(armature_obj, 'lower_arm.L', 1, (r(-60), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 1, (r(-90), 0, r(20)))
    pkr(armature_obj, 'lower_arm.R', 1, (r(-60), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 1, (r(5), 0, r(-3)))
    pkr(armature_obj, 'upper_leg.R', 1, (r(5), 0, r(3)))

    # Frame 2: side chest — turn slightly, one arm across
    pkl(armature_obj, 'root', 2, (0, 0, -0.02))
    pkr(armature_obj, 'spine', 2, (r(-3), r(5), r(-5)))
    pkr(armature_obj, 'chest', 2, (r(-10), r(5), r(-8)))
    pkr(armature_obj, 'head', 2, (r(3), 0, r(10)))
    pkr(armature_obj, 'upper_arm.L', 2, (r(-70), 0, r(-30)))
    pkr(armature_obj, 'lower_arm.L', 2, (r(-70), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 2, (r(20), 0, r(10)))
    pkr(armature_obj, 'lower_arm.R', 2, (r(-50), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 2, (r(8), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 2, (r(-5), 0, 0))

    # Frame 3: most muscular (crab pose) — hunched, arms in, tense
    pkl(armature_obj, 'root', 3, (0, 0, -0.04))
    pkr(armature_obj, 'spine', 3, (r(10), 0, 0))
    pkr(armature_obj, 'chest', 3, (r(5), 0, 0))
    pkr(armature_obj, 'head', 3, (r(-8), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 3, (r(-40), 0, r(-25)))
    pkr(armature_obj, 'lower_arm.L', 3, (r(-70), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 3, (r(-40), 0, r(25)))
    pkr(armature_obj, 'lower_arm.R', 3, (r(-70), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 3, (r(15), 0, r(-5)))
    pkr(armature_obj, 'upper_leg.R', 3, (r(15), 0, r(5)))
    pkr(armature_obj, 'lower_leg.L', 3, (r(-15), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 3, (r(-15), 0, 0))

    # Frame 4: back to standing, arms relaxed at sides (transition frame)
    pkl(armature_obj, 'root', 4, (0, 0, 0))
    pkr(armature_obj, 'spine', 4, (r(0), 0, 0))
    pkr(armature_obj, 'chest', 4, (r(-5), 0, 0))
    pkr(armature_obj, 'head', 4, (r(3), 0, r(-5)))
    pkr(armature_obj, 'upper_arm.L', 4, (r(-60), 0, r(-15)))
    pkr(armature_obj, 'lower_arm.L', 4, (r(-40), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 4, (r(-60), 0, r(15)))
    pkr(armature_obj, 'lower_arm.R', 4, (r(-40), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 4, (r(3), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 4, (r(3), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 4, (r(-3), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 4, (r(-3), 0, 0))


def create_flex_action(armature_obj):
    """Flexing shockwave attack — power pose that deals AoE. Frames 1-6."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'flex')
    r = math.radians

    # Frame 1: wind-up crouch, gathering power
    pkl(armature_obj, 'root', 1, (0, 0, -0.06))
    pkr(armature_obj, 'spine', 1, (r(15), 0, 0))
    pkr(armature_obj, 'chest', 1, (r(10), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 1, (r(15), 0, r(-15)))
    pkr(armature_obj, 'upper_arm.R', 1, (r(15), 0, r(15)))
    pkr(armature_obj, 'lower_arm.L', 1, (r(-30), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 1, (r(-30), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 1, (r(25), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 1, (r(25), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 1, (r(-40), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 1, (r(-40), 0, 0))

    # Frame 2: rising tension
    pkl(armature_obj, 'root', 2, (0, 0, -0.03))
    pkr(armature_obj, 'spine', 2, (r(5), 0, 0))
    pkr(armature_obj, 'chest', 2, (r(-5), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 2, (r(-50), 0, r(-20)))
    pkr(armature_obj, 'upper_arm.R', 2, (r(-50), 0, r(20)))
    pkr(armature_obj, 'lower_arm.L', 2, (r(-50), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 2, (r(-50), 0, 0))

    # Frame 3: EXPLOSIVE FLEX — full double bicep, standing tall
    pkl(armature_obj, 'root', 3, (0, 0, 0.03))
    pkr(armature_obj, 'spine', 3, (r(-8), 0, 0))
    pkr(armature_obj, 'chest', 3, (r(-15), 0, 0))
    pkr(armature_obj, 'head', 3, (r(10), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 3, (r(-100), 0, r(-35)))
    pkr(armature_obj, 'lower_arm.L', 3, (r(-80), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 3, (r(-100), 0, r(35)))
    pkr(armature_obj, 'lower_arm.R', 3, (r(-80), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 3, (r(-3), 0, r(-8)))
    pkr(armature_obj, 'upper_leg.R', 3, (r(-3), 0, r(8)))

    # Frame 4: hold flex (shockwave is active)
    pkl(armature_obj, 'root', 4, (0, 0, 0.02))
    pkr(armature_obj, 'spine', 4, (r(-6), 0, 0))
    pkr(armature_obj, 'chest', 4, (r(-12), 0, 0))
    pkr(armature_obj, 'head', 4, (r(8), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 4, (r(-95), 0, r(-32)))
    pkr(armature_obj, 'lower_arm.L', 4, (r(-75), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 4, (r(-95), 0, r(32)))
    pkr(armature_obj, 'lower_arm.R', 4, (r(-75), 0, 0))

    # Frame 5: relaxing
    pkl(armature_obj, 'root', 5, (0, 0, 0))
    pkr(armature_obj, 'spine', 5, (r(0), 0, 0))
    pkr(armature_obj, 'chest', 5, (r(-5), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 5, (r(-50), 0, r(-15)))
    pkr(armature_obj, 'upper_arm.R', 5, (r(-50), 0, r(15)))
    pkr(armature_obj, 'lower_arm.L', 5, (r(-40), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 5, (r(-40), 0, 0))

    # Frame 6: return to neutral
    pkl(armature_obj, 'root', 6, (0, 0, 0))
    pkr(armature_obj, 'spine', 6, (r(3), 0, 0))
    pkr(armature_obj, 'chest', 6, (r(0), 0, 0))
    pkr(armature_obj, 'head', 6, (r(0), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 6, (r(-20), 0, r(-5)))
    pkr(armature_obj, 'upper_arm.R', 6, (r(-20), 0, r(5)))
    pkr(armature_obj, 'lower_arm.L', 6, (r(-15), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 6, (r(-15), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 6, (r(3), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 6, (r(3), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 6, (r(-3), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 6, (r(-3), 0, 0))


def create_throw_action(armature_obj):
    """Dumbbell throw — wind up and hurl. Frames 1-6."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'throw')
    r = math.radians

    # Frame 1: pull back right arm (throwing arm)
    pkl(armature_obj, 'root', 1, (0, 0, 0))
    pkr(armature_obj, 'spine', 1, (r(5), r(-5), r(10)))
    pkr(armature_obj, 'chest', 1, (r(0), r(-8), r(10)))
    pkr(armature_obj, 'upper_arm.R', 1, (r(-40), 0, r(30)))
    pkr(armature_obj, 'lower_arm.R', 1, (r(-30), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 1, (r(10), 0, r(-10)))
    pkr(armature_obj, 'upper_leg.L', 1, (r(10), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 1, (r(-5), 0, 0))

    # Frame 2: deeper wind-up, weight shifts back
    pkl(armature_obj, 'root', 2, (-0.03, 0, 0))
    pkr(armature_obj, 'spine', 2, (r(8), r(-10), r(15)))
    pkr(armature_obj, 'chest', 2, (r(5), r(-12), r(15)))
    pkr(armature_obj, 'upper_arm.R', 2, (r(-60), 0, r(40)))
    pkr(armature_obj, 'lower_arm.R', 2, (r(-20), 0, 0))

    # Frame 3: RELEASE — arm whips forward
    pkl(armature_obj, 'root', 3, (0.02, 0, 0))
    pkr(armature_obj, 'spine', 3, (r(-5), r(5), r(-10)))
    pkr(armature_obj, 'chest', 3, (r(-10), r(8), r(-12)))
    pkr(armature_obj, 'head', 3, (r(5), 0, r(-10)))
    pkr(armature_obj, 'upper_arm.R', 3, (r(70), 0, r(10)))
    pkr(armature_obj, 'lower_arm.R', 3, (r(-5), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 3, (r(-20), 0, r(-15)))
    pkr(armature_obj, 'upper_leg.L', 3, (r(-5), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 3, (r(10), 0, 0))

    # Frame 4: follow through
    pkl(armature_obj, 'root', 4, (0.04, 0, -0.02))
    pkr(armature_obj, 'spine', 4, (r(-8), r(8), r(-15)))
    pkr(armature_obj, 'chest', 4, (r(-12), r(10), r(-15)))
    pkr(armature_obj, 'upper_arm.R', 4, (r(80), 0, r(5)))
    pkr(armature_obj, 'lower_arm.R', 4, (r(5), 0, 0))

    # Frame 5: recover weight
    pkl(armature_obj, 'root', 5, (0.02, 0, 0))
    pkr(armature_obj, 'spine', 5, (r(0), r(3), r(-5)))
    pkr(armature_obj, 'chest', 5, (r(-3), r(3), r(-5)))
    pkr(armature_obj, 'head', 5, (r(0), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 5, (r(30), 0, r(10)))
    pkr(armature_obj, 'lower_arm.R', 5, (r(-15), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 5, (r(0), 0, r(-5)))

    # Frame 6: back to stance
    pkl(armature_obj, 'root', 6, (0, 0, 0))
    pkr(armature_obj, 'spine', 6, (r(3), 0, 0))
    pkr(armature_obj, 'chest', 6, (r(0), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 6, (r(0), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 6, (r(0), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 6, (r(0), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 6, (r(3), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 6, (r(3), 0, 0))


def create_sweep_action(armature_obj):
    """Weight bench sweep — grab and swing wide. Frames 1-8."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'sweep')
    r = math.radians

    # Frame 1: reach down (picking up bench)
    pkl(armature_obj, 'root', 1, (0, 0, -0.06))
    pkr(armature_obj, 'spine', 1, (r(20), 0, 0))
    pkr(armature_obj, 'chest', 1, (r(15), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 1, (r(50), 0, r(-10)))
    pkr(armature_obj, 'upper_arm.R', 1, (r(50), 0, r(10)))
    pkr(armature_obj, 'lower_arm.L', 1, (r(-10), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 1, (r(-10), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 1, (r(25), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 1, (r(25), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 1, (r(-35), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 1, (r(-35), 0, 0))

    # Frame 2: lifting bench overhead
    pkl(armature_obj, 'root', 2, (0, 0, 0))
    pkr(armature_obj, 'spine', 2, (r(-5), 0, 0))
    pkr(armature_obj, 'chest', 2, (r(-10), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 2, (r(-80), 0, r(-20)))
    pkr(armature_obj, 'upper_arm.R', 2, (r(-80), 0, r(20)))
    pkr(armature_obj, 'lower_arm.L', 2, (r(10), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 2, (r(10), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 2, (r(5), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 2, (r(5), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 2, (r(-5), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 2, (r(-5), 0, 0))

    # Frame 3: held overhead, twisted right
    pkl(armature_obj, 'root', 3, (0, 0, 0.02))
    pkr(armature_obj, 'spine', 3, (r(-5), 0, r(15)))
    pkr(armature_obj, 'chest', 3, (r(-8), 0, r(20)))
    pkr(armature_obj, 'upper_arm.L', 3, (r(-120), 0, r(-20)))
    pkr(armature_obj, 'upper_arm.R', 3, (r(-120), 0, r(20)))
    pkr(armature_obj, 'lower_arm.L', 3, (r(15), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 3, (r(15), 0, 0))

    # Frame 4: SWING — sweeping left
    pkl(armature_obj, 'root', 4, (0, 0, 0))
    pkr(armature_obj, 'spine', 4, (r(5), 0, r(-20)))
    pkr(armature_obj, 'chest', 4, (r(0), 0, r(-25)))
    pkr(armature_obj, 'head', 4, (r(0), 0, r(-15)))
    pkr(armature_obj, 'upper_arm.L', 4, (r(-60), 0, r(-35)))
    pkr(armature_obj, 'upper_arm.R', 4, (r(-60), 0, r(5)))
    pkr(armature_obj, 'lower_arm.L', 4, (r(5), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 4, (r(5), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 4, (r(5), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 4, (r(10), 0, 0))

    # Frame 5: swing continues through
    pkl(armature_obj, 'root', 5, (0, 0, -0.02))
    pkr(armature_obj, 'spine', 5, (r(8), 0, r(-30)))
    pkr(armature_obj, 'chest', 5, (r(5), 0, r(-35)))
    pkr(armature_obj, 'head', 5, (r(0), 0, r(-20)))
    pkr(armature_obj, 'upper_arm.L', 5, (r(-30), 0, r(-40)))
    pkr(armature_obj, 'upper_arm.R', 5, (r(-30), 0, r(-10)))
    pkr(armature_obj, 'lower_arm.L', 5, (r(0), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 5, (r(0), 0, 0))

    # Frame 6: impact/end of sweep
    pkl(armature_obj, 'root', 6, (0, 0, -0.04))
    pkr(armature_obj, 'spine', 6, (r(10), 0, r(-20)))
    pkr(armature_obj, 'chest', 6, (r(8), 0, r(-25)))
    pkr(armature_obj, 'upper_arm.L', 6, (r(10), 0, r(-35)))
    pkr(armature_obj, 'upper_arm.R', 6, (r(10), 0, r(-15)))

    # Frame 7: recovering
    pkl(armature_obj, 'root', 7, (0, 0, -0.02))
    pkr(armature_obj, 'spine', 7, (r(5), 0, r(-8)))
    pkr(armature_obj, 'chest', 7, (r(3), 0, r(-8)))
    pkr(armature_obj, 'head', 7, (r(0), 0, r(-5)))
    pkr(armature_obj, 'upper_arm.L', 7, (r(-20), 0, r(-15)))
    pkr(armature_obj, 'upper_arm.R', 7, (r(-20), 0, r(5)))

    # Frame 8: neutral
    pkl(armature_obj, 'root', 8, (0, 0, 0))
    pkr(armature_obj, 'spine', 8, (r(3), 0, 0))
    pkr(armature_obj, 'chest', 8, (r(0), 0, 0))
    pkr(armature_obj, 'head', 8, (r(0), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 8, (r(0), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 8, (r(0), 0, 0))
    pkr(armature_obj, 'lower_arm.L', 8, (r(0), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 8, (r(0), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 8, (r(3), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 8, (r(3), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 8, (r(-3), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 8, (r(-3), 0, 0))


def create_hurt_action(armature_obj):
    """Recoil from hit. Frames 1-2."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'hurt')
    r = math.radians

    # Frame 1: knocked back, flinch
    pkl(armature_obj, 'root', 1, (-0.06, 0, 0))
    pkr(armature_obj, 'chest', 1, (r(-20), 0, 0))
    pkr(armature_obj, 'head', 1, (r(-15), 0, r(-10)))
    pkr(armature_obj, 'upper_arm.L', 1, (r(-30), 0, r(-25)))
    pkr(armature_obj, 'upper_arm.R', 1, (r(-30), 0, r(25)))
    pkr(armature_obj, 'lower_arm.L', 1, (r(-20), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 1, (r(-20), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 1, (r(8), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 1, (r(8), 0, 0))

    # Frame 2: recovering
    pkl(armature_obj, 'root', 2, (-0.03, 0, -0.02))
    pkr(armature_obj, 'chest', 2, (r(-10), 0, 0))
    pkr(armature_obj, 'head', 2, (r(-8), 0, r(-5)))
    pkr(armature_obj, 'upper_arm.L', 2, (r(-15), 0, r(-12)))
    pkr(armature_obj, 'upper_arm.R', 2, (r(-15), 0, r(12)))
    pkr(armature_obj, 'lower_arm.L', 2, (r(-10), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 2, (r(-10), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 2, (r(5), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 2, (r(5), 0, 0))


def create_death_action(armature_obj):
    """Dramatic bodybuilder death — staggers, flexes one last time, collapses. Frames 1-8."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'death')
    r = math.radians

    # Frame 1: initial stagger
    pkl(armature_obj, 'root', 1, (-0.04, 0, 0))
    pkr(armature_obj, 'chest', 1, (r(-15), 0, 0))
    pkr(armature_obj, 'head', 1, (r(-10), 0, r(-10)))
    pkr(armature_obj, 'upper_arm.L', 1, (r(-25), 0, r(-20)))
    pkr(armature_obj, 'upper_arm.R', 1, (r(-25), 0, r(20)))

    # Frame 2: hand to chest, "impossible..."
    pkl(armature_obj, 'root', 2, (-0.06, 0, -0.02))
    pkr(armature_obj, 'chest', 2, (r(-20), 0, r(5)))
    pkr(armature_obj, 'head', 2, (r(-12), 0, r(8)))
    pkr(armature_obj, 'upper_arm.L', 2, (r(25), 0, r(-10)))
    pkr(armature_obj, 'lower_arm.L', 2, (r(-50), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 2, (r(-40), 0, r(25)))

    # Frame 3: one last defiant flex
    pkl(armature_obj, 'root', 3, (-0.05, 0, -0.01))
    pkr(armature_obj, 'chest', 3, (r(-10), 0, 0))
    pkr(armature_obj, 'head', 3, (r(5), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 3, (r(-90), 0, r(-25)))
    pkr(armature_obj, 'lower_arm.L', 3, (r(-70), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 3, (r(-90), 0, r(25)))
    pkr(armature_obj, 'lower_arm.R', 3, (r(-70), 0, 0))

    # Frame 4: flex fails, stumble
    pkl(armature_obj, 'root', 4, (-0.08, 0, -0.06))
    pkr(armature_obj, 'chest', 4, (r(-35), 0, r(8)))
    pkr(armature_obj, 'head', 4, (r(-20), 0, r(10)))
    pkr(armature_obj, 'upper_arm.L', 4, (r(-60), 0, r(-30)))
    pkr(armature_obj, 'upper_arm.R', 4, (r(-50), 0, r(35)))
    pkr(armature_obj, 'lower_arm.L', 4, (r(-30), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 4, (r(-20), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 4, (r(15), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 4, (r(10), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 4, (r(-15), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 4, (r(-10), 0, 0))

    # Frame 5: knees buckle
    pkl(armature_obj, 'root', 5, (-0.10, 0, -0.15))
    pkr(armature_obj, 'chest', 5, (r(-50), 0, r(5)))
    pkr(armature_obj, 'head', 5, (r(-15), 0, r(12)))
    pkr(armature_obj, 'upper_arm.L', 5, (r(-55), 0, r(-35)))
    pkr(armature_obj, 'upper_arm.R', 5, (r(-45), 0, r(40)))
    pkr(armature_obj, 'upper_leg.L', 5, (r(30), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 5, (r(25), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 5, (r(-40), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 5, (r(-35), 0, 0))

    # Frame 6: collapsing
    pkl(armature_obj, 'root', 6, (-0.12, 0, -0.25))
    pkr(armature_obj, 'chest', 6, (r(-65), 0, 0))
    pkr(armature_obj, 'head', 6, (r(-10), 0, r(15)))
    pkr(armature_obj, 'upper_arm.L', 6, (r(-60), 0, r(-38)))
    pkr(armature_obj, 'upper_arm.R', 6, (r(-45), 0, r(42)))
    pkr(armature_obj, 'lower_arm.L', 6, (r(-15), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 6, (r(-10), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 6, (r(40), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 6, (r(35), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 6, (r(-55), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 6, (r(-50), 0, 0))

    # Frame 7: almost down — "I'll... be... back..."
    pkl(armature_obj, 'root', 7, (-0.14, 0, -0.35))
    pkr(armature_obj, 'chest', 7, (r(-75), 0, r(5)))
    pkr(armature_obj, 'head', 7, (r(-5), 0, r(15)))
    pkr(armature_obj, 'upper_arm.R', 7, (r(-90), 0, r(30)))
    pkr(armature_obj, 'lower_arm.R', 7, (r(-50), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 7, (r(-55), 0, r(-35)))
    pkr(armature_obj, 'upper_leg.L', 7, (r(45), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 7, (r(40), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 7, (r(-60), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 7, (r(-55), 0, 0))
    pkr(armature_obj, 'foot.L', 7, (r(20), 0, 0))
    pkr(armature_obj, 'foot.R', 7, (r(15), 0, 0))

    # Frame 8: flat — one fist still clenched
    pkl(armature_obj, 'root', 8, (-0.15, 0, -0.42))
    pkr(armature_obj, 'chest', 8, (r(-80), 0, 0))
    pkr(armature_obj, 'head', 8, (r(-5), 0, r(10)))
    pkr(armature_obj, 'upper_arm.R', 8, (r(-70), 0, r(35)))
    pkr(armature_obj, 'lower_arm.R', 8, (r(-30), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 8, (r(-50), 0, r(-40)))
    pkr(armature_obj, 'lower_arm.L', 8, (r(-15), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 8, (r(45), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 8, (r(40), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 8, (r(-60), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 8, (r(-55), 0, 0))
    pkr(armature_obj, 'foot.L', 8, (r(25), 0, 0))
    pkr(armature_obj, 'foot.R', 8, (r(20), 0, 0))


# ---------------------------------------------------------------------------
# Scene Setup
# ---------------------------------------------------------------------------

def setup_scene():
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 8
    scene.render.fps = 10

    bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))
    sun = bpy.context.active_object
    sun.name = 'SpriteLight'
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(30), math.radians(10), math.radians(20))

    bpy.ops.object.light_add(type='SUN', location=(-2, 2, 3))
    fill = bpy.context.active_object
    fill.name = 'FillLight'
    fill.data.energy = 1.5
    fill.rotation_euler = (math.radians(50), math.radians(-30), math.radians(-20))

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
    print("Creating Arnoldo Boss Model (Venice Beach)")
    print("=" * 60)

    clear_scene()
    mats = create_materials()
    parts = create_body_meshes(mats)
    armature_obj = create_armature()
    parent_meshes_to_armature(parts, armature_obj)
    create_animations(armature_obj)
    setup_scene()

    bpy.context.view_layer.objects.active = armature_obj
    idle_action = bpy.data.actions.get('idle')
    if idle_action:
        armature_obj.animation_data.action = idle_action

    script_dir = os.path.dirname(os.path.abspath(__file__))
    blend_path = os.path.join(script_dir, 'arnoldo.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"\nSaved: {blend_path}")

    print(f"\nMeshes: {len([o for o in bpy.data.objects if o.type == 'MESH'])}")
    print(f"Bones: {len(armature_obj.data.bones)}")
    print(f"Actions: {len(bpy.data.actions)}")
    for act in bpy.data.actions:
        print(f"  {act.name}")
    print("\nDone!")


if __name__ == '__main__':
    main()
