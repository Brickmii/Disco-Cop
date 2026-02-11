extends BossBase
## Debbie Harry — Blondie Concert at CBGB boss. 3 phases, 5 attack patterns.

enum AttackPattern { IDLE, HEART_OF_GLASS, CALL_ME, ONE_WAY, RAPTURE, ATOMIC }

const MOVE_SPEED := 110.0
const HEART_OF_GLASS_DAMAGE := 20.0
const CALL_ME_DAMAGE := 14.0
const ONE_WAY_DAMAGE := 20.0
const RAPTURE_DAMAGE := 16.0
const ATOMIC_DAMAGE := 14.0

var _current_attack: AttackPattern = AttackPattern.IDLE
var _attack_timer := 0.0
var _attack_cooldown := 2.5
var _pattern_timer := 0.0
var _is_attacking := false
var _speed_multiplier := 1.0
var _one_way_fired_1 := false
var _one_way_fired_2 := false

var _projectile_scene: PackedScene


func _ready() -> void:
	boss_name = "Debbie Harry"
	max_health = 900.0
	phase_thresholds = [0.66, 0.33]
	super._ready()
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("debbie_harry_projectiles") == 0:
		ObjectPool.preload_pool("debbie_harry_projectiles", _projectile_scene, 50)


func _update_boss(delta: float) -> void:
	_update_sprite_facing()

	if _is_attacking:
		_update_attack(delta)
		return

	_attack_timer -= delta
	if _attack_timer <= 0:
		_start_next_attack()

	# Walk toward player between attacks
	if _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * MOVE_SPEED * 0.5 * _speed_multiplier
	_play_sprite_animation("idle")


func _start_next_attack() -> void:
	_is_attacking = true
	_pattern_timer = 0.0
	_one_way_fired_1 = false
	_one_way_fired_2 = false
	velocity.x = 0.0

	var roll := randf()
	match current_phase:
		1:
			# HEART_OF_GLASS(40%) + CALL_ME(30%) + RAPTURE(30%)
			if roll < 0.4:
				_current_attack = AttackPattern.HEART_OF_GLASS
			elif roll < 0.7:
				_current_attack = AttackPattern.CALL_ME
			else:
				_current_attack = AttackPattern.RAPTURE
			_attack_cooldown = 2.5
		2:
			# All 25% each
			if roll < 0.25:
				_current_attack = AttackPattern.HEART_OF_GLASS
			elif roll < 0.5:
				_current_attack = AttackPattern.CALL_ME
			elif roll < 0.75:
				_current_attack = AttackPattern.ONE_WAY
			else:
				_current_attack = AttackPattern.RAPTURE
			_attack_cooldown = 2.0
		3:
			# ATOMIC(25%), others ~19% each
			if roll < 0.25:
				_current_attack = AttackPattern.ATOMIC
			elif roll < 0.44:
				_current_attack = AttackPattern.HEART_OF_GLASS
			elif roll < 0.63:
				_current_attack = AttackPattern.CALL_ME
			elif roll < 0.82:
				_current_attack = AttackPattern.ONE_WAY
			else:
				_current_attack = AttackPattern.RAPTURE
			_attack_cooldown = 1.5


func _update_attack(delta: float) -> void:
	_pattern_timer += delta
	match _current_attack:
		AttackPattern.HEART_OF_GLASS:
			_attack_heart_of_glass(delta)
		AttackPattern.CALL_ME:
			_attack_call_me(delta)
		AttackPattern.ONE_WAY:
			_attack_one_way(delta)
		AttackPattern.RAPTURE:
			_attack_rapture(delta)
		AttackPattern.ATOMIC:
			_attack_atomic(delta)


