class_name WeaponData
extends Resource
## Data container for a procedurally generated weapon.

enum WeaponType { PISTOL, SMG, SHOTGUN, ASSAULT_RIFLE, SNIPER, ROCKET_LAUNCHER }
enum Element { NONE, FIRE, ICE, ELECTRIC, EXPLOSIVE }

@export var weapon_name: String = "Pistol"
@export var weapon_type: WeaponType = WeaponType.PISTOL
@export var rarity: Rarity.Tier = Rarity.Tier.COMMON
@export var element: Element = Element.NONE
@export var manufacturer: String = ""

# Core stats
@export var damage: float = 10.0
@export var fire_rate: float = 5.0  # shots per second
@export var reload_time: float = 1.5  # seconds
@export var magazine_size: int = 12
@export var accuracy: float = 0.95  # 1.0 = perfect, lower = more spread
@export var projectile_speed: float = 800.0
@export var projectile_count: int = 1  # >1 for shotguns
@export var burst_count: int = 1  # >1 for burst fire
@export var burst_delay: float = 0.05  # delay between burst shots

# Element stats
@export var element_damage: float = 0.0  # bonus damage per tick
@export var element_chance: float = 0.0  # chance to proc element
@export var element_duration: float = 0.0  # status effect duration

# Special modifiers
@export var crit_chance: float = 0.05
@export var crit_multiplier: float = 2.0
@export var knockback: float = 50.0
@export var projectile_size: float = 1.0  # visual scale

# Calculated level (for display)
@export var item_level: int = 1


const TYPE_NAMES: Dictionary = {
	WeaponType.PISTOL: "Pistol",
	WeaponType.SMG: "SMG",
	WeaponType.SHOTGUN: "Shotgun",
	WeaponType.ASSAULT_RIFLE: "Assault Rifle",
	WeaponType.SNIPER: "Sniper",
	WeaponType.ROCKET_LAUNCHER: "Rocket Launcher",
}

const ELEMENT_NAMES: Dictionary = {
	Element.NONE: "None",
	Element.FIRE: "Fire",
	Element.ICE: "Ice",
	Element.ELECTRIC: "Electric",
	Element.EXPLOSIVE: "Explosive",
}

const ELEMENT_COLORS: Dictionary = {
	Element.NONE: Color.WHITE,
	Element.FIRE: Color.ORANGE_RED,
	Element.ICE: Color.LIGHT_BLUE,
	Element.ELECTRIC: Color.YELLOW,
	Element.EXPLOSIVE: Color.DARK_RED,
}


func get_dps() -> float:
	return damage * fire_rate * projectile_count


func get_display_name() -> String:
	var parts: PackedStringArray = []
	if manufacturer != "":
		parts.append(manufacturer)
	parts.append(weapon_name)
	return " ".join(parts)


func get_rarity_color() -> Color:
	return Rarity.COLORS[rarity]
