extends Control
class_name PlayerHUD
## Per-player HUD element showing health, shield, weapon, and ammo.

@export var player_index := 0

@onready var health_bar: ProgressBar = $VBox/HealthBar
@onready var shield_bar: ProgressBar = $VBox/ShieldBar
@onready var weapon_label: Label = $VBox/WeaponLabel
@onready var ammo_label: Label = $VBox/AmmoLabel
@onready var lives_label: Label = $VBox/LivesLabel

const PLAYER_COLORS: Array[Color] = [
	Color(0.2, 0.8, 0.3),
	Color(0.3, 0.5, 1.0),
	Color(1.0, 0.4, 0.2),
	Color(0.8, 0.2, 0.8),
]


func _ready() -> void:
	EventBus.player_health_changed.connect(_on_health_changed)
	EventBus.player_shield_changed.connect(_on_shield_changed)
	EventBus.weapon_swapped.connect(_on_weapon_changed)
	EventBus.weapon_fired.connect(_on_weapon_fired)
	EventBus.weapon_reloading.connect(_on_reloading)
	EventBus.weapon_reload_complete.connect(_on_reload_complete)

	# Set color accent
	if player_index < PLAYER_COLORS.size():
		modulate = PLAYER_COLORS[player_index]


func _on_health_changed(idx: int, current: float, maximum: float) -> void:
	if idx != player_index:
		return
	if health_bar:
		health_bar.max_value = maximum
		health_bar.value = current


func _on_shield_changed(idx: int, current: float, maximum: float) -> void:
	if idx != player_index:
		return
	if shield_bar:
		shield_bar.max_value = maximum
		shield_bar.value = current


func _on_weapon_changed(idx: int, weapon: Resource) -> void:
	if idx != player_index or weapon == null:
		return
	if weapon_label and weapon is WeaponData:
		weapon_label.text = weapon.get_display_name()
		weapon_label.modulate = weapon.get_rarity_color()


func _on_weapon_fired(idx: int, _weapon: Resource) -> void:
	if idx != player_index:
		return
	_update_ammo()


func _on_reloading(idx: int, _duration: float) -> void:
	if idx != player_index:
		return
	if ammo_label:
		ammo_label.text = "RELOADING..."


func _on_reload_complete(idx: int) -> void:
	if idx != player_index:
		return
	_update_ammo()


func _update_ammo() -> void:
	# Find player node and read ammo from weapon holder
	var player_data: Dictionary = GameManager.player_data[player_index]
	var player_node: Node = player_data.get("node")
	if player_node and player_node.has_node("WeaponHolder"):
		var holder: WeaponHolder = player_node.get_node("WeaponHolder")
		if holder.current_weapon and ammo_label:
			ammo_label.text = "%d / %d" % [holder.current_ammo, holder.current_weapon.magazine_size]


func update_lives(lives: int) -> void:
	if lives_label:
		lives_label.text = "Lives: %d" % lives
