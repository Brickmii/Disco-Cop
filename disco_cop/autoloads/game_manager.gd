extends Node
## Manages game state, player registry, lives, and scene transitions.

enum GameState { MENU, LOBBY, PLAYING, PAUSED, GAME_OVER, VICTORY }
enum PlayMode { NORMAL, DISCO_FEVER, SATURDAY_NIGHT_SLAUGHTER }

const MAX_PLAYERS := 4
const DEFAULT_LIVES := 3
const SAVE_PATH := "user://save.json"

const MODE_SCALING: Dictionary = {
	PlayMode.NORMAL: {"hp": 1.0, "damage": 1.0, "loot_bonus": 0},
	PlayMode.DISCO_FEVER: {"hp": 1.5, "damage": 1.4, "loot_bonus": 1},
	PlayMode.SATURDAY_NIGHT_SLAUGHTER: {"hp": 2.0, "damage": 1.8, "loot_bonus": 2},
}

const MODE_NAMES: Dictionary = {
	PlayMode.NORMAL: "Normal",
	PlayMode.DISCO_FEVER: "Disco Fever",
	PlayMode.SATURDAY_NIGHT_SLAUGHTER: "Saturday Night Slaughter",
}

const LEVEL_ORDER: Array[String] = [
	"tutorial", "level_01", "level_02",
]

const LEVEL_SCENES: Dictionary = {
	"tutorial": "res://scenes/levels/test_level.tscn",
	"level_01": "res://scenes/levels/level_01.tscn",
	"level_02": "res://scenes/levels/level_02.tscn",
}

var current_state: GameState = GameState.MENU
var current_level: String = ""
var play_mode: PlayMode = PlayMode.NORMAL
var unlocked_modes: Array[int] = [PlayMode.NORMAL]  # Array[int] for Variant compat
var player_data: Array[Dictionary] = []  # [{index, device_id, lives, node, active}]
var player_scenes: Array[Node] = []
var player_weapons: Dictionary = {}  # {player_index: Array[WeaponData]}
var run_stats: Dictionary = {"enemies_killed": 0, "bosses_defeated": 0, "loot_collected": 0}

var _player_scene: PackedScene = null


func _ready() -> void:
	for i in MAX_PLAYERS:
		player_data.append({
			"index": i,
			"device_id": -1,
			"lives": DEFAULT_LIVES,
			"node": null,
			"active": false,
		})
	load_game()


func register_player(player_index: int, device_id: int) -> void:
	if player_index < 0 or player_index >= MAX_PLAYERS:
		return
	player_data[player_index]["device_id"] = device_id
	player_data[player_index]["active"] = true
	player_data[player_index]["lives"] = DEFAULT_LIVES
	EventBus.player_joined.emit(player_index, device_id)


func unregister_player(player_index: int) -> void:
	if player_index < 0 or player_index >= MAX_PLAYERS:
		return
	player_data[player_index]["active"] = false
	player_data[player_index]["device_id"] = -1
	player_data[player_index]["node"] = null
	EventBus.player_left.emit(player_index)


func get_active_player_count() -> int:
	var count := 0
	for pd in player_data:
		if pd["active"]:
			count += 1
	return count


func get_active_player_indices() -> Array[int]:
	var indices: Array[int] = []
	for pd in player_data:
		if pd["active"]:
			indices.append(pd["index"])
	return indices


func lose_life(player_index: int) -> bool:
	## Returns true if player has lives remaining.
	player_data[player_index]["lives"] -= 1
	if player_data[player_index]["lives"] <= 0:
		player_data[player_index]["lives"] = 0
		return false
	return true


func all_players_dead() -> bool:
	for pd in player_data:
		if pd["active"] and pd["lives"] > 0:
			return false
	return true


func change_state(new_state: GameState) -> void:
	current_state = new_state
	match new_state:
		GameState.PLAYING:
			get_tree().paused = false
		GameState.PAUSED:
			get_tree().paused = true
			EventBus.game_paused.emit()
		GameState.GAME_OVER:
			EventBus.game_over.emit()


func save_player_weapons(player_index: int, weapons: Array[WeaponData]) -> void:
	player_weapons[player_index] = weapons.duplicate()


func get_player_weapons(player_index: int) -> Array[WeaponData]:
	if player_weapons.has(player_index):
		return player_weapons[player_index]
	return [] as Array[WeaponData]


func get_difficulty_scale() -> Dictionary:
	return MODE_SCALING[play_mode]


func unlock_next_mode() -> void:
	## Unlock the next play mode after beating the game.
	match play_mode:
		PlayMode.NORMAL:
			if PlayMode.DISCO_FEVER not in unlocked_modes:
				unlocked_modes.append(PlayMode.DISCO_FEVER)
		PlayMode.DISCO_FEVER:
			if PlayMode.SATURDAY_NIGHT_SLAUGHTER not in unlocked_modes:
				unlocked_modes.append(PlayMode.SATURDAY_NIGHT_SLAUGHTER)
	save_game()


func cycle_play_mode(direction: int) -> void:
	## Cycle through unlocked modes. direction: +1 or -1.
	var idx := unlocked_modes.find(play_mode as int)
	idx = (idx + direction) % unlocked_modes.size()
	if idx < 0:
		idx += unlocked_modes.size()
	play_mode = unlocked_modes[idx] as PlayMode


func get_next_level() -> String:
	## Returns the next level key, or "" if game is complete.
	var idx := LEVEL_ORDER.find(current_level)
	if idx >= 0 and idx < LEVEL_ORDER.size() - 1:
		return LEVEL_ORDER[idx + 1]
	return ""


func save_game() -> void:
	var data := {
		"unlocked_modes": unlocked_modes,
		"play_mode": play_mode as int,
	}
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data))


func load_game() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if not file:
		return
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if parsed is Dictionary:
		var data: Dictionary = parsed
		if data.has("unlocked_modes"):
			unlocked_modes.clear()
			for m in data["unlocked_modes"]:
				unlocked_modes.append(int(m))
		if data.has("play_mode"):
			play_mode = int(data["play_mode"]) as PlayMode


func reset_game() -> void:
	for pd in player_data:
		pd["lives"] = DEFAULT_LIVES
		pd["node"] = null
	player_weapons.clear()
	run_stats = {"enemies_killed": 0, "bosses_defeated": 0, "loot_collected": 0}
	current_level = ""
	current_state = GameState.MENU
