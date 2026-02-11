extends BaseEnemy
## Stage Diver — melee charger. Launches at player at high speed, self-stuns after.

const LAUNCH_SPEED := 400.0
const STUN_DURATION := 0.4

var _is_launching := false
var _launch_timer := 0.0
var _stunned := false
var _stun_timer := 0.0


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Stage Diver"
		enemy_data.enemy_type = EnemyData.EnemyType.STAGE_DIVER
		enemy_data.max_health = 40.0
		enemy_data.move_speed = 160.0
		enemy_data.damage = 18.0
		enemy_data.attack_range = 35.0
		enemy_data.detection_range = 320.0
		enemy_data.attack_cooldown = 1.5
		enemy_data.loot_chance = 0.3
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


func _state_attack(delta: float) -> void:
	if _is_launching:
		_launch_timer -= delta
		if _launch_timer <= 0:
			_is_launching = false
			_stunned = true
			_stun_timer = STUN_DURATION
			velocity.x = 0.0
			_change_state(State.CHASE)
		return

	if _attack_timer <= 0:
		_perform_attack()
		_attack_timer = enemy_data.attack_cooldown
	_play_sprite_animation("walk")


func _perform_attack() -> void:
	if _target == null:
		return
	# Launch toward target
	var dir: float = sign(_target.global_position.x - global_position.x)
	velocity.x = dir * LAUNCH_SPEED
	velocity.y = -120.0
	_is_launching = true
	_launch_timer = 0.3

	if _target.has_method("take_damage"):
		var scale: Dictionary = GameManager.get_difficulty_scale()
		var dmg: float = enemy_data.damage * scale["damage"]
		_target.take_damage(dmg, global_position)


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
	_is_launching = false
	if source_position != Vector2.ZERO:
		var knockback_dir: float = sign(global_position.x - source_position.x)
		velocity.x = knockback_dir * 100.0
