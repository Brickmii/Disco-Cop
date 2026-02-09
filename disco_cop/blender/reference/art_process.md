# Disco Cop — Art Production Process

## 1. Overview

This document captures the exact process used to create the player model and render its sprite sheets. It exists so that future Claude Code sessions (or any contributor) can reproduce the pipeline for every remaining entity without rediscovering the pitfalls.

**Audience:** Claude Code sessions working on Disco Cop art assets.
**Companion doc:** `art_build_plan.md` (same directory) — specs for every entity's animations, sizes, and render commands.

---

## 2. Why Programmatic Modeling

We write Python scripts that build Blender models from scratch rather than modeling interactively. Reasons:

1. **Repeatability.** Running the script always produces the same .blend file. No "what did I click?" ambiguity.
2. **Version control.** A `.py` file diffs cleanly in git. A `.blend` is a binary blob.
3. **Automation.** The full pipeline (model → render → sprite sheet) runs headless via `blender -b`. No GUI needed.
4. **AI-friendly.** Claude Code can write, read, and modify Python. It cannot operate a Blender GUI.
5. **Tiny output target.** Sprites are 24×48 pixels. Complex manual modeling is wasted — low-poly programmatic geometry is the right fidelity level.

---

## 3. Pipeline Steps

Every entity follows these 6 steps in order:

### Step 1: Write the model script
Create `disco_cop/blender/models/create_{entity}_model.py`. This script:
- Clears the scene
- Creates materials (flat colors, no textures)
- Builds all meshes (body parts as primitives)
- Creates an armature with bones
- Parents meshes to bones via vertex groups
- Creates animation actions with keyframes
- Sets up lighting and world
- Saves the `.blend` file

### Step 2: Run the script in Blender CLI
```bash
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" -b -P disco_cop\blender\models\create_{entity}_model.py
```
This produces `disco_cop/blender/models/{entity}.blend`.

### Step 3: Verify the .blend file
Open it in Blender GUI (optional) or check console output for:
- Correct mesh count
- Correct bone count
- All expected actions listed
- No errors/warnings

### Step 4: Render sprite sheets
Run the render script for each animation:
```bash
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" -b disco_cop\blender\models\{entity}.blend -P disco_cop\blender\render_scripts\render_spritesheet.py -- --output disco_cop\assets\sprites\{category}\ --name {entity}_{animation} --frames {count} --width {W} --height {H} --action {action_name} --start-frame 1
```
See `art_build_plan.md` Section 5 for complete copy-paste commands per entity.

### Step 5: Verify PNGs
Check that:
- `{entity}_{animation}_sheet.png` exists in the output directory
- Sheet dimensions = frame_width × frame_count by frame_height
- Transparency works (no black background)
- Character faces RIGHT
- Character feet are at the bottom edge

### Step 6: Integrate in Godot (on Pi)
Pull from git, open Godot, swap null textures in SpriteFrames resources. See `art_build_plan.md` Section 7 for per-entity instructions.

---

## 4. Blender 5.0 API Specifics

Blender 5.0 introduced breaking changes. These are the ones we hit and solved:

### 4a. Actions / FCurves — Layered Action System
**Problem:** `action.fcurves` was removed in Blender 5.0. The old pattern of creating FCurves and inserting keyframes manually no longer works.

**Solution:** Use `pose_bone.keyframe_insert()` instead:
```python
pbone = armature_obj.pose.bones[bone_name]
pbone.rotation_euler = (rx, ry, rz)
pbone.keyframe_insert(data_path='rotation_euler', frame=frame_num)
```
The action must be assigned to `armature_obj.animation_data.action` before keyframing. Blender auto-creates the FCurves internally.

### 4b. EEVEE Engine Rename
**Problem:** `BLENDER_EEVEE_NEXT` was renamed back to `BLENDER_EEVEE` in Blender 5.0. Using the old name throws an error.

**Solution:** The render script checks which identifier exists at runtime:
```python
if 'BLENDER_EEVEE' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]:
    scene.render.engine = 'BLENDER_EEVEE'
else:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
```

### 4c. `Material.use_nodes` Deprecation
**Problem:** `mat.use_nodes = True` is deprecated and will be removed in Blender 6.0.

**Status:** Still works in 5.0 with a deprecation warning. No immediate fix needed, but be aware it will break in 6.0.

### 4d. Pillow Not in Blender's Python Path
**Problem:** Blender bundles its own Python interpreter that doesn't include user-installed site-packages. `from PIL import Image` fails even though Pillow is installed system-wide.

**Solution:** Added to the top of `render_spritesheet.py`:
```python
import site
_user_site = site.getusersitepackages()
if _user_site not in sys.path:
    sys.path.append(_user_site)
```

