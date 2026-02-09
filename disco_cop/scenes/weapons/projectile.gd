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
@onready var sprite: Sprite2D = $Sprite

# Preloaded projectile textures — null until PNGs exist in assets/sprites/weapons/
static var _tex_bullet: Texture2D = _load_tex("res://assets/sprites/weapons/projectile_bullet.png")
static var _tex_fire: Texture2D = _load_tex("res://assets/sprites/weapons/projectile_fire.png")
static var _tex_ice: Texture2D = _load_tex("res://assets/sprites/weapons/projectile_ice.png")
static var _tex_electric: Texture2D = _load_tex("res://assets/sprites/weapons/projectile_electric.png")
static var _tex_explosive: Texture2D = _load_tex("res://assets/sprites/weapons/projectile_explosive.png")
static var _tex_enemy: Texture2D = _load_tex("res://assets/sprites/weapons/projectile_enemy.png")


static func _load_tex(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path)
	return null


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

	# Set texture by element, fall back to color tinting if no texture
	_update_projectile_visual()

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
	# Projectiles pass through barriers and walls
	if body.is_in_group("barrier") or body.is_in_group("wall"):
		return
	if body.has_method("take_damage"):
		body.take_damage(get_final_damage(), global_position)
		_emit_hit()
	_spawn_impact_vfx()
	_deactivate()


func _on_area_entered(area: Area2D) -> void:
	# Hit hurtboxes
	if area.has_method("receive_hit"):
		area.receive_hit(self)
		_spawn_impact_vfx()
		_deactivate()


func _update_projectile_visual() -> void:
	if sprite == null:
		return

	# Try to set texture by element
	var tex: Texture2D = null
	match element:
		WeaponData.Element.NONE: tex = _tex_bullet
		WeaponData.Element.FIRE: tex = _tex_fire
		WeaponData.Element.ICE: tex = _tex_ice
		WeaponData.Element.ELECTRIC: tex = _tex_electric
		WeaponData.Element.EXPLOSIVE: tex = _tex_explosive

	# Enemy projectile (player_index == -1 and not player-owned)
	if owner_player_index < 0 and _tex_enemy:
		tex = _tex_enemy

	if tex:
		sprite.texture = tex
		sprite.modulate = Color.WHITE
	else:
		# Fallback: tint a blank sprite by element color
		match element:
			WeaponData.Element.NONE: sprite.modulate = Color.WHITE
			WeaponData.Element.FIRE: sprite.modulate = Color.ORANGE_RED
			WeaponData.Element.ICE: sprite.modulate = Color.LIGHT_BLUE
			WeaponData.Element.ELECTRIC: sprite.modulate = Color.YELLOW
			WeaponData.Element.EXPLOSIVE: sprite.modulate = Color.DARK_RED


func _spawn_impact_vfx() -> void:
	if element == WeaponData.Element.EXPLOSIVE:
		VFXSpawner.spawn("explosion", global_position, 1.5)
	else:
		VFXSpawner.spawn("impact", global_position)


func _emit_hit() -> void:
	EventBus.damage_dealt.emit(global_position, get_final_damage(), is_crit, element)


func _deactivate() -> void:
	set_deferred("monitoring", false)
	set_deferred("monitorable", false)
	call_deferred("_do_pool_release")


func _do_pool_release() -> void:
	ObjectPool.release_instance(self)
