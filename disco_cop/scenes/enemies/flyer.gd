extends BaseEnemy
class_name EnemyFlyer
## Aerial enemy — hovers and swoops at players.

const HOVER_HEIGHT := 100.0
const SWOOP_SPEED := 350.0
const HOVER_SPEED := 60.0

var _swoop_target := Vector2.ZERO
var _is_swooping := false
var _swoop_timer := 0.0
var _hover_offset := 0.0


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Flyer"
		enemy_data.enemy_type = EnemyData.EnemyType.FLYER
		enemy_data.max_health = 15.0
		enemy_data.move_speed = 100.0
		enemy_data.damage = 12.0
		enemy_data.attack_range = 200.0
		enemy_data.detection_range = 350.0
		enemy_data.attack_cooldown = 2.5
		enemy_data.loot_chance = 0.35
	super._ready()
	_hover_offset = randf() * TAU  # Randomize hover phase


func _is_flying() -> bool:
	return true


func _state_patrol(delta: float) -> void:
	# Hover in a sine wave pattern
	_hover_offset += delta * 2.0
	velocity.x = sin(_hover_offset) * HOVER_SPEED
	velocity.y = cos(_hover_offset * 1.5) * HOVER_SPEED * 0.5
	facing_right = velocity.x > 0

	if _target and _distance_to_target() < enemy_data.detection_range:
		_change_state(State.CHASE)


func _state_chase(delta: float) -> void:
	if _target == null:
		_change_state(State.PATROL)
		return

	# Hover above target
	var target_pos := _target.global_position + Vector2(0, -HOVER_HEIGHT)
	var dir := (target_pos - global_position).normalized()
	velocity = dir * enemy_data.move_speed
	facing_right = _target.global_position.x > global_position.x

	if _distance_to_target() < enemy_data.attack_range:
		_change_state(State.ATTACK)
	elif _distance_to_target() > enemy_data.detection_range * 1.5:
		_change_state(State.PATROL)


func _state_attack(delta: float) -> void:
	if _is_swooping:
		# Swoop toward target
		var dir := (_swoop_target - global_position).normalized()
		velocity = dir * SWOOP_SPEED
		_swoop_timer -= delta

		if _swoop_timer <= 0 or global_position.distance_to(_swoop_target) < 20.0:
			_is_swooping = false
			_change_state(State.CHASE)
		return

	velocity = velocity.move_toward(Vector2.ZERO, 200.0 * delta)

	if _attack_timer <= 0:
		_perform_attack()
		_attack_timer = enemy_data.attack_cooldown

	if _target == null or _distance_to_target() > enemy_data.attack_range * 2.0:
		_change_state(State.CHASE)


func _perform_attack() -> void:
	if _target == null:
		return
	# Swoop attack
	_swoop_target = _target.global_position
	_is_swooping = true
	_swoop_timer = 1.0


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
	# Interrupt swoop on hit
	_is_swooping = false
