"""
Create the Disco King boss model in Blender 5.0+.

Run via:
    blender -b -P create_disco_king_model.py

Produces disco_king.blend in the same directory as this script.
Character: John Travolta-style disco fever dancer. Big, flashy boss
with white bell-bottom suit, gold chain, open chest, tall platform boots,
massive afro with crown. Always dancing. 48x80 pixel frame.

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
    mats['skin'] = make_material('Skin', 0.50, 0.30, 0.18)
    mats['afro'] = make_material('Afro', 0.06, 0.04, 0.03)
    mats['crown'] = make_material('Crown', 0.95, 0.80, 0.15)          # gold crown
    mats['sunglasses'] = make_material('Sunglasses', 0.02, 0.02, 0.02)
    mats['suit'] = make_material('Suit', 0.95, 0.95, 0.92)            # white suit
    mats['shirt'] = make_material('Shirt', 0.90, 0.15, 0.60)          # magenta open shirt
    mats['chain'] = make_material('Chain', 0.90, 0.75, 0.10)          # gold chain
    mats['belt'] = make_material('Belt', 0.90, 0.75, 0.10)            # gold belt
    mats['pants'] = make_material('Pants', 0.95, 0.95, 0.92)          # white bell-bottoms
    mats['boots'] = make_material('Boots', 0.90, 0.75, 0.10)          # gold platform boots
    mats['hands'] = make_material('Hands', 0.50, 0.30, 0.18)
    return mats


# ---------------------------------------------------------------------------
# Mesh Creation
# ---------------------------------------------------------------------------

# 48x80 pixel frame. ortho_scale=2.0.
# Visible area: 1.2 BU wide x 2.0 BU tall (48/80 * 2.0 = 1.2 wide).
# Character ~3.2 BU tall (bigger boss), scaled to fit in 2.0 BU visible height.
# Actually let's keep to ~1.9 BU total (body 1.6 + crown/afro 0.3) to fit frame.
#
# Proportions (ground up):
#   Boots:     0.00 - 0.20
#   Legs:      0.10 - 0.70
#   Belt:      0.70 - 0.74
#   Torso:     0.70 - 1.10
#   Chest/shirt: 0.95 - 1.10
#   Chain:     1.00
#   Arms:      0.65 - 1.10
#   Head:      1.10 - 1.45
#   Afro:      1.30 - 1.65
#   Crown:     1.60 - 1.75

def create_body_meshes(mats):
    parts = {}

    # --- HEAD ---
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=14, ring_count=10, radius=0.22,
        location=(0, 0, 1.28))
    head = bpy.context.active_object
    head.name = 'Head'
    assign_material(head, mats['skin'])
    set_smooth(head, True)
    parts['head'] = head

    # --- AFRO (big, boss-sized) ---
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=14, ring_count=10, radius=0.34,
        location=(0, 0, 1.45))
    afro = bpy.context.active_object
    afro.name = 'Afro'
    assign_material(afro, mats['afro'])
    set_smooth(afro, True)
    parts['afro'] = afro

    # --- CROWN (on top of afro) ---
    bpy.ops.mesh.primitive_cone_add(
        vertices=8, radius1=0.18, radius2=0.05, depth=0.18,
        location=(0, 0, 1.72))
    crown = bpy.context.active_object
    crown.name = 'Crown'
    assign_material(crown, mats['crown'])
    parts['crown'] = crown

    # --- SUNGLASSES ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.14, 0, 1.30))
    glasses = bpy.context.active_object
    glasses.name = 'Sunglasses'
    glasses.scale = (0.10, 0.24, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(glasses, mats['sunglasses'])
    parts['sunglasses'] = glasses

    # --- TORSO (suit jacket, wide shoulders) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.90))
    torso = bpy.context.active_object
    torso.name = 'Torso'
    torso.scale = (0.50, 0.40, 0.26)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(torso, mats['suit'])
    parts['torso'] = torso

    # --- OPEN SHIRT (V-neck, visible chest) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.18, 0, 0.98))
    shirt = bpy.context.active_object
    shirt.name = 'Shirt'
    shirt.scale = (0.10, 0.20, 0.16)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(shirt, mats['shirt'])
    parts['shirt'] = shirt

    # --- GOLD CHAIN ---
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.12, minor_radius=0.02,
        major_segments=12, minor_segments=4,
        location=(0.20, 0, 0.95))
    chain = bpy.context.active_object
    chain.name = 'Chain'
    chain.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    assign_material(chain, mats['chain'])
    parts['chain'] = chain

    # --- BELT ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.72))
    belt = bpy.context.active_object
    belt.name = 'Belt'
    belt.scale = (0.46, 0.36, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(belt, mats['belt'])
    parts['belt'] = belt

    # --- LEFT UPPER ARM ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.12, depth=0.28, location=(0, 0.35, 1.00))
    parts['upper_arm_l'] = bpy.context.active_object
    parts['upper_arm_l'].name = 'UpperArm.L'
    assign_material(parts['upper_arm_l'], mats['suit'])

    # --- LEFT LOWER ARM ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.10, depth=0.25, location=(0, 0.35, 0.74))
    parts['lower_arm_l'] = bpy.context.active_object
    parts['lower_arm_l'].name = 'LowerArm.L'
    assign_material(parts['lower_arm_l'], mats['skin'])

    # --- LEFT HAND ---
    bpy.ops.mesh.primitive_cube_add(size=0.14, location=(0, 0.35, 0.58))
    parts['hand_l'] = bpy.context.active_object
    parts['hand_l'].name = 'Hand.L'
    assign_material(parts['hand_l'], mats['hands'])

    # --- RIGHT UPPER ARM ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.12, depth=0.28, location=(0, -0.35, 1.00))
    parts['upper_arm_r'] = bpy.context.active_object
    parts['upper_arm_r'].name = 'UpperArm.R'
    assign_material(parts['upper_arm_r'], mats['suit'])

    # --- RIGHT LOWER ARM ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.10, depth=0.25, location=(0, -0.35, 0.74))
    parts['lower_arm_r'] = bpy.context.active_object
    parts['lower_arm_r'].name = 'LowerArm.R'
    assign_material(parts['lower_arm_r'], mats['skin'])

    # --- RIGHT HAND ---
    bpy.ops.mesh.primitive_cube_add(size=0.14, location=(0, -0.35, 0.58))
    parts['hand_r'] = bpy.context.active_object
    parts['hand_r'].name = 'Hand.R'
    assign_material(parts['hand_r'], mats['hands'])

    # --- LEFT UPPER LEG ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.14, depth=0.30, location=(0, 0.14, 0.50))
    parts['upper_leg_l'] = bpy.context.active_object
    parts['upper_leg_l'].name = 'UpperLeg.L'
    assign_material(parts['upper_leg_l'], mats['pants'])

    # --- LEFT LOWER LEG (bell-bottom flare) ---
    bpy.ops.mesh.primitive_cone_add(
        vertices=8, radius1=0.24, radius2=0.14, depth=0.30,
        location=(0, 0.14, 0.22))
    parts['lower_leg_l'] = bpy.context.active_object
    parts['lower_leg_l'].name = 'LowerLeg.L'
    assign_material(parts['lower_leg_l'], mats['pants'])

    # --- LEFT BOOT (tall platform) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.03, 0.14, 0.08))
    parts['boot_l'] = bpy.context.active_object
    parts['boot_l'].name = 'Boot.L'
    parts['boot_l'].scale = (0.28, 0.12, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(parts['boot_l'], mats['boots'])

    # --- RIGHT UPPER LEG ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.14, depth=0.30, location=(0, -0.14, 0.50))
    parts['upper_leg_r'] = bpy.context.active_object
    parts['upper_leg_r'].name = 'UpperLeg.R'
    assign_material(parts['upper_leg_r'], mats['pants'])

    # --- RIGHT LOWER LEG (bell-bottom flare) ---
    bpy.ops.mesh.primitive_cone_add(
        vertices=8, radius1=0.24, radius2=0.14, depth=0.30,
        location=(0, -0.14, 0.22))
    parts['lower_leg_r'] = bpy.context.active_object
    parts['lower_leg_r'].name = 'LowerLeg.R'
    assign_material(parts['lower_leg_r'], mats['pants'])

    # --- RIGHT BOOT (tall platform) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.03, -0.14, 0.08))
    parts['boot_r'] = bpy.context.active_object
    parts['boot_r'].name = 'Boot.R'
    parts['boot_r'].scale = (0.28, 0.12, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    assign_material(parts['boot_r'], mats['boots'])

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
    spine.head = (0, 0, 0.68)
    spine.tail = (0, 0, 0.90)
    spine.parent = root

    # --- Chest ---
    chest = arm.edit_bones.new('chest')
    chest.head = (0, 0, 0.90)
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
    upper_arm_l.head = (0, 0.32, 1.10)
    upper_arm_l.tail = (0, 0.35, 0.86)
    upper_arm_l.parent = chest

    lower_arm_l = arm.edit_bones.new('lower_arm.L')
    lower_arm_l.head = (0, 0.35, 0.86)
    lower_arm_l.tail = (0, 0.35, 0.58)
    lower_arm_l.parent = upper_arm_l
    lower_arm_l.use_connect = True

    # --- Right arm ---
    upper_arm_r = arm.edit_bones.new('upper_arm.R')
    upper_arm_r.head = (0, -0.32, 1.10)
    upper_arm_r.tail = (0, -0.35, 0.86)
    upper_arm_r.parent = chest

    lower_arm_r = arm.edit_bones.new('lower_arm.R')
    lower_arm_r.head = (0, -0.35, 0.86)
    lower_arm_r.tail = (0, -0.35, 0.58)
    lower_arm_r.parent = upper_arm_r
    lower_arm_r.use_connect = True

    # --- Left leg ---
    upper_leg_l = arm.edit_bones.new('upper_leg.L')
    upper_leg_l.head = (0, 0.14, 0.68)
    upper_leg_l.tail = (0, 0.14, 0.35)
    upper_leg_l.parent = root

    lower_leg_l = arm.edit_bones.new('lower_leg.L')
    lower_leg_l.head = (0, 0.14, 0.35)
    lower_leg_l.tail = (0, 0.14, 0.10)
    lower_leg_l.parent = upper_leg_l
    lower_leg_l.use_connect = True

    foot_l = arm.edit_bones.new('foot.L')
    foot_l.head = (0, 0.14, 0.10)
    foot_l.tail = (0.12, 0.14, 0.0)
    foot_l.parent = lower_leg_l
    foot_l.use_connect = True

    # --- Right leg ---
    upper_leg_r = arm.edit_bones.new('upper_leg.R')
    upper_leg_r.head = (0, -0.14, 0.68)
    upper_leg_r.tail = (0, -0.14, 0.35)
    upper_leg_r.parent = root

    lower_leg_r = arm.edit_bones.new('lower_leg.R')
    lower_leg_r.head = (0, -0.14, 0.35)
    lower_leg_r.tail = (0, -0.14, 0.10)
    lower_leg_r.parent = upper_leg_r
    lower_leg_r.use_connect = True

    foot_r = arm.edit_bones.new('foot.R')
    foot_r.head = (0, -0.14, 0.10)
    foot_r.tail = (0.12, -0.14, 0.0)
    foot_r.parent = lower_leg_r
    foot_r.use_connect = True

    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj


# ---------------------------------------------------------------------------
# Parenting
# ---------------------------------------------------------------------------

MESH_BONE_MAP = {
    'Head': 'head',
    'Afro': 'head',
    'Crown': 'head',
    'Sunglasses': 'head',
    'Torso': 'chest',
    'Shirt': 'chest',
    'Chain': 'chest',
    'Belt': 'spine',
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
    create_disco_ball_action(armature_obj)
    create_slam_action(armature_obj)
    create_laser_action(armature_obj)
    create_hurt_action(armature_obj)
    create_death_action(armature_obj)

    bpy.ops.object.mode_set(mode='OBJECT')


def create_idle_action(armature_obj):
    """Travolta disco dance — constant grooving. Frames 1-4, looping."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'idle')
    r = math.radians

    # Frame 1: classic Travolta — right arm up pointing, left on hip, lean left
    pkl(armature_obj, 'root', 1, (0, 0, 0))
    pkr(armature_obj, 'spine', 1, (r(5), 0, r(-8)))
    pkr(armature_obj, 'chest', 1, (r(-5), 0, r(-5)))
    pkr(armature_obj, 'head', 1, (r(-5), 0, r(10)))
    pkr(armature_obj, 'upper_arm.R', 1, (r(-120), 0, r(20)))
    pkr(armature_obj, 'lower_arm.R', 1, (r(30), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 1, (r(20), 0, r(-15)))
    pkr(armature_obj, 'lower_arm.L', 1, (r(-40), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 1, (r(5), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 1, (r(-10), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 1, (r(-5), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 1, (r(-15), 0, 0))

    # Frame 2: hip thrust right, arms swap — left up, right on hip
    pkl(armature_obj, 'root', 2, (0, 0, -0.03))
    pkr(armature_obj, 'spine', 2, (r(5), 0, r(8)))
    pkr(armature_obj, 'chest', 2, (r(-5), 0, r(5)))
    pkr(armature_obj, 'head', 2, (r(-5), 0, r(-10)))
    pkr(armature_obj, 'upper_arm.L', 2, (r(-120), 0, r(-20)))
    pkr(armature_obj, 'lower_arm.L', 2, (r(30), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 2, (r(20), 0, r(15)))
    pkr(armature_obj, 'lower_arm.R', 2, (r(-40), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 2, (r(5), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 2, (r(-10), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 2, (r(-5), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 2, (r(-15), 0, 0))

    # Frame 3: both arms up, legs wide — disco fever peak
    pkl(armature_obj, 'root', 3, (0, 0, 0.02))
    pkr(armature_obj, 'spine', 3, (r(-5), 0, 0))
    pkr(armature_obj, 'chest', 3, (r(-10), 0, 0))
    pkr(armature_obj, 'head', 3, (r(5), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 3, (r(-100), 0, r(-25)))
    pkr(armature_obj, 'lower_arm.L', 3, (r(20), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 3, (r(-100), 0, r(25)))
    pkr(armature_obj, 'lower_arm.R', 3, (r(20), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 3, (r(15), 0, r(-5)))
    pkr(armature_obj, 'upper_leg.R', 3, (r(15), 0, r(5)))
    pkr(armature_obj, 'lower_leg.L', 3, (r(-10), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 3, (r(-10), 0, 0))

    # Frame 4: drop down, compact — ready to spring back to frame 1
    pkl(armature_obj, 'root', 4, (0, 0, -0.04))
    pkr(armature_obj, 'spine', 4, (r(10), 0, 0))
    pkr(armature_obj, 'chest', 4, (r(5), 0, 0))
    pkr(armature_obj, 'head', 4, (r(-8), 0, r(5)))
    pkr(armature_obj, 'upper_arm.L', 4, (r(-30), 0, r(-10)))
    pkr(armature_obj, 'lower_arm.L', 4, (r(-20), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 4, (r(-30), 0, r(10)))
    pkr(armature_obj, 'lower_arm.R', 4, (r(-20), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 4, (r(25), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 4, (r(25), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 4, (r(-35), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 4, (r(-35), 0, 0))


def create_disco_ball_action(armature_obj):
    """Radial projectile burst — dramatic pose. Frames 1-6."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'disco_ball')
    r = math.radians

    # Frame 1: crouch gather energy
    pkl(armature_obj, 'root', 1, (0, 0, -0.06))
    pkr(armature_obj, 'spine', 1, (r(15), 0, 0))
    pkr(armature_obj, 'chest', 1, (r(10), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 1, (r(30), 0, r(-20)))
    pkr(armature_obj, 'upper_arm.R', 1, (r(30), 0, r(20)))
    pkr(armature_obj, 'lower_arm.L', 1, (r(-30), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 1, (r(-30), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 1, (r(25), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 1, (r(25), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 1, (r(-40), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 1, (r(-40), 0, 0))

    # Frame 2: rising
    pkl(armature_obj, 'root', 2, (0, 0, -0.02))
    pkr(armature_obj, 'spine', 2, (r(5), 0, 0))
    pkr(armature_obj, 'chest', 2, (r(-5), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 2, (r(-60), 0, r(-15)))
    pkr(armature_obj, 'upper_arm.R', 2, (r(-60), 0, r(15)))
    pkr(armature_obj, 'lower_arm.L', 2, (r(10), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 2, (r(10), 0, 0))

    # Frame 3: BURST — arms spread wide, chest open
    pkl(armature_obj, 'root', 3, (0, 0, 0.04))
    pkr(armature_obj, 'spine', 3, (r(-10), 0, 0))
    pkr(armature_obj, 'chest', 3, (r(-15), 0, 0))
    pkr(armature_obj, 'head', 3, (r(10), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 3, (r(-110), 0, r(-35)))
    pkr(armature_obj, 'upper_arm.R', 3, (r(-110), 0, r(35)))
    pkr(armature_obj, 'lower_arm.L', 3, (r(15), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 3, (r(15), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 3, (r(-5), 0, r(-10)))
    pkr(armature_obj, 'upper_leg.R', 3, (r(-5), 0, r(10)))

    # Frame 4: hold pose
    pkl(armature_obj, 'root', 4, (0, 0, 0.03))
    pkr(armature_obj, 'spine', 4, (r(-8), 0, 0))
    pkr(armature_obj, 'chest', 4, (r(-12), 0, 0))
    pkr(armature_obj, 'head', 4, (r(8), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 4, (r(-105), 0, r(-30)))
    pkr(armature_obj, 'upper_arm.R', 4, (r(-105), 0, r(30)))

    # Frame 5: recover
    pkl(armature_obj, 'root', 5, (0, 0, 0))
    pkr(armature_obj, 'spine', 5, (r(0), 0, 0))
    pkr(armature_obj, 'chest', 5, (r(-5), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 5, (r(-50), 0, r(-15)))
    pkr(armature_obj, 'upper_arm.R', 5, (r(-50), 0, r(15)))

    # Frame 6: return to dance stance
    pkl(armature_obj, 'root', 6, (0, 0, 0))
    pkr(armature_obj, 'spine', 6, (r(5), 0, 0))
    pkr(armature_obj, 'chest', 6, (r(0), 0, 0))
    pkr(armature_obj, 'head', 6, (r(0), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 6, (r(-20), 0, r(-5)))
    pkr(armature_obj, 'upper_arm.R', 6, (r(-20), 0, r(5)))
    pkr(armature_obj, 'upper_leg.L', 6, (r(5), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 6, (r(5), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 6, (r(-5), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 6, (r(-5), 0, 0))


def create_slam_action(armature_obj):
    """Ground slam — jump up, slam down, shockwave. Frames 1-8."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'slam')
    r = math.radians

    # Frame 1: crouch wind-up
    pkl(armature_obj, 'root', 1, (0, 0, -0.06))
    pkr(armature_obj, 'spine', 1, (r(15), 0, 0))
    pkr(armature_obj, 'chest', 1, (r(10), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 1, (r(20), 0, r(-10)))
    pkr(armature_obj, 'upper_arm.R', 1, (r(20), 0, r(10)))
    pkr(armature_obj, 'upper_leg.L', 1, (r(30), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 1, (r(30), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 1, (r(-45), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 1, (r(-45), 0, 0))

    # Frame 2: launch up
    pkl(armature_obj, 'root', 2, (0, 0, 0.10))
    pkr(armature_obj, 'spine', 2, (r(-10), 0, 0))
    pkr(armature_obj, 'chest', 2, (r(-15), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 2, (r(-80), 0, r(-20)))
    pkr(armature_obj, 'upper_arm.R', 2, (r(-80), 0, r(20)))
    pkr(armature_obj, 'upper_leg.L', 2, (r(-15), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 2, (r(-15), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 2, (r(-5), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 2, (r(-5), 0, 0))

    # Frame 3: peak — arms up, legs tucked
    pkl(armature_obj, 'root', 3, (0, 0, 0.18))
    pkr(armature_obj, 'spine', 3, (r(-5), 0, 0))
    pkr(armature_obj, 'chest', 3, (r(-10), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 3, (r(-130), 0, r(-25)))
    pkr(armature_obj, 'upper_arm.R', 3, (r(-130), 0, r(25)))
    pkr(armature_obj, 'lower_arm.L', 3, (r(20), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 3, (r(20), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 3, (r(20), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 3, (r(20), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 3, (r(-40), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 3, (r(-40), 0, 0))

    # Frame 4: angling down — arms forward for slam
    pkl(armature_obj, 'root', 4, (0, 0, 0.12))
    pkr(armature_obj, 'spine', 4, (r(15), 0, 0))
    pkr(armature_obj, 'chest', 4, (r(20), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 4, (r(40), 0, r(-10)))
    pkr(armature_obj, 'upper_arm.R', 4, (r(40), 0, r(10)))
    pkr(armature_obj, 'lower_arm.L', 4, (r(-10), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 4, (r(-10), 0, 0))

    # Frame 5: coming down fast
    pkl(armature_obj, 'root', 5, (0, 0, 0.04))
    pkr(armature_obj, 'spine', 5, (r(20), 0, 0))
    pkr(armature_obj, 'chest', 5, (r(25), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 5, (r(60), 0, r(-5)))
    pkr(armature_obj, 'upper_arm.R', 5, (r(60), 0, r(5)))

    # Frame 6: IMPACT — slam pose, crouched deep
    pkl(armature_obj, 'root', 6, (0, 0, -0.08))
    pkr(armature_obj, 'spine', 6, (r(25), 0, 0))
    pkr(armature_obj, 'chest', 6, (r(15), 0, 0))
    pkr(armature_obj, 'head', 6, (r(10), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 6, (r(70), 0, r(-15)))
    pkr(armature_obj, 'upper_arm.R', 6, (r(70), 0, r(15)))
    pkr(armature_obj, 'lower_arm.L', 6, (r(-5), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 6, (r(-5), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 6, (r(35), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 6, (r(35), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 6, (r(-50), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 6, (r(-50), 0, 0))

    # Frame 7: shockwave reverberation
    pkl(armature_obj, 'root', 7, (0, 0, -0.04))
    pkr(armature_obj, 'spine', 7, (r(15), 0, 0))
    pkr(armature_obj, 'chest', 7, (r(8), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 7, (r(30), 0, r(-10)))
    pkr(armature_obj, 'upper_arm.R', 7, (r(30), 0, r(10)))
    pkr(armature_obj, 'upper_leg.L', 7, (r(20), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 7, (r(20), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 7, (r(-25), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 7, (r(-25), 0, 0))

    # Frame 8: standing back up
    pkl(armature_obj, 'root', 8, (0, 0, 0))
    pkr(armature_obj, 'spine', 8, (r(5), 0, 0))
    pkr(armature_obj, 'chest', 8, (r(0), 0, 0))
    pkr(armature_obj, 'head', 8, (r(0), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 8, (r(0), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 8, (r(0), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 8, (r(5), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 8, (r(5), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 8, (r(-5), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 8, (r(-5), 0, 0))


def create_laser_action(armature_obj):
    """Laser sweep — one arm extended, sweeping. Frames 1-6."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'laser')
    r = math.radians

    # Frame 1: plant feet, aim right arm forward
    pkl(armature_obj, 'root', 1, (0, 0, 0))
    pkr(armature_obj, 'chest', 1, (r(5), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 1, (r(80), 0, r(10)))
    pkr(armature_obj, 'lower_arm.R', 1, (r(-5), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 1, (r(15), 0, r(-10)))

    # Frame 2: sweep up-right
    pkr(armature_obj, 'chest', 2, (r(-5), 0, r(-5)))
    pkr(armature_obj, 'upper_arm.R', 2, (r(-40), 0, r(15)))
    pkr(armature_obj, 'lower_arm.R', 2, (r(5), 0, 0))
    pkr(armature_obj, 'head', 2, (r(-5), 0, r(-5)))
    pkr(armature_obj, 'upper_arm.L', 2, (r(10), 0, r(-15)))

    # Frame 3: sweep across high
    pkr(armature_obj, 'chest', 3, (r(-10), 0, r(5)))
    pkr(armature_obj, 'upper_arm.R', 3, (r(-80), 0, r(20)))
    pkr(armature_obj, 'lower_arm.R', 3, (r(15), 0, 0))
    pkr(armature_obj, 'head', 3, (r(0), 0, r(5)))

    # Frame 4: sweep down-left
    pkr(armature_obj, 'chest', 4, (r(5), 0, r(10)))
    pkr(armature_obj, 'upper_arm.R', 4, (r(40), 0, r(25)))
    pkr(armature_obj, 'lower_arm.R', 4, (r(-10), 0, 0))
    pkr(armature_obj, 'head', 4, (r(5), 0, r(10)))

    # Frame 5: sweep low
    pkr(armature_obj, 'chest', 5, (r(10), 0, r(5)))
    pkr(armature_obj, 'upper_arm.R', 5, (r(70), 0, r(15)))
    pkr(armature_obj, 'lower_arm.R', 5, (r(-5), 0, 0))
    pkr(armature_obj, 'head', 5, (r(8), 0, r(5)))

    # Frame 6: return
    pkr(armature_obj, 'chest', 6, (r(0), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 6, (r(0), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 6, (r(0), 0, 0))
    pkr(armature_obj, 'head', 6, (r(0), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 6, (r(0), 0, 0))


def create_hurt_action(armature_obj):
    """Recoil. Frames 1-2."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'hurt')
    r = math.radians

    # Frame 1: knocked back
    pkl(armature_obj, 'root', 1, (-0.06, 0, 0))
    pkr(armature_obj, 'chest', 1, (r(-20), 0, 0))
    pkr(armature_obj, 'head', 1, (r(-15), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 1, (r(-35), 0, r(-25)))
    pkr(armature_obj, 'upper_arm.R', 1, (r(-35), 0, r(25)))
    pkr(armature_obj, 'upper_leg.L', 1, (r(10), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 1, (r(10), 0, 0))

    # Frame 2: recover
    pkl(armature_obj, 'root', 2, (-0.03, 0, -0.02))
    pkr(armature_obj, 'chest', 2, (r(-10), 0, 0))
    pkr(armature_obj, 'head', 2, (r(-8), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 2, (r(-20), 0, r(-12)))
    pkr(armature_obj, 'upper_arm.R', 2, (r(-20), 0, r(12)))
    pkr(armature_obj, 'upper_leg.L', 2, (r(5), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 2, (r(5), 0, 0))


def create_death_action(armature_obj):
    """Dramatic death — staggers, spins, collapses. Frames 1-8."""
    reset_pose(armature_obj)
    start_action(armature_obj, 'death')
    r = math.radians

    # Frame 1: initial hit stagger
    pkl(armature_obj, 'root', 1, (-0.04, 0, 0))
    pkr(armature_obj, 'chest', 1, (r(-15), 0, 0))
    pkr(armature_obj, 'head', 1, (r(-10), 0, r(-10)))
    pkr(armature_obj, 'upper_arm.L', 1, (r(-25), 0, r(-15)))
    pkr(armature_obj, 'upper_arm.R', 1, (r(-25), 0, r(15)))

    # Frame 2: dramatic stagger — one hand to chest
    pkl(armature_obj, 'root', 2, (-0.06, 0, -0.02))
    pkr(armature_obj, 'chest', 2, (r(-25), 0, r(5)))
    pkr(armature_obj, 'head', 2, (r(-15), 0, r(10)))
    pkr(armature_obj, 'upper_arm.L', 2, (r(30), 0, r(-10)))
    pkr(armature_obj, 'lower_arm.L', 2, (r(-40), 0, 0))
    pkr(armature_obj, 'upper_arm.R', 2, (r(-40), 0, r(20)))

    # Frame 3: spinning — arms flail
    pkl(armature_obj, 'root', 3, (-0.08, 0, -0.04))
    pkr(armature_obj, 'chest', 3, (r(-35), 0, r(-10)))
    pkr(armature_obj, 'head', 3, (r(-20), 0, r(-15)))
    pkr(armature_obj, 'upper_arm.L', 3, (r(-50), 0, r(-30)))
    pkr(armature_obj, 'upper_arm.R', 3, (r(-60), 0, r(35)))
    pkr(armature_obj, 'lower_arm.L', 3, (r(25), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 3, (r(20), 0, 0))

    # Frame 4: leaning far back
    pkl(armature_obj, 'root', 4, (-0.10, 0, -0.08))
    pkr(armature_obj, 'chest', 4, (r(-50), 0, 0))
    pkr(armature_obj, 'head', 4, (r(-25), 0, r(5)))
    pkr(armature_obj, 'upper_arm.L', 4, (r(-70), 0, r(-35)))
    pkr(armature_obj, 'upper_arm.R', 4, (r(-70), 0, r(35)))
    pkr(armature_obj, 'upper_leg.L', 4, (r(15), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 4, (r(15), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 4, (r(-15), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 4, (r(-15), 0, 0))

    # Frame 5: knees buckling
    pkl(armature_obj, 'root', 5, (-0.10, 0, -0.15))
    pkr(armature_obj, 'chest', 5, (r(-60), 0, r(5)))
    pkr(armature_obj, 'head', 5, (r(-20), 0, r(10)))
    pkr(armature_obj, 'upper_arm.L', 5, (r(-60), 0, r(-40)))
    pkr(armature_obj, 'upper_arm.R', 5, (r(-55), 0, r(45)))
    pkr(armature_obj, 'upper_leg.L', 5, (r(30), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 5, (r(25), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 5, (r(-40), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 5, (r(-35), 0, 0))

    # Frame 6: collapsing
    pkl(armature_obj, 'root', 6, (-0.12, 0, -0.25))
    pkr(armature_obj, 'chest', 6, (r(-70), 0, 0))
    pkr(armature_obj, 'head', 6, (r(-15), 0, r(15)))
    pkr(armature_obj, 'upper_arm.L', 6, (r(-65), 0, r(-40)))
    pkr(armature_obj, 'upper_arm.R', 6, (r(-50), 0, r(45)))
    pkr(armature_obj, 'lower_arm.L', 6, (r(30), 0, 0))
    pkr(armature_obj, 'lower_arm.R', 6, (r(25), 0, 0))
    pkr(armature_obj, 'upper_leg.L', 6, (r(40), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 6, (r(35), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 6, (r(-55), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 6, (r(-50), 0, 0))

    # Frame 7: almost down — dramatic final reach
    pkl(armature_obj, 'root', 7, (-0.14, 0, -0.35))
    pkr(armature_obj, 'chest', 7, (r(-75), 0, r(5)))
    pkr(armature_obj, 'head', 7, (r(-10), 0, r(15)))
    pkr(armature_obj, 'upper_arm.R', 7, (r(-100), 0, r(30)))
    pkr(armature_obj, 'lower_arm.R', 7, (r(20), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 7, (r(-60), 0, r(-35)))
    pkr(armature_obj, 'upper_leg.L', 7, (r(45), 0, 0))
    pkr(armature_obj, 'upper_leg.R', 7, (r(40), 0, 0))
    pkr(armature_obj, 'lower_leg.L', 7, (r(-60), 0, 0))
    pkr(armature_obj, 'lower_leg.R', 7, (r(-55), 0, 0))
    pkr(armature_obj, 'foot.L', 7, (r(20), 0, 0))
    pkr(armature_obj, 'foot.R', 7, (r(15), 0, 0))

    # Frame 8: flat on ground — one arm still reaching up (Travolta style)
    pkl(armature_obj, 'root', 8, (-0.15, 0, -0.42))
    pkr(armature_obj, 'chest', 8, (r(-80), 0, 0))
    pkr(armature_obj, 'head', 8, (r(-5), 0, r(10)))
    pkr(armature_obj, 'upper_arm.R', 8, (r(-120), 0, r(25)))
    pkr(armature_obj, 'lower_arm.R', 8, (r(15), 0, 0))
    pkr(armature_obj, 'upper_arm.L', 8, (r(-50), 0, r(-40)))
    pkr(armature_obj, 'lower_arm.L', 8, (r(30), 0, 0))
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
    print("Creating Disco King Boss Model")
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
    blend_path = os.path.join(script_dir, 'disco_king.blend')
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
