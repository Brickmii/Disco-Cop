extends BossBase
## Disco King — 3-phase boss with disco ball patterns, lasers, and enrage.

enum AttackPattern { IDLE, DISCO_BALL, GROUND_SLAM, LASER_SWEEP, FLOOR_PATTERN, ENRAGE_RUSH }

const MOVE_SPEED := 120.0
const SLAM_DAMAGE := 30.0
const PROJECTILE_DAMAGE := 15.0
const LASER_DAMAGE := 25.0
const DISCO_BALL_COUNT := 8
const RUSH_SPEED := 400.0

var _current_attack: AttackPattern = AttackPattern.IDLE
var _attack_timer := 0.0
var _attack_cooldown := 2.0
var _pattern_timer := 0.0
var _is_attacking := false
var _slam_pos := Vector2.ZERO
var _laser_angle := 0.0
var _rush_direction := 1.0

var _projectile_scene: PackedScene


func _ready() -> void:
	boss_name = "Disco King"
	max_health = 500.0
	phase_thresholds = [0.66, 0.33]
	super._ready()
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	if ObjectPool.get_pool_size("boss_projectiles") == 0:
		ObjectPool.preload_pool("boss_projectiles", _projectile_scene, 40)


func _update_boss(delta: float) -> void:
	_update_sprite_facing()

	if _is_attacking:
		_update_attack(delta)
		return

	_attack_timer -= delta
	if _attack_timer <= 0:
		_start_next_attack()

	# Move toward player between attacks
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
			# Phase 1: disco ball + ground slam
			if randf() < 0.5:
				_current_attack = AttackPattern.DISCO_BALL
			else:
				_current_attack = AttackPattern.GROUND_SLAM
			_attack_cooldown = 2.5
		2:
			# Phase 2: add laser sweep + floor patterns
			var roll := randf()
			if roll < 0.3:
				_current_attack = AttackPattern.DISCO_BALL
			elif roll < 0.5:
				_current_attack = AttackPattern.GROUND_SLAM
			elif roll < 0.75:
				_current_attack = AttackPattern.LASER_SWEEP
			else:
				_current_attack = AttackPattern.FLOOR_PATTERN
			_attack_cooldown = 2.0
		3:
			# Phase 3: enrage — faster attacks, add rush
			var roll := randf()
			if roll < 0.2:
				_current_attack = AttackPattern.DISCO_BALL
			elif roll < 0.35:
				_current_attack = AttackPattern.GROUND_SLAM
			elif roll < 0.5:
				_current_attack = AttackPattern.LASER_SWEEP
			elif roll < 0.7:
				_current_attack = AttackPattern.FLOOR_PATTERN
			else:
				_current_attack = AttackPattern.ENRAGE_RUSH
			_attack_cooldown = 1.5


func _update_attack(delta: float) -> void:
	_pattern_timer += delta

	match _current_attack:
		AttackPattern.DISCO_BALL:
			_attack_disco_ball(delta)
		AttackPattern.GROUND_SLAM:
			_attack_ground_slam(delta)
		AttackPattern.LASER_SWEEP:
			_attack_laser_sweep(delta)
		AttackPattern.FLOOR_PATTERN:
			_attack_floor_pattern(delta)
		AttackPattern.ENRAGE_RUSH:
			_attack_enrage_rush(delta)


func _attack_disco_ball(_delta: float) -> void:
	_play_sprite_animation("disco_ball")
	# Fire projectiles in a radial pattern at the start
	if _pattern_timer < 0.1:
		for i in DISCO_BALL_COUNT:
			var angle := (TAU / DISCO_BALL_COUNT) * i
			_fire_boss_projectile(global_position + Vector2(0, -40), Vector2.from_angle(angle), PROJECTILE_DAMAGE)
	if _pattern_timer > 0.5:
		_end_attack()


func _attack_ground_slam(_delta: float) -> void:
	_play_sprite_animation("slam")
	if _pattern_timer < 0.5:
		# Telegraph: rise up
		velocity.y = -200.0
	elif _pattern_timer < 0.6:
		# Slam down
		velocity.y = 800.0
	elif is_on_floor() and _pattern_timer > 0.6:
		# Ground wave on landing
		_spawn_ground_wave()
		EventBus.camera_shake_requested.emit(8.0, 0.3)
		_end_attack()


func _attack_laser_sweep(_delta: float) -> void:
	_play_sprite_animation("laser")
	# Sweep a "laser" (fast projectiles) across the arena
	if _pattern_timer < 2.0:
		_laser_angle += _delta * PI * 0.5  # Half-circle over 2 seconds
		if fmod(_pattern_timer, 0.1) < 0.02:
			var dir := Vector2.from_angle(-PI + _laser_angle)
			_fire_boss_projectile(global_position + Vector2(0, -30), dir, LASER_DAMAGE, 600.0)
	else:
		_laser_angle = 0.0
		_end_attack()


func _attack_floor_pattern(_delta: float) -> void:
	# Columns of projectiles from above at regular intervals
	if _pattern_timer < 2.0:
		if fmod(_pattern_timer, 0.4) < 0.02:
			var x_pos := global_position.x + randf_range(-300, 300)
			_fire_boss_projectile(Vector2(x_pos, global_position.y - 300), Vector2.DOWN, PROJECTILE_DAMAGE, 500.0)
	else:
		_end_attack()


func _attack_enrage_rush(_delta: float) -> void:
	var flash_target: Node = sprite if sprite else self
	if _pattern_timer < 0.3:
		# Telegraph
		velocity.x = 0.0
		flash_target.modulate = Color(1.5, 0.5, 0.5)
	elif _pattern_timer < 1.5:
		# Rush toward player
		if _target and _pattern_timer < 0.4:
			_rush_direction = sign(_target.global_position.x - global_position.x)
		velocity.x = _rush_direction * RUSH_SPEED
	else:
		flash_target.modulate = Color.WHITE
		_end_attack()


func _fire_boss_projectile(pos: Vector2, dir: Vector2, dmg: float, spd: float = 400.0) -> void:
	var proj: Projectile = ObjectPool.get_instance("boss_projectiles") as Projectile
	if proj == null:
		return

	var weapon := WeaponData.new()
	weapon.damage = dmg
	weapon.projectile_speed = spd
	weapon.knockback = 60.0
	weapon.crit_chance = 0.0
	weapon.crit_multiplier = 1.0
	weapon.projectile_size = 1.2
	weapon.element = WeaponData.Element.NONE

	proj.activate(pos, dir, weapon, -1, false)
	proj.collision_layer = 5  # EnemyProjectiles
	proj.collision_mask = 2   # Players


func _spawn_ground_wave() -> void:
	# Fire projectiles left and right along the ground
	for i in 5:
		var offset := (i + 1) * 0.1
		_fire_boss_projectile(global_position + Vector2(-20, -5), Vector2.LEFT, SLAM_DAMAGE * 0.6, 300.0 + i * 50)
		_fire_boss_projectile(global_position + Vector2(20, -5), Vector2.RIGHT, SLAM_DAMAGE * 0.6, 300.0 + i * 50)


func _end_attack() -> void:
	_is_attacking = false
	_attack_timer = _attack_cooldown
	velocity.x = 0.0


func _on_phase_change(phase: int) -> void:
	# Visual feedback on phase change
	var flash_target: Node = sprite if sprite else self
	var tween := create_tween()
	tween.tween_property(flash_target, "modulate", Color(2, 0.5, 2), 0.2)
	tween.tween_property(flash_target, "modulate", Color.WHITE, 0.3)
