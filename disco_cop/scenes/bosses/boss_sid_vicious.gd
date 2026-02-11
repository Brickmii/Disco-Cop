extends BossBase
## Sid Vicious — Sex Pistols Concert dual boss. Physical/melee focused, 3 phases.

enum AttackPattern { IDLE, BASS_SWING, CHAIN_WHIP, PUNK_SPIT, STAGE_DIVE, BERSERKER }

const MOVE_SPEED := 120.0
const BASS_SWING_DAMAGE := 25.0
const CHAIN_WHIP_DAMAGE := 18.0
const PUNK_SPIT_DAMAGE := 15.0
const STAGE_DIVE_DAMAGE := 30.0
const BERSERKER_DAMAGE := 20.0
const STAGE_DIVE_SPEED := 400.0
const BERSERKER_FIRE_INTERVAL := 0.2

var _current_attack: AttackPattern = AttackPattern.IDLE
var _attack_timer := 0.0
var _attack_cooldown := 2.0
var _pattern_timer := 0.0
var _is_attacking := false
var _speed_multiplier := 1.0
var _berserker_fire_timer := 0.0
var _berserker_side := false  # Alternates L/R

var _projectile_scene: PackedScene


func _ready() -> void:
	boss_name = "Sid Vicious"
	max_health = 400.0
	phase_thresholds = [0.66, 0.33]
	super._ready()
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("sid_vicious_projectiles") == 0:
		ObjectPool.preload_pool("sid_vicious_projectiles", _projectile_scene, 30)


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
			# BASS_SWING(40%) + CHAIN_WHIP(30%) + PUNK_SPIT(30%)
			if roll < 0.4:
				_current_attack = AttackPattern.BASS_SWING
			elif roll < 0.7:
				_current_attack = AttackPattern.CHAIN_WHIP
			else:
				_current_attack = AttackPattern.PUNK_SPIT
			_attack_cooldown = 2.0
		2:
			# All 25% each
			if roll < 0.25:
				_current_attack = AttackPattern.BASS_SWING
			elif roll < 0.5:
				_current_attack = AttackPattern.CHAIN_WHIP
			elif roll < 0.75:
				_current_attack = AttackPattern.PUNK_SPIT
			else:
				_current_attack = AttackPattern.STAGE_DIVE
			_attack_cooldown = 1.5
		3:
			# BERSERKER(25%), others ~19% each
			if roll < 0.25:
				_current_attack = AttackPattern.BERSERKER
			elif roll < 0.44:
				_current_attack = AttackPattern.BASS_SWING
			elif roll < 0.63:
				_current_attack = AttackPattern.CHAIN_WHIP
			elif roll < 0.82:
				_current_attack = AttackPattern.PUNK_SPIT
			else:
				_current_attack = AttackPattern.STAGE_DIVE
			_attack_cooldown = 1.2


func _update_attack(delta: float) -> void:
	_pattern_timer += delta
	match _current_attack:
		AttackPattern.BASS_SWING:
			_attack_bass_swing(delta)
		AttackPattern.CHAIN_WHIP:
			_attack_chain_whip(delta)
		AttackPattern.PUNK_SPIT:
			_attack_punk_spit(delta)
		AttackPattern.STAGE_DIVE:
			_attack_stage_dive(delta)
		AttackPattern.BERSERKER:
			_attack_berserker(delta)


func _attack_bass_swing(_delta: float) -> void:
	# Walk toward player, fire 2 short-range projectiles L/R
	if _pattern_timer < 0.3 and _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * MOVE_SPEED * _speed_multiplier
	elif _pattern_timer >= 0.3 and _pattern_timer < 0.4:
		velocity.x = 0.0
		_fire_projectile(global_position + Vector2(-15, -30), Vector2.LEFT, BASS_SWING_DAMAGE, 200.0)
		_fire_projectile(global_position + Vector2(15, -30), Vector2.RIGHT, BASS_SWING_DAMAGE, 200.0)
	if _pattern_timer > 0.6:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_chain_whip(_delta: float) -> void:
	# 3 aimed projectiles in tight spread
	velocity.x = 0.0
	if _pattern_timer < 0.1 and _target:
		var base_dir := (_target.global_position - global_position).normalized()
		_fire_projectile(global_position + Vector2(0, -30), base_dir, CHAIN_WHIP_DAMAGE, 350.0)
		_fire_projectile(global_position + Vector2(0, -30), base_dir.rotated(0.08), CHAIN_WHIP_DAMAGE, 340.0)
		_fire_projectile(global_position + Vector2(0, -30), base_dir.rotated(-0.08), CHAIN_WHIP_DAMAGE, 340.0)
	if _pattern_timer > 0.8:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_punk_spit(_delta: float) -> void:
	# Single aimed projectile
	velocity.x = 0.0
	if _pattern_timer < 0.1 and _target:
		var dir := (_target.global_position - global_position).normalized()
		_fire_projectile(global_position + Vector2(0, -35), dir, PUNK_SPIT_DAMAGE, 400.0)
	if _pattern_timer > 0.5:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_stage_dive(_delta: float) -> void:
	# Charge at player, fire projectile mid-dive
	if _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * STAGE_DIVE_SPEED * _speed_multiplier
	if _pattern_timer >= 0.5 and _pattern_timer < 0.6 and _target:
		var aim := (_target.global_position - global_position).normalized()
		_fire_projectile(global_position + Vector2(0, -30), aim, STAGE_DIVE_DAMAGE, 300.0)
	if _pattern_timer > 1.2:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_berserker(delta: float) -> void:
	# Phase 3 only — rapid alternating swings and spits
	if _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * MOVE_SPEED * 1.5 * _speed_multiplier

	_berserker_fire_timer -= delta
	if _berserker_fire_timer <= 0:
		_berserker_side = not _berserker_side
		if _berserker_side:
			_fire_projectile(global_position + Vector2(-15, -30), Vector2.LEFT, BERSERKER_DAMAGE, 250.0)
			_fire_projectile(global_position + Vector2(15, -30), Vector2.RIGHT, BERSERKER_DAMAGE, 250.0)
		elif _target:
			var aim := (_target.global_position - global_position).normalized()
			_fire_projectile(global_position + Vector2(0, -35), aim, BERSERKER_DAMAGE, 380.0)
		_berserker_fire_timer = BERSERKER_FIRE_INTERVAL

	if _pattern_timer > 2.5:
		_end_attack()
	_play_sprite_animation("idle")


func _fire_projectile(pos: Vector2, dir: Vector2, dmg: float, spd: float = 400.0) -> void:
	var proj: Node2D = ObjectPool.get_instance("sid_vicious_projectiles") as Node2D
	if proj == null:
		return

	var weapon := WeaponData.new()
	weapon.damage = dmg
	weapon.projectile_speed = spd
	weapon.knockback = 80.0
	weapon.crit_chance = 0.0
	weapon.crit_multiplier = 1.0
	weapon.projectile_size = 1.0
	weapon.element = WeaponData.Element.NONE

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
	tween.tween_property(flash_target, "modulate", Color(0.5, 2.0, 0.5), 0.2)
	tween.tween_property(flash_target, "modulate", Color.WHITE, 0.3)

	match phase:
		2:
			_speed_multiplier = 1.3
		3:
			_speed_multiplier = 1.5
