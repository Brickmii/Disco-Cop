extends BaseEnemy
## Seagull — dive-bombing flyer on Venice Beach.

const HOVER_HEIGHT := 100.0
const SWOOP_SPEED := 350.0
const HOVER_SPEED := 60.0

var _swoop_target := Vector2.ZERO
var _swoop_timer := 0.0
var _hover_offset := 0.0


func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Seagull"
		enemy_data.enemy_type = EnemyData.EnemyType.SEAGULL
		enemy_data.max_health = 15.0
		enemy_data.move_speed = 150.0
		enemy_data.damage = 12.0
		enemy_data.attack_range = 200.0
		enemy_data.detection_range = 400.0
		enemy_data.attack_cooldown = 2.0
		enemy_data.loot_chance = 0.15
	super._ready()


func _is_flying() -> bool:
	return true


func _state_patrol(delta: float) -> void:
	_hover_offset += delta * 2.0
	velocity.x = _patrol_direction * enemy_data.move_speed * 0.4
	velocity.y = sin(_hover_offset) * HOVER_SPEED
	facing_right = _patrol_direction > 0
	_update_sprite_facing()

	_patrol_timer -= delta
	if _patrol_timer <= 0:
		_patrol_direction *= -1.0
		_patrol_timer = randf_range(2.0, 4.0)

	if _target and _distance_to_target() < enemy_data.detection_range:
		_change_state(State.CHASE)
	_play_sprite_animation("fly")


func _state_chase(delta: float) -> void:
	if _target == null:
		_change_state(State.PATROL)
		return

	var target_pos := _target.global_position + Vector2(0, -HOVER_HEIGHT)
	var dir := (target_pos - global_position).normalized()
	velocity = dir * enemy_data.move_speed
	facing_right = _target.global_position.x > global_position.x
	_update_sprite_facing()

	if _distance_to_target() < enemy_data.attack_range and _attack_timer <= 0:
		_change_state(State.ATTACK)
	_play_sprite_animation("fly")


func _state_attack(delta: float) -> void:
	_swoop_timer -= delta

	if _swoop_timer > 0:
		var dir := (_swoop_target - global_position).normalized()
		velocity = dir * SWOOP_SPEED
		_play_sprite_animation("attack")

		if global_position.distance_to(_swoop_target) < 20.0 or _swoop_timer <= 0:
			_perform_attack()
			_swoop_timer = 0.0
			_attack_timer = enemy_data.attack_cooldown
			_change_state(State.CHASE)
	else:
		_play_sprite_animation("fly")
		_change_state(State.CHASE)


func _enter_state(state: State) -> void:
	super._enter_state(state)
	if state == State.ATTACK and _target:
		_swoop_target = _target.global_position
		_swoop_timer = 1.0


func take_damage(amount: float, source_position: Vector2 = Vector2.ZERO) -> void:
	super.take_damage(amount, source_position)
	if current_state == State.ATTACK:
		_swoop_timer = 0.0
		_change_state(State.CHASE)


func _get_idle_animation() -> String:
	return "fly"


func _get_walk_animation() -> String:
	return "fly"


func _get_attack_animation() -> String:
	return "attack"
