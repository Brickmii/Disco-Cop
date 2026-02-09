extends Node2D
class_name MuzzleFlash
## Brief muzzle flash visual at weapon barrel on fire.

@onready var visual: ColorRect = $Visual
var _timer := 0.0
const FLASH_DURATION := 0.05


func _ready() -> void:
	visible = false


func flash(pos: Vector2, angle: float) -> void:
	global_position = pos
	rotation = angle
	visible = true
	_timer = FLASH_DURATION

	# Random size variation
	var s := randf_range(0.8, 1.3)
	scale = Vector2(s, s)


func _process(delta: float) -> void:
	if _timer > 0:
		_timer -= delta
		if _timer <= 0:
			visible = false
