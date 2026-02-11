extends BossBase
## Johnny Rotten — Sex Pistols Concert boss. 3 phases, 5 attack patterns.

enum AttackPattern { IDLE, SWEEP, FEEDBACK, PYRO, CHORD, SOLO }

const MOVE_SPEED := 100.0
const SWEEP_DAMAGE := 25.0
const FEEDBACK_DAMAGE := 15.0
const PYRO_DAMAGE := 20.0
const CHORD_DAMAGE := 18.0
const SOLO_DAMAGE := 12.0
const SOLO_FIRE_INTERVAL := 0.15

var _current_attack: AttackPattern = AttackPattern.IDLE
var _attack_timer := 0.0
var _attack_cooldown := 2.5
var _pattern_timer := 0.0
var _is_attacking := false
var _solo_fire_timer := 0.0
var _solo_sine_time := 0.0
var _speed_multiplier := 1.0

var _projectile_scene: PackedScene


func _ready() -> void:
	boss_name = "Johnny Rotten"
	max_health = 500.0
	phase_thresholds = [0.66, 0.33]
	super._ready()
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("johnny_rotten_projectiles") == 0:
		ObjectPool.preload_pool("johnny_rotten_projectiles", _projectile_scene, 50)


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
	velocity.x = 0.0

	var roll := randf()
	match current_phase:
		1:
			# SWEEP(40%) + FEEDBACK(30%) + CHORD(30%)
			if roll < 0.4:
				_current_attack = AttackPattern.SWEEP
			elif roll < 0.7:
				_current_attack = AttackPattern.FEEDBACK
			else:
				_current_attack = AttackPattern.CHORD
			_attack_cooldown = 2.5
		2:
			# All 25% each
			if roll < 0.25:
				_current_attack = AttackPattern.SWEEP
			elif roll < 0.5:
				_current_attack = AttackPattern.FEEDBACK
			elif roll < 0.75:
				_current_attack = AttackPattern.PYRO
			else:
				_current_attack = AttackPattern.CHORD
			_attack_cooldown = 2.0
		3:
			# SOLO(25%), others ~18-19% each
			if roll < 0.25:
				_current_attack = AttackPattern.SOLO
			elif roll < 0.44:
				_current_attack = AttackPattern.SWEEP
			elif roll < 0.63:
				_current_attack = AttackPattern.FEEDBACK
			elif roll < 0.82:
				_current_attack = AttackPattern.PYRO
			else:
				_current_attack = AttackPattern.CHORD
			_attack_cooldown = 1.5


func _update_attack(delta: float) -> void:
	_pattern_timer += delta
	match _current_attack:
		AttackPattern.SWEEP:
			_attack_sweep(delta)
		AttackPattern.FEEDBACK:
			_attack_feedback(delta)
		AttackPattern.PYRO:
			_attack_pyro(delta)
		AttackPattern.CHORD:
			_attack_chord(delta)
		AttackPattern.SOLO:
			_attack_solo(delta)


func _attack_sweep(_delta: float) -> void:
	# Walk toward player, fire 2 short-range projectiles L/R
	if _pattern_timer < 0.4 and _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * MOVE_SPEED * _speed_multiplier
	elif _pattern_timer >= 0.4 and _pattern_timer < 0.5:
		velocity.x = 0.0
		_fire_projectile(global_position + Vector2(-20, -30), Vector2.LEFT, SWEEP_DAMAGE, 250.0)
		_fire_projectile(global_position + Vector2(20, -30), Vector2.RIGHT, SWEEP_DAMAGE, 250.0)
	if _pattern_timer > 0.8:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_feedback(_delta: float) -> void:
	# Stationary, 8 projectiles in radial burst
	velocity.x = 0.0
	if _pattern_timer < 0.1:
		for i in 8:
			var angle := (TAU / 8) * i
			_fire_projectile(global_position + Vector2(0, -40), Vector2.from_angle(angle), FEEDBACK_DAMAGE, 280.0)
	if _pattern_timer > 1.0:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_pyro(_delta: float) -> void:
	# 6 fire projectiles burst from random ground position
	velocity.x = 0.0
	if _pattern_timer < 0.1:
		var base_x := global_position.x + randf_range(-150.0, 150.0)
		var ground_y := global_position.y  # Spawn at boss feet level
		for i in 6:
			var spread_x := randf_range(-60.0, 60.0)
			var dir := Vector2(randf_range(-0.3, 0.3), -1.0).normalized()
			_fire_projectile(Vector2(base_x + spread_x, ground_y), dir, PYRO_DAMAGE, 320.0, WeaponData.Element.FIRE)
	if _pattern_timer > 1.5:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_chord(_delta: float) -> void:
	# 3-shot aimed burst at player with slight spread
	velocity.x = 0.0
	if _pattern_timer < 0.1 and _target:
		var base_dir := (_target.global_position - global_position).normalized()
		_fire_projectile(global_position + Vector2(0, -30), base_dir, CHORD_DAMAGE, 400.0)
		_fire_projectile(global_position + Vector2(0, -30), base_dir.rotated(0.12), CHORD_DAMAGE, 380.0)
		_fire_projectile(global_position + Vector2(0, -30), base_dir.rotated(-0.12), CHORD_DAMAGE, 380.0)
	if _pattern_timer > 0.8:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_solo(delta: float) -> void:
	# Phase 3 only — sine wave movement, rapid fire
	_solo_sine_time += delta * 4.0
	velocity.x = sin(_solo_sine_time) * MOVE_SPEED * 2.0 * _speed_multiplier

	_solo_fire_timer -= delta
	if _solo_fire_timer <= 0 and _target:
		var dir := (_target.global_position - global_position).normalized()
		dir = dir.rotated(randf_range(-0.15, 0.15))
		_fire_projectile(global_position + Vector2(0, -30), dir, SOLO_DAMAGE, 450.0)
		_solo_fire_timer = SOLO_FIRE_INTERVAL

	if _pattern_timer > 3.0:
		_solo_sine_time = 0.0
		_end_attack()
	_play_sprite_animation("idle")


func _fire_projectile(pos: Vector2, dir: Vector2, dmg: float, spd: float = 400.0, elem: WeaponData.Element = WeaponData.Element.NONE) -> void:
	var proj: Node2D = ObjectPool.get_instance("johnny_rotten_projectiles") as Node2D
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
	tween.tween_property(flash_target, "modulate", Color(1.5, 0.5, 2.0), 0.2)
	tween.tween_property(flash_target, "modulate", Color.WHITE, 0.3)

	match phase:
		2:
			_speed_multiplier = 1.3
		3:
			_speed_multiplier = 1.5
