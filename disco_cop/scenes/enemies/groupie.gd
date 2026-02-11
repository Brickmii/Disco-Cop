extends BaseEnemy
## Groupie — fast fragile melee rusher. Dies in 1-2 hits, swarms the player.

var _stunned := false
var _stun_timer := 0.0


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Groupie"
		enemy_data.enemy_type = EnemyData.EnemyType.GROUPIE
		enemy_data.max_health = 12.0
		enemy_data.move_speed = 230.0
		enemy_data.damage = 8.0
		enemy_data.attack_range = 35.0
		enemy_data.detection_range = 400.0
		enemy_data.attack_cooldown = 0.8
		enemy_data.loot_chance = 0.15
	super._ready()


func _state_patrol(delta: float) -> void:
	velocity.x = _patrol_direction * enemy_data.move_speed * 0.6
	facing_right = _patrol_direction > 0
	_update_sprite_facing()

	_patrol_timer -= delta
	if _patrol_timer <= 0:
		_patrol_direction *= -1.0
		_patrol_timer = randf_range(1.0, 2.5)

	if is_on_wall():
		_patrol_direction *= -1.0
		_patrol_timer = randf_range(1.0, 2.5)

	if _target and _distance_to_target() < enemy_data.detection_range:
		_change_state(State.CHASE)
	_play_sprite_animation("walk")


func _state_chase(delta: float) -> void:
	if _stunned:
		_stun_timer -= delta
		if _stun_timer <= 0:
			_stunned = false
		else:
			velocity.x *= 0.85
			_play_sprite_animation("walk")
			return

	if _target == null:
		_change_state(State.PATROL)
		return

	# Full speed chase — no 0.5x multiplier
	var dir: float = sign(_target.global_position.x - global_position.x)
	velocity.x = dir * enemy_data.move_speed
	facing_right = dir > 0
	_update_sprite_facing()

	if _distance_to_target() < enemy_data.attack_range:
		_change_state(State.ATTACK)
	elif _distance_to_target() > enemy_data.detection_range * 1.5:
		_change_state(State.PATROL)
	_play_sprite_animation("walk")


func _state_attack(delta: float) -> void:
	if _attack_timer <= 0:
		_perform_attack()
		_attack_timer = enemy_data.attack_cooldown
		_stunned = true
		_stun_timer = 0.2
		_change_state(State.CHASE)
	_play_sprite_animation("walk")


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
	if source_position != Vector2.ZERO:
		var knockback_dir: float = sign(global_position.x - source_position.x)
		velocity.x = knockback_dir * 180.0
