class_name ShieldData
extends Resource
## Data container for a procedurally generated shield.

@export var shield_name: String = "Basic Shield"
@export var rarity: Rarity.Tier = Rarity.Tier.COMMON
@export var manufacturer: String = ""

@export var capacity: float = 50.0
@export var recharge_rate: float = 10.0  # per second
@export var recharge_delay: float = 4.0  # seconds after last hit before recharging

# Element resistance (0.0 = none, 1.0 = immune)
@export var fire_resistance: float = 0.0
@export var ice_resistance: float = 0.0
@export var electric_resistance: float = 0.0
@export var explosive_resistance: float = 0.0

# Special modifiers
@export var damage_reduction: float = 0.0  # flat % reduction while shield is active
@export var nova_on_break: bool = false
@export var nova_element: WeaponData.Element = WeaponData.Element.NONE
@export var nova_damage: float = 0.0

@export var item_level: int = 1


func get_resistance(element: WeaponData.Element) -> float:
	match element:
		WeaponData.Element.FIRE: return fire_resistance
		WeaponData.Element.ICE: return ice_resistance
		WeaponData.Element.ELECTRIC: return electric_resistance
		WeaponData.Element.EXPLOSIVE: return explosive_resistance
	return 0.0


func get_rarity_color() -> Color:
	return Rarity.COLORS[rarity]


func get_display_name() -> String:
	if manufacturer != "":
		return "%s %s" % [manufacturer, shield_name]
	return shield_name