func _attack_heart_of_glass(_delta: float) -> void:
	# Walk toward player, fire 3 glass-shard projectiles in tight spread
	if _pattern_timer < 0.4 and _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * MOVE_SPEED * _speed_multiplier
	elif _pattern_timer >= 0.4 and _pattern_timer < 0.5 and _target:
		velocity.x = 0.0
		var base_dir := (_target.global_position - global_position).normalized()
		_fire_projectile(global_position + Vector2(0, -30), base_dir, HEART_OF_GLASS_DAMAGE, 240.0)
		_fire_projectile(global_position + Vector2(0, -30), base_dir.rotated(0.1), HEART_OF_GLASS_DAMAGE, 240.0)
		_fire_projectile(global_position + Vector2(0, -30), base_dir.rotated(-0.1), HEART_OF_GLASS_DAMAGE, 240.0)
	if _pattern_timer > 0.8:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_call_me(_delta: float) -> void:
	# Stationary, 12 radial burst projectiles
	velocity.x = 0.0
	if _pattern_timer < 0.1:
		for i in 12:
			var angle := (TAU / 12.0) * i
			_fire_projectile(global_position + Vector2(0, -40), Vector2.from_angle(angle), CALL_ME_DAMAGE, 280.0)
	if _pattern_timer > 1.0:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_one_way(_delta: float) -> void:
	# Charge at player, fire 2 aimed projectiles at 0.4s and 0.9s
	if _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * 320.0 * _speed_multiplier

	if _pattern_timer >= 0.4 and not _one_way_fired_1 and _target:
		var aim_dir := (_target.global_position - global_position).normalized()
		_fire_projectile(global_position + Vector2(0, -30), aim_dir, ONE_WAY_DAMAGE, 360.0)
		_one_way_fired_1 = true

	if _pattern_timer >= 0.9 and not _one_way_fired_2 and _target:
		var aim_dir := (_target.global_position - global_position).normalized()
		_fire_projectile(global_position + Vector2(0, -30), aim_dir, ONE_WAY_DAMAGE, 360.0)
		_one_way_fired_2 = true

	if _pattern_timer > 1.5:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_rapture(_delta: float) -> void:
	# 7 horizontal wave projectiles with slight y-spread
	velocity.x = 0.0
	if _pattern_timer < 0.1:
		var base_dir := Vector2.RIGHT if _target == null or _target.global_position.x > global_position.x else Vector2.LEFT
		for i in 7:
			var y_offset: float = (i - 3) * 0.08
			_fire_projectile(global_position + Vector2(0, -30), Vector2(base_dir.x, y_offset).normalized(), RAPTURE_DAMAGE, 320.0)
	if _pattern_timer > 1.2:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_atomic(_delta: float) -> void:
	# P3 only — teleport to random x, fire 5-burst spread, EXPLOSIVE element
	velocity.x = 0.0
	if _pattern_timer < 0.1:
		# Teleport
		var new_x := randf_range(global_position.x - 200.0, global_position.x + 200.0)
		new_x = clampf(new_x, 100.0, 6900.0)
		global_position.x = new_x
	elif _pattern_timer >= 0.3 and _pattern_timer < 0.4 and _target:
		var base_dir := (_target.global_position - global_position).normalized()
		for i in 5:
			var spread: float = (i - 2) * 0.2
			_fire_projectile(global_position + Vector2(0, -30), base_dir.rotated(spread), ATOMIC_DAMAGE, 450.0, WeaponData.Element.EXPLOSIVE)
	if _pattern_timer > 2.0:
		_end_attack()
	_play_sprite_animation("idle")


func _fire_projectile(pos: Vector2, dir: Vector2, dmg: float, spd: float = 400.0, elem: WeaponData.Element = WeaponData.Element.NONE) -> void:
	var proj: Node2D = ObjectPool.get_instance("debbie_harry_projectiles") as Node2D
	if proj == null:
		return

	var weapon := WeaponData.new()
	weapon.damage = dmg
	weapon.projectile_speed = spd
	weapon.knockback = 60.0
	weapon.crit_chance = 0.0
	weapon.crit_multiplier = 1.0
	weapon.projectile_size = 1.2
	weapon.element = elem

	proj.activate(pos, dir, weapon, -1, false)
	proj.collision_layer = 5
	proj.collision_mask = 2


func _end_attack() -> void:
	_is_attacking = false
	_attack_timer = _attack_cooldown
	velocity.x = 0.0


func _on_phase_change(phase: int) -> void:
	var flash_target: Node = sprite if sprite else self
	var tween := create_tween()
	tween.tween_property(flash_target, "modulate", Color(2.0, 0.8, 1.5), 0.2)
	tween.tween_property(flash_target, "modulate", Color.WHITE, 0.3)

	match phase:
		2:
			_speed_multiplier = 1.3
		3:
			_speed_multiplier = 1.6
