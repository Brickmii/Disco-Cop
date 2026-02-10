# Build Pass 3: Polish Pass — Detailed Plan

## Overview
Make the existing game feel finished. Fix bugs, add juice, build the full level chain,
add NG+ system, credits screen. When this pass is done, the game structure is final —
Content Pass just fills in levels 2-5.

---

## Phase 1: Bug Fixes

### 1.1 Fix Pause Menu (frozen while paused)
Same bug we fixed on game_over — `_input()` doesn't fire with PROCESS_MODE_ALWAYS while tree is paused.

**File:** `scenes/ui/pause_menu.gd`
- Remove `get_tree().paused` entirely (like game_over fix)
- Instead: freeze gameplay by setting level node's process_mode to DISABLED
- OR: simpler — poll `Input.is_action_just_pressed("pause")` in `_process()` instead of `_input()`
- Keep PROCESS_MODE_ALWAYS so _process runs while game is "paused"
- Actually simplest: don't pause tree. Just show overlay + set a GameManager.is_paused flag
  that the level/enemies/player check. But that's invasive.
- **Best approach:** Use `_process` + `Input.is_action_just_pressed("pause")` polling.
  The pause action is defined in project.godot so it works for both keyboard and gamepad.
  Keep `get_tree().paused` for actual pause (stops physics/enemies). Only the pause toggle
  input detection needs the fix.

**Changes (~10 lines):**
```
- Remove _input() function
- Add _process():
    if Input.is_action_just_pressed("pause"):
        toggle_pause()
- toggle_pause() stays the same (pauses/unpauses tree)
- Resume button: use _on_resume_pressed signal from button (UI buttons work while paused
  because the button node itself has PROCESS_MODE_ALWAYS inherited from parent)
```

### 1.2 Fix Quit Button on Pause Menu
- `_on_quit_pressed` uses `change_scene_to_file` (not deferred) — should be deferred
  to avoid cascade during paused state

**File:** `scenes/ui/pause_menu.gd`

---

## Phase 2: Screen Transitions

### 2.1 Transition Overlay (new autoload)
Fade-to-black between scenes for polish. Simple ColorRect + tween.

**New file:** `autoloads/transition.gd`
**Register as autoload in project.godot**

```
extends CanvasLayer

var _color_rect: ColorRect
var _is_transitioning := false

func _ready():
    layer = 100  # On top of everything
    _color_rect = ColorRect.new()
    _color_rect.color = Color.BLACK
    _color_rect.size = Vector2(1280, 720)
    _color_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _color_rect.visible = false
    add_child(_color_rect)

func change_scene(path: String, duration: float = 0.3):
    if _is_transitioning: return
    _is_transitioning = true
    _color_rect.visible = true
    _color_rect.modulate.a = 0.0
    var tween = create_tween()
    tween.tween_property(_color_rect, "modulate:a", 1.0, duration)
    tween.tween_callback(func(): get_tree().change_scene_to_file(path))
    tween.tween_property(_color_rect, "modulate:a", 0.0, duration)
    tween.tween_callback(func():
        _color_rect.visible = false
        _is_transitioning = false
    )
```

### 2.2 Replace all raw scene changes
Every `get_tree().change_scene_to_file()` and `call_deferred("change_scene_to_file")`
needs to go through `Transition.change_scene()` instead.

**Files to update:**
- `scenes/ui/main_menu.gd` — start button
- `scenes/ui/lobby.gd` — start game, skip tutorial
- `scenes/ui/game_over.gd` — continue (tutorial→L1, victory→menu)
- `scenes/ui/pause_menu.gd` — quit to menu
- `scenes/levels/test_level.gd` — tutorial complete → Level 1

---

## Phase 3: Level Chain & Progression

### 3.1 Level Registry in GameManager
Define the full level sequence so game_over.gd can auto-advance.

**File:** `autoloads/game_manager.gd`

```
const LEVEL_ORDER: Array[String] = [
    "tutorial",   # test_level.tscn (auto-advances, not in this list for victory)
    "level_01",   # Disco Rink
    "level_02",   # Venice Beach
    "level_03",   # Led Zeppelin Concert
    "level_04",   # Blondie Concert
    "level_05",   # Bee Gees
]

const LEVEL_SCENES: Dictionary = {
    "tutorial": "res://scenes/levels/test_level.tscn",
    "level_01": "res://scenes/levels/level_01.tscn",
    "level_02": "res://scenes/levels/level_02.tscn",
    "level_03": "res://scenes/levels/level_03.tscn",
    "level_04": "res://scenes/levels/level_04.tscn",
    "level_05": "res://scenes/levels/level_05.tscn",
}

func get_next_level() -> String:
    var idx := LEVEL_ORDER.find(current_level)
    if idx >= 0 and idx < LEVEL_ORDER.size() - 1:
        return LEVEL_ORDER[idx + 1]
    return ""  # No next level = game complete
```

