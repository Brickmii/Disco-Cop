extends BaseEnemy
## Floor Bouncer — tanky melee for disco floor.


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Floor Bouncer"
		enemy_data.enemy_type = EnemyData.EnemyType.FLOOR_BOUNCER
		enemy_data.max_health = 65.0
		enemy_data.move_speed = 90.0
		enemy_data.damage = 22.0
		enemy_data.attack_range = 42.0
		enemy_data.detection_range = 270.0
		enemy_data.attack_cooldown = 2.0
		enemy_data.loot_chance = 0.3
	super._ready()


func _state_patrol(delta: float) -> void:
	velocity.x = _patrol_direction * enemy_data.move_speed * 0.4
	facing_right = _patrol_direction > 0
	_update_sprite_facing()

	_patrol_timer -= delta
	if _patrol_timer <= 0:
		_patrol_direction *= -1.0
		_patrol_timer = randf_range(2.0, 4.0)

	if is_on_wall():
		_patrol_direction *= -1.0
		_patrol_timer = randf_range(2.0, 4.0)

	if _target and _distance_to_target() < enemy_data.detection_range:
		_change_state(State.CHASE)
	_play_sprite_animation("walk")


func _state_chase(_delta: float) -> void:
	if _target == null:
		_change_state(State.PATROL)
		return

	var dir: float = sign(_target.global_position.x - global_position.x)
	velocity.x = dir * enemy_data.move_speed
	facing_right = dir > 0
	_update_sprite_facing()

	if _distance_to_target() < enemy_data.attack_range:
		_change_state(State.ATTACK)
	elif _distance_to_target() > enemy_data.detection_range * 1.5:
		_change_state(State.PATROL)
	_play_sprite_animation("walk")


func _perform_attack() -> void:
	if _target and _target.has_method("take_damage"):
		var scale: Dictionary = GameManager.get_difficulty_scale()
		var dmg: float = enemy_data.damage * scale["damage"]
		_target.take_damage(dmg, global_position)


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
	if source_position != Vector2.ZERO:
		var knockback_dir: float = sign(global_position.x - source_position.x)
		velocity.x = knockback_dir * 60.0
