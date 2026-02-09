extends Camera2D
class_name MultiTargetCamera
## Camera that tracks all active players with dynamic zoom and smooth follow.

@export var min_zoom := 0.5
@export var max_zoom := 1.0
@export var zoom_margin := 150.0  # Extra padding around players
@export var smooth_speed := 5.0

var targets: Array[Node2D] = []
var level_bounds := Rect2(0, 0, 5000, 1000)  # Override per level


func _ready() -> void:
	EventBus.player_spawned.connect(_on_player_spawned)
	EventBus.player_died.connect(_on_player_died)


func _process(delta: float) -> void:
	if targets.is_empty():
		return

	# Remove freed targets
	targets = targets.filter(func(t: Node2D) -> bool: return is_instance_valid(t))

	if targets.is_empty():
		return

	# Calculate bounding rect of all targets
	var target_rect := _get_target_rect()

	# Center position
	var target_pos := target_rect.get_center()

	# Clamp to level bounds
	target_pos.x = clampf(target_pos.x, level_bounds.position.x + get_viewport_rect().size.x / 2.0 / zoom.x,
						   level_bounds.end.x - get_viewport_rect().size.x / 2.0 / zoom.x)
	target_pos.y = clampf(target_pos.y, level_bounds.position.y + get_viewport_rect().size.y / 2.0 / zoom.y,
						   level_bounds.end.y - get_viewport_rect().size.y / 2.0 / zoom.y)

	# Smooth follow
	global_position = global_position.lerp(target_pos, smooth_speed * delta)

	# Dynamic zoom based on spread
	if targets.size() > 1:
		var needed_width := target_rect.size.x + zoom_margin * 2.0
		var needed_height := target_rect.size.y + zoom_margin * 2.0
		var viewport_size := get_viewport_rect().size

		var zoom_x := viewport_size.x / needed_width
		var zoom_y := viewport_size.y / needed_height
		var target_zoom := minf(zoom_x, zoom_y)
		target_zoom = clampf(target_zoom, min_zoom, max_zoom)

		var current_zoom_value := zoom.x
		var new_zoom := lerpf(current_zoom_value, target_zoom, smooth_speed * delta * 0.5)
		zoom = Vector2(new_zoom, new_zoom)
	else:
		# Single player: zoom to max
		var new_zoom := lerpf(zoom.x, max_zoom, smooth_speed * delta * 0.5)
		zoom = Vector2(new_zoom, new_zoom)


func _get_target_rect() -> Rect2:
	if targets.is_empty():
		return Rect2()

	var min_pos := targets[0].global_position
	var max_pos := targets[0].global_position

	for target in targets:
		min_pos.x = minf(min_pos.x, target.global_position.x)
		min_pos.y = minf(min_pos.y, target.global_position.y)
		max_pos.x = maxf(max_pos.x, target.global_position.x)
		max_pos.y = maxf(max_pos.y, target.global_position.y)

	return Rect2(min_pos, max_pos - min_pos)


func add_target(target: Node2D) -> void:
	if target not in targets:
		targets.append(target)


func remove_target(target: Node2D) -> void:
	targets.erase(target)


func _on_player_spawned(player_index: int, player_node: Node) -> void:
	if player_node is Node2D:
		add_target(player_node)


func _on_player_died(player_index: int) -> void:
	# Don't remove immediately — let death animation play
	pass
