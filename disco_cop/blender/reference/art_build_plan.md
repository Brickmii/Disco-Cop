# Disco Cop — Cross-Platform Art Production Build Plan

## Context
All 11 code phases are complete and running at 250+ FPS on Pi 5. Every entity currently uses placeholder ColorRects. This plan defines the exact workflow for producing real sprite art on PC (Blender) and deploying it to Pi via GitHub, ensuring consistency when jumping between machines and IDEs.

---

## 1. Machines & Tools

| Machine | Role | Software | Project Path |
|---------|------|----------|--------------|
| **PC** | Art production (Blender modeling, rendering) | Blender 4.x, Python 3.11+, Pillow, Git, VS Code | `~/Disco-Cop/` |
| **Pi 5** | Game runtime (Godot dev + testing) | Godot 4.5.1, Git | `~/PycharmProjects/Disco Cop/` |

**GitHub repo:** `git@github.com:Brickmii/Disco-Cop.git` (branch: `master`)

---

## 2. Directory Layout (already in repo)

```
disco_cop/
├── assets/sprites/          <- RENDERED SPRITES LAND HERE (both machines see this)
│   ├── players/             <- player_idle_sheet.png, player_run_sheet.png, ...
│   ├── enemies/             <- grunt_walk_sheet.png, shooter_idle_sheet.png, ...
│   ├── bosses/              <- disco_king_idle_sheet.png, ...
│   ├── weapons/             <- projectile_bullet.png, muzzle_flash_sheet.png
│   ├── effects/             <- explosion_sheet.png, shield_break_sheet.png
│   ├── environment/         <- tileset.png, parallax layers
│   └── ui/                  <- health_bar.png, icons
├── blender/                 <- .gdignore'd — Godot skips this entirely
│   ├── models/              <- .blend source files (one per entity)
│   │   ├── player.blend
│   │   ├── grunt.blend
│   │   ├── shooter.blend
│   │   ├── flyer.blend
│   │   ├── disco_king.blend
│   │   └── props/           <- loot_crate.blend, projectiles.blend, etc.
│   ├── render_scripts/
│   │   └── render_spritesheet.py   <- already written
│   └── reference/           <- concept art, color palettes, style guides
```

---

## 3. Sprite Sheet Specifications (per entity)

All sprites use **nearest-neighbor filtering** (already set in `project.godot`: `default_texture_filter=0`).
All sheets are **horizontal strips** (frames side by side, single row).
File format: **PNG with transparency** (RGBA).

### 3a. Player (24x48 px per frame)

| Animation | File Name | Frames | FPS | Loop | Notes |
|-----------|-----------|--------|-----|------|-------|
| idle | `player_idle_sheet.png` | 4 | 5 | yes | Subtle breathing/bobble |
| run | `player_run_sheet.png` | 8 | 10 | yes | Full run cycle |
| jump | `player_jump_sheet.png` | 2 | 5 | no | Crouch-launch |
| fall | `player_fall_sheet.png` | 2 | 5 | no | Arms up, legs down |
| double_jump | `player_double_jump_sheet.png` | 4 | 5 | no | Flip/spin |
| hurt | `player_hurt_sheet.png` | 2 | 5 | no | Knockback pose |

- **Render size:** `--size 48` (height-dominant; 24 wide means the render square is 48, character centered)
- **Collision:** 24x48 rectangle, origin at feet (0, 0), sprite centered at (0, -24)
- **Facing:** Draw facing RIGHT. Code uses `flip_h` for left-facing
- **Scene node:** `AnimatedSprite2D` already exists with SpriteFrames resource — replace null textures with AtlasTextures from sheets
- **Also remove:** `BodyRect` ColorRect placeholder once sprites are in

### 3b. Grunt Enemy (20x40 px per frame)

