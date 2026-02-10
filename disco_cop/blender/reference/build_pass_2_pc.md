# Disco Cop — Build Pass 2: PC Art Production

## What's Done (Build Pass 1 Art)
- Player: 6 animation sheets (idle, run, jump, fall, double_jump, hurt) — 24x48
- Skating Grunt: 4 sheets (skate, charge, hurt, death) — 20x40
- Skating Shooter: 4 sheets (skate, shoot_skate, hurt, death) — 20x40
- Flyer: 4 sheets (fly, attack, hurt, death) — 24x24
- Disco King: 6 sheets (idle, disco_ball, slam, laser, hurt, death) — 48x80
- Projectiles: 6 single-frame PNGs (bullet, fire, ice, electric, explosive, enemy)
- Loot: 4 icons (weapon, shield, health, ammo) — 16x16
- Effects: 5 sheets (explosion, shield_break, loot_glow, muzzle_flash, impact)
- Environment: tileset + 3 parallax layers (sky, city_far, city_near)
- Weapons: gun sprite

## What's Next (4 Phases)

Each phase aligns with the Pi-side Build Pass 2 so assets arrive before the Pi needs them.

---

## Phase 1: HUD Sprites

**Supports Pi Phase 2 (HUD wiring)**

**Goal**: Provide styled UI art so the HUD isn't raw Godot ProgressBars.

**Specs**:

| Asset | File | Size | Notes |
|-------|------|------|-------|
| Health bar frame | `hud_health_frame.png` | 100x12 | Outer border/frame, 9-patch friendly |
| Health bar fill | `hud_health_fill.png` | 96x8 | Red gradient, stretches horizontally |
| Shield bar frame | `hud_shield_frame.png` | 100x12 | Same frame style as health |
| Shield bar fill | `hud_shield_fill.png` | 96x8 | Cyan/blue gradient |
| Boss bar frame | `hud_boss_frame.png` | 200x16 | Wider, more ornate |
| Boss bar fill | `hud_boss_fill.png` | 196x12 | Gold/magenta gradient |
| Weapon icons (6) | `icon_pistol.png` ... `icon_launcher.png` | 16x16 | One per weapon type |
| Ammo icon | `icon_ammo.png` | 8x8 | Small bullet symbol |
| Lives icon | `icon_life.png` | 12x12 | Mini player head |

**Output directory**: `disco_cop/assets/sprites/ui/`

**Approach**: These are flat 2D sprites, no Blender needed. Create with a Python script using Pillow — draw colored rectangles, gradients, and simple shapes directly. Disco color palette (magenta, cyan, gold on dark backgrounds).

**Tasks**:
1. Write `disco_cop/blender/scripts/create_hud_sprites.py` (Pillow-based, no Blender)
2. Generate all HUD PNGs to `assets/sprites/ui/`
3. Commit and push — Pi pulls and wires into `game_hud.tscn` / `player_hud.tscn`

**Estimated scope**: ~150 lines of Python

---

## Phase 2: Rink Environment Art

**Supports Pi Phase 4 (Level Design — Roller Rink Rumble)**

**Goal**: Replace the generic city environment with rink-specific tiles and parallax.

### Tileset Additions

The current `tileset.png` has generic platform tiles. The rink needs:

| Tile | Size | Color | Notes |
|------|------|-------|-------|
| Rink floor | 32x32 | `#8C5A33` warm wood | Lane line detail, polished look |
| Rink floor variant | 32x32 | `#D4A76A` lighter wood | Alternating tiles for visual variety |
| Lobby carpet | 32x32 | `#4A0E4E` deep purple | Patterned carpet texture |
| Chrome barrier top | 32x24 | `#C0C0C0` silver | Shiny rail, enemies bounce off |
| Chrome barrier side | 24x32 | `#C0C0C0` silver | Vertical barrier segment |
| Rink wall | 32x32 | `#1A0A2E` dark purple | Background wall behind barriers |

**Approach**: Extend the existing tileset or create `tileset_rink.png` as a separate atlas. Pillow script — draw wood grain patterns, chrome gradients, carpet texture.

### Parallax Backgrounds (rink-specific)

Replace/supplement the city parallax with rink interior:

