extends Area2D
class_name Projectile
## Pooled projectile that travels in a direction and deals damage on hit.

var direction := Vector2.RIGHT
var speed := 800.0
var damage := 10.0
var element: WeaponData.Element = WeaponData.Element.NONE
var element_damage := 0.0
var element_chance := 0.0
var element_duration := 0.0
var knockback_force := 50.0
var is_crit := false
var crit_multiplier := 2.0
var owner_player_index := -1
var lifetime := 0.0
var max_lifetime := 3.0

@onready var collision_shape: CollisionShape2D = $CollisionShape2D
@onready var visual: ColorRect = $Visual


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)


func activate(pos: Vector2, dir: Vector2, weapon: WeaponData, player_idx: int, crit: bool) -> void:
	global_position = pos
	direction = dir.normalized()
	rotation = direction.angle()
	speed = weapon.projectile_speed
	damage = weapon.damage
	element = weapon.element
	element_damage = weapon.element_damage
	element_chance = weapon.element_chance
	element_duration = weapon.element_duration
	knockback_force = weapon.knockback
	is_crit = crit
	crit_multiplier = weapon.crit_multiplier
	owner_player_index = player_idx
	lifetime = 0.0
	max_lifetime = 3.0

	# Visual color by element
	if visual:
		match element:
			WeaponData.Element.NONE: visual.color = Color.WHITE
			WeaponData.Element.FIRE: visual.color = Color.ORANGE_RED
			WeaponData.Element.ICE: visual.color = Color.LIGHT_BLUE
			WeaponData.Element.ELECTRIC: visual.color = Color.YELLOW
			WeaponData.Element.EXPLOSIVE: visual.color = Color.DARK_RED

	# Scale for weapon projectile_size
	var s := weapon.projectile_size
	scale = Vector2(s, s)

	process_mode = Node.PROCESS_MODE_INHERIT
	visible = true
	monitoring = true
	monitorable = true


func _physics_process(delta: float) -> void:
	position += direction * speed * delta
	lifetime += delta

	if lifetime >= max_lifetime:
		_deactivate()


func get_final_damage() -> float:
	var d := damage
	if is_crit:
		d *= crit_multiplier
	return d


func _on_body_entered(body: Node2D) -> void:
	if body.has_method("take_damage"):
		body.take_damage(get_final_damage(), global_position)
	_emit_hit()
	_deactivate()


func _on_area_entered(area: Area2D) -> void:
	# Hit hurtboxes
	if area.has_method("receive_hit"):
		area.receive_hit(self)
		_deactivate()


func _emit_hit() -> void:
	EventBus.damage_dealt.emit(global_position, get_final_damage(), is_crit, element)


func _deactivate() -> void:
	set_deferred("monitoring", false)
	set_deferred("monitorable", false)
	call_deferred("_do_pool_release")


func _do_pool_release() -> void:
	ObjectPool.release_instance(self)
