extends BaseEnemy
## Pogo Punk — fast melee. Bounces vertically while chasing.

const BOUNCE_VELOCITY := -200.0
const BOUNCE_INTERVAL := 0.6

var _bounce_timer := 0.0


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Pogo Punk"
		enemy_data.enemy_type = EnemyData.EnemyType.POGO_PUNK
		enemy_data.max_health = 28.0
		enemy_data.move_speed = 220.0
		enemy_data.damage = 12.0
		enemy_data.attack_range = 40.0
		enemy_data.detection_range = 300.0
		enemy_data.attack_cooldown = 0.8
		enemy_data.loot_chance = 0.25
	super._ready()


func _state_chase(delta: float) -> void:
	if _target == null:
		_change_state(State.PATROL)
		return

	var dir: float = sign(_target.global_position.x - global_position.x)
	velocity.x = dir * enemy_data.move_speed
	facing_right = dir > 0
	_update_sprite_facing()

	# Pogo bounce
	_bounce_timer -= delta
	if _bounce_timer <= 0 and is_on_floor():
		velocity.y = BOUNCE_VELOCITY
		_bounce_timer = BOUNCE_INTERVAL

	if _distance_to_target() < enemy_data.attack_range:
		_change_state(State.ATTACK)
	elif _distance_to_target() > enemy_data.detection_range * 1.5:
		_change_state(State.PATROL)
	_play_sprite_animation("walk")


func _state_patrol(delta: float) -> void:
	velocity.x = _patrol_direction * enemy_data.move_speed * 0.5
	facing_right = _patrol_direction > 0
	_update_sprite_facing()

	_patrol_timer -= delta
	if _patrol_timer <= 0:
		_patrol_direction *= -1.0
		_patrol_timer = randf_range(2.0, 4.0)

	if is_on_wall():
		_patrol_direction *= -1.0
		_patrol_timer = randf_range(2.0, 4.0)

	# Bounce even while patrolling
	_bounce_timer -= delta
	if _bounce_timer <= 0 and is_on_floor():
		velocity.y = BOUNCE_VELOCITY
		_bounce_timer = BOUNCE_INTERVAL

	if _target and _distance_to_target() < enemy_data.detection_range:
		_change_state(State.CHASE)
	_play_sprite_animation("walk")


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
	if source_position != Vector2.ZERO:
		var knockback_dir: float = sign(global_position.x - source_position.x)
		velocity.x = knockback_dir * 130.0
