extends CharacterBody2D
class_name BaseEnemy
## Base class for all enemies. Subclasses override behavior methods.

enum State { IDLE, PATROL, CHASE, ATTACK, HURT, DEAD }

@export var enemy_data: EnemyData

var current_state: State = State.IDLE
var health_component: HealthComponent
var facing_right := true
var _attack_timer := 0.0
var _hurt_timer := 0.0
var _target: Node2D = null
var _patrol_direction := 1.0
var _patrol_timer := 0.0
var _target_search_counter := 0

const HURT_DURATION := 0.2
const TARGET_SEARCH_INTERVAL := 6  # Check for closest player every N physics frames
const GRAVITY := 980.0

@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite")


func _ready() -> void:
	# Create health component
	health_component = HealthComponent.new()
	add_child(health_component)
	if enemy_data:
		var scale: Dictionary = GameManager.get_difficulty_scale()
		var scaled_hp: float = enemy_data.max_health * scale["hp"]
		health_component.max_health = scaled_hp
		health_component.current_health = scaled_hp
	health_component.died.connect(_on_died)

	collision_layer = 4  # Enemies layer (bit 3)
	collision_mask = 1   # World layer

	_enter_state(State.PATROL)
	EventBus.enemy_spawned.emit(self)


func _physics_process(delta: float) -> void:
	if current_state == State.DEAD:
		return

	# Gravity (unless flying)
	if not _is_flying() and not is_on_floor():
		velocity.y += GRAVITY * delta

	# Timers
	if _attack_timer > 0:
		_attack_timer -= delta
	if _hurt_timer > 0:
		_hurt_timer -= delta

	# Find closest player (throttled to save CPU)
	_target_search_counter += 1
	if _target_search_counter >= TARGET_SEARCH_INTERVAL or _target == null:
		_target_search_counter = 0
		_target = _find_closest_player()

	match current_state:
		State.IDLE:
			_state_idle(delta)
		State.PATROL:
			_state_patrol(delta)
		State.CHASE:
			_state_chase(delta)
		State.ATTACK:
			_state_attack(delta)
		State.HURT:
			_state_hurt(delta)

	move_and_slide()


func _state_idle(delta: float) -> void:
	velocity.x = 0.0
	_patrol_timer -= delta
	if _patrol_timer <= 0:
		_change_state(State.PATROL)
	if _target and _distance_to_target() < enemy_data.detection_range:
		_change_state(State.CHASE)
	_play_sprite_animation(_get_idle_animation())


func _state_patrol(delta: float) -> void:
	velocity.x = _patrol_direction * enemy_data.move_speed * 0.5
	facing_right = _patrol_direction > 0
	_update_sprite_facing()

	_patrol_timer -= delta
	if _patrol_timer <= 0:
		_patrol_direction *= -1.0
		_patrol_timer = randf_range(2.0, 4.0)

	# Check for walls
	if is_on_wall():
		_patrol_direction *= -1.0
		_patrol_timer = randf_range(2.0, 4.0)

	if _target and _distance_to_target() < enemy_data.detection_range:
		_change_state(State.CHASE)
	_play_sprite_animation(_get_walk_animation())


func _state_chase(delta: float) -> void:
	if _target == null:
		_change_state(State.PATROL)
		return

	var dir: float = sign(_target.global_position.x - global_position.x)
	velocity.x = dir * enemy_data.move_speed
	facing_right = dir > 0
	_update_sprite_facing()

	if _distance_to_target() < enemy_data.attack_range:
		_change_state(State.ATTACK)
	elif _distance_to_target() > enemy_data.detection_range * 1.5:
		_change_state(State.PATROL)
	_play_sprite_animation(_get_walk_animation())


func _state_attack(delta: float) -> void:
	velocity.x = 0.0

	if _attack_timer <= 0:
		_perform_attack()
		_attack_timer = enemy_data.attack_cooldown

	if _target == null or _distance_to_target() > enemy_data.attack_range * 1.5:
		_change_state(State.CHASE)
	_play_sprite_animation(_get_attack_animation())


func _state_hurt(_delta: float) -> void:
	_play_sprite_animation("hurt")
	if _hurt_timer <= 0:
		if _target and _distance_to_target() < enemy_data.attack_range * 1.5:
			_change_state(State.ATTACK)
		else:
			_change_state(State.CHASE)


# --- Override in subclasses ---

func _perform_attack() -> void:
	## Override: deal damage to target.
	if _target and _target.has_method("take_damage"):
		var scale: Dictionary = GameManager.get_difficulty_scale()
		var dmg: float = enemy_data.damage * scale["damage"]
		_target.take_damage(dmg, global_position)


func _is_flying() -> bool:
	return false


# --- Common helpers ---

func take_damage(amount: float, _source_position: Vector2 = Vector2.ZERO) -> void:
	if current_state == State.DEAD:
		return
	health_component.take_damage(amount)
	_change_state(State.HURT)
	EventBus.enemy_hit.emit(self, amount, 0)

	# Visual feedback: flash white on sprite if available, else whole node
	var flash_target: Node = sprite if sprite else self
	flash_target.modulate = Color.WHITE * 3.0
	var tween := create_tween()
	tween.tween_property(flash_target, "modulate", Color.WHITE, 0.1)


func _on_died() -> void:
	_change_state(State.DEAD)
	velocity = Vector2.ZERO

	EventBus.enemy_died.emit(self, global_position)

	# Play death animation then fade out
	_play_sprite_animation("death")
	var tween := create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.5)
	tween.tween_callback(queue_free)


func _find_closest_player() -> Node2D:
	var closest: Node2D = null
	var closest_dist := INF
	for node in get_tree().get_nodes_in_group("players"):
		var dist := global_position.distance_to(node.global_position)
		if dist < closest_dist:
			closest_dist = dist
			closest = node
	return closest


func _distance_to_target() -> float:
	if _target == null:
		return INF
	return global_position.distance_to(_target.global_position)


func _change_state(new_state: State) -> void:
	_exit_state(current_state)
	current_state = new_state
	_enter_state(new_state)


func _enter_state(state: State) -> void:
	match state:
		State.PATROL:
			_patrol_timer = randf_range(2.0, 4.0)
		State.HURT:
			_hurt_timer = HURT_DURATION


func _exit_state(_state: State) -> void:
	pass


# --- Sprite helpers (overridable for enemy-specific animations) ---

func _play_sprite_animation(anim_name: String) -> void:
	if sprite and sprite.sprite_frames and sprite.sprite_frames.has_animation(anim_name):
		if sprite.animation != anim_name:
			sprite.play(anim_name)


func _update_sprite_facing() -> void:
	if sprite:
		sprite.flip_h = not facing_right


func _get_idle_animation() -> String:
	return "walk"


func _get_walk_animation() -> String:
	return "walk"


func _get_attack_animation() -> String:
	return "attack"
