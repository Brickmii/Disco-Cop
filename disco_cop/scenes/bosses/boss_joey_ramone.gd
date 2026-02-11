extends BossBase
## Joey Ramone — CBGB Punk Alley boss. 3 phases, 5 attack patterns.

enum AttackPattern { IDLE, MIC_SWING, FEEDBACK_SHRIEK, CROWD_SURF, WALL_OF_SOUND, BLITZKRIEG_BOP }

const MOVE_SPEED := 110.0
const MIC_SWING_DAMAGE := 22.0
const FEEDBACK_SHRIEK_DAMAGE := 14.0
const CROWD_SURF_DAMAGE := 18.0
const WALL_OF_SOUND_DAMAGE := 16.0
const BLITZKRIEG_BOP_DAMAGE := 12.0
const CROWD_SURF_SPEED := 380.0
const BLITZKRIEG_FIRE_INTERVAL := 0.12
const BLITZKRIEG_BOUNCE_SPEED := 450.0

var _current_attack: AttackPattern = AttackPattern.IDLE
var _attack_timer := 0.0
var _attack_cooldown := 2.5
var _pattern_timer := 0.0
var _is_attacking := false
var _speed_multiplier := 1.0
var _blitz_fire_timer := 0.0
var _blitz_direction := 1.0

var _projectile_scene: PackedScene


func _ready() -> void:
	boss_name = "Joey Ramone"
	max_health = 900.0
	phase_thresholds = [0.66, 0.33]
	super._ready()
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("joey_ramone_projectiles") == 0:
		ObjectPool.preload_pool("joey_ramone_projectiles", _projectile_scene, 50)


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
			# MIC_SWING(40%) + FEEDBACK_SHRIEK(30%) + WALL_OF_SOUND(30%)
			if roll < 0.4:
				_current_attack = AttackPattern.MIC_SWING
			elif roll < 0.7:
				_current_attack = AttackPattern.FEEDBACK_SHRIEK
			else:
				_current_attack = AttackPattern.WALL_OF_SOUND
			_attack_cooldown = 2.5
		2:
			# All 25% each
			if roll < 0.25:
				_current_attack = AttackPattern.MIC_SWING
			elif roll < 0.5:
				_current_attack = AttackPattern.FEEDBACK_SHRIEK
			elif roll < 0.75:
				_current_attack = AttackPattern.CROWD_SURF
			else:
				_current_attack = AttackPattern.WALL_OF_SOUND
			_attack_cooldown = 2.0
		3:
			# BLITZKRIEG_BOP(25%), others ~19% each
			if roll < 0.25:
				_current_attack = AttackPattern.BLITZKRIEG_BOP
			elif roll < 0.44:
				_current_attack = AttackPattern.MIC_SWING
			elif roll < 0.63:
				_current_attack = AttackPattern.FEEDBACK_SHRIEK
			elif roll < 0.82:
				_current_attack = AttackPattern.CROWD_SURF
			else:
				_current_attack = AttackPattern.WALL_OF_SOUND
			_attack_cooldown = 1.5


func _update_attack(delta: float) -> void:
	_pattern_timer += delta
	match _current_attack:
		AttackPattern.MIC_SWING:
			_attack_mic_swing(delta)
		AttackPattern.FEEDBACK_SHRIEK:
			_attack_feedback_shriek(delta)
		AttackPattern.CROWD_SURF:
			_attack_crowd_surf(delta)
		AttackPattern.WALL_OF_SOUND:
			_attack_wall_of_sound(delta)
		AttackPattern.BLITZKRIEG_BOP:
			_attack_blitzkrieg_bop(delta)


func _attack_mic_swing(_delta: float) -> void:
	# Walk toward player, fire 2 melee-range projectiles L/R
	if _pattern_timer < 0.4 and _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * MOVE_SPEED * _speed_multiplier
	elif _pattern_timer >= 0.4 and _pattern_timer < 0.5:
		velocity.x = 0.0
		_fire_projectile(global_position + Vector2(-20, -35), Vector2.LEFT, MIC_SWING_DAMAGE, 220.0)
		_fire_projectile(global_position + Vector2(20, -35), Vector2.RIGHT, MIC_SWING_DAMAGE, 220.0)
	if _pattern_timer > 0.8:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_feedback_shriek(_delta: float) -> void:
	# Stationary, 10 radial burst projectiles
	velocity.x = 0.0
	if _pattern_timer < 0.1:
		for i in 10:
			var angle := (TAU / 10) * i
			_fire_projectile(global_position + Vector2(0, -45), Vector2.from_angle(angle), FEEDBACK_SHRIEK_DAMAGE, 260.0)
	if _pattern_timer > 1.0:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_crowd_surf(_delta: float) -> void:
	# Charge at player, fire projectiles while moving
	if _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * CROWD_SURF_SPEED * _speed_multiplier
	# Fire projectiles at 0.3s and 0.8s during charge
	if (_pattern_timer >= 0.3 and _pattern_timer < 0.4) or (_pattern_timer >= 0.8 and _pattern_timer < 0.9):
		if _target:
			var aim := (_target.global_position - global_position).normalized()
			_fire_projectile(global_position + Vector2(0, -35), aim, CROWD_SURF_DAMAGE, 350.0)
	if _pattern_timer > 1.5:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_wall_of_sound(_delta: float) -> void:
	# 5 horizontal wave projectiles toward player
	velocity.x = 0.0
	if _pattern_timer < 0.1 and _target:
		var base_dir: float = sign(_target.global_position.x - global_position.x)
		for i in 5:
			var y_offset := -60.0 + (i * 15.0)
			var dir := Vector2(base_dir, 0.0).normalized()
			_fire_projectile(global_position + Vector2(base_dir * 20.0, y_offset), dir, WALL_OF_SOUND_DAMAGE, 300.0 + i * 20.0)
	if _pattern_timer > 1.0:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_blitzkrieg_bop(delta: float) -> void:
	# Phase 3 only — bounce between walls, rapid fire
	velocity.x = _blitz_direction * BLITZKRIEG_BOUNCE_SPEED * _speed_multiplier

	# Bounce off walls
	if is_on_wall():
		_blitz_direction *= -1.0

	_blitz_fire_timer -= delta
	if _blitz_fire_timer <= 0 and _target:
		var aim := (_target.global_position - global_position).normalized()
		aim = aim.rotated(randf_range(-0.2, 0.2))
		_fire_projectile(global_position + Vector2(0, -35), aim, BLITZKRIEG_BOP_DAMAGE, 400.0)
		_blitz_fire_timer = BLITZKRIEG_FIRE_INTERVAL

	if _pattern_timer > 3.0:
		_blitz_direction = 1.0 if _target and _target.global_position.x > global_position.x else -1.0
		_end_attack()
	_play_sprite_animation("idle")


func _fire_projectile(pos: Vector2, dir: Vector2, dmg: float, spd: float = 400.0, elem: WeaponData.Element = WeaponData.Element.NONE) -> void:
	var proj: Node2D = ObjectPool.get_instance("joey_ramone_projectiles") as Node2D
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
	tween.tween_property(flash_target, "modulate", Color(2.0, 0.5, 1.5), 0.2)
	tween.tween_property(flash_target, "modulate", Color.WHITE, 0.3)

	match phase:
		2:
			_speed_multiplier = 1.3
		3:
			_speed_multiplier = 1.5
			# Set initial blitz direction toward player
			if _target:
				_blitz_direction = sign(_target.global_position.x - global_position.x)
