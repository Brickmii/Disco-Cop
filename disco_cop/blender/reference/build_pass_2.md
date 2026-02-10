# Disco Cop — Build Pass 2: Gameplay Systems

## What's Done (Build Pass 1)
- 11 code phases complete, 39 scripts, 20 scenes
- Player with 6 animations, 8-dir aiming, double jump, coyote time
- 5 enemy types (skating grunt, skating shooter, flyer, grunt, shooter) + Disco King boss
- Procedural weapon generator (6 types, 5 elements, 5 rarities)
- Shield generator with element resistances and nova-on-break
- Object-pooled projectiles (30) and VFX (10)
- VFX: muzzle flash, impact, explosion, shield break
- Parallax 3-layer scrolling background with real sprites
- Controller support (8BitDo USB, gamepad fallback for P1)
- Barrier-stuck mechanic with wiggle escape
- 5120px side-scrolling test level with camera tracking

## What's Next (5 Phases)

---

## Phase 1: Enemy Loot Drops (wire existing systems)

**Goal**: Enemies drop weapons, shields, health, ammo on death.

**Already built**:
- `LootTable.roll_drop(loot_chance, level, rarity_bonus)` — weighted random drops
- `LootTable.roll_boss_drop(level)` — guaranteed Epic+ weapon + Rare+ shield
- `LootDrop` scene with pickup, texture, rarity color, bob animation
- `base_enemy.gd` calls `LootTable.roll_drop()` in `_on_died()` already
- `boss_base.gd` calls `LootTable.roll_boss_drop()` in `_on_died()` already

**Problem**: Both emit `EventBus.loot_dropped` but nobody spawns the actual LootDrop scene. `level_base.gd` has `_on_loot_dropped()` that instantiates the scene, but test_level doesn't extend LevelBase.

**Tasks**:
1. Add loot drop spawning to `test_level.gd`:
   - Connect `EventBus.loot_dropped` signal
   - Instantiate `loot_drop.tscn`, call `setup(data, position)`, add to scene
2. Verify `base_enemy._on_died()` emits the signal with correct data format
3. Verify `boss_disco_king._on_died()` drops boss loot (2 items)
4. Test: kill enemy, see loot pop up, walk over it, equip weapon/shield

**Estimated scope**: ~20 lines of code changes

---

## Phase 2: HUD (wire existing UI)

**Goal**: Health bar, shield bar, ammo count, weapon name, boss health bar visible during gameplay.

**Already built**:
- `game_hud.gd` — CanvasLayer with boss health bar, damage numbers, spawns PlayerHUD per player
- `game_hud.tscn` — boss ProgressBar + name label
- `player_hud.gd` — health/shield bars, weapon label, ammo display, lives counter
- `player_hud.tscn` — VBox with ProgressBar + Label nodes
- All EventBus signals already emitted by player.gd, weapon_holder.gd, shield_component.gd

**Problem**: GameHUD is instantiated by `level_base.gd` but test_level doesn't extend LevelBase. Nobody creates GameHUD in the test level.

**Tasks**:
1. Add GameHUD instantiation to `test_level.gd`:
   - `var hud_scene := preload("res://scenes/ui/game_hud.tscn")`
   - `add_child(hud_scene.instantiate())`
2. Verify `game_hud.gd` connects to `EventBus.player_spawned` and creates PlayerHUDs
3. Verify `player_hud.gd` connects to health/shield/weapon/ammo signals
4. Style pass: make bars readable at 720p on Pi (font size, bar colors)
5. Test: take damage → health bar drops, pick up weapon → label changes, boss fight → boss bar shows

**Estimated scope**: ~10 lines + styling tweaks

---

## Phase 3: Sound Effects (populate AudioManager)

**Goal**: Gunshots, impacts, explosions, enemy death, loot pickup, music.

**Already built**:
- `AudioManager` autoload with 16-channel SFX pool + music player
- `AudioManager.play_sfx(stream, volume_db)` and `play_music(stream, volume_db)`
- All gameplay events already emit EventBus signals

**Approach**: Generate placeholder SFX using sfxr/jsfxr (free retro sound generator) or source from freesound.org. Disco/funk music loop from a free library.

