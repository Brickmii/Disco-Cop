extends BaseEnemy
## Speaker Stack — stationary turret. Zero movement, fires 3-shot spread bursts.

const BURST_COUNT := 3
const BURST_SPREAD := 0.2  # radians between shots
const BURST_DELAY := 0.1

var _projectile_scene: PackedScene
var _burst_remaining := 0
var _burst_timer := 0.0
var _burst_dir := Vector2.ZERO


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Speaker Stack"
		enemy_data.enemy_type = EnemyData.EnemyType.SPEAKER_STACK
		enemy_data.max_health = 50.0
		enemy_data.move_speed = 0.0
		enemy_data.damage = 15.0
		enemy_data.attack_range = 400.0
		enemy_data.detection_range = 450.0
		enemy_data.attack_cooldown = 2.5
		enemy_data.loot_chance = 0.3
	super._ready()
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("speaker_projectiles") == 0:
		ObjectPool.preload_pool("speaker_projectiles", _projectile_scene, 20)


func _state_idle(_delta: float) -> void:
	velocity.x = 0.0
	if _target and _distance_to_target() < enemy_data.detection_range:
		_change_state(State.ATTACK)
	_play_sprite_animation("walk")


func _state_patrol(_delta: float) -> void:
	# Stationary — skip patrol, go straight to idle/attack
	velocity.x = 0.0
	if _target and _distance_to_target() < enemy_data.detection_range:
		_change_state(State.ATTACK)
	else:
		_change_state(State.IDLE)
	_play_sprite_animation("walk")


func _state_chase(_delta: float) -> void:
	# Stationary — never chase, just attack or idle
	velocity.x = 0.0
	if _target and _distance_to_target() < enemy_data.attack_range and _attack_timer <= 0:
		_change_state(State.ATTACK)
	elif _target == null or _distance_to_target() > enemy_data.detection_range * 1.5:
		_change_state(State.IDLE)
	_play_sprite_animation("walk")


func _state_attack(delta: float) -> void:
	velocity.x = 0.0

	# Handle burst firing
	if _burst_remaining > 0:
		_burst_timer -= delta
		if _burst_timer <= 0:
			_fire_one_projectile(_burst_dir.rotated((_burst_remaining - 2) * BURST_SPREAD))
			_burst_remaining -= 1
			_burst_timer = BURST_DELAY
		_play_sprite_animation("walk")
		return

	if _attack_timer <= 0:
		_perform_attack()
		_attack_timer = enemy_data.attack_cooldown

	if _target == null or _distance_to_target() > enemy_data.detection_range * 1.5:
		_change_state(State.IDLE)
	elif _burst_remaining <= 0 and _attack_timer > 0:
		# Stay in attack state while cooldown ticks; face target
		if _target:
			facing_right = _target.global_position.x > global_position.x
			_update_sprite_facing()
	_play_sprite_animation("walk")


func _perform_attack() -> void:
	if _target == null:
		return
	_burst_dir = (_target.global_position - global_position).normalized()
	_burst_remaining = BURST_COUNT
	_burst_timer = 0.0  # Fire first shot immediately


func _fire_one_projectile(dir: Vector2) -> void:
	var proj: Node2D = ObjectPool.get_instance("speaker_projectiles") as Node2D
	if proj == null:
		return

	var weapon := WeaponData.new()
	var scale: Dictionary = GameManager.get_difficulty_scale()
	weapon.damage = enemy_data.damage * scale["damage"]
	weapon.projectile_speed = 300.0
	weapon.knockback = 50.0
	weapon.crit_chance = 0.0
	weapon.crit_multiplier = 1.0
	weapon.projectile_size = 1.2
	weapon.element = WeaponData.Element.NONE

	proj.activate(global_position + Vector2(0, -25), dir, weapon, -1, false)
	proj.collision_layer = 5
	proj.collision_mask = 2


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
	# Stationary — no knockback movement