### 3.2 Update game_over.gd Victory Flow
Instead of hardcoded tutorial→L1 check, use the level chain.

**File:** `scenes/ui/game_over.gd`

```
func _on_continue_pressed():
    if not _is_showing: return
    _is_showing = false
    visible = false
    if _is_victory:
        var next := GameManager.get_next_level()
        if next != "":
            # Save weapons and advance
            _save_all_player_weapons()
            Transition.change_scene(GameManager.LEVEL_SCENES[next])
        else:
            # Beat the game! Show credits
            Transition.change_scene("res://scenes/ui/credits.tscn")
    else:
        GameManager.reset_game()
        Transition.change_scene("res://scenes/ui/main_menu.tscn")
```

### 3.3 Update test_level.gd
Tutorial auto-advances without going through game_over victory screen.
Keep current behavior but use Transition.

### 3.4 Each Level Sets current_level
Already done for tutorial and level_01. Future levels will follow same pattern.

---

## Phase 4: NG+ System

### 4.1 Play Mode Enum & Tracking

**File:** `autoloads/game_manager.gd`

```
enum PlayMode { NORMAL, DISCO_FEVER, SATURDAY_NIGHT_SLAUGHTER }

var play_mode: PlayMode = PlayMode.NORMAL
var unlocked_modes: Array[PlayMode] = [PlayMode.NORMAL]

# Difficulty scaling per mode
const MODE_SCALING: Dictionary = {
    PlayMode.NORMAL: {"hp": 1.0, "damage": 1.0, "count": 1.0, "loot_bonus": 0},
    PlayMode.DISCO_FEVER: {"hp": 1.5, "damage": 1.4, "count": 1.25, "loot_bonus": 1},
    PlayMode.SATURDAY_NIGHT_SLAUGHTER: {"hp": 2.0, "damage": 1.8, "count": 1.5, "loot_bonus": 2},
}

func get_difficulty_scale() -> Dictionary:
    return MODE_SCALING[play_mode]
```

### 4.2 Enemy Scaling
Enemies read difficulty from GameManager at spawn.

**File:** `scenes/enemies/base_enemy.gd`
- In `_ready()`: multiply max_health and damage by mode scaling
- Spawner spawn_count already set per level, so count scaling applies in level scripts

### 4.3 Loot Scaling
WeaponGenerator and ShieldGenerator get a rarity bonus from mode.

**File:** `resources/weapons/weapon_generator.gd`
- `generate()` already takes `level` param — add mode bonus to effective level
- Rarity roll shifted by loot_bonus (fewer commons, more rares)

### 4.4 Unlock Flow
After credits, unlock next mode.

**File:** `scenes/ui/credits.gd` (new)
- Show stats + "Disco Fever Unlocked!" message
- On continue → main menu with mode select available

### 4.5 Mode Select
Add to lobby or main menu.

**File:** `scenes/ui/lobby.gd` or `scenes/ui/main_menu.gd`
- Show current mode, allow cycling through unlocked modes
- Left/Right or LB/RB to change mode

### 4.6 Save/Load System
Persist unlocked modes + player gear between sessions.

**File:** `autoloads/game_manager.gd`
- `save_game()` — write to `user://save.json`
- `load_game()` — read on startup
- Data: unlocked_modes, play_mode, player_weapons (serialized WeaponData)
- Load in `_ready()`, save after credits unlock

---

## Phase 5: Credits Screen

### 5.1 Credits Scene (new)

**New file:** `scenes/ui/credits.tscn` + `scenes/ui/credits.gd`

Content:
- "CONGRATULATIONS!" title
- Stats: enemies killed, bosses defeated, time elapsed, loot collected
- "Mode Unlocked: Disco Fever!" (if applicable)
- Scrolling credits: game name, your name, music credits
- "Press ENTER to continue" → unlock mode → main menu

### 5.2 Stats Tracking

**File:** `autoloads/game_manager.gd`
```
var stats: Dictionary = {
    "enemies_killed": 0,
    "bosses_defeated": 0,
    "loot_collected": 0,
    "time_elapsed": 0.0,
}
```

**File:** `scenes/levels/level_base.gd`
- Increment enemies_killed on EventBus.enemy_died
- Increment bosses_defeated on EventBus.boss_defeated
- Track time in _process

