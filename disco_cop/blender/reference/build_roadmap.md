# Disco Cop — Build Roadmap (Passes 3-8)

## Design Philosophy
- Couch coop run-and-gun that runs on a Pi 5. If it dev's on the Pi, it plays on the Pi.
- Minimal, tight, fun. Castle Crashers energy — genre nobody's filling anymore.
- Borderlands loot loop meets Contra gameplay.
- Develop on Pi (Godot), art on PC (Blender), GitHub syncs both.

---

## Game Structure (Final)

| # | Level | Theme | Boss | Status |
|---|-------|-------|------|--------|
| 0 | Tutorial | Skating Rink | None | DONE |
| 1 | Level 1 | Disco Rink | Disco King | DONE |
| 2 | Level 2 | 70's Venice Beach / Muscle Beach | "Arnoldo" (Schwarzenegger parody) | Not started |
| 3 | Level 3 | Led Zeppelin Concert | Jimmy Page (guitar weapon) | Not started |
| 4 | Level 4 | Blondie Concert | Blondie (flyer on giant Heart of Glass) | Not started |
| 5 | Level 5 | The Bee Gees | Barry, Robin & Maurice Gibb (all 3 at once) | Not started |

### Game Flow
Main Menu -> Lobby -> Tutorial -> L1 -> L2 -> L3 -> L4 -> L5 -> Credits -> Unlock next mode

### Play Modes (Borderlands-style NG+)
1. **Normal** — First playthrough. Standard enemy stats, standard loot.
2. **Disco Fever** (NG+) — Unlocked after beating Normal. Tougher enemies, better gun drops, keep your gear.
3. **Saturday Night Slaughter** (NG++) — Unlocked after Fever. Hardest difficulty, legendary drop rates up, enemies hit like trucks.

Weapons and gear carry between levels AND between playthroughs. Each mode scales enemy HP/damage and loot rarity tables.

---

## Build Pass 3: Polish Pass
*Make what exists feel finished. Lock down design bible.*

### 3.1 Game Flow & Progression System
- Full level chain: Tutorial -> L1 -> L2 -> L3 -> L4 -> L5 -> Credits
- Weapon carry-over between ALL levels (already works Tutorial -> L1)
- Credits/stats screen after beating the Bee Gees (enemies killed, time, loot count)
- NG+ unlock system: track play mode in GameManager, scale enemies + loot per mode
- Save system: persist player gear + unlocked modes between sessions

### 3.2 Character Sizes & Designs
- Character sizing is a PC-side concern — adjust in Blender render params
- Player 24x48, enemies 20x40, bosses 48x80 are current targets
- Visual style guide needed per level (color palettes, enemy silhouettes)
- Bee Gees: Barry (ranged/leader, falsetto attacks?), Robin (speed), Maurice (tank)
- Arnoldo: huge sprite, flexing attacks, throws dumbbells
- Jimmy Page: guitar sweeps, pyrotechnic AoE, amp feedback waves
- Blondie on Heart of Glass: flyer boss, swooping attacks, glass shard projectiles

### 3.3 Backgrounds & Environments
- Level 2: Venice Beach — sand, boardwalk, weight benches, palm trees, ocean parallax
- Level 3: Led Zeppelin stage — concert stage, amps, Marshall stacks, crowd silhouettes, pyro
- Level 4: Blondie stage — CBGB punk club aesthetic, neon, crowd parallax
- Level 5: Bee Gees arena — ultimate disco floor, mirror balls, spotlight beams, light-up tiles

### 3.4 Mechanical Polish (Pi-side code)
- Fix pause menu (_input while paused bug — same approach as game_over fix)
- Screen transitions (fade in/out between scenes)
- Boss health bar on HUD
- Weapon pickup toast/notification
- Death/respawn effect (flash + brief invincibility)
- Camera polish (smooth transitions entering scroll-lock zones)
- Level-to-level transition flow (victory -> brief delay -> next level auto-load)

---

## Build Pass 4: Content Pass
*Build all remaining levels, enemies, and bosses*

### 4.1 Enemy Types Per Level