### 4e. Camera Setup for Non-Square Sprites
**Problem:** The player is 24×48 (non-square). Using `--size 48` renders a 48×48 square with wasted horizontal space.

**Solution:** Use `--width 24 --height 48` instead of `--size 48`. The render script's `resolve_dimensions()` handles this. The camera auto-calculates `ortho_scale = 2.0` and positions at `(0, -10, cam_z)` looking from -Y toward the origin (90° X rotation).

---

## 5. Model Script Anatomy

The player model script (`create_player_model.py`) follows a specific structure. All future entity scripts should follow the same pattern:

### Section Order
1. **Helpers** — `clear_scene()`, `make_material()`, `assign_material()`, `set_smooth()`
2. **Materials** — `create_materials()` returns a dict of named materials
3. **Meshes** — `create_body_meshes(mats)` creates primitives, assigns materials, returns a dict
4. **Armature** — `create_armature()` builds the bone hierarchy in edit mode
5. **Parenting** — `parent_meshes_to_armature()` uses a `MESH_BONE_MAP` dict to assign each mesh to a bone via vertex groups + Armature modifier
6. **Animations** — One function per action. Each: resets pose → creates action → sets/keys bone transforms per frame
7. **Scene setup** — Lighting (Sun + Fill), world background (black, strength 0)
8. **Main** — Calls everything in order, saves .blend

### Conventions
- **Origin at feet.** `(0, 0, 0)` is where feet touch the ground.
- **Faces +X.** Character's front/right side faces screen-right when viewed from -Y.
- **1 BU ≈ scaled to fit render frame.** At `ortho_scale=2.0`, the visible area is ~2.0 BU wide × 2.0 BU tall.
- **Materials are flat.** `Roughness=1.0`, `Metallic=0.0`, `Specular=0.0`. No textures — just base colors.
- **Armature modifier, not parenting.** Meshes get an Armature modifier + vertex group (all vertices, weight 1.0) for each bone assignment.
- **Actions use `use_fake_user = True`** so they persist in the .blend even if not actively assigned.
- **Frame ranges start at 1.** An 8-frame animation uses frames 1–8.

### Animation Keyframing Pattern
```python
def create_{anim}_action(armature_obj):
    reset_pose(armature_obj)
    action = start_action(armature_obj, '{anim}')
    r = math.radians

    # Frame 1
    pose_and_key_rot(armature_obj, 'bone_name', 1, (r(angle), 0, 0))
    pose_and_key_loc(armature_obj, 'root', 1, (0, 0, offset))
    # ... more bones ...

    # Frame 2
    # ... etc ...
```

### Mesh-to-Bone Mapping
Defined as a constant dict at module level:
```python
MESH_BONE_MAP = {
    'MeshName': 'bone_name',
    # ...
}
```
Every mesh in the model MUST appear in this map or it won't deform with the armature.

---

## 6. Render Pipeline

### How `render_spritesheet.py` Works

1. **Parse args** — Reads `--output`, `--name`, `--frames`, `--width`/`--height`/`--size`, `--action`, `--start-frame`, `--ortho-scale`
2. **Set action** — Finds the armature, finds the named action, assigns it to `animation_data.action`
3. **Setup camera** — Creates orthographic camera at `(0, -10, cam_z)` with 90° X rotation, `ortho_scale=2.0`
4. **Setup render** — Sets resolution to width×height, transparent background, RGBA PNG, EEVEE engine
5. **Render frames** — Iterates `start_frame` to `start_frame + frames - 1`, renders each to a temp PNG
6. **Assemble sheet** — Uses Pillow to paste frames left-to-right into a horizontal strip, saves as `{name}_sheet.png`
7. **Cleanup** — Deletes individual frame PNGs

### Camera Math
- Camera looks from -Y toward origin (rotation: 90° on X axis)
- `cam_z = height / max(width, height) * ortho_scale * 0.5` — centers the camera vertically on the character
- `ortho_scale = 2.0` (default) — captures ~2 BU of scene height
- For the 24×48 player: `cam_z = 48/48 * 2.0 * 0.5 = 1.0`

### Batch Mode
The script supports `--batch manifest.json` to render multiple sheets from one .blend in a single Blender session. The manifest is a JSON array of objects with the same fields as CLI args.

---

## 7. Common Pitfalls

### `action.fcurves` removed in Blender 5.0
**Symptom:** `AttributeError: 'Action' object has no attribute 'fcurves'`
**Fix:** Use `pose_bone.keyframe_insert()`. See Section 4a.

