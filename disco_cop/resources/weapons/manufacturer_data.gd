class_name ManufacturerData
extends Resource
## Defines manufacturer identity and stat modifiers for weapon generation.

@export var manufacturer_name: String = ""
@export var prefix: String = ""  # Name prefix for weapons

# Stat modifiers (multipliers, 1.0 = no change)
@export var damage_mod: float = 1.0
@export var fire_rate_mod: float = 1.0
@export var reload_time_mod: float = 1.0
@export var magazine_mod: float = 1.0
@export var accuracy_mod: float = 1.0
@export var projectile_speed_mod: float = 1.0
@export var crit_chance_mod: float = 1.0
@export var knockback_mod: float = 1.0

# Specialization
@export var favored_types: Array[WeaponData.WeaponType] = []
@export var favored_elements: Array[WeaponData.Element] = []
@export var flavor_text: String = ""
