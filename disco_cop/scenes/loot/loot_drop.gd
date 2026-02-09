extends Area2D
class_name LootDrop
## A dropped item that players can pick up.

var drop_data: Dictionary = {}  # {type: LootTable.DropType, data: Resource}
var _bob_offset := 0.0
var _initial_y := 0.0

@onready var visual: ColorRect = $Visual
@onready var label: Label = $Label


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
	if visual == null:
		return

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
	visual.color = color

	# Label
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
