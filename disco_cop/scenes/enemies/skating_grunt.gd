extends BaseEnemy
class_name SkatingGrunt
## Melee skating enemy — builds momentum, charges, overshoots, bounces off barriers.

const SKATE_ACCEL := 600.0
const MAX_SKATE_SPEED := 250.0
const SKATE_FRICTION := 0.98
const BRAKE_FRICTION := 0.90
const BARRIER_BOUNCE := 0.7
const CHARGE_SPEED_BOOST := 1.5
const STUN_DURATION := 0.1

var _stun_timer := 0.0
var _is_charging := false


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Skating Grunt"
		enemy_data.enemy_type = EnemyData.EnemyType.SKATING_GRUNT
		enemy_data.max_health = 25.0
		enemy_data.move_speed = 250.0
		enemy_data.damage = 12.0
		enemy_data.attack_range = 35.0
		enemy_data.detection_range = 300.0
		enemy_data.attack_cooldown = 1.2
		enemy_data.loot_chance = 0.25
	super._ready()


func _physics_process(delta: float) -> void:
	if current_state == State.DEAD:
		return

	# Gravity
	if not is_on_floor():
		velocity.y += GRAVITY * delta

	# Timers
	if _attack_timer > 0:
		_attack_timer -= delta
	if _hurt_timer > 0:
		_hurt_timer -= delta
	if _stun_timer > 0:
		_stun_timer -= delta
		move_and_slide()
		return

	# Find closest player (throttled)
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

	# Apply skating friction
	velocity.x *= SKATE_FRICTION

	move_and_slide()

	# Barrier bounce check
	_check_barrier_bounce()


# --- Skating overrides ---

func _state_patrol(delta: float) -> void:
	# Skate back and forth with acceleration
	var target_dir := _patrol_direction
	velocity.x += target_dir * SKATE_ACCEL * 0.5 * delta
	velocity.x = clampf(velocity.x, -enemy_data.move_speed * 0.5, enemy_data.move_speed * 0.5)

	if velocity.x > 10.0:
		facing_right = true
	elif velocity.x < -10.0:
		facing_right = false
	_update_sprite_facing()

	_patrol_timer -= delta
	if _patrol_timer <= 0:
		_patrol_direction *= -1.0
		_patrol_timer = randf_range(2.0, 4.0)

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

	# Accelerate toward target instead of instant velocity
	velocity.x += dir * SKATE_ACCEL * delta
	velocity.x = clampf(velocity.x, -MAX_SKATE_SPEED, MAX_SKATE_SPEED)

	if velocity.x > 10.0:
		facing_right = true
	elif velocity.x < -10.0:
		facing_right = false
	_update_sprite_facing()

	if _distance_to_target() < enemy_data.attack_range:
		_change_state(State.ATTACK)
	elif _distance_to_target() > enemy_data.detection_range * 1.5:
		_change_state(State.PATROL)
	_play_sprite_animation(_get_walk_animation())


func _state_attack(delta: float) -> void:
	if not _is_charging:
		# Start charge toward player
		if _attack_timer <= 0 and _target:
			_is_charging = true
			var dir: float = sign(_target.global_position.x - global_position.x)
			velocity.x = dir * MAX_SKATE_SPEED * CHARGE_SPEED_BOOST
			facing_right = dir > 0
			_update_sprite_facing()
	else:
		# Sliding through charge — check for hit
		if _target and _distance_to_target() < enemy_data.attack_range:
			_perform_attack()
			_attack_timer = enemy_data.attack_cooldown
			_is_charging = false
			_change_state(State.CHASE)
			return

		# Charge ends when speed drops low enough (friction slowed us)
		if absf(velocity.x) < 50.0:
			_is_charging = false
			_attack_timer = enemy_data.attack_cooldown
			_change_state(State.CHASE)
			return

	_play_sprite_animation(_get_attack_animation())

	# If target gone or too far, abort
	if _target == null or _distance_to_target() > enemy_data.attack_range * 8.0:
		_is_charging = false
		_change_state(State.CHASE)


func _perform_attack() -> void:
	if _target and _distance_to_target() < enemy_data.attack_range:
		if _target.has_method("take_damage"):
			_target.take_damage(enemy_data.damage, global_position)


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	if current_state == State.DEAD:
		return
	_is_charging = false

	# Skating enemies slide further on knockback
	var knockback_dir: float = sign(global_position.x - source_position.x)
	velocity.x = knockback_dir * 150.0

	super.take_damage(amount, source_position)


func _check_barrier_bounce() -> void:
	for i in get_slide_collision_count():
		var collision := get_slide_collision(i)
		var collider := collision.get_collider()
		if collider is Node and collider.is_in_group("barrier"):
			velocity.x *= -BARRIER_BOUNCE
			_stun_timer = STUN_DURATION
			_is_charging = false
			break


# --- Animation overrides ---

func _get_idle_animation() -> String:
	return "skate"


func _get_walk_animation() -> String:
	return "skate"


func _get_attack_animation() -> String:
	return "charge"
