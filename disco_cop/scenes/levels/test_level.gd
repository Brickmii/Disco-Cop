extends Node2D
## Side-scrolling test level — camera tracks the player horizontally.

@onready var camera: Camera2D = $Camera2D
@onready var player: CharacterBody2D = $Player

var _loot_drop_scene: PackedScene = preload("res://scenes/loot/loot_drop.tscn")
var _game_hud_scene: PackedScene = preload("res://scenes/ui/game_hud.tscn")

const KILL_Y := 900.0


func _ready() -> void:
	# HUD
	add_child(_game_hud_scene.instantiate())

	# Loot signals
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.boss_defeated.connect(_on_boss_defeated)

	EventBus.level_started.emit()


func _physics_process(_delta: float) -> void:
	if player and camera:
		camera.position.x = player.position.x
		# Kill zone — fall death
		if player.position.y > KILL_Y:
			if player.has_method("take_damage"):
				player.take_damage(9999.0, player.global_position)


func _on_enemy_died(enemy_node: Node, pos: Vector2) -> void:
	if enemy_node is BaseEnemy and enemy_node.enemy_data:
		var drop := LootTable.roll_drop(enemy_node.enemy_data.loot_chance)
		if not drop.is_empty():
			_spawn_loot(drop, pos)


func _on_boss_defeated(boss_node: Node) -> void:
	var drops := LootTable.roll_boss_drop()
	for drop in drops:
		var offset := Vector2(randf_range(-40, 40), 0)
		_spawn_loot(drop, boss_node.global_position + offset)


func _spawn_loot(drop_data: Dictionary, pos: Vector2) -> void:
	var loot: Node = _loot_drop_scene.instantiate()
	loot.call("setup", drop_data, pos)
	call_deferred("add_child", loot)
