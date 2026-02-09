extends Node
class_name ScreenShake
## Applies screen shake to the parent Camera2D.

var _shake_intensity := 0.0
var _shake_duration := 0.0
var _camera: Camera2D = null


func _ready() -> void:
	_camera = get_parent() as Camera2D
	EventBus.camera_shake_requested.connect(shake)


func _process(delta: float) -> void:
	if _shake_duration <= 0 or _camera == null:
		return

	_shake_duration -= delta
	var offset := Vector2(
		randf_range(-_shake_intensity, _shake_intensity),
		randf_range(-_shake_intensity, _shake_intensity)
	)
	_camera.offset = offset

	# Decay
	_shake_intensity = lerpf(_shake_intensity, 0.0, 5.0 * delta)

	if _shake_duration <= 0:
		_camera.offset = Vector2.ZERO


func shake(intensity: float, duration: float) -> void:
	if intensity > _shake_intensity:
		_shake_intensity = intensity
	_shake_duration = maxf(_shake_duration, duration)