| Animation | File Name | Frames | FPS | Loop |
|-----------|-----------|--------|-----|------|
| walk | `grunt_walk_sheet.png` | 6 | 8 | yes |
| attack | `grunt_attack_sheet.png` | 4 | 10 | no |
| hurt | `grunt_hurt_sheet.png` | 2 | 5 | no |
| death | `grunt_death_sheet.png` | 4 | 8 | no |

- **Render size:** `--size 40`
- **Collision:** 20x40 rectangle, origin at feet, shape center at (0, -20)
- **Current visual:** `AnimatedSprite2D` named `Sprite` with SpriteFrames (null textures)

### 3c. Shooter Enemy (20x40 px per frame)

| Animation | File Name | Frames | FPS | Loop |
|-----------|-----------|--------|-----|------|
| idle | `shooter_idle_sheet.png` | 4 | 5 | yes |
| walk | `shooter_walk_sheet.png` | 6 | 8 | yes |
| shoot | `shooter_shoot_sheet.png` | 3 | 10 | no |
| hurt | `shooter_hurt_sheet.png` | 2 | 5 | no |
| death | `shooter_death_sheet.png` | 4 | 8 | no |

- Same dimensions as Grunt (20x40)

### 3d. Flyer Enemy (24x24 px per frame)

| Animation | File Name | Frames | FPS | Loop |
|-----------|-----------|--------|-----|------|
| fly | `flyer_fly_sheet.png` | 4 | 8 | yes |
| attack | `flyer_attack_sheet.png` | 3 | 10 | no |
| hurt | `flyer_hurt_sheet.png` | 2 | 5 | no |
| death | `flyer_death_sheet.png` | 4 | 8 | no |

- **Render size:** `--size 24`
- **Collision:** 24x24 rectangle, origin center-bottom, shape center at (0, -12)

### 3e. Disco King Boss (48x80 px per frame — body 48x64 + crown 16 above)

| Animation | File Name | Frames | FPS | Loop |
|-----------|-----------|--------|-----|------|
| idle | `disco_king_idle_sheet.png` | 4 | 5 | yes |
| attack_disco_ball | `disco_king_disco_ball_sheet.png` | 6 | 8 | no |
| attack_slam | `disco_king_slam_sheet.png` | 8 | 10 | no |
| attack_laser | `disco_king_laser_sheet.png` | 6 | 8 | no |
| hurt | `disco_king_hurt_sheet.png` | 2 | 5 | no |
| death | `disco_king_death_sheet.png` | 8 | 6 | no |

- **Render size:** `--size 80` (48 wide x 80 tall total, includes crown)
- **Collision:** 48x64 body, origin at feet, shape center at (0, -32)

### 3f. Projectile (10x4 px — single frame per type)

| Type | File Name | Size |
|------|-----------|------|
| Bullet (default) | `projectile_bullet.png` | 10x4 |
| Fire | `projectile_fire.png` | 10x4 |
| Ice | `projectile_ice.png` | 10x4 |
| Electric | `projectile_electric.png` | 10x4 |
| Explosive | `projectile_explosive.png` | 12x6 |
| Enemy bullet | `projectile_enemy.png` | 8x4 |

- Single-frame sprites (no animation sheet needed)
- Code in `projectile.gd` swaps texture by element, falls back to color tinting

### 3g. Loot Drop (16x16 — single frame per type)

| Type | File Name |
|------|-----------|
| Weapon | `loot_weapon.png` |
| Shield | `loot_shield.png` |
| Health | `loot_health.png` |
| Ammo | `loot_ammo.png` |

- Rarity color is applied via `modulate` on the sprite — draw base art in **white/neutral**

### 3h. Effects (various sizes)

| Effect | File Name | Frame Size | Frames |
|--------|-----------|------------|--------|
| Muzzle flash | `muzzle_flash_sheet.png` | 16x16 | 3 |
| Bullet impact | `impact_sheet.png` | 16x16 | 4 |
| Explosion | `explosion_sheet.png` | 32x32 | 6 |
| Shield break | `shield_break_sheet.png` | 32x32 | 4 |
| Loot glow | `loot_glow_sheet.png` | 24x24 | 4 |

