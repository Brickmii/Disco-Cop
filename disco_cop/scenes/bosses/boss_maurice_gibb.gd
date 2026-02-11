extends BossBase
## Maurice Gibb — Bee Gees invisible pop-up boss. Toggles visibility, teleports when invisible.

enum AttackPattern { IDLE, LASER_SWEEP, LASER_CROSS, LASER_SPIRAL }

const MOVE_SPEED := 90.0
const LASER_SWEEP_DAMAGE := 24.0
const LASER_CROSS_DAMAGE := 20.0
const LASER_SPIRAL_DAMAGE := 18.0

var _current_attack: AttackPattern = AttackPattern.IDLE
var _attack_timer := 0.0
var _attack_cooldown := 1.5
var _pattern_timer := 0.0
var _is_attacking := false

var _is_visible := false
var _visibility_timer := 0.0
var _invisible_duration := 5.0
var _visible_duration := 5.0

var _projectile_scene: PackedScene


func _ready() -> void:
	boss_name = "Maurice Gibb"
	max_health = 300.0
	phase_thresholds = [0.66, 0.33]
	super._ready()
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("maurice_gibb_projectiles") == 0:
		ObjectPool.preload_pool("maurice_gibb_projectiles", _projectile_scene, 40)

	# Start invisible
	_set_invisible()
	_visibility_timer = _invisible_duration


func _update_boss(delta: float) -> void:
	_update_sprite_facing()

	# Visibility toggle
	_visibility_timer -= delta
	if _visibility_timer <= 0:
		if _is_visible:
			_set_invisible()
			_visibility_timer = _invisible_duration
			_is_attacking = false
			# Teleport to random x
			global_position.x = randf_range(200.0, 5200.0)
		else:
			_set_visible()
			_visibility_timer = _visible_duration
			_attack_timer = 0.3  # Brief delay before first attack

	if not _is_visible:
		velocity.x = 0.0
		return

	if _is_attacking:
		_update_attack(delta)
		return

	_attack_timer -= delta
	if _attack_timer <= 0:
		_start_next_attack()

	# Walk toward player between attacks
	if _target:
		var dir: float = sign(_target.global_position.x - global_position.x)
		velocity.x = dir * MOVE_SPEED * 0.5
	_play_sprite_animation("idle")


func _set_invisible() -> void:
	_is_visible = false
	modulate.a = 0.0
	collision_layer = 0  # Projectiles pass through


func _set_visible() -> void:
	_is_visible = true
	modulate.a = 1.0
	collision_layer = 4  # Can be hit


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	if not _is_visible:
		return
	super.take_damage(amount, source_position)


func _start_next_attack() -> void:
	_is_attacking = true
	_pattern_timer = 0.0
	velocity.x = 0.0

	var roll := randf()
	match current_phase:
		1:
			_current_attack = AttackPattern.LASER_SWEEP
			_attack_cooldown = 1.5
		2:
			if roll < 0.5:
				_current_attack = AttackPattern.LASER_SWEEP
			else:
				_current_attack = AttackPattern.LASER_CROSS
			_attack_cooldown = 1.2
		3:
			if roll < 0.35:
				_current_attack = AttackPattern.LASER_SWEEP
			elif roll < 0.7:
				_current_attack = AttackPattern.LASER_CROSS
			else:
				_current_attack = AttackPattern.LASER_SPIRAL
			_attack_cooldown = 1.0


func _update_attack(delta: float) -> void:
	_pattern_timer += delta
	match _current_attack:
		AttackPattern.LASER_SWEEP:
			_attack_laser_sweep(delta)
		AttackPattern.LASER_CROSS:
			_attack_laser_cross(delta)
		AttackPattern.LASER_SPIRAL:
			_attack_laser_spiral(delta)


func _attack_laser_sweep(_delta: float) -> void:
	# 3 fast laser projectiles aimed at player
	velocity.x = 0.0
	if _pattern_timer < 0.1 and _target:
		var base_dir := (_target.global_position - global_position).normalized()
		_fire_projectile(global_position + Vector2(0, -30), base_dir, LASER_SWEEP_DAMAGE, 500.0)
		_fire_projectile(global_position + Vector2(0, -30), base_dir.rotated(0.08), LASER_SWEEP_DAMAGE, 500.0)
		_fire_projectile(global_position + Vector2(0, -30), base_dir.rotated(-0.08), LASER_SWEEP_DAMAGE, 500.0)
	if _pattern_timer > 0.6:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_laser_cross(_delta: float) -> void:
	# P2+ — 4 lasers in + pattern
	velocity.x = 0.0
	if _pattern_timer < 0.1:
		_fire_projectile(global_position + Vector2(0, -30), Vector2.UP, LASER_CROSS_DAMAGE, 450.0)
		_fire_projectile(global_position + Vector2(0, -30), Vector2.DOWN, LASER_CROSS_DAMAGE, 450.0)
		_fire_projectile(global_position + Vector2(0, -30), Vector2.LEFT, LASER_CROSS_DAMAGE, 450.0)
		_fire_projectile(global_position + Vector2(0, -30), Vector2.RIGHT, LASER_CROSS_DAMAGE, 450.0)
	if _pattern_timer > 0.8:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_laser_spiral(_delta: float) -> void:
	# P3 only — 12 lasers in radial burst
	velocity.x = 0.0
	if _pattern_timer < 0.1:
		for i in 12:
			var angle := (TAU / 12.0) * i
			_fire_projectile(global_position + Vector2(0, -30), Vector2.from_angle(angle), LASER_SPIRAL_DAMAGE, 420.0)
	if _pattern_timer > 1.0:
		_end_attack()
	_play_sprite_animation("idle")


func _fire_projectile(pos: Vector2, dir: Vector2, dmg: float, spd: float = 400.0, elem: WeaponData.Element = WeaponData.Element.ELECTRIC) -> void:
	var proj: Node2D = ObjectPool.get_instance("maurice_gibb_projectiles") as Node2D
	if proj == null:
		return

	var weapon := WeaponData.new()
	weapon.damage = dmg
	weapon.projectile_speed = spd
	weapon.knockback = 60.0
	weapon.crit_chance = 0.0
	weapon.crit_multiplier = 1.0
	weapon.projectile_size = 1.0
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
	if _is_visible:
		var tween := create_tween()
		tween.tween_property(flash_target, "modulate", Color(0.5, 2.0, 0.5), 0.2)
		tween.tween_property(flash_target, "modulate", Color.WHITE, 0.3)

	match phase:
		2:
			_invisible_duration = 4.0
		3:
			_invisible_duration = 3.0
