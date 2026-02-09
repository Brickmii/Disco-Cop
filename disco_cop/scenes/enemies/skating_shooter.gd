extends BaseEnemy
class_name SkatingShooter
## Ranged skating enemy — drive-by shooting while maintaining momentum.

const SKATE_ACCEL := 500.0
const MAX_SKATE_SPEED := 200.0
const SKATE_FRICTION := 0.98
const BRAKE_FRICTION := 0.90
const BARRIER_BOUNCE := 0.7
const PREFERRED_DISTANCE := 180.0
const STUN_DURATION := 0.1
const PROJECTILE_POOL_NAME := "skating_shooter_projectiles"

var _stun_timer := 0.0
var _projectile_scene: PackedScene


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Skating Shooter"
		enemy_data.enemy_type = EnemyData.EnemyType.SKATING_SHOOTER
		enemy_data.max_health = 18.0
		enemy_data.move_speed = 200.0
		enemy_data.damage = 10.0
		enemy_data.attack_range = 280.0
		enemy_data.detection_range = 400.0
		enemy_data.attack_cooldown = 1.8
		enemy_data.loot_chance = 0.30
	super._ready()

	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size(PROJECTILE_POOL_NAME) == 0:
		ObjectPool.preload_pool(PROJECTILE_POOL_NAME, _projectile_scene, 15)


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
	velocity.x += _patrol_direction * SKATE_ACCEL * 0.4 * delta
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

	var dist := _distance_to_target()
	var dir: float = sign(_target.global_position.x - global_position.x)

	# Maintain preferred distance — skate past then brake
	if dist < PREFERRED_DISTANCE * 0.6:
		# Too close — brake and skate away
		velocity.x += -dir * SKATE_ACCEL * delta
	elif dist > PREFERRED_DISTANCE * 1.4:
		# Too far — skate toward
		velocity.x += dir * SKATE_ACCEL * delta
	else:
		# Good range — apply light friction to slow down
		velocity.x *= BRAKE_FRICTION

	velocity.x = clampf(velocity.x, -MAX_SKATE_SPEED, MAX_SKATE_SPEED)

	if velocity.x > 10.0:
		facing_right = true
	elif velocity.x < -10.0:
		facing_right = false
	# Always face the target when in range
	if dist < enemy_data.attack_range:
		facing_right = dir > 0
	_update_sprite_facing()

	if dist < enemy_data.attack_range:
		_change_state(State.ATTACK)
	elif dist > enemy_data.detection_range * 1.5:
		_change_state(State.PATROL)
	_play_sprite_animation(_get_walk_animation())


func _state_attack(delta: float) -> void:
	# Drive-by: keep skating while shooting
	if _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		facing_right = dir > 0
		_update_sprite_facing()

		# Maintain some momentum — don't stop
		var dist := _distance_to_target()
		if dist < PREFERRED_DISTANCE * 0.5:
			velocity.x += -dir * SKATE_ACCEL * 0.6 * delta
		else:
			velocity.x += dir * SKATE_ACCEL * 0.3 * delta
		velocity.x = clampf(velocity.x, -MAX_SKATE_SPEED, MAX_SKATE_SPEED)

	if _attack_timer <= 0:
		_perform_attack()
		_attack_timer = enemy_data.attack_cooldown

	if _target == null or _distance_to_target() > enemy_data.attack_range * 1.5:
		_change_state(State.CHASE)
	_play_sprite_animation(_get_attack_animation())


func _perform_attack() -> void:
	if _target == null:
		return

	var weapon := WeaponData.new()
	weapon.damage = enemy_data.damage
	weapon.projectile_speed = 400.0
	weapon.knockback = 30.0
	weapon.crit_chance = 0.0
	weapon.crit_multiplier = 1.0
	weapon.projectile_size = 0.8

	var proj: Projectile = ObjectPool.get_instance(PROJECTILE_POOL_NAME) as Projectile
	if proj == null:
		return

	var dir := (_target.global_position - global_position).normalized()
	proj.activate(global_position, dir, weapon, -1, false)
	proj.collision_layer = 5  # EnemyProjectiles
	proj.collision_mask = 2   # Players


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	if current_state == State.DEAD:
		return

	# Skating enemies slide further on knockback
	var knockback_dir: float = sign(global_position.x - source_position.x)
	velocity.x = knockback_dir * 120.0

	super.take_damage(amount, source_position)


func _check_barrier_bounce() -> void:
	for i in get_slide_collision_count():
		var collision := get_slide_collision(i)
		var collider := collision.get_collider()
		if collider is Node and collider.is_in_group("barrier"):
			velocity.x *= -BARRIER_BOUNCE
			_stun_timer = STUN_DURATION
			break


# --- Animation overrides ---

func _get_idle_animation() -> String:
	return "skate"


func _get_walk_animation() -> String:
	return "skate"


func _get_attack_animation() -> String:
	return "shoot_skate"