---

## Phase 6: Death & Respawn Polish

### 6.1 Respawn Invincibility
Brief flash + invincibility after respawn.

**File:** `scenes/player/player.gd`
- On respawn: 2 second invincibility window
- Flash sprite (modulate alpha oscillation)
- HealthComponent ignores damage during invincibility

### 6.2 Death Effect
Screen flash or slowmo on last player death.

**File:** `scenes/levels/level_base.gd`
- On game_over: brief Engine.time_scale = 0.3 for 0.5s, then normal

---

## Phase 7: Weapon Pickup Notification

### 7.1 Pickup Toast on HUD

**File:** `scenes/ui/game_hud.gd`
- Connect EventBus.weapon_picked_up
- Show floating label: weapon name in rarity color
- Auto-fade after 2 seconds
- Stack if multiple pickups happen quickly

---

## Phase 8: Camera Polish

### 8.1 Smooth Zone Entry
Camera snaps a bit when entering scroll-lock zones.

**File:** `scenes/camera/multi_target_camera.gd`
- Increase smooth_speed lerp during zone transitions
- Or: scroll_lock_zone nudges camera bounds smoothly

---

## Implementation Order

| Step | Phase | Est. Lines | Priority |
|------|-------|-----------|----------|
| 1 | 1.1-1.2 Pause menu fix | ~15 | HIGH — bug |
| 2 | 2.1-2.2 Screen transitions | ~40 + updates | HIGH — juice |
| 3 | 3.1-3.4 Level chain | ~30 | HIGH — structure |
| 4 | 5.2 Stats tracking | ~15 | MED — needed for credits |
| 5 | 5.1 Credits screen | ~50 | MED — endgame |
| 6 | 4.1-4.3 NG+ scaling | ~40 | MED — replayability |
| 7 | 4.4-4.5 Unlock + mode select | ~30 | MED — replayability |
| 8 | 4.6 Save/load system | ~50 | MED — persistence |
| 9 | 6.1-6.2 Death/respawn polish | ~25 | LOW — juice |
| 10 | 7.1 Weapon pickup toast | ~25 | LOW — juice |
| 11 | 8.1 Camera polish | ~10 | LOW — juice |

Total: ~330 lines of new/modified code across ~12 files.

---

## Files Summary

| File | Status | Changes |
|------|--------|---------|
| `autoloads/game_manager.gd` | MODIFY | Level registry, NG+ mode, stats, save/load |
| `autoloads/transition.gd` | NEW | Scene transition overlay |
| `project.godot` | MODIFY | Register Transition autoload |
| `scenes/ui/pause_menu.gd` | MODIFY | Fix _input → _process polling |
| `scenes/ui/game_over.gd` | MODIFY | Level chain advancement |
| `scenes/ui/main_menu.gd` | MODIFY | Use Transition, mode display |
| `scenes/ui/lobby.gd` | MODIFY | Use Transition, mode select |
| `scenes/ui/credits.gd` | NEW | Credits + stats + unlock |
| `scenes/ui/credits.tscn` | NEW | Credits scene |
| `scenes/ui/game_hud.gd` | MODIFY | Weapon pickup toast |
| `scenes/enemies/base_enemy.gd` | MODIFY | NG+ HP/damage scaling |
| `scenes/player/player.gd` | MODIFY | Respawn invincibility |
| `scenes/levels/level_base.gd` | MODIFY | Stats tracking, death slowmo |
| `scenes/levels/test_level.gd` | MODIFY | Use Transition |
| `scenes/camera/multi_target_camera.gd` | MODIFY | Smoother zone transitions |
| `resources/weapons/weapon_generator.gd` | MODIFY | NG+ loot bonus |

---

## Verification Checklist

- [ ] Pause menu opens and closes with ESC/Start while game is running
- [ ] Screen fades to black between every scene change
- [ ] Beat Level 1 → auto-advances to Level 2 (placeholder scene OK)
- [ ] Beat final level → credits screen with stats
- [ ] Credits → "Disco Fever Unlocked!" → main menu
- [ ] Mode select visible in lobby, can switch between unlocked modes
- [ ] Disco Fever mode: enemies visibly tankier, better loot drops
- [ ] Save + quit + relaunch: unlocked modes persist
- [ ] Player respawns with brief invincibility flash
- [ ] Weapon pickup shows name/rarity toast on HUD
- [ ] Camera doesn't jerk when entering scroll-lock zones
- [ ] Full playthrough: Menu → Lobby → Tutorial → L1 → (L2 placeholder) → no crashes
