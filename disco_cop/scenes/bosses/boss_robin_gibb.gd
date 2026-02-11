extends BossBase
## Robin Gibb — Bee Gees ground boss. Standard ground fighter with spread shots.

enum AttackPattern { IDLE, SPREAD_SHOT, DISCO_STOMP, SPINNING_RECORDS, FALSETTO_WAVE }

const MOVE_SPEED := 105.0
const SPREAD_SHOT_DAMAGE := 18.0
const DISCO_STOMP_DAMAGE := 26.0
const SPINNING_RECORDS_DAMAGE := 16.0
const FALSETTO_WAVE_DAMAGE := 20.0

var _current_attack: AttackPattern = AttackPattern.IDLE
var _attack_timer := 0.0
var _attack_cooldown := 2.0
var _pattern_timer := 0.0
var _is_attacking := false
var _speed_multiplier := 1.0
var _stomp_fired := false

var _projectile_scene: PackedScene


func _ready() -> void:
	boss_name = "Robin Gibb"
	max_health = 350.0
	phase_thresholds = [0.66, 0.33]
	super._ready()
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("robin_gibb_projectiles") == 0:
		ObjectPool.preload_pool("robin_gibb_projectiles", _projectile_scene, 50)


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
	_stomp_fired = false
	velocity.x = 0.0

	var roll := randf()
	match current_phase:
		1:
			# SPREAD_SHOT(60%) + DISCO_STOMP(40%)
			if roll < 0.6:
				_current_attack = AttackPattern.SPREAD_SHOT
			else:
				_current_attack = AttackPattern.DISCO_STOMP
			_attack_cooldown = 2.0
		2:
			# All ~33%
			if roll < 0.33:
				_current_attack = AttackPattern.SPREAD_SHOT
			elif roll < 0.66:
				_current_attack = AttackPattern.DISCO_STOMP
			else:
				_current_attack = AttackPattern.SPINNING_RECORDS
			_attack_cooldown = 1.5
		3:
			# FALSETTO_WAVE(25%), others ~25%
			if roll < 0.25:
				_current_attack = AttackPattern.FALSETTO_WAVE
			elif roll < 0.5:
				_current_attack = AttackPattern.SPREAD_SHOT
			elif roll < 0.75:
				_current_attack = AttackPattern.DISCO_STOMP
			else:
				_current_attack = AttackPattern.SPINNING_RECORDS
			_attack_cooldown = 1.2


func _update_attack(delta: float) -> void:
	_pattern_timer += delta
	match _current_attack:
		AttackPattern.SPREAD_SHOT:
			_attack_spread_shot(delta)
		AttackPattern.DISCO_STOMP:
			_attack_disco_stomp(delta)
		AttackPattern.SPINNING_RECORDS:
			_attack_spinning_records(delta)
		AttackPattern.FALSETTO_WAVE:
			_attack_falsetto_wave(delta)


func _attack_spread_shot(_delta: float) -> void:
	# 5 projectiles in fan (-0.3 to +0.3 rad)
	velocity.x = 0.0
	if _pattern_timer < 0.1 and _target:
		var base_dir := (_target.global_position - global_position).normalized()
		for i in 5:
			var spread: float = -0.3 + (0.6 / 4.0) * i
			_fire_projectile(global_position + Vector2(0, -30), base_dir.rotated(spread), SPREAD_SHOT_DAMAGE, 340.0)
	if _pattern_timer > 0.8:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_disco_stomp(_delta: float) -> void:
	# Walk to player, fire 2 ground-level projectiles L/R
	if _pattern_timer < 0.5 and _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * MOVE_SPEED * _speed_multiplier
	elif not _stomp_fired:
		velocity.x = 0.0
		_stomp_fired = true
		_fire_projectile(global_position + Vector2(-10, -5), Vector2.LEFT, DISCO_STOMP_DAMAGE, 200.0)
		_fire_projectile(global_position + Vector2(10, -5), Vector2.RIGHT, DISCO_STOMP_DAMAGE, 200.0)
	if _pattern_timer > 1.0:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_spinning_records(_delta: float) -> void:
	# P2+ — 3 projectiles at 120 degree intervals
	velocity.x = 0.0
	if _pattern_timer < 0.1:
		for i in 3:
			var angle := (TAU / 3.0) * i
			_fire_projectile(global_position + Vector2(0, -30), Vector2.from_angle(angle), SPINNING_RECORDS_DAMAGE, 280.0)
	if _pattern_timer > 1.2:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_falsetto_wave(_delta: float) -> void:
	# P3 only — 8 horizontal projectiles with y-spread
	velocity.x = 0.0
	if _pattern_timer < 0.1:
		var base_dir := Vector2.RIGHT if _target == null or _target.global_position.x > global_position.x else Vector2.LEFT
		for i in 8:
			var y_offset: float = (i - 3.5) * 0.06
			_fire_projectile(global_position + Vector2(0, -30), Vector2(base_dir.x, y_offset).normalized(), FALSETTO_WAVE_DAMAGE, 360.0)
	if _pattern_timer > 1.0:
		_end_attack()
	_play_sprite_animation("idle")


func _fire_projectile(pos: Vector2, dir: Vector2, dmg: float, spd: float = 400.0, elem: WeaponData.Element = WeaponData.Element.NONE) -> void:
	var proj: Node2D = ObjectPool.get_instance("robin_gibb_projectiles") as Node2D
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
	tween.tween_property(flash_target, "modulate", Color(2.0, 1.5, 0.5), 0.2)
	tween.tween_property(flash_target, "modulate", Color.WHITE, 0.3)

	match phase:
		2:
			_speed_multiplier = 1.3
		3:
			_speed_multiplier = 1.5
