extends Node
## Manages game state, player registry, lives, and scene transitions.

enum GameState { MENU, LOBBY, PLAYING, PAUSED, GAME_OVER, VICTORY }

const MAX_PLAYERS := 4
const DEFAULT_LIVES := 3

const LEVEL_ORDER: Array[String] = [
	"tutorial", "level_01", "level_02", "level_03", "level_04", "level_05",
]

const LEVEL_SCENES: Dictionary = {
	"tutorial": "res://scenes/levels/test_level.tscn",
	"level_01": "res://scenes/levels/level_01.tscn",
	"level_02": "res://scenes/levels/level_02.tscn",
	"level_03": "res://scenes/levels/level_03.tscn",
	"level_04": "res://scenes/levels/level_04.tscn",
	"level_05": "res://scenes/levels/level_05.tscn",
}

var current_state: GameState = GameState.MENU
var current_level: String = ""
var player_data: Array[Dictionary] = []  # [{index, device_id, lives, node, active}]
var player_scenes: Array[Node] = []
var player_weapons: Dictionary = {}  # {player_index: Array[WeaponData]}

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


func get_next_level() -> String:
	## Returns the next level key, or "" if game is complete.
	var idx := LEVEL_ORDER.find(current_level)
	if idx >= 0 and idx < LEVEL_ORDER.size() - 1:
		return LEVEL_ORDER[idx + 1]
	return ""


func reset_game() -> void:
	for pd in player_data:
		pd["lives"] = DEFAULT_LIVES
		pd["node"] = null
	player_weapons.clear()
	current_level = ""
	current_state = GameState.MENU