---

## 4. Blender Modeling Conventions

### Scene setup per .blend file
- **World origin (0,0,0)** = character's feet (ground contact point)
- **Model faces +X** (screen-right) — code uses `flip_h`/`scale.x = -1` for left
- **Scale:** 1 Blender unit = 1 pixel at render size
- **Armature name:** `Armature` (default)
- **Mesh name:** `{entity}_mesh` (e.g., `player_mesh`, `grunt_mesh`)

### Animation naming
- Action names in Blender **must match** the file name suffixes: `idle`, `run`, `jump`, `fall`, `walk`, `attack`, `shoot`, `fly`, `hurt`, `death`, etc.
- Keep frame ranges tight: start at frame 1, end at frame count (e.g., 8-frame run = frames 1-8)

### Style rules
- Low-poly or stylized — not realistic (it's pixel art at output)
- Bright, saturated colors (disco theme: magenta, gold, cyan, orange)
- No complex materials/textures — flat colors or simple gradients (renders to tiny sprites)
- Outlines optional — will be visible at 48px height

---

## 5. Render Commands (run on PC in Blender CLI)

The render script lives at: `disco_cop/blender/render_scripts/render_spritesheet.py`

### Dependencies (install once on PC)
```bash
pip install Pillow
```

### Command pattern
```bash
blender -b disco_cop/blender/models/{model}.blend \
  -P disco_cop/blender/render_scripts/render_spritesheet.py \
  -- --output disco_cop/assets/sprites/{category}/ \
     --name {entity}_{animation} \
     --frames {count} \
     --size {pixel_height} \
     --action {blender_action_name} \
     --start-frame 1
```

### Full render commands (copy-paste ready)

**Player:**
```bash
cd ~/Disco-Cop
blender -b disco_cop/blender/models/player.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/players/ --name player_idle --frames 4 --size 48 --action idle --start-frame 1
blender -b disco_cop/blender/models/player.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/players/ --name player_run --frames 8 --size 48 --action run --start-frame 1
blender -b disco_cop/blender/models/player.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/players/ --name player_jump --frames 2 --size 48 --action jump --start-frame 1
blender -b disco_cop/blender/models/player.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/players/ --name player_fall --frames 2 --size 48 --action fall --start-frame 1
blender -b disco_cop/blender/models/player.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/players/ --name player_double_jump --frames 4 --size 48 --action double_jump --start-frame 1
blender -b disco_cop/blender/models/player.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/players/ --name player_hurt --frames 2 --size 48 --action hurt --start-frame 1
```

**Grunt:**
```bash
blender -b disco_cop/blender/models/grunt.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name grunt_walk --frames 6 --size 40 --action walk --start-frame 1
blender -b disco_cop/blender/models/grunt.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name grunt_attack --frames 4 --size 40 --action attack --start-frame 1
blender -b disco_cop/blender/models/grunt.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name grunt_hurt --frames 2 --size 40 --action hurt --start-frame 1
blender -b disco_cop/blender/models/grunt.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name grunt_death --frames 4 --size 40 --action death --start-frame 1
```

**Shooter:**
```bash
blender -b disco_cop/blender/models/shooter.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name shooter_idle --frames 4 --size 40 --action idle --start-frame 1
blender -b disco_cop/blender/models/shooter.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name shooter_walk --frames 6 --size 40 --action walk --start-frame 1
blender -b disco_cop/blender/models/shooter.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name shooter_shoot --frames 3 --size 40 --action shoot --start-frame 1
blender -b disco_cop/blender/models/shooter.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name shooter_hurt --frames 2 --size 40 --action hurt --start-frame 1
blender -b disco_cop/blender/models/shooter.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name shooter_death --frames 4 --size 40 --action death --start-frame 1
```

**Flyer:**
```bash
blender -b disco_cop/blender/models/flyer.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name flyer_fly --frames 4 --size 24 --action fly --start-frame 1
blender -b disco_cop/blender/models/flyer.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name flyer_attack --frames 3 --size 24 --action attack --start-frame 1
blender -b disco_cop/blender/models/flyer.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name flyer_hurt --frames 2 --size 24 --action hurt --start-frame 1
blender -b disco_cop/blender/models/flyer.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/enemies/ --name flyer_death --frames 4 --size 24 --action death --start-frame 1
```

**Disco King:**
```bash
blender -b disco_cop/blender/models/disco_king.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/bosses/ --name disco_king_idle --frames 4 --size 80 --action idle --start-frame 1
blender -b disco_cop/blender/models/disco_king.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/bosses/ --name disco_king_disco_ball --frames 6 --size 80 --action attack_disco_ball --start-frame 1
blender -b disco_cop/blender/models/disco_king.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/bosses/ --name disco_king_slam --frames 8 --size 80 --action attack_slam --start-frame 1
blender -b disco_cop/blender/models/disco_king.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/bosses/ --name disco_king_laser --frames 6 --size 80 --action attack_laser --start-frame 1
blender -b disco_cop/blender/models/disco_king.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/bosses/ --name disco_king_hurt --frames 2 --size 80 --action hurt --start-frame 1
blender -b disco_cop/blender/models/disco_king.blend -P disco_cop/blender/render_scripts/render_spritesheet.py -- --output disco_cop/assets/sprites/bosses/ --name disco_king_death --frames 8 --size 80 --action death --start-frame 1
```

---

## 6. Git Workflow (step by step)

### On PC (art production)
```bash
# 1. Start of session — always pull first
cd ~/Disco-Cop
git pull origin master

# 2. Create/edit .blend files in disco_cop/blender/models/

# 3. Render sprite sheets (commands from Section 5)

# 4. Verify output PNGs exist in disco_cop/assets/sprites/

# 5. Commit and push
git add disco_cop/assets/sprites/ disco_cop/blender/models/
git commit -m "Art: add {entity} sprite sheets"
git push origin master
```

### On Pi (game integration)
```bash
# 1. Pull latest art
cd ~/PycharmProjects/Disco\ Cop
git pull origin master

# 2. Godot auto-imports new PNGs on next editor open
#    (creates .import files automatically)

# 3. Open Godot, wire sprites into scenes (Section 7)

# 4. Test at 60fps
godot --display-driver wayland --rendering-driver opengl3 --path disco_cop/

# 5. Commit scene changes and push
git add disco_cop/scenes/ disco_cop/assets/sprites/
git commit -m "Integrate {entity} sprites into scenes"
git push origin master
```

### Rules
- **Never edit .blend files on Pi** — Blender is PC-only
- **Never edit .gd/.tscn on PC** — Godot is Pi-only (for now)
- **Always pull before starting work on either machine**
- **Commit frequently** — one commit per entity or batch of related sprites
- If .blend files get large (>50MB), add Git LFS: `git lfs track "*.blend"`

---

## 7. Placeholder Swap Procedure (on Pi in Godot)

### 7a. Player (already has AnimatedSprite2D)

The player scene already has an `AnimatedSprite2D` node with a `SpriteFrames` resource containing 6 animation slots with null textures. The swap:

1. Open `scenes/player/player.tscn` in Godot editor
2. Select `AnimatedSprite2D` node
3. Click the `SpriteFrames` resource in the Inspector
4. For each animation (idle, run, jump, fall, double_jump, hurt):
   - Delete the null frame
   - Click "Add frames from sprite sheet"
   - Select the corresponding `_sheet.png` from `assets/sprites/players/`
   - Set horizontal frames = frame count, vertical = 1
   - Select all frames, click "Add"
5. Verify `AnimatedSprite2D.position` stays at `Vector2(0, -24)` (center of body)

Code changes needed: **None.** `player.gd` already calls `sprite.play("idle")` etc. via `_update_sprite_animation()` and uses `sprite.flip_h` for facing direction.

### 7b. Enemies (Grunt, Shooter, Flyer)

Each enemy .tscn now has an `AnimatedSprite2D` named `Sprite` with a `SpriteFrames` resource containing animation slots with null textures. The swap for each:

1. Open the .tscn in Godot editor (e.g., `scenes/enemies/grunt.tscn`)
2. Select the `Sprite` AnimatedSprite2D node
3. Click the `SpriteFrames` resource in the Inspector
4. For each animation:
   - Delete the null frame
   - Click "Add frames from sprite sheet"
   - Select the corresponding `_sheet.png` from `assets/sprites/enemies/`
   - Set horizontal frames = frame count, vertical = 1
   - Select all frames, click "Add"
5. Verify position:
   - Grunt/Shooter: `Vector2(0, -20)` (half of 40px height)
   - Flyer: `Vector2(0, -12)` (half of 24px height)

Code changes needed: **None.** `base_enemy.gd` already handles `sprite.play()`, `sprite.flip_h`, and hit flash on the sprite node.

### 7c. Boss (Disco King)

1. Open `scenes/bosses/boss_disco_king.tscn`
2. Select the `Sprite` AnimatedSprite2D node
3. Click the `SpriteFrames` resource in the Inspector
4. For each animation (idle, disco_ball, slam, laser, hurt, death):
   - Delete the null frame, add frames from corresponding sheet
5. Verify position: `Vector2(0, -40)` (center of 80px total height)

Code changes needed: **None.** `boss_disco_king.gd` already plays animations per attack pattern.

### 7d. Projectile

1. Open `scenes/weapons/projectile.tscn`
2. The `Sprite` Sprite2D node is already in place
3. Just drop the PNG files into `assets/sprites/weapons/`
4. `projectile.gd` auto-loads textures via `ResourceLoader.exists()` on next run

Code changes needed: **None.** Texture swapping per element is already wired.

### 7e. Loot Drop

1. Open `scenes/loot/loot_drop.tscn`
2. The `Sprite` Sprite2D node is already in place
3. Drop PNG files into `assets/sprites/ui/`
4. `loot_drop.gd` auto-loads textures via `ResourceLoader.exists()` on next run

Code changes needed: **None.** Texture swapping per type is already wired.

---

## 8. Art Production Order (recommended)

1. **Player** — most visible, validates full pipeline end-to-end
2. **Grunt** — simplest enemy, tests enemy sprite swap pattern
3. **Projectiles** — tiny, fast to model, big visual impact
4. **Loot drops** — tiny icons, quick wins
5. **Shooter** — builds on grunt workflow
6. **Flyer** — tests non-humanoid model
7. **Disco King** — most complex, do last
8. **Effects** — muzzle flash, impacts, explosions
9. **Environment** — tileset, parallax backgrounds

---

## 9. Verification Checklist (per entity)

On PC after rendering:
- [ ] PNG files exist in correct `assets/sprites/` subdirectory
- [ ] Sheet dimensions match: width = frame_width * frame_count, height = frame_height
- [ ] Transparency works (no black background)
- [ ] Character faces RIGHT in all frames
- [ ] Character feet are at bottom edge of frame

On Pi after integration:
- [ ] Godot imports sprites (check `.import` files appear)
- [ ] AnimatedSprite2D plays all animations in editor preview
- [ ] No visual offset — sprite aligns with collision shape
- [ ] `flip_h` works correctly for left-facing
- [ ] Hit flash still works (modulate on correct node)
- [ ] Death animation plays before queue_free
- [ ] FPS stays above 60 with new sprites: `godot --display-driver wayland --rendering-driver opengl3 --path disco_cop/`