**File structure**:
```
assets/audio/
├── sfx/
│   ├── shoot_pistol.wav
│   ├── shoot_shotgun.wav
│   ├── shoot_sniper.wav
│   ├── impact_hit.wav
│   ├── impact_crit.wav
│   ├── explosion.wav
│   ├── enemy_death.wav
│   ├── player_hurt.wav
│   ├── player_death.wav
│   ├── shield_break.wav
│   ├── shield_recharge.wav
│   ├── loot_pickup.wav
│   ├── weapon_reload.wav
│   ├── weapon_swap.wav
│   └── menu_select.wav
└── music/
    ├── menu_theme.ogg
    ├── level_theme.ogg
    └── boss_theme.ogg
```

**Tasks**:
1. Create `assets/audio/sfx/` and `assets/audio/music/` directories
2. Generate/source ~15 SFX files (WAV, short, retro style)
3. Source 2-3 music loops (OGG, 30-60 sec loops, disco/funk/synthwave)
4. Create `autoloads/sfx_library.gd` — preloads all SFX as constants:
   ```gdscript
   const SHOOT_PISTOL := preload("res://assets/audio/sfx/shoot_pistol.wav")
   const IMPACT_HIT := preload("res://assets/audio/sfx/impact_hit.wav")
   # etc.
   ```
5. Create `autoloads/music_manager.gd` or extend AudioManager — connects to EventBus signals:
   - `weapon_fired` → play shoot SFX (vary by weapon type)
   - `damage_dealt` → play impact SFX (crit = louder/different)
   - `enemy_died` → play death SFX
   - `shield_broken` → play shield break SFX
   - `loot_picked_up` → play pickup SFX
   - `level_started` → play level music
   - `boss_spawned` → crossfade to boss music
6. Test: every action should have audio feedback

**Estimated scope**: ~80 lines of code + audio files

**Note**: Audio files are created on PC or downloaded. Push via git, pull on Pi. Godot auto-imports WAV/OGG.

---

## Phase 4: Level Design (real progression)

**Goal**: Turn the game into a playable 3-5 minute run from start to boss.

**Already built**:
- `scroll_lock_zone.gd` — locks camera, spawns waves, removes walls when cleared
- `spawner.gd` — spawns N enemies with delay, tracks defeats
- `level_01.gd` — full 6-section level with terrain, parallax, scroll locks, boss
- `level_base.gd` — player spawning, HUD, loot, pause/game-over menus

**Current test_level**: flat ground, scattered enemies, no progression. Fun for testing but no structure.

**Two options** (pick one):

### Option A: Upgrade test_level to a real level
Keep the side-scroller format, add scroll-lock combat zones:
- **Zone 1** (x: 200-900): 3 skating grunts, 1 skating shooter. Barrier at x:900 until cleared.
- **Zone 2** (x: 900-2000): 2 shooters, 2 flyers. Platform jumping section.
- **Zone 3** (x: 2000-3200): Mixed wave — 4 grunts + 2 shooters + 1 flyer. Tighter barriers.
- **Zone 4** (x: 3200-4300): Pre-boss gauntlet. Heavy enemies, health drops.
- **Boss** (x: 4300-5120): Disco King arena with side platforms.

### Option B: Fix level_01 to use working sprites
- Change level_01 to use skating_grunt/skating_shooter/flyer instead of base grunt/shooter
- Use parallax sprite textures instead of ColorRects
- Extend LevelBase for automatic HUD/loot/pause integration
- Already has scroll-lock zones and boss placement

**Tasks (Option A)**:
1. Add scroll-lock zones to test_level.tscn (invisible walls + spawner triggers)
2. Wire spawner.gd to spawn skating enemies and flyers
3. Add barriers between zones (collision_layer 8, break when zone cleared)
4. Place health/ammo pickups between zones
5. Test full run: fight through 4 zones, reach boss, beat boss → victory screen

**Tasks (Option B)**:
1. Update level_01.gd enemy scenes to skating variants
2. Replace ColorRect parallax with sprite parallax textures
3. Add kill zones for all bottomless pits
4. Change lobby.gd back to level_01.tscn
5. Test full run through level_01