| Layer | File | Size | Content |
|-------|------|------|---------|
| Far (ceiling) | `parallax_rink_ceiling.png` | 640x360 | Dark ceiling, disco ball glow spots (magenta, cyan, gold circles) |
| Mid (bleachers) | `parallax_rink_mid.png` | 640x360 | Bleacher silhouettes, neon exit signs, rink wall |
| Near (detail) | `parallax_rink_near.png` | 640x360 | Shoe counter, arcade machines, rink rail close-up |

**Approach**: Pillow script. Flat geometric shapes, neon glow effects (bright color + slightly larger dim halo behind), silhouette crowd in bleachers.

### Props (stretch)

| Prop | File | Size | Notes |
|------|------|------|-------|
| Disco ball | `prop_disco_ball.png` | 32x32 | Hanging from ceiling, mirrored facets |
| DJ booth | `prop_dj_booth.png` | 64x48 | Background decoration |
| Shoe counter | `prop_shoe_counter.png` | 48x32 | Lobby decoration |

**Output directory**: `disco_cop/assets/sprites/environment/`

**Tasks**:
1. Write `disco_cop/blender/scripts/create_rink_tiles.py` (Pillow)
2. Write `disco_cop/blender/scripts/create_rink_parallax.py` (Pillow)
3. Generate tiles to `assets/sprites/environment/`
4. Generate parallax layers to `assets/sprites/environment/`
5. Optionally create prop sprites
6. Commit and push — Pi pulls and wires into level_01

**Estimated scope**: ~300 lines across 2 scripts

---

## Phase 3: Audio Production

**Supports Pi Phase 3 (Sound Effects)**

**Goal**: Generate/source all SFX and music files. Audio can't be created on Pi — it's a PC task.

### SFX (generate with jsfxr or Pillow/numpy WAV synthesis)

| Sound | File | Style |
|-------|------|-------|
| Pistol shot | `shoot_pistol.wav` | Short pop, snappy |
| Shotgun blast | `shoot_shotgun.wav` | Wide boom, bass-heavy |
| SMG burst | `shoot_smg.wav` | Rapid staccato tap |
| Sniper crack | `shoot_sniper.wav` | Sharp crack, echo tail |
| Rifle shot | `shoot_rifle.wav` | Medium punch |
| Launcher thump | `shoot_launcher.wav` | Deep thud/whomp |
| Bullet impact | `impact_hit.wav` | Metallic ping |
| Critical hit | `impact_crit.wav` | Louder ping + crunch |
| Explosion | `explosion.wav` | Bass boom, crackle |
| Enemy death | `enemy_death.wav` | Short descending tone |
| Player hurt | `player_hurt.wav` | Grunt/thud |
| Player death | `player_death.wav` | Longer descending tone |
| Shield break | `shield_break.wav` | Glass shatter, electric zap |
| Shield recharge | `shield_recharge.wav` | Rising hum |
| Loot pickup | `loot_pickup.wav` | Bright ascending chime |
| Weapon swap | `weapon_swap.wav` | Click/rack sound |
| Menu select | `menu_select.wav` | UI blip |

**Approach — Option A (programmatic)**: Write a Python script using numpy to generate retro 8-bit style WAVs. Sine/square/noise waveforms with frequency sweeps and envelopes. ~200 lines.

**Approach — Option B (jsfxr)**: Use https://sfxr.me/ in a browser, export WAVs manually. Faster per-sound but manual.

**Approach — Option C (hybrid)**: Script the repetitive ones (shots, impacts), manually create the distinctive ones (shield break, loot pickup).

### Music (source or generate)

| Track | File | Duration | Style |
|-------|------|----------|-------|
| Menu theme | `menu_theme.ogg` | 30-60s loop | Chill disco, bass groove |
| Level theme | `level_theme.ogg` | 60-90s loop | Upbeat funk, driving rhythm |
| Boss theme | `boss_theme.ogg` | 60-90s loop | Intense disco, faster tempo |

**Approach**: Source from free music libraries (freesound.org, opengameart.org) or generate with a tool like Suno/Udio. Must be royalty-free. Convert to OGG with ffmpeg.

**Output directory**: `disco_cop/assets/audio/sfx/` and `disco_cop/assets/audio/music/`

