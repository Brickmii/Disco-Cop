# Level 01: Roller Rink Rumble — Build Plan

## Concept

The first level is a **70s roller skating rink**. The player fights through a neon-lit rink where all enemies are on roller skates and use momentum-based sliding movement. The disco theme is front and center — disco ball, colored floor lights, wooden rink surface, chrome barriers.

The skating mechanic is the level's identity: enemies can't stop on a dime. They build speed, slide past you, slam into barriers, and regroup. Combat feels different from a standard platformer because threats come at you fast but overshoot.

---

## Level Layout

**Total size:** ~4800 x 1000 (similar scale to current level_01)

```
[Lobby] → [Rink Entrance] → [Main Rink Floor] → [Center Island] → [DJ Booth Arena] → [Boss: Rink Manager]

Section 1          Section 2              Section 3              Section 4           Section 5
x: 0-800           x: 800-1600           x: 1600-3200          x: 3200-4000        x: 4000-4800
```

### Section 1: Lobby (x: 0–800)
- **Vibe:** Carpet-floored entrance with benches, shoe cubbies, a ticket booth
- **Terrain:** Normal ground (no skating mechanic here — tutorial area)
- **Platforms:** Ground floor + 2 small elevated platforms (bench tops, counter)
- **Enemies:** 2 regular grunts (no skates) — ease the player in
- **Scroll lock:** First combat encounter, teaches basics before the rink

### Section 2: Rink Entrance (x: 800–1600)
- **Vibe:** Transition from carpet to polished wood floor. Rink barriers appear. Neon strips on the walls.
- **Terrain:** Ground floor with a short ramp down into the rink (rink floor is ~50px lower than lobby)
- **Rink barrier:** Chrome rails along top and bottom edges of the rink — enemies bounce off these
- **Enemies:** 3 skating grunts — first encounter with the slide mechanic
- **Scroll lock:** Locks when player drops onto rink floor

### Section 3: Main Rink Floor (x: 1600–3200)
- **Vibe:** The big open rink. Disco ball overhead casting colored light spots. Lane markings on the floor.
- **Terrain:** Wide flat rink floor (1600px long, the longest open area in the game)
- **Platforms:**
  - Rink barriers along top/bottom edges
  - 2 small elevated platforms (referee stands) at x:2000 and x:2800
  - Optional: bleacher seating along top edge as high platforms
- **Enemies:** 5 skating grunts + 2 skating shooters in 2 waves
  - Wave 1: 3 grunts from the right side
  - Wave 2: 2 grunts + 2 shooters from both sides
- **Scroll lock:** Large zone covering the rink, 2 spawner waves
- **Hazard:** Zamboni area at x:2400 — a moving platform/obstacle that crosses the rink periodically (optional, stretch goal)

### Section 4: Center Island / DJ Booth Approach (x: 3200–4000)
- **Vibe:** Elevated DJ booth visible in background, rink narrows with more barriers
- **Terrain:** Rink floor continues but with barriers creating a corridor/funnel
- **Platforms:**
  - 3 barrier islands (small platforms enemies can skate around)
  - Elevated walkway along the top (bleachers/seating area)
- **Enemies:** 4 skating grunts + 2 skating shooters — tighter space makes sliding more dangerous
- **Scroll lock:** Corridor combat, enemies ping-pong off barriers

### Section 5: Boss Arena — Rink Manager (x: 4000–4800)
- **Vibe:** The main show rink. Biggest disco ball. Spotlights. The Rink Manager stands center stage.
- **Terrain:** Wide flat arena (800px) with rink floor
- **Platforms:**
  - Large floor
  - 2 side platforms (elevated barrier sections) at edges
  - 1 center overhead platform (hanging speakers/DJ equipment)
- **Boss:** Rink Manager (re-skin/variant of Disco King, or a new mini-boss — TBD)
- **Scroll lock:** Boss arena locks on entry

---

## The Skating Mechanic

### Core Physics (Enemies Only)
The player does NOT skate — they have normal movement. Only enemies are on skates. This creates asymmetric combat: the player is precise, enemies are fast but sloppy.

### How It Works
Skating enemies replace direct velocity control with **acceleration-based movement**:

```
Current base_enemy behavior:
  velocity.x = direction * move_speed        # instant speed

Skating enemy behavior:
  velocity.x += direction * SKATE_ACCEL * delta    # gradual acceleration
  velocity.x = clamp(velocity.x, -MAX_SKATE_SPEED, MAX_SKATE_SPEED)
  velocity.x *= SKATE_FRICTION                     # slight deceleration each frame
```

### Tuning Parameters
```gdscript
const SKATE_ACCEL := 600.0       # How fast they build speed
const MAX_SKATE_SPEED := 250.0   # Faster than regular grunt (120)
const SKATE_FRICTION := 0.98     # Per-frame multiplier (1.0 = no friction, 0.9 = heavy friction)
const BRAKE_FRICTION := 0.90     # When actively trying to stop/reverse
const BARRIER_BOUNCE := 0.7      # Velocity retained after hitting a barrier
```

### Skating Behaviors by State

| State | Skating Behavior |
|-------|-----------------|
| **PATROL** | Skate back and forth at half accel, smooth turns |
| **CHASE** | Full accel toward player, overshoots on direction change |
| **ATTACK** | Lunge/charge — boost speed, then slide through attack zone |
| **HURT** | Knocked back and slides further than normal enemies |
| **Direction change** | Can't reverse instantly — decelerates to 0, then accelerates the other way. Creates a "sliding past" window where they're vulnerable |

### Barrier Bounce
When a skating enemy hits a rink barrier (StaticBody2D with a "barrier" group tag):
- `velocity.x *= -BARRIER_BOUNCE`
- Brief stun (0.1s) — visual wobble
- Continues sliding in reflected direction

This creates dynamic combat: enemies ricochet around the rink.

---

## New Enemy Types

### Skating Grunt (`skating_grunt.gd`)
- **Extends:** BaseEnemy (or EnemyGrunt with skating override)
- **Visual:** Grunt body + roller skates instead of boots, maybe a headband
- **Size:** 20x40 (same as regular grunt)
- **Stats:**
  ```
  max_health = 25.0        # Slightly less than regular grunt (30)
  move_speed = 250.0       # Max skating speed (higher than grunt's 120)
  damage = 12.0            # Slightly less per hit
  attack_range = 35.0      # Melee charge — closer range
  detection_range = 300.0  # Wider detection (they cover ground fast)
  attack_cooldown = 1.2    # Longer cooldown (they need to circle back)
  loot_chance = 0.25
  ```
- **Attack pattern:** Charge attack — accelerates toward player, slides through. If they miss, they overshoot and need to brake/turn around. Vulnerable during the turn.
- **Animations:** skate (replaces walk, 6 frames), charge (replaces attack, 4 frames), hurt (2 frames), death (4 frames — falls and slides)

### Skating Shooter (`skating_shooter.gd`)
- **Extends:** BaseEnemy (or EnemyShooter with skating override)
- **Visual:** Shooter body + roller skates, maybe disco-themed gun
- **Size:** 20x40
- **Stats:**
  ```
  max_health = 18.0
  move_speed = 200.0       # Fast but not as fast as skating grunt
  damage = 10.0
  attack_range = 280.0     # Shoots while skating
  detection_range = 400.0
  attack_cooldown = 1.8
  loot_chance = 0.30
  ```
- **Attack pattern:** Drive-by shooting — skates past the player while firing. Doesn't stop to shoot. Maintains momentum.
- **Animations:** skate (6 frames), shoot_skate (3 frames — shooting while moving), hurt (2 frames), death (4 frames)

---

## Environment Art

### Rink Floor
- **Material:** Polished wood — warm brown with lane line markings
- **Visual approach:** Tiled horizontal strip, repeating pattern
- **Size:** Full-width tiles, ~32px tall platform visuals (thicker than standard)
- **Color:** `Color(0.55, 0.35, 0.20)` base, lighter lane lines

### Rink Barriers
- **Material:** Chrome/metal rails
- **Visual:** Thin horizontal bars, shiny silver/white
- **Function:** StaticBody2D in group "barrier" — enemies bounce, player can jump over
- **Height:** 24px tall barriers (player can jump over, enemies cannot — they're on skates)

### Parallax Background
- **Layer 1 (far):** Dark rink ceiling with disco ball glow spots (magenta, cyan, gold circles)
- **Layer 2 (mid):** Bleacher seating silhouettes, neon exit signs
- **Layer 3 (near):** Rink wall detail, shoe rental counter, arcade machines

### Disco Ball Effect (stretch goal)
- Colored light spots that slowly move across the rink floor
- Implemented as animated ColorRects or Light2D nodes with low energy
- Purely cosmetic — no gameplay effect

### Color Palette
```
Rink floor:     #8C5A33 (warm wood)
Lane lines:     #D4A76A (lighter wood)
Barriers:       #C0C0C0 (chrome silver)
Barrier glow:   #FF69B4 (hot pink neon)
Carpet (lobby): #4A0E4E (deep purple)
Walls:          #1A0A2E (dark purple)
Neon accents:   #00FFFF (cyan), #FF1493 (deep pink), #FFD700 (gold)
Disco spots:    rotating cycle of magenta, cyan, gold, white
```

---

## Implementation Order

### Phase 1: Skating Grunt (ties into art build order #2)
1. Create `create_skating_grunt_model.py` — grunt body with roller skates
2. Generate `skating_grunt.blend`, render sprite sheets (skate, charge, hurt, death)
3. Create `skating_grunt.gd` extending BaseEnemy with skating physics
4. Create `skating_grunt.tscn` with sprites wired up
5. Test in `test_level.tscn` — verify sliding, direction changes, barrier bouncing

### Phase 2: Level Shell
1. Create `level_01_rink.gd` extending LevelBase
2. Build Section 1 (lobby) with normal platforms — re-use `_add_platform()`
3. Add rink floor helper: `_add_rink_floor()` — wider platforms with wood color
4. Add barrier helper: `_add_barrier()` — StaticBody2D in "barrier" group
5. Build all 5 sections with terrain only (no enemies yet)
6. Add parallax background layers with rink colors

### Phase 3: Combat Encounters
1. Wire up scroll-lock zones with skating grunt spawners
2. Add skating shooter (Phase 1 equivalent for shooter variant)
3. Tune spawn counts and wave timing
4. Add barrier bounce logic to skating enemies

### Phase 4: Boss
1. Design Rink Manager boss (variant of Disco King or new enemy)
2. Build model, render sprites
3. Implement boss AI — skating-based attacks
4. Wire into Section 5

### Phase 5: Polish (stretch goals)
1. Disco ball light effect
2. Zamboni moving obstacle
3. Floor lane line detail sprites
4. Neon glow effects on barriers
5. Environment sprite sheets (bleachers, DJ booth, shoe counter)

---

## Technical Notes

### Barrier Bounce Implementation
```gdscript
# In skating enemy's move_and_slide() override or _physics_process:
func _physics_process(delta: float) -> void:
    # ... normal skating accel logic ...
    move_and_slide()

    # Check for barrier collision
    for i in get_slide_collision_count():
        var collision := get_slide_collision(i)
        var collider := collision.get_collider()
        if collider.is_in_group("barrier"):
            velocity.x *= -BARRIER_BOUNCE
            # Brief stun
            _stun_timer = 0.1
```

### Rink Floor vs Normal Floor
No special physics on the floor itself — the skating mechanic is entirely in the enemy scripts. The rink floor is just a visual distinction (wood color vs carpet color). This keeps things simple and avoids modifying player physics.

### Replacing Level 01
The current `level_01.gd` (Disco Dungeon) gets replaced by the skating rink. The new file can be `level_01.gd` directly, or we create `level_01_rink.gd` and swap the reference. Decision: **replace in-place** since there's no reason to keep the placeholder dungeon layout.

---

## File Manifest

| File | Status | Purpose |
|------|--------|---------|
| `scenes/levels/level_01.gd` | Replace | Skating rink level script |
| `scenes/enemies/skating_grunt.gd` | New | Skating grunt with slide physics |
| `scenes/enemies/skating_grunt.tscn` | New | Skating grunt scene |
| `scenes/enemies/skating_shooter.gd` | New | Skating shooter with drive-by |
| `scenes/enemies/skating_shooter.tscn` | New | Skating shooter scene |
| `blender/models/create_skating_grunt_model.py` | New | Grunt + skates model |
| `blender/models/create_skating_shooter_model.py` | New | Shooter + skates model |
| `assets/sprites/enemies/skating_grunt_*.png` | New | Skating grunt sheets |
| `assets/sprites/enemies/skating_shooter_*.png` | New | Skating shooter sheets |
| `blender/reference/skating_rink_level_plan.md` | New | This document |
