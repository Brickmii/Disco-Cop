extends BaseEnemy
## Biker — heavy tank. Slow charge, massive damage, long self-stun after attack.

const CHARGE_ACCEL := 300.0
const MAX_CHARGE_SPEED := 120.0

var _charge_speed := 0.0
var _stunned := false
var _stun_timer := 0.0


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Biker"
		enemy_data.enemy_type = EnemyData.EnemyType.BIKER
		enemy_data.max_health = 100.0
		enemy_data.move_speed = 70.0
		enemy_data.damage = 30.0
		enemy_data.attack_range = 55.0
		enemy_data.detection_range = 280.0
		enemy_data.attack_cooldown = 2.5
		enemy_data.loot_chance = 0.35
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
	_charge_speed = minf(_charge_speed + CHARGE_ACCEL * delta, MAX_CHARGE_SPEED)
	velocity.x = dir * _charge_speed
	facing_right = dir > 0
	_update_sprite_facing()

	if _distance_to_target() < enemy_data.attack_range:
		_change_state(State.ATTACK)
	elif _distance_to_target() > enemy_data.detection_range * 1.5:
		_charge_speed = 0.0
		_change_state(State.PATROL)
	_play_sprite_animation("walk")


func _state_attack(_delta: float) -> void:
	if _attack_timer <= 0:
		_perform_attack()
		_attack_timer = enemy_data.attack_cooldown
		_stunned = true
		_stun_timer = 0.8
		_charge_speed = 0.0
		_change_state(State.CHASE)
	_play_sprite_animation("walk")


func _perform_attack() -> void:
	if _target and _target.has_method("take_damage"):
		var scale: Dictionary = GameManager.get_difficulty_scale()
		var dmg: float = enemy_data.damage * scale["damage"]
		_target.take_damage(dmg, global_position)
		# High knockback push
		if _target.has_method("apply_knockback"):
			var kb_dir: float = sign(_target.global_position.x - global_position.x)
			_target.apply_knockback(Vector2(kb_dir * 250.0, -80.0))


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
	if source_position != Vector2.ZERO:
		var knockback_dir: float = sign(global_position.x - source_position.x)
		velocity.x = knockback_dir * 60.0
	_charge_speed = 0.0