**Level 2 — Venice Beach:**
- Weightlifter Brute: slow, tanky, melee slams (reskinned grunt archetype)
- Roller Skater: fast, charges at player (reskinned skating grunt)
- Beach Bum Shooter: ranged, throws frisbees/volleyballs (reskinned shooter)
- Seagull Flyer: dive-bombs from above (reskinned flyer)

**Level 3 — Led Zeppelin Concert:**
- Roadie: melee, carries amp/equipment as weapon
- Groupie Rusher: fast, swarm type, low HP
- Pyro Technician: ranged, fire element projectiles
- Speaker Stack: stationary turret, sonic wave attacks

**Level 4 — Blondie Concert:**
- Punk Mosher: melee, erratic movement
- Bouncer: tanky, blocks path
- Stagehand: ranged, throws equipment
- Spotlight Drone: flyer, tracks player with beam

**Level 5 — Bee Gees:**
- Disco Minions between boss phases? Or pure boss fight?

### 4.2 Boss Designs

**Arnoldo (Level 2):**
- Phase 1: Flexing attacks, throws dumbbells
- Phase 2: Picks up weight bench, sweeping melee
- Phase 3: "I'll be back" — enrage rush, rapid dumbbell throw

**Jimmy Page (Level 3):**
- Phase 1: Guitar sweep melee, amp feedback waves
- Phase 2: Pyrotechnic AoE columns, power chord projectiles
- Phase 3: Guitar solo — bullet hell pattern, stage lights laser sweep

**Blondie / Heart of Glass (Level 4):**
- Flyer boss — rides giant glass heart
- Phase 1: Swooping attacks, glass shard projectiles
- Phase 2: Heart cracks, shards rain from above, faster swoops
- Phase 3: Heart shatters — Blondie attacks directly, desperate fast attacks

**The Bee Gees (Level 5) — ALL 3 AT ONCE:**
- Barry Gibb: ranged leader, falsetto sonic waves, commands brothers
- Robin Gibb: speed, dashes across arena, combo attacks
- Maurice Gibb: tank, ground pounds, shields brothers
- When one dies, survivors enrage (faster, harder hits)
- Must kill all 3 to win

### 4.3 Level Design
- Each level: 3-4 scroll-lock combat zones + boss arena
- Difficulty curve: more enemies per zone, tighter spacing, faster spawns
- Level 5: possibly just a boss arena (no regular zones, pure Bee Gees fight)
- NG+ scaling: enemy count +25%, HP +50%, damage +40% per mode

### 4.4 Weapons & Loot
- Loot scales with level number (level param to WeaponGenerator)
- Each boss guarantees Epic+ drop (already works for Disco King)
- NG+ modes shift rarity tables (more Rare/Epic/Legendary)
- Consider 1 new manufacturer per level theme?

---

## Build Pass 5: Art Integration
*Wire all new content art from PC*

- Enemy sprites for all new types (4 per level x 4 levels = ~16 enemy variants)
- Boss sprites: Arnoldo, Jimmy Page, Blondie/Heart of Glass, 3x Bee Gees
- Environment tilesets + parallax for Levels 2-5
- Effects (muzzle flash, impact, explosion, shield break, loot glow)
- UI: boss health bar, weapon pickup toast, credits screen, play mode select

---

## Build Pass 6: Multiplayer + Final Art
*Make 2-4 player rock solid*

- Test all 5 levels + all 3 modes with P2-P4
- Camera behavior with spread-out players
- Shared lives vs individual lives decision
- Player revival mechanic (down state + revive timer?)
- Final art integration (anything remaining from PC)
- P2/P3/P4 palette swaps for all content

---

## Build Pass 7: Rough Final Build
*Everything together, playable start to finish*

- Full playthrough: Tutorial through Bee Gees on all 3 modes
- Performance profiling on Pi 5 (target 60fps throughout, all modes)
- Balance pass: enemy HP, damage, spawn counts, boss difficulty per mode
- Audio pass: unique music per level, SFX coverage check
- Object pool tuning for worst-case projectile counts
- Bug sweep

---

## Build Pass 8: Final MVP Pass
*Ship it*

- Final bug fixes from playtesting
- Difficulty tuning
- Main menu polish (title art, mode select, options)
- Save/load system (gear + unlocked modes persist)
- Any last visual/audio polish
- Release build for Pi 5
- Consider: itch.io release? Other platforms?