**Tasks**:
1. Create directory structure: `assets/audio/sfx/`, `assets/audio/music/`
2. Generate/source 17 SFX files (WAV, 16-bit, 44100 Hz)
3. Source/generate 3 music loops (OGG, stereo, 44100 Hz)
4. Commit and push — Pi pulls, Godot auto-imports, `sfx_library.gd` preloads

**Estimated scope**: ~200 lines if scripted, or manual browser work

---

## Phase 4: Player 2 Visual Distinction

**Supports Pi Phase 5 (2-Player Co-op)**

**Goal**: Player 2 needs to look different from Player 1 on screen.

**Approach — Palette swap**: Take existing player sprite sheets, shift colors. Player 1 keeps the original magenta/gold disco cop look. Player 2 gets a cyan/silver variant.

**Color mapping**:
| Element | Player 1 | Player 2 |
|---------|----------|----------|
| Jacket | Magenta | Cyan |
| Pants | Gold | Silver |
| Afro | Dark brown | Blonde/white |
| Skin | Original | Same |
| Shades | Gold frames | Silver frames |

**Output**: Duplicate set of 6 sheets with `_p2` suffix:
- `player_idle_p2_sheet.png`
- `player_run_p2_sheet.png`
- `player_jump_p2_sheet.png`
- `player_fall_p2_sheet.png`
- `player_double_jump_p2_sheet.png`
- `player_hurt_p2_sheet.png`

**Output directory**: `disco_cop/assets/sprites/players/`

**Approach**: Python script with Pillow — load each P1 sheet, map specific pixel colors to P2 palette, save. Or re-render from the Blender model with swapped materials.

**Option A (Pillow color swap)**: ~50 lines, fast, pixel-accurate.
**Option B (Blender re-render)**: Modify `create_player_model.py` to accept a color scheme parameter, re-render all 6 animations. More work but higher quality if we ever change the model.

**Tasks**:
1. Pick approach (A or B)
2. Generate 6 P2 sprite sheets
3. Commit and push — Pi loads P2 textures when `player_index == 1`

**Estimated scope**: ~50-100 lines

---

## Build Order

```
Phase 1: HUD Sprites      ← smallest, unblocks Pi Phase 2 immediately
Phase 2: Rink Environment  ← unblocks Pi Phase 4 (level design)
Phase 3: Audio             ← can run in parallel with Phase 2
Phase 4: Player 2 Sprites  ← last, only needed for co-op
```

Phases 1 + 2 should ship first — they unblock the most Pi-side work.
Phase 3 can happen anytime since audio is independent of other art.
Phase 4 is lowest priority — co-op works fine with identical players using `modulate` tinting as a fallback.

---

## Git Workflow Reminder

```bash
# Start of session
cd ~/Disco-Cop        # or C:\Users\Ian\Disco Cop on Windows
git pull origin master

# After generating assets
git add disco_cop/assets/sprites/ disco_cop/assets/audio/ disco_cop/blender/scripts/
git commit -m "Art: {describe what was added}"
git push origin master

# Pi side pulls and integrates
```

---

## Verification Checklist

### Phase 1: HUD
- [ ] All PNGs exist in `assets/sprites/ui/`
- [ ] Health/shield bars have frame + fill as separate images
- [ ] 6 weapon icons, 1 ammo icon, 1 lives icon
- [ ] All use disco color palette (magenta/cyan/gold)
- [ ] Transparent backgrounds

### Phase 2: Rink Environment
- [ ] Rink floor tiles (2 variants) in tileset
- [ ] Carpet tile for lobby
- [ ] Chrome barrier tiles (top + side)
- [ ] 3 parallax layers with rink interior theme
- [ ] Disco ball glow spots visible in far parallax
- [ ] Colors match palette from skating_rink_level_plan.md

### Phase 3: Audio
- [ ] 17 SFX files in `assets/audio/sfx/` (WAV)
- [ ] 3 music files in `assets/audio/music/` (OGG)
- [ ] No clipping/distortion
- [ ] All under 500KB each (SFX) / 2MB each (music)
- [ ] Retro/disco aesthetic matches game style

### Phase 4: Player 2
- [ ] 6 P2 sprite sheets in `assets/sprites/players/`
- [ ] Visually distinct from P1 at 720p
- [ ] Same frame counts and dimensions as P1
- [ ] Animations look correct (no color bleeding artifacts)