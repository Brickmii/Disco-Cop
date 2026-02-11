extends BossBase
## Barry Gibb — Bee Gees flyer boss. Always airborne, fires heat-seeking missiles.

enum AttackPattern { IDLE, HEAT_SEEKER, MISSILE_RAIN, STROBE_BURST }

const MOVE_SPEED := 100.0
const HOVER_HEIGHT := 120.0
const HEAT_SEEKER_DAMAGE := 22.0
const MISSILE_RAIN_DAMAGE := 18.0
const STROBE_BURST_DAMAGE := 14.0
const HEATSEEKER_LERP := 0.06

var _current_attack: AttackPattern = AttackPattern.IDLE
var _attack_timer := 0.0
var _attack_cooldown := 2.5
var _pattern_timer := 0.0
var _is_attacking := false
var _speed_multiplier := 1.0
var _hover_sine := 0.0
var _active_heatseekers: Array = []
var _rain_fired := false

var _projectile_scene: PackedScene


func _ready() -> void:
	boss_name = "Barry Gibb"
	max_health = 350.0
	phase_thresholds = [0.66, 0.33]
	super._ready()
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("barry_gibb_projectiles") == 0:
		ObjectPool.preload_pool("barry_gibb_projectiles", _projectile_scene, 40)


func _physics_process(delta: float) -> void:
	if is_dead:
		return

	# Override gravity — always airborne
	_target = _find_closest_player()
	_update_boss(delta)
	move_and_slide()


func _update_boss(delta: float) -> void:
	_update_sprite_facing()
	_update_heatseekers()

	if _is_attacking:
		_update_attack(delta)
		return

	_attack_timer -= delta
	if _attack_timer <= 0:
		_start_next_attack()

	# Sine-wave lateral drift while hovering
	_hover_sine += delta * 2.0
	if _target:
		var target_pos := _target.global_position + Vector2(0, -HOVER_HEIGHT)
		var diff := target_pos - global_position
		velocity.x = diff.x * 0.8 * _speed_multiplier + sin(_hover_sine) * 40.0
		velocity.y = diff.y * 1.5
	else:
		velocity.x = sin(_hover_sine) * 60.0
		velocity.y = 0.0

	_play_sprite_animation("idle")


func _update_heatseekers() -> void:
	# Update active heat-seeking projectiles to track nearest player
	var valid: Array = []
	for proj in _active_heatseekers:
		if proj == null or not is_instance_valid(proj):
			continue
		if not proj.has_method("is_active") or not proj.is_active():
			continue
		valid.append(proj)

		var closest: Node2D = _find_closest_player()
		if closest:
			var desired_dir := (closest.global_position - proj.global_position).normalized()
			var current_dir: Vector2 = proj.direction
			var new_dir := current_dir.lerp(desired_dir, HEATSEEKER_LERP).normalized()
			proj.direction = new_dir

	_active_heatseekers = valid


func _start_next_attack() -> void:
	_is_attacking = true
	_pattern_timer = 0.0
	_rain_fired = false

	var roll := randf()
	match current_phase:
		1:
			if roll < 0.6:
				_current_attack = AttackPattern.HEAT_SEEKER
			else:
				_current_attack = AttackPattern.MISSILE_RAIN
			_attack_cooldown = 2.5
		2:
			if roll < 0.6:
				_current_attack = AttackPattern.HEAT_SEEKER
			else:
				_current_attack = AttackPattern.MISSILE_RAIN
			_attack_cooldown = 2.0
		3:
			if roll < 0.4:
				_current_attack = AttackPattern.HEAT_SEEKER
			elif roll < 0.7:
				_current_attack = AttackPattern.MISSILE_RAIN
			else:
				_current_attack = AttackPattern.STROBE_BURST
			_attack_cooldown = 1.5


func _update_attack(delta: float) -> void:
	_pattern_timer += delta
	match _current_attack:
		AttackPattern.HEAT_SEEKER:
			_attack_heat_seeker(delta)
		AttackPattern.MISSILE_RAIN:
			_attack_missile_rain(delta)
		AttackPattern.STROBE_BURST:
			_attack_strobe_burst(delta)


func _attack_heat_seeker(_delta: float) -> void:
	# Fire 1 homing missile
	if _pattern_timer < 0.1 and _target:
		var dir := (_target.global_position - global_position).normalized()
		var proj := _fire_projectile(global_position + Vector2(0, 10), dir, HEAT_SEEKER_DAMAGE, 280.0)
		if proj:
			_active_heatseekers.append(proj)
	if _pattern_timer > 0.5:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_missile_rain(_delta: float) -> void:
	# Fly to top, fire 5 missiles downward in spread
	if _pattern_timer < 0.5:
		velocity.y = -300.0
	elif not _rain_fired:
		velocity.y = 0.0
		_rain_fired = true
		for i in 5:
			var spread: float = (i - 2) * 0.25
			_fire_projectile(global_position + Vector2(0, 10), Vector2(spread, 1.0).normalized(), MISSILE_RAIN_DAMAGE, 320.0)
	if _pattern_timer > 1.5:
		_end_attack()
	_play_sprite_animation("idle")


func _attack_strobe_burst(_delta: float) -> void:
	# P3 only — 10 radial burst while moving
	if _pattern_timer < 0.1:
		for i in 10:
			var angle := (TAU / 10.0) * i
			_fire_projectile(global_position, Vector2.from_angle(angle), STROBE_BURST_DAMAGE, 300.0)
	if _pattern_timer > 1.0:
		_end_attack()
	_play_sprite_animation("idle")


func _fire_projectile(pos: Vector2, dir: Vector2, dmg: float, spd: float = 400.0, elem: WeaponData.Element = WeaponData.Element.NONE) -> Node2D:
	var proj: Node2D = ObjectPool.get_instance("barry_gibb_projectiles") as Node2D
	if proj == null:
		return null

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
	return proj


func _end_attack() -> void:
	_is_attacking = false
	_attack_timer = _attack_cooldown


func _on_phase_change(phase: int) -> void:
	var flash_target: Node = sprite if sprite else self
	var tween := create_tween()
	tween.tween_property(flash_target, "modulate", Color(1.0, 1.5, 2.0), 0.2)
	tween.tween_property(flash_target, "modulate", Color.WHITE, 0.3)

	match phase:
		2:
			_speed_multiplier = 1.3
		3:
			_speed_multiplier = 1.5
