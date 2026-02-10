extends Node2D
class_name LevelBase
## Base class for all levels. Manages scroll-lock zones and player spawning.

@export var level_bounds := Rect2(0, 0, 5000, 1000)
@export var spawn_points: Array[Vector2] = [Vector2(200, 600)]

var _player_scene: PackedScene = preload("res://scenes/player/player.tscn")
var _loot_drop_scene: PackedScene = preload("res://scenes/loot/loot_drop.tscn")
var _game_hud_scene: PackedScene = preload("res://scenes/ui/game_hud.tscn")
var _pause_menu_scene: PackedScene = preload("res://scenes/ui/pause_menu.tscn")
var _game_over_scene: PackedScene = preload("res://scenes/ui/game_over.tscn")
var _camera: MultiTargetCamera = null


func _ready() -> void:
	_camera = $MultiTargetCamera as MultiTargetCamera
	if _camera:
		_camera.level_bounds = level_bounds

	# Add UI layers
	add_child(_game_hud_scene.instantiate())
	add_child(_pause_menu_scene.instantiate())
	add_child(_game_over_scene.instantiate())

	_spawn_players()

	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.boss_defeated.connect(_on_boss_defeated)
	EventBus.level_started.emit()
	GameManager.change_state(GameManager.GameState.PLAYING)


func _spawn_players() -> void:
	var active_indices := GameManager.get_active_player_indices()
	if active_indices.is_empty():
		# Default to single player
		active_indices = [0]
		GameManager.register_player(0, -1)

	for i in active_indices.size():
		var player: Node2D = _player_scene.instantiate() as Node2D
		player.set("player_index", active_indices[i])

		var spawn_pos: Vector2
		if i < spawn_points.size():
			spawn_pos = spawn_points[i]
		else:
			spawn_pos = spawn_points[0] + Vector2(i * 40, 0)

		player.global_position = spawn_pos
		add_child(player)
		GameManager.player_data[active_indices[i]]["node"] = player


func _on_enemy_died(enemy_node: Node, pos: Vector2) -> void:
	# Spawn loot from enemy
	if enemy_node is BaseEnemy and enemy_node.enemy_data:
		var drop := LootTable.roll_drop(enemy_node.enemy_data.loot_chance)
		if not drop.is_empty():
			_spawn_loot_at(pos, drop)


func _spawn_loot_at(pos: Vector2, drop_data: Dictionary = {}) -> void:
	if drop_data.is_empty():
		drop_data = LootTable.roll_drop(0.5)
	if drop_data.is_empty():
		return

	var loot: Node = _loot_drop_scene.instantiate()
	loot.call("setup", drop_data, pos)
	call_deferred("add_child", loot)


func _on_boss_defeated(boss_node: Node) -> void:
	var drops: Array = LootTable.roll_boss_drop()
	for drop in drops:
		var offset := Vector2(randf_range(-40, 40), 0)
		_spawn_loot_at(boss_node.global_position + offset, drop)
