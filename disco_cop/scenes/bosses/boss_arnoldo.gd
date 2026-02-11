extends BossBase
## Arnoldo — Venice Beach boss. Flex, throw, sweep, rush.

enum AttackPattern { IDLE, FLEX, THROW, SWEEP, RUSH }

const MOVE_SPEED := 100.0
const THROW_DAMAGE := 20.0
const FLEX_DAMAGE := 15.0
const SWEEP_DAMAGE := 35.0
const RUSH_SPEED := 350.0

var _current_attack: AttackPattern = AttackPattern.IDLE
var _attack_timer := 0.0
var _attack_cooldown := 2.5
var _pattern_timer := 0.0
var _is_attacking := false
var _rush_direction := 1.0

var _projectile_scene: PackedScene


func _ready() -> void:
	boss_name = "Arnoldo"
	max_health = 600.0
	phase_thresholds = [0.66, 0.33]
	super._ready()
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("arnoldo_projectiles") == 0:
		ObjectPool.preload_pool("arnoldo_projectiles", _projectile_scene, 30)


func _update_boss(delta: float) -> void:
	_update_sprite_facing()

	if _is_attacking:
		_update_attack(delta)
		return

	_attack_timer -= delta
	if _attack_timer <= 0:
		_start_next_attack()

	if _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * MOVE_SPEED * 0.5
	_play_sprite_animation("idle")


func _start_next_attack() -> void:
	_is_attacking = true
	_pattern_timer = 0.0
	velocity.x = 0.0

	match current_phase:
		1:
			if randf() < 0.5:
				_current_attack = AttackPattern.FLEX
			else:
				_current_attack = AttackPattern.THROW
			_attack_cooldown = 2.5
		2:
			var roll := randf()
			if roll < 0.3:
				_current_attack = AttackPattern.FLEX
			elif roll < 0.6:
				_current_attack = AttackPattern.THROW
			else:
				_current_attack = AttackPattern.SWEEP
			_attack_cooldown = 2.0
		3:
			var roll := randf()
			if roll < 0.2:
				_current_attack = AttackPattern.FLEX
			elif roll < 0.4:
				_current_attack = AttackPattern.THROW
			elif roll < 0.6:
				_current_attack = AttackPattern.SWEEP
			else:
				_current_attack = AttackPattern.RUSH
			_attack_cooldown = 1.5


func _update_attack(delta: float) -> void:
	_pattern_timer += delta
	match _current_attack:
		AttackPattern.FLEX:
			_attack_flex(delta)
		AttackPattern.THROW:
			_attack_throw(delta)
		AttackPattern.SWEEP:
			_attack_sweep(delta)
		AttackPattern.RUSH:
			_attack_rush(delta)


func _attack_flex(_delta: float) -> void:
	_play_sprite_animation("flex")
	if _pattern_timer < 0.1:
		for i in 6:
			var angle := (TAU / 6) * i
			_fire_projectile(global_position + Vector2(0, -40), Vector2.from_angle(angle), FLEX_DAMAGE)
	if _pattern_timer > 0.5:
		_end_attack()


func _attack_throw(_delta: float) -> void:
	_play_sprite_animation("throw")
	if _pattern_timer < 0.1 and _target:
		var dir := (_target.global_position - global_position).normalized()
		_fire_projectile(global_position + Vector2(0, -30), dir, THROW_DAMAGE, 500.0)
		_fire_projectile(global_position + Vector2(0, -30), dir.rotated(0.15), THROW_DAMAGE, 450.0)
		_fire_projectile(global_position + Vector2(0, -30), dir.rotated(-0.15), THROW_DAMAGE, 450.0)
	if _pattern_timer > 0.6:
		_end_attack()


func _attack_sweep(_delta: float) -> void:
	_play_sprite_animation("sweep")
	if _pattern_timer < 0.5:
		velocity.y = -150.0
	elif _pattern_timer < 0.6:
		velocity.y = 600.0
	elif _pattern_timer > 0.6:
		if is_on_floor() or _pattern_timer > 2.0:
			for i in 4:
				_fire_projectile(global_position + Vector2(-20, -5), Vector2.LEFT, SWEEP_DAMAGE * 0.5, 250.0 + i * 60)
				_fire_projectile(global_position + Vector2(20, -5), Vector2.RIGHT, SWEEP_DAMAGE * 0.5, 250.0 + i * 60)
			EventBus.camera_shake_requested.emit(8.0, 0.3)
			_end_attack()


func _attack_rush(_delta: float) -> void:
	var flash_target: Node = sprite if sprite else self
	if _pattern_timer < 0.3:
		velocity.x = 0.0
		flash_target.modulate = Color(1.5, 0.5, 0.5)
	elif _pattern_timer < 1.5:
		if _target and _pattern_timer < 0.4:
			_rush_direction = sign(_target.global_position.x - global_position.x)
		velocity.x = _rush_direction * RUSH_SPEED
	else:
		flash_target.modulate = Color.WHITE
		_end_attack()


func _fire_projectile(pos: Vector2, dir: Vector2, dmg: float, spd: float = 400.0) -> void:
	var proj: Node2D = ObjectPool.get_instance("arnoldo_projectiles") as Node2D
	if proj == null:
		return

	var weapon := WeaponData.new()
	weapon.damage = dmg
	weapon.projectile_speed = spd
	weapon.knockback = 80.0
	weapon.crit_chance = 0.0
	weapon.crit_multiplier = 1.0
	weapon.projectile_size = 1.3
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
	tween.tween_property(flash_target, "modulate", Color(2, 0.5, 2), 0.2)
	tween.tween_property(flash_target, "modulate", Color.WHITE, 0.3)
