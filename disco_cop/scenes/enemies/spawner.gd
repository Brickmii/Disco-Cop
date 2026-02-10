extends Node2D
class_name EnemySpawner
## Spawns enemies when triggered. Used in scroll-lock zones and level sections.

signal all_enemies_defeated()

@export var enemy_scenes: Array[PackedScene] = []
@export var spawn_count: int = 3
@export var spawn_delay: float = 0.5
@export var auto_spawn: bool = false
@export var spawn_radius: float = 50.0

var _spawned_enemies: Array[Node] = []
var _enemies_remaining := 0
var _spawn_timer := 0.0
var _spawns_left := 0
var _active := false
var _all_cleared := false


func _ready() -> void:
	EventBus.enemy_died.connect(_on_enemy_died)
	if auto_spawn:
		activate()


func _process(delta: float) -> void:
	if not _active:
		return

	if _spawns_left > 0:
		_spawn_timer -= delta
		if _spawn_timer <= 0:
			_spawn_one()
			_spawns_left -= 1
			_spawn_timer = spawn_delay


func activate() -> void:
	_active = true
	_spawns_left = spawn_count
	_enemies_remaining = spawn_count
	_spawn_timer = 0.0  # Spawn first one immediately
	_all_cleared = false


func _spawn_one() -> void:
	if enemy_scenes.is_empty():
		return

	var scene: PackedScene = enemy_scenes[randi() % enemy_scenes.size()]
	var enemy: Node2D = scene.instantiate() as Node2D

	var offset := Vector2(randf_range(-spawn_radius, spawn_radius), 0)
	var spawn_pos := global_position + offset

	get_parent().add_child(enemy)
	enemy.global_position = spawn_pos
	_spawned_enemies.append(enemy)


func _on_enemy_died(enemy_node: Node, _pos: Vector2) -> void:
	if _all_cleared:
		return
	if enemy_node not in _spawned_enemies:
		return

	_enemies_remaining -= 1
	if _enemies_remaining <= 0 and _spawns_left <= 0:
		_all_cleared = true
		all_enemies_defeated.emit()