**Estimated scope**: 100-200 lines depending on option

---

## Phase 5: 2-Player Co-op

**Goal**: Two players on screen with split/shared camera.

**Already built**:
- `InputManager` — 4-player device mapping, gamepad per-player
- `GameManager` — player registry with lives tracking
- `multi_target_camera.gd` — camera that tracks multiple players
- Lobby join system — gamepad button press registers new player
- `level_base.gd` — spawns players at `spawn_points[i]` for each registered player

**Current blocker**: test_level hardcodes a single Player node. Need dynamic spawning.

**Tasks**:
1. Remove hardcoded Player from test_level.tscn
2. Add player spawning in test_level.gd (like level_base does):
   ```gdscript
   var player_scene := preload("res://scenes/player/player.tscn")
   for i in GameManager.get_active_player_indices():
       var p := player_scene.instantiate()
       p.player_index = i
       p.position = spawn_points[i]
       add_child(p)
   ```
3. Replace Camera2D with MultiTargetCamera (tracks all players, zooms to fit)
4. Fix InputManager to assign 2nd gamepad to player 1 in lobby
5. Add spawn_points array to test_level (P1 left, P2 slightly right)
6. Test: join 2 players in lobby → both spawn → camera tracks both → independent controls
7. Verify: each player gets own HUD, loot pickups work per-player, death/respawn

**Hardware**: 8BitDo (USB) + Xbox controller (Bluetooth)
- Pair Xbox: `bluetoothctl` → `scan on` → pair → trust → connect
- Godot should see it as joypad device 1

**Estimated scope**: ~50 lines of code

---

## Build Order (recommended)

```
Phase 1: Loot Drops    (~30 min)  ← smallest, instant gratification
Phase 2: HUD           (~30 min)  ← makes combat readable
Phase 4: Level Design   (~1-2 hr) ← makes it a real game
Phase 3: Sound          (~1-2 hr) ← needs audio files from PC or web
Phase 5: Co-op         (~1 hr)    ← needs 2nd controller paired
```

Phases 1+2 can be done in one session (under 1 hour).
Phase 4 is the big one that turns this into a playable game.
Phase 3 depends on sourcing audio files.
Phase 5 is a bonus — test when 2nd controller is ready.

---

## Verification Checklist (per phase)

### Phase 1: Loot
- [ ] Kill skating grunt → random drop appears
- [ ] Kill flyer → random drop appears
- [ ] Walk over weapon drop → weapon equips, label changes
- [ ] Walk over health drop → health refills
- [ ] Kill Disco King → guaranteed Epic+ weapon drops
- [ ] FPS stays above 60 with loot on screen

### Phase 2: HUD
- [ ] Health bar visible, updates on damage
- [ ] Shield bar visible, drains and recharges
- [ ] Weapon name + ammo count shown
- [ ] Boss health bar appears during Disco King fight
- [ ] Damage numbers pop up on enemy hits
- [ ] All text readable at 720p

### Phase 3: Sound
- [ ] Gunshot on every fire
- [ ] Impact sound on every hit
- [ ] Explosion sound for explosive weapons
- [ ] Enemy death sound
- [ ] Shield break sound
- [ ] Loot pickup sound
- [ ] Background music loops
- [ ] Boss music plays in boss fight
- [ ] No audio glitches or clipping

### Phase 4: Level
- [ ] Scroll-lock zones block progress until enemies cleared
- [ ] Enemy waves spawn correctly per zone
- [ ] Difficulty ramps up across zones
- [ ] Boss arena works (Disco King + platforms)
- [ ] Victory screen on boss defeat
- [ ] Game Over on player death (with continue option)
- [ ] Full run takes 3-5 minutes

### Phase 5: Co-op
- [ ] 2 players join in lobby
- [ ] Both spawn in level
- [ ] Camera tracks both players
- [ ] Independent controls (each player moves/shoots separately)
- [ ] Each player has own HUD
- [ ] Loot pickups work per-player
- [ ] Game Over only when ALL players dead
