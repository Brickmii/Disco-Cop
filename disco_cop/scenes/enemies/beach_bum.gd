extends BaseEnemy
## Beach Bum Shooter — ranged skating enemy on Venice Beach.

const SKATE_ACCEL := 500.0
const MAX_SKATE_SPEED := 200.0
const PREFERRED_DISTANCE := 180.0
const BRAKE_FRICTION := 0.92

var _skate_speed := 0.0
var _projectile_scene: PackedScene


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Beach Bum"
		enemy_data.enemy_type = EnemyData.EnemyType.BEACH_BUM
		enemy_data.max_health = 20.0
		enemy_data.move_speed = 180.0
		enemy_data.damage = 10.0
		enemy_data.attack_range = 250.0
		enemy_data.detection_range = 350.0
		enemy_data.attack_cooldown = 1.5
		enemy_data.loot_chance = 0.25
	super._ready()
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("beachbum_projectiles") == 0:
		ObjectPool.preload_pool("beachbum_projectiles", _projectile_scene, 15)


func _state_patrol(delta: float) -> void:
	velocity.x = _patrol_direction * enemy_data.move_speed * 0.5
	facing_right = _patrol_direction > 0
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
	_play_sprite_animation("skate")


func _state_chase(delta: float) -> void:
	if _target == null:
		_change_state(State.PATROL)
		return

	var dist := _distance_to_target()
	var dir: float = sign(_target.global_position.x - global_position.x)

	if dist > PREFERRED_DISTANCE + 30.0:
		_skate_speed = minf(_skate_speed + SKATE_ACCEL * delta, MAX_SKATE_SPEED)
		velocity.x = dir * _skate_speed
	elif dist < PREFERRED_DISTANCE - 30.0:
		_skate_speed = minf(_skate_speed + SKATE_ACCEL * delta, MAX_SKATE_SPEED)
		velocity.x = -dir * _skate_speed * 0.5
	else:
		_skate_speed *= BRAKE_FRICTION
		velocity.x = dir * _skate_speed

	facing_right = dir > 0
	_update_sprite_facing()

	if dist < enemy_data.attack_range and _attack_timer <= 0:
		_change_state(State.ATTACK)
	_play_sprite_animation("skate")


func _state_attack(delta: float) -> void:
	velocity.x *= BRAKE_FRICTION

	if _attack_timer <= 0:
		_perform_attack()
		_attack_timer = enemy_data.attack_cooldown
		_change_state(State.CHASE)
	_play_sprite_animation("shoot_skate")


func _perform_attack() -> void:
	if _target == null:
		return
	var proj: Node2D = ObjectPool.get_instance("beachbum_projectiles") as Node2D
	if proj == null:
		return

	var dir := (_target.global_position - global_position).normalized()
	var weapon := WeaponData.new()
	var scale: Dictionary = GameManager.get_difficulty_scale()
	weapon.damage = enemy_data.damage * scale["damage"]
	weapon.projectile_speed = 400.0
	weapon.knockback = 30.0
	weapon.crit_chance = 0.0
	weapon.crit_multiplier = 1.0
	weapon.projectile_size = 1.0
	weapon.element = WeaponData.Element.NONE

	proj.activate(global_position + Vector2(facing_right as int * 20 - 10, -20), dir, weapon, -1, false)
	proj.collision_layer = 5
	proj.collision_mask = 2


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
	if source_position != Vector2.ZERO:
		var knockback_dir: float = sign(global_position.x - source_position.x)
		velocity.x = knockback_dir * 120.0
	_skate_speed = 0.0


func _get_idle_animation() -> String:
	return "skate"


func _get_walk_animation() -> String:
	return "skate"


func _get_attack_animation() -> String:
	return "shoot_skate"
