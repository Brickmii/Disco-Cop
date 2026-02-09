extends Node
## Manages game state, player registry, lives, and scene transitions.

enum GameState { MENU, LOBBY, PLAYING, PAUSED, GAME_OVER, VICTORY }

const MAX_PLAYERS := 4
const DEFAULT_LIVES := 3

var current_state: GameState = GameState.MENU
var player_data: Array[Dictionary] = []  # [{index, device_id, lives, node, active}]
var player_scenes: Array[Node] = []

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


func reset_game() -> void:
	for pd in player_data:
		pd["lives"] = DEFAULT_LIVES
		pd["node"] = null
	current_state = GameState.MENU
