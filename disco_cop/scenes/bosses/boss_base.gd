extends CharacterBody2D
class_name BossBase
## Base class for bosses. Multi-phase fights with health bars.

signal phase_changed(phase: int)
signal boss_defeated()

@export var boss_name: String = "Boss"
@export var max_health: float = 500.0
@export var phase_thresholds: Array[float] = [0.66, 0.33]  # Health % triggers

var current_health: float
var current_phase := 1
var is_dead := false
var _target: Node2D = null

const GRAVITY := 980.0

@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite")


func _ready() -> void:
	var scale: Dictionary = GameManager.get_difficulty_scale()
	max_health *= scale["hp"]
	current_health = max_health
	collision_layer = 4  # Enemies (bit 3)
	collision_mask = 1   # World
	add_to_group("bosses")
	EventBus.boss_spawned.emit(self)


func _physics_process(delta: float) -> void:
	if is_dead:
		return

	if not is_on_floor():
		velocity.y += GRAVITY * delta

	_target = _find_closest_player()
	_update_boss(delta)
	move_and_slide()


func _update_boss(_delta: float) -> void:
	## Override in subclasses.
	pass


func take_damage(amount: float, _source_position: Vector2 = Vector2.ZERO) -> void:
	if is_dead:
		return

	current_health -= amount
	EventBus.enemy_hit.emit(self, amount, 0)

	# Visual hit feedback
	var flash_target: Node = sprite if sprite else self
	flash_target.modulate = Color(3, 3, 3)
	var tween := create_tween()
	tween.tween_property(flash_target, "modulate", Color.WHITE, 0.1)

	# Check phase transitions
	var health_pct := current_health / max_health
	for i in phase_thresholds.size():
		if health_pct <= phase_thresholds[i] and current_phase <= i + 1:
			current_phase = i + 2
			_on_phase_change(current_phase)
			phase_changed.emit(current_phase)
			EventBus.boss_phase_changed.emit(self, current_phase)
			break

	if current_health <= 0:
		current_health = 0
		_die()


func _die() -> void:
	is_dead = true
	velocity = Vector2.ZERO

	# Play death animation then fade out
	_play_sprite_animation("death")
	var tween := create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 1.0)
	tween.tween_callback(queue_free)

	# Emit defeat signals deferred to avoid cascade during physics
	call_deferred("_emit_defeat_signals")


func _emit_defeat_signals() -> void:
	boss_defeated.emit()
	EventBus.boss_defeated.emit(self)


func _on_phase_change(_phase: int) -> void:
	## Override in subclasses.
	pass


func _find_closest_player() -> Node2D:
	var closest: Node2D = null
	var closest_dist := INF
	for node in get_tree().get_nodes_in_group("players"):
		var dist := global_position.distance_to(node.global_position)
		if dist < closest_dist:
			closest_dist = dist
			closest = node
	return closest


func get_health_percent() -> float:
	return current_health / max_health


func _play_sprite_animation(anim_name: String) -> void:
	if sprite and sprite.sprite_frames and sprite.sprite_frames.has_animation(anim_name):
		if sprite.animation != anim_name:
			sprite.play(anim_name)


func _update_sprite_facing() -> void:
	if sprite:
		sprite.flip_h = not (_target == null or _target.global_position.x >= global_position.x)
