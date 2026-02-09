extends CharacterBody2D
## Player controller with state machine, double jump, coyote time, 8-dir aiming.

enum State { IDLE, RUN, JUMP, FALL, DOUBLE_JUMP, HURT, DEAD }
enum AimDir { RIGHT, UP_RIGHT, UP, UP_LEFT, LEFT, DOWN_LEFT, DOWN, DOWN_RIGHT }

# Movement tuning
const SPEED := 300.0
const ACCELERATION := 2000.0
const FRICTION := 1800.0
const AIR_ACCELERATION := 1200.0
const AIR_FRICTION := 600.0
const JUMP_VELOCITY := -420.0
const DOUBLE_JUMP_VELOCITY := -380.0
const GRAVITY := 980.0
const MAX_FALL_SPEED := 600.0
const COYOTE_TIME := 0.12
const JUMP_BUFFER_TIME := 0.1
const HURT_KNOCKBACK := Vector2(-200, -150)
const HURT_DURATION := 0.3
const INVINCIBILITY_DURATION := 1.0

@export var player_index := 0

var current_state: State = State.IDLE
var aim_direction: AimDir = AimDir.RIGHT
var facing_right := true
var can_double_jump := true
var coyote_timer := 0.0
var jump_buffer_timer := 0.0
var hurt_timer := 0.0
var invincibility_timer := 0.0
var is_invincible := false

# References set in _ready
@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var collision_shape: CollisionShape2D = $CollisionShape2D
@onready var aim_indicator: Node2D = $AimIndicator
@onready var health_component: HealthComponent = $HealthComponent
@onready var shield_component: ShieldComponent = $ShieldComponent
@onready var weapon_holder: WeaponHolder = $WeaponHolder


func _ready() -> void:
	add_to_group("players")
	_enter_state(State.IDLE)

	# Connect health/shield signals
	health_component.health_changed.connect(_on_health_changed)
	health_component.died.connect(_on_died)
	shield_component.shield_changed.connect(_on_shield_changed)

	# Give a starter shield
	var starter_shield := ShieldGenerator.generate(1, Rarity.Tier.COMMON)
	shield_component.equip_shield(starter_shield)

	EventBus.player_spawned.emit(player_index, self)


func _physics_process(delta: float) -> void:
	# Timers
	if coyote_timer > 0:
		coyote_timer -= delta
	if jump_buffer_timer > 0:
		jump_buffer_timer -= delta
	if hurt_timer > 0:
		hurt_timer -= delta
	if invincibility_timer > 0:
		invincibility_timer -= delta
		# Flash effect
		visible = fmod(invincibility_timer, 0.1) > 0.05
	elif is_invincible:
		is_invincible = false
		visible = true

	# Process current state
	match current_state:
		State.IDLE:
			_state_idle(delta)
		State.RUN:
			_state_run(delta)
		State.JUMP:
			_state_jump(delta)
		State.FALL:
			_state_fall(delta)
		State.DOUBLE_JUMP:
			_state_double_jump(delta)
		State.HURT:
			_state_hurt(delta)
		State.DEAD:
			return

	# Aim direction (always updated)
	_update_aim()

	move_and_slide()


# --- State handlers ---

func _state_idle(delta: float) -> void:
	_apply_gravity(delta)
	_apply_friction(delta, FRICTION)

	if not is_on_floor():
		coyote_timer = COYOTE_TIME
		_change_state(State.FALL)
		return

	if _wants_jump():
		_do_jump()
		return

	var dir := _get_move_input()
	if dir != 0.0:
		_change_state(State.RUN)

	_update_sprite_animation("idle")


func _state_run(delta: float) -> void:
	_apply_gravity(delta)
	var dir := _get_move_input()

	if dir != 0.0:
		velocity.x = move_toward(velocity.x, dir * SPEED, ACCELERATION * delta)
		facing_right = dir > 0
	else:
		_apply_friction(delta, FRICTION)
		if absf(velocity.x) < 10.0:
			velocity.x = 0.0
			_change_state(State.IDLE)
			return

	if not is_on_floor():
		coyote_timer = COYOTE_TIME
		_change_state(State.FALL)
		return

	if _wants_jump():
		_do_jump()
		return

	_update_sprite_animation("run")


func _state_jump(delta: float) -> void:
	_apply_gravity(delta)
	_apply_air_movement(delta)

	if velocity.y >= 0:
		_change_state(State.FALL)
		return

	if InputManager.is_action_just_pressed(player_index, "jump") and can_double_jump:
		_do_double_jump()
		return

	_update_sprite_animation("jump")


func _state_fall(delta: float) -> void:
	_apply_gravity(delta)
	_apply_air_movement(delta)

	# Coyote time jump
	if _wants_jump() and coyote_timer > 0:
		_do_jump()
		return

	# Double jump
	if InputManager.is_action_just_pressed(player_index, "jump") and can_double_jump:
		_do_double_jump()
		return

	# Buffer jump
	if InputManager.is_action_just_pressed(player_index, "jump"):
		jump_buffer_timer = JUMP_BUFFER_TIME

	if is_on_floor():
		if jump_buffer_timer > 0:
			_do_jump()
			return
		var dir := _get_move_input()
		if dir != 0.0:
			_change_state(State.RUN)
		else:
			_change_state(State.IDLE)
		return

	_update_sprite_animation("fall")


func _state_double_jump(delta: float) -> void:
	_apply_gravity(delta)
	_apply_air_movement(delta)

	if velocity.y >= 0:
		_change_state(State.FALL)
		return

	_update_sprite_animation("double_jump")


