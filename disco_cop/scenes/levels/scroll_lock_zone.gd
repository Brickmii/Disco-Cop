extends Area2D
class_name ScrollLockZone
## Locks camera and blocks player exit until all enemies in the zone are defeated.

signal zone_cleared()

@export var zone_rect := Rect2(0, 0, 640, 400)

var _active := false
var _spawners: Array[EnemySpawner] = []
var _spawners_cleared := 0
var _left_wall: StaticBody2D = null
var _right_wall: StaticBody2D = null


func _ready() -> void:
	collision_layer = 7  # Triggers
	collision_mask = 2   # Players
	body_entered.connect(_on_body_entered)

	# Find child spawners
	for child in get_children():
		if child is EnemySpawner:
			_spawners.append(child)
			child.all_enemies_defeated.connect(_on_spawner_cleared)

	# Create invisible walls (inactive by default)
	_create_walls()


func _on_body_entered(body: Node2D) -> void:
	if _active or not body.is_in_group("players"):
		return
	_activate()


func _activate() -> void:
	_active = true
	_spawners_cleared = 0

	# Enable walls
	if _left_wall:
		_left_wall.collision_layer = 1
	if _right_wall:
		_right_wall.collision_layer = 1

	# Activate all spawners
	for spawner in _spawners:
		spawner.activate()

	EventBus.scroll_lock_entered.emit(self)


func _on_spawner_cleared() -> void:
	_spawners_cleared += 1
	if _spawners_cleared >= _spawners.size():
		_deactivate()


func _deactivate() -> void:
	_active = false

	# Remove walls
	if _left_wall:
		_left_wall.collision_layer = 0
	if _right_wall:
		_right_wall.collision_layer = 0

	zone_cleared.emit()
	EventBus.scroll_lock_cleared.emit(self)


func _create_walls() -> void:
	var wall_shape := RectangleShape2D.new()
	wall_shape.size = Vector2(16, zone_rect.size.y)

	# Left wall
	_left_wall = StaticBody2D.new()
	_left_wall.collision_layer = 0  # Starts inactive
	_left_wall.position = Vector2(zone_rect.position.x, zone_rect.position.y + zone_rect.size.y / 2.0)
	var left_col := CollisionShape2D.new()
	left_col.shape = wall_shape
	_left_wall.add_child(left_col)
	add_child(_left_wall)

	# Right wall
	_right_wall = StaticBody2D.new()
	_right_wall.collision_layer = 0
	_right_wall.position = Vector2(zone_rect.end.x, zone_rect.position.y + zone_rect.size.y / 2.0)
	var right_col := CollisionShape2D.new()
	right_col.shape = wall_shape
	_right_wall.add_child(right_col)
	add_child(_right_wall)
