extends Area2D
class_name LootDrop
## A dropped item that players can pick up.

var drop_data: Dictionary = {}  # {type: LootTable.DropType, data: Resource}
var _bob_offset := 0.0
var _initial_y := 0.0

@onready var sprite: Sprite2D = $Sprite
@onready var label: Label = $Label

# Preloaded loot textures — null until PNGs exist in assets/sprites/ui/
static var _tex_weapon: Texture2D = _load_tex("res://assets/sprites/ui/loot_weapon.png")
static var _tex_shield: Texture2D = _load_tex("res://assets/sprites/ui/loot_shield.png")
static var _tex_health: Texture2D = _load_tex("res://assets/sprites/ui/loot_health.png")
static var _tex_ammo: Texture2D = _load_tex("res://assets/sprites/ui/loot_ammo.png")


static func _load_tex(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path)
	return null


func _ready() -> void:
	collision_layer = 6  # Loot
	collision_mask = 2   # Players
	body_entered.connect(_on_body_entered)
	_initial_y = position.y
	_update_visual()

	# Pop-up effect
	var tween := create_tween()
	tween.tween_property(self, "position", position + Vector2(randf_range(-30, 30), -40), 0.3)
	tween.set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)


func setup(data: Dictionary, pos: Vector2) -> void:
	drop_data = data
	global_position = pos


func _process(delta: float) -> void:
	# Gentle bobbing
	_bob_offset += delta * 3.0
	position.y = _initial_y + sin(_bob_offset) * 3.0


func _update_visual() -> void:
	# Set texture by drop type
	if sprite and drop_data.has("type"):
		var tex: Texture2D = null
		match drop_data["type"]:
			LootTable.DropType.WEAPON: tex = _tex_weapon
			LootTable.DropType.SHIELD: tex = _tex_shield
			LootTable.DropType.HEALTH: tex = _tex_health
			LootTable.DropType.AMMO: tex = _tex_ammo
		if tex:
			sprite.texture = tex

	# Rarity color via modulate (sprites should be white/neutral base)
	var color := Color.WHITE
	if drop_data.has("data") and drop_data["data"] != null:
		var data: Resource = drop_data["data"]
		if data.has_method("get_rarity_color"):
			color = data.get_rarity_color()
	elif drop_data.has("type"):
		match drop_data["type"]:
			LootTable.DropType.HEALTH:
				color = Color.GREEN
			LootTable.DropType.AMMO:
				color = Color.DARK_CYAN
	if sprite:
		sprite.modulate = color

	# Label (kept as fallback when no textures yet)
	if label and drop_data.has("type"):
		match drop_data["type"]:
			LootTable.DropType.WEAPON:
				label.text = "W"
			LootTable.DropType.SHIELD:
				label.text = "S"
			LootTable.DropType.HEALTH:
				label.text = "+"
			LootTable.DropType.AMMO:
				label.text = "A"


func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("players"):
		return

	var player_index := 0
	if body.has_method("get") and "player_index" in body:
		player_index = body.player_index

	_apply_pickup(body, player_index)
	EventBus.loot_picked_up.emit(player_index, drop_data.get("data"))
	queue_free()


func _apply_pickup(player: Node2D, player_index: int) -> void:
	if not drop_data.has("type"):
		return

	match drop_data["type"]:
		LootTable.DropType.WEAPON:
			if drop_data.get("data") and player.has_node("WeaponHolder"):
				var holder: WeaponHolder = player.get_node("WeaponHolder")
				holder.equip_weapon(drop_data["data"])
		LootTable.DropType.SHIELD:
			if drop_data.get("data") and player.has_node("ShieldComponent"):
				var shield_comp: ShieldComponent = player.get_node("ShieldComponent")
				shield_comp.equip_shield(drop_data["data"])
		LootTable.DropType.HEALTH:
			if player.has_node("HealthComponent"):
				var hp: HealthComponent = player.get_node("HealthComponent")
				hp.heal(30.0)
		LootTable.DropType.AMMO:
			if player.has_node("WeaponHolder"):
				var holder: WeaponHolder = player.get_node("WeaponHolder")
				holder.current_ammo = holder.current_weapon.magazine_size if holder.current_weapon else 0
