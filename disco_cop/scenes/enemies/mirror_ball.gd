extends BaseEnemy
## Mirror Ball — flying ranged. Fires 6 radial burst projectiles.

const HOVER_HEIGHT := 120.0
const HOVER_SPEED := 60.0

var _hover_offset := 0.0
var _projectile_scene: PackedScene


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Mirror Ball"
		enemy_data.enemy_type = EnemyData.EnemyType.MIRROR_BALL
		enemy_data.max_health = 28.0
		enemy_data.move_speed = 110.0
		enemy_data.damage = 12.0
		enemy_data.attack_range = 240.0
		enemy_data.detection_range = 380.0
		enemy_data.attack_cooldown = 2.5
		enemy_data.loot_chance = 0.3
	super._ready()
	_hover_offset = randf() * TAU
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("mirrorball_projectiles") == 0:
		ObjectPool.preload_pool("mirrorball_projectiles", _projectile_scene, 20)


func _is_flying() -> bool:
	return true


func _state_patrol(delta: float) -> void:
	_hover_offset += delta * 2.0
	velocity.x = sin(_hover_offset) * HOVER_SPEED
	velocity.y = cos(_hover_offset * 1.5) * HOVER_SPEED * 0.5
	facing_right = velocity.x > 0
	_update_sprite_facing()
	_play_sprite_animation("walk")

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
	_update_sprite_facing()
	_play_sprite_animation("walk")

	if _distance_to_target() < enemy_data.attack_range and _attack_timer <= 0:
		_change_state(State.ATTACK)
	elif _distance_to_target() > enemy_data.detection_range * 1.5:
		_change_state(State.PATROL)


func _state_attack(delta: float) -> void:
	velocity = velocity.move_toward(Vector2.ZERO, 200.0 * delta)

	if _attack_timer <= 0:
		_perform_attack()
		_attack_timer = enemy_data.attack_cooldown
		_change_state(State.CHASE)
	_play_sprite_animation("walk")


func _perform_attack() -> void:
	# 6 radial burst
	for i in 6:
		var angle := (TAU / 6.0) * i
		var proj: Node2D = ObjectPool.get_instance("mirrorball_projectiles") as Node2D
		if proj == null:
			continue

		var weapon := WeaponData.new()
		var scale: Dictionary = GameManager.get_difficulty_scale()
		weapon.damage = enemy_data.damage * scale["damage"]
		weapon.projectile_speed = 280.0
		weapon.knockback = 30.0
		weapon.crit_chance = 0.0
		weapon.crit_multiplier = 1.0
		weapon.projectile_size = 0.8
		weapon.element = WeaponData.Element.NONE

		proj.activate(global_position, Vector2.from_angle(angle), weapon, -1, false)
		proj.collision_layer = 5
		proj.collision_mask = 2


func _get_idle_animation() -> String:
	return "walk"


func _get_walk_animation() -> String:
	return "walk"


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
