extends BaseEnemy
## Punk Rocker — standard melee fighter. Tougher grunt with self-stun after attack.

var _stunned := false
var _stun_timer := 0.0


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Punk Rocker"
		enemy_data.enemy_type = EnemyData.EnemyType.PUNK_ROCKER
		enemy_data.max_health = 35.0
		enemy_data.move_speed = 120.0
		enemy_data.damage = 15.0
		enemy_data.attack_range = 40.0
		enemy_data.detection_range = 300.0
		enemy_data.attack_cooldown = 1.2
		enemy_data.loot_chance = 0.25
	super._ready()


func _state_chase(delta: float) -> void:
	if _stunned:
		_stun_timer -= delta
		if _stun_timer <= 0:
			_stunned = false
		else:
			velocity.x *= 0.9
			_play_sprite_animation("walk")
			return

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


func _state_attack(_delta: float) -> void:
	if _attack_timer <= 0:
		_perform_attack()
		_attack_timer = enemy_data.attack_cooldown
		_stunned = true
		_stun_timer = 0.3
		_change_state(State.CHASE)
	_play_sprite_animation("walk")


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
	if source_position != Vector2.ZERO:
		var knockback_dir: float = sign(global_position.x - source_position.x)
		velocity.x = knockback_dir * 100.0
