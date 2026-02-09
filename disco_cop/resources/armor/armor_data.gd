class_name ArmorData
extends Resource
## Data container for armor bonuses (passive stat modifiers).

@export var armor_name: String = "Basic Armor"
@export var rarity: Rarity.Tier = Rarity.Tier.COMMON

@export var max_health_bonus: float = 0.0  # flat bonus
@export var speed_bonus: float = 0.0  # percentage (0.1 = +10%)
@export var damage_bonus: float = 0.0  # percentage
@export var reload_speed_bonus: float = 0.0  # percentage
@export var crit_bonus: float = 0.0  # flat bonus to crit chance

@export var item_level: int = 1


func get_rarity_color() -> Color:
	return Rarity.COLORS[rarity]
