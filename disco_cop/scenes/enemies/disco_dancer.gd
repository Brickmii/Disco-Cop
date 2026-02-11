extends BaseEnemy
## Disco Dancer — fast melee zigzagger. Alternates velocity.x direction every 0.4s.

const ZIGZAG_INTERVAL := 0.4

var _zigzag_timer := 0.0
var _zigzag_sign := 1.0


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Disco Dancer"
		enemy_data.enemy_type = EnemyData.EnemyType.DISCO_DANCER
		enemy_data.max_health = 32.0
		enemy_data.move_speed = 190.0
		enemy_data.damage = 13.0
		enemy_data.attack_range = 38.0
		enemy_data.detection_range = 310.0
		enemy_data.attack_cooldown = 1.0
		enemy_data.loot_chance = 0.25
	super._ready()


func _state_chase(delta: float) -> void:
	if _target == null:
		_change_state(State.PATROL)
		return

	var dir: float = sign(_target.global_position.x - global_position.x)

	# Zigzag during chase
	_zigzag_timer -= delta
	if _zigzag_timer <= 0:
		_zigzag_sign *= -1.0
		_zigzag_timer = ZIGZAG_INTERVAL

	velocity.x = _zigzag_sign * absf(dir) * enemy_data.move_speed
	# Bias toward target even when zigzagging
	velocity.x += dir * enemy_data.move_speed * 0.3

	facing_right = _target.global_position.x > global_position.x
	_update_sprite_facing()

	if _distance_to_target() < enemy_data.attack_range:
		_change_state(State.ATTACK)
	elif _distance_to_target() > enemy_data.detection_range * 1.5:
		_change_state(State.PATROL)
	_play_sprite_animation("walk")


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
	if source_position != Vector2.ZERO:
		var knockback_dir: float = sign(global_position.x - source_position.x)
		velocity.x = knockback_dir * 120.0