### EEVEE engine name changed
**Symptom:** `ValueError: ... 'BLENDER_EEVEE_NEXT' not found in ...`
**Fix:** Check available engine identifiers at runtime. See Section 4b.

### Pillow import fails in Blender
**Symptom:** `ModuleNotFoundError: No module named 'PIL'`
**Fix:** Add `site.getusersitepackages()` to `sys.path`. See Section 4d.

### Camera pointing wrong direction
**Symptom:** Sprite shows top of character's head instead of side view.
**Fix:** Camera must be at `(0, -10, cam_z)` with `rotation_euler = (π/2, 0, 0)`. This looks from -Y toward origin, showing the character's side (+X = screen right).

### Using `--size` instead of `--width`/`--height` for non-square sprites
**Symptom:** 24×48 character renders into a 48×48 square with empty horizontal space.
**Fix:** Use `--width 24 --height 48` instead of `--size 48`.

### Bones not deforming meshes
**Symptom:** Character stays in rest pose during animation render.
**Fix:** Every mesh needs: (1) a vertex group named after the bone, (2) all vertices added to that group with weight 1.0, (3) an Armature modifier pointing to the armature object.

### Actions not persisting in .blend
**Symptom:** Opening the .blend shows no actions, or actions disappear.
**Fix:** Set `action.use_fake_user = True` on every action after creation.

---

## 8. Template for Next Entity

Use this checklist when creating the grunt (or any subsequent entity):

### Pre-work
- [ ] Read specs in `art_build_plan.md` (Section 3b for grunt: 20×40, 4 animations)
- [ ] Read this document fully

### Create Model Script
- [ ] Create `disco_cop/blender/models/create_grunt_model.py`
- [ ] Follow the section order from Section 5 above
- [ ] Use `create_player_model.py` as reference — copy the helper functions, adapt meshes/bones/animations
- [ ] Grunt proportions: shorter than player, stockier, simpler (no afro/glasses)
- [ ] Grunt animations: walk (6 frames), attack (4 frames), hurt (2 frames), death (4 frames)
- [ ] Origin at feet, faces +X, flat materials, disco color palette

### Generate .blend
- [ ] Run: `& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" -b -P disco_cop\blender\models\create_grunt_model.py`
- [ ] Verify console output: mesh count, bone count, 4 actions listed

### Render Sprite Sheets
- [ ] Run 4 render commands (see `art_build_plan.md` Section 5 — Grunt)
- [ ] Use `--width 20 --height 40` (NOT `--size 40`)
- [ ] Output to `disco_cop/assets/sprites/enemies/`

### Verify
- [ ] 4 PNGs exist: `grunt_walk_sheet.png`, `grunt_attack_sheet.png`, `grunt_hurt_sheet.png`, `grunt_death_sheet.png`
- [ ] Sheet dimensions correct (e.g., walk: 120×40 = 6 frames × 20px)
- [ ] Transparent background
- [ ] Faces right
- [ ] Feet at bottom

### Commit
- [ ] `git add disco_cop/blender/models/create_grunt_model.py disco_cop/blender/models/grunt.blend disco_cop/assets/sprites/enemies/`
- [ ] `git commit -m "Art: add grunt model and sprite sheets"`

---

## 9. File Reference

### Key Paths
| File | Purpose |
|------|---------|
| `disco_cop/blender/models/create_player_model.py` | Player model script (reference implementation) |
| `disco_cop/blender/models/player.blend` | Generated player .blend file |
| `disco_cop/blender/render_scripts/render_spritesheet.py` | Sprite sheet renderer |
| `disco_cop/blender/reference/art_build_plan.md` | Entity specs, render commands, integration guide |
| `disco_cop/blender/reference/art_process.md` | This document |
| `disco_cop/assets/sprites/players/` | Player sprite sheet output |
| `disco_cop/assets/sprites/enemies/` | Enemy sprite sheet output |
| `disco_cop/assets/sprites/bosses/` | Boss sprite sheet output |

### Commands

**Generate a model:**
```bash
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" -b -P disco_cop\blender\models\create_{entity}_model.py
```

**Render a sprite sheet:**
```bash
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" -b disco_cop\blender\models\{entity}.blend -P disco_cop\blender\render_scripts\render_spritesheet.py -- --output disco_cop\assets\sprites\{category}\ --name {entity}_{anim} --frames {N} --width {W} --height {H} --action {anim} --start-frame 1
```

### Blender Install Path
```
C:\Program Files\Blender Foundation\Blender 5.0\blender.exe
```

### Python Dependencies
- **Pillow** — installed via `pip install Pillow` in system Python (Blender picks it up via `site.getusersitepackages()`)
