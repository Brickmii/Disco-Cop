extends BaseEnemy
class_name EnemyShooter
## Ranged enemy — keeps distance and fires projectiles.

const PREFERRED_DISTANCE := 200.0
const PROJECTILE_POOL_NAME := "enemy_projectiles"

var _projectile_scene: PackedScene


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Shooter"
		enemy_data.enemy_type = EnemyData.EnemyType.SHOOTER
		enemy_data.max_health = 20.0
		enemy_data.move_speed = 80.0
		enemy_data.damage = 10.0
		enemy_data.attack_range = 300.0
		enemy_data.detection_range = 400.0
		enemy_data.attack_cooldown = 1.5
		enemy_data.loot_chance = 0.30
	super._ready()

	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size(PROJECTILE_POOL_NAME) == 0:
		ObjectPool.preload_pool(PROJECTILE_POOL_NAME, _projectile_scene, 20)


func _state_chase(delta: float) -> void:
	if _target == null:
		_change_state(State.PATROL)
		return

	var dist := _distance_to_target()
	var dir: float = sign(_target.global_position.x - global_position.x)
	facing_right = dir > 0

	# Try to maintain preferred distance
	if dist < PREFERRED_DISTANCE * 0.7:
		velocity.x = -dir * enemy_data.move_speed  # Back away
	elif dist > PREFERRED_DISTANCE * 1.3:
		velocity.x = dir * enemy_data.move_speed  # Approach
	else:
		velocity.x = 0.0

	if dist < enemy_data.attack_range:
		_change_state(State.ATTACK)
	elif dist > enemy_data.detection_range * 1.5:
		_change_state(State.PATROL)


func _perform_attack() -> void:
	if _target == null:
		return

	# Create a weapon data for the enemy projectile
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

	# Override collision to hit players instead of enemies
	proj.collision_layer = 5  # EnemyProjectiles
	proj.collision_mask = 2   # Players
