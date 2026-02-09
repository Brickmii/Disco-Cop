extends AnimatedSprite2D
class_name VFX
## One-shot visual effect. Plays animation then returns to pool.

const POOL_NAME := "vfx"


func _ready() -> void:
	animation_finished.connect(_on_animation_finished)


func play_effect(effect_name: String, pos: Vector2, effect_scale: float = 1.0, angle: float = 0.0) -> void:
	global_position = pos
	scale = Vector2(effect_scale, effect_scale)
	rotation = angle
	visible = true
	if sprite_frames and sprite_frames.has_animation(effect_name):
		play(effect_name)
	else:
		_on_animation_finished()


func _on_animation_finished() -> void:
	visible = false
	ObjectPool.release_instance(self)
