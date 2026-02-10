extends CanvasLayer
## Screen transition overlay — fade to black between scenes.

var _color_rect: ColorRect
var _is_transitioning := false


func _ready() -> void:
	layer = 100
	process_mode = Node.PROCESS_MODE_ALWAYS
	_color_rect = ColorRect.new()
	_color_rect.color = Color.BLACK
	_color_rect.anchors_preset = Control.PRESET_FULL_RECT
	_color_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_color_rect.modulate.a = 0.0
	_color_rect.visible = false
	add_child(_color_rect)


func change_scene(path: String, duration: float = 0.3) -> void:
	if _is_transitioning:
		return
	_is_transitioning = true
	_color_rect.visible = true
	_color_rect.modulate.a = 0.0

	# Unpause tree so tween runs (in case we're paused)
	var was_paused := get_tree().paused
	get_tree().paused = false

	var tween := create_tween()
	tween.tween_property(_color_rect, "modulate:a", 1.0, duration)
	tween.tween_callback(_do_change.bind(path))
	tween.tween_property(_color_rect, "modulate:a", 0.0, duration)
	tween.tween_callback(_on_transition_done)


func _do_change(path: String) -> void:
	get_tree().change_scene_to_file(path)


func _on_transition_done() -> void:
	_color_rect.visible = false
	_is_transitioning = false