func _state_hurt(delta: float) -> void:
	_apply_gravity(delta)
	velocity.x = move_toward(velocity.x, 0, FRICTION * delta * 0.5)

	if hurt_timer <= 0:
		if is_on_floor():
			_change_state(State.IDLE)
		else:
			_change_state(State.FALL)

	_update_sprite_animation("hurt")


# --- Movement helpers ---

func _apply_gravity(delta: float) -> void:
	if not is_on_floor():
		velocity.y = minf(velocity.y + GRAVITY * delta, MAX_FALL_SPEED)


func _apply_friction(delta: float, amount: float) -> void:
	velocity.x = move_toward(velocity.x, 0, amount * delta)


func _apply_air_movement(delta: float) -> void:
	var dir := _get_move_input()
	if dir != 0.0:
		velocity.x = move_toward(velocity.x, dir * SPEED, AIR_ACCELERATION * delta)
		facing_right = dir > 0
	else:
		_apply_friction(delta, AIR_FRICTION)


func _get_move_input() -> float:
	return InputManager.get_axis(player_index, "move_left", "move_right")


func _wants_jump() -> bool:
	return InputManager.is_action_just_pressed(player_index, "jump")


func _do_jump() -> void:
	velocity.y = JUMP_VELOCITY
	coyote_timer = 0.0
	jump_buffer_timer = 0.0
	can_double_jump = true
	_change_state(State.JUMP)


func _do_double_jump() -> void:
	velocity.y = DOUBLE_JUMP_VELOCITY
	can_double_jump = false
	_change_state(State.DOUBLE_JUMP)


# --- Aim system ---

func _update_aim() -> void:
	var h := InputManager.get_axis(player_index, "move_left", "move_right")
	var v_up := InputManager.is_action_pressed(player_index, "aim_up")
	var v_down := InputManager.is_action_pressed(player_index, "aim_down")

	var aim_h := 0
	var aim_v := 0

	if h > 0.2:
		aim_h = 1
	elif h < -0.2:
		aim_h = -1

	if v_up:
		aim_v = -1
	elif v_down:
		aim_v = 1

	# Determine aim direction
	if aim_h == 0 and aim_v == 0:
		# Default to facing direction
		aim_direction = AimDir.RIGHT if facing_right else AimDir.LEFT
	elif aim_h > 0 and aim_v < 0:
		aim_direction = AimDir.UP_RIGHT
	elif aim_h > 0 and aim_v == 0:
		aim_direction = AimDir.RIGHT
	elif aim_h > 0 and aim_v > 0:
		aim_direction = AimDir.DOWN_RIGHT
	elif aim_h == 0 and aim_v < 0:
		aim_direction = AimDir.UP
	elif aim_h == 0 and aim_v > 0:
		aim_direction = AimDir.DOWN
	elif aim_h < 0 and aim_v < 0:
		aim_direction = AimDir.UP_LEFT
	elif aim_h < 0 and aim_v == 0:
		aim_direction = AimDir.LEFT
	elif aim_h < 0 and aim_v > 0:
		aim_direction = AimDir.DOWN_LEFT

	# Update aim indicator visual
	if aim_indicator:
		aim_indicator.rotation = get_aim_angle()


func get_aim_angle() -> float:
	match aim_direction:
		AimDir.RIGHT: return 0.0
		AimDir.UP_RIGHT: return -PI / 4.0
		AimDir.UP: return -PI / 2.0
		AimDir.UP_LEFT: return -3.0 * PI / 4.0
		AimDir.LEFT: return PI
		AimDir.DOWN_LEFT: return 3.0 * PI / 4.0
		AimDir.DOWN: return PI / 2.0
		AimDir.DOWN_RIGHT: return PI / 4.0
	return 0.0


func get_aim_vector() -> Vector2:
	return Vector2.from_angle(get_aim_angle())


# --- State machine ---

func _change_state(new_state: State) -> void:
	_exit_state(current_state)
	current_state = new_state
	_enter_state(new_state)


func _enter_state(state: State) -> void:
	match state:
		State.IDLE:
			can_double_jump = true
		State.JUMP:
			pass
		State.HURT:
			hurt_timer = HURT_DURATION
			invincibility_timer = INVINCIBILITY_DURATION
			is_invincible = true


func _exit_state(_state: State) -> void:
	pass


func _update_sprite_animation(anim_name: String) -> void:
	if sprite:
		sprite.flip_h = not facing_right
		if sprite.sprite_frames and sprite.sprite_frames.has_animation(anim_name):
			if sprite.animation != anim_name:
				sprite.play(anim_name)


# --- Damage interface ---

func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO, element: WeaponData.Element = WeaponData.Element.NONE) -> void:
	if is_invincible or current_state == State.DEAD:
		return

	# Shield absorbs first, remainder goes to health
	var remaining := shield_component.absorb_damage(amount, element)
	if remaining > 0:
		health_component.take_damage(remaining)

	var knockback := HURT_KNOCKBACK
	if source_position.x > global_position.x:
		knockback.x = -absf(knockback.x)
	else:
		knockback.x = absf(knockback.x)
	velocity = knockback
	_change_state(State.HURT)


func _on_health_changed(current: float, maximum: float) -> void:
	EventBus.player_health_changed.emit(player_index, current, maximum)


func _on_shield_changed(current: float, maximum: float) -> void:
	EventBus.player_shield_changed.emit(player_index, current, maximum)


func _on_died() -> void:
	_change_state(State.DEAD)
	EventBus.player_died.emit(player_index)
