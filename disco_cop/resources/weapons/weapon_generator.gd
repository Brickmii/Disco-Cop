class_name WeaponGenerator
## Procedurally generates weapons with Borderlands-style stat rolls.

# Base stats per weapon type [damage, fire_rate, reload, mag_size, accuracy, proj_speed, proj_count, knockback]
const BASE_STATS: Dictionary = {
	WeaponData.WeaponType.PISTOL: [12.0, 4.0, 1.5, 12, 0.92, 800.0, 1, 40.0],
	WeaponData.WeaponType.SMG: [8.0, 10.0, 1.8, 30, 0.82, 700.0, 1, 20.0],
	WeaponData.WeaponType.SHOTGUN: [8.0, 1.5, 2.2, 6, 0.65, 600.0, 6, 100.0],
	WeaponData.WeaponType.ASSAULT_RIFLE: [14.0, 7.0, 2.0, 24, 0.88, 750.0, 1, 35.0],
	WeaponData.WeaponType.SNIPER: [50.0, 1.0, 2.5, 4, 0.98, 1200.0, 1, 80.0],
	WeaponData.WeaponType.ROCKET_LAUNCHER: [80.0, 0.5, 3.0, 1, 0.70, 400.0, 1, 200.0],
}

# Manufacturer presets
static var manufacturers: Array[ManufacturerData] = []


static func _static_init() -> void:
	_init_manufacturers()


static func _init_manufacturers() -> void:
	manufacturers.clear()

	# Disco Arms — high damage, low fire rate
	var disco := ManufacturerData.new()
	disco.manufacturer_name = "Disco Arms"
	disco.prefix = "Groovy"
	disco.damage_mod = 1.3
	disco.fire_rate_mod = 0.85
	disco.accuracy_mod = 1.1
	disco.knockback_mod = 1.2
	disco.flavor_text = "Feel the beat of every bullet."
	manufacturers.append(disco)

	# Funky Munitions — high fire rate, lower accuracy
	var funky := ManufacturerData.new()
	funky.manufacturer_name = "Funky Munitions"
	funky.prefix = "Funky"
	funky.damage_mod = 0.9
	funky.fire_rate_mod = 1.35
	funky.accuracy_mod = 0.85
	funky.magazine_mod = 1.25
	funky.flavor_text = "Spray and slay!"
	manufacturers.append(funky)

	# Groove Tech — balanced, better crits
	var groove := ManufacturerData.new()
	groove.manufacturer_name = "Groove Tech"
	groove.prefix = "Smooth"
	groove.damage_mod = 1.05
	groove.fire_rate_mod = 1.05
	groove.accuracy_mod = 1.05
	groove.crit_chance_mod = 1.5
	groove.flavor_text = "Precision is our rhythm."
	manufacturers.append(groove)

	# Soul Ballistics — element specialist
	var soul := ManufacturerData.new()
	soul.manufacturer_name = "Soul Ballistics"
	soul.prefix = "Soulfire"
	soul.damage_mod = 0.95
	soul.fire_rate_mod = 1.0
	soul.accuracy_mod = 0.95
	soul.favored_elements = [WeaponData.Element.FIRE, WeaponData.Element.ELECTRIC]
	soul.flavor_text = "Burn with passion."
	manufacturers.append(soul)

	# Neon Dynamics — fast projectiles, fast reload
	var neon := ManufacturerData.new()
	neon.manufacturer_name = "Neon Dynamics"
	neon.prefix = "Neon"
	neon.reload_time_mod = 0.75
	neon.projectile_speed_mod = 1.3
	neon.accuracy_mod = 1.05
	neon.damage_mod = 0.95
	neon.flavor_text = "Speed of light, twice the fight."
	manufacturers.append(neon)


static func generate(level: int = 1, forced_rarity: Rarity.Tier = -1, forced_type: WeaponData.WeaponType = -1) -> WeaponData:
	var weapon := WeaponData.new()

	# Roll rarity
	if forced_rarity >= 0:
		weapon.rarity = forced_rarity as Rarity.Tier
	else:
		weapon.rarity = _roll_rarity()

	# Roll weapon type
	if forced_type >= 0:
		weapon.weapon_type = forced_type as WeaponData.WeaponType
	else:
		weapon.weapon_type = _roll_weapon_type()

	# Pick manufacturer
	var mfr: ManufacturerData = manufacturers[randi() % manufacturers.size()]
	weapon.manufacturer = mfr.manufacturer_name
	weapon.item_level = level

	# Apply base stats
	var base: Array = BASE_STATS[weapon.weapon_type]
	weapon.damage = base[0]
	weapon.fire_rate = base[1]
	weapon.reload_time = base[2]
	weapon.magazine_size = base[3]
	weapon.accuracy = base[4]
	weapon.projectile_speed = base[5]
	weapon.projectile_count = base[6]
	weapon.knockback = base[7]

	# Level scaling (5% per level)
	var level_scale := 1.0 + (level - 1) * 0.05
	weapon.damage *= level_scale

	# Rarity scaling
	var rarity_mult: float = Rarity.STAT_MULTIPLIERS[weapon.rarity]
	weapon.damage *= rarity_mult
	weapon.magazine_size = ceili(weapon.magazine_size * rarity_mult * 0.8)
	weapon.fire_rate *= lerpf(1.0, rarity_mult, 0.3)

	# Manufacturer modifiers
	weapon.damage *= mfr.damage_mod
	weapon.fire_rate *= mfr.fire_rate_mod
	weapon.reload_time *= mfr.reload_time_mod
	weapon.magazine_size = ceili(weapon.magazine_size * mfr.magazine_mod)
	weapon.accuracy = clampf(weapon.accuracy * mfr.accuracy_mod, 0.3, 1.0)
	weapon.projectile_speed *= mfr.projectile_speed_mod
	weapon.crit_chance *= mfr.crit_chance_mod
	weapon.knockback *= mfr.knockback_mod

	# Random variance (±10%)
	weapon.damage *= randf_range(0.9, 1.1)
	weapon.fire_rate *= randf_range(0.95, 1.05)

	# Element roll
	_roll_element(weapon, mfr)

	# Burst mode for some weapon types at higher rarities
	if weapon.weapon_type == WeaponData.WeaponType.PISTOL and weapon.rarity >= Rarity.Tier.RARE:
		if randf() < 0.3:
			weapon.burst_count = 3
			weapon.burst_delay = 0.06
			weapon.fire_rate *= 0.5  # Slower between bursts

	if weapon.weapon_type == WeaponData.WeaponType.ASSAULT_RIFLE and randf() < 0.2:
		weapon.burst_count = 3
		weapon.burst_delay = 0.05

	# Generate name
	weapon.weapon_name = _generate_name(weapon, mfr)

	return weapon


static func _roll_rarity() -> Rarity.Tier:
	var total := 0.0
	for tier in Rarity.DROP_WEIGHTS:
		total += Rarity.DROP_WEIGHTS[tier]

	var roll := randf() * total
	var cumulative := 0.0
	for tier in Rarity.DROP_WEIGHTS:
		cumulative += Rarity.DROP_WEIGHTS[tier]
		if roll <= cumulative:
			return tier as Rarity.Tier
	return Rarity.Tier.COMMON


static func _roll_weapon_type() -> WeaponData.WeaponType:
	var types := WeaponData.WeaponType.values()
	return types[randi() % types.size()] as WeaponData.WeaponType


static func _roll_element(weapon: WeaponData, mfr: ManufacturerData) -> void:
	var element_chance := 0.0
	match weapon.rarity:
		Rarity.Tier.COMMON: element_chance = 0.05
		Rarity.Tier.UNCOMMON: element_chance = 0.15
		Rarity.Tier.RARE: element_chance = 0.35
		Rarity.Tier.EPIC: element_chance = 0.60
		Rarity.Tier.LEGENDARY: element_chance = 0.85

	if randf() > element_chance:
		weapon.element = WeaponData.Element.NONE
		return

	# Pick element (bias toward manufacturer favorites)
	if mfr.favored_elements.size() > 0 and randf() < 0.6:
		weapon.element = mfr.favored_elements[randi() % mfr.favored_elements.size()]
	else:
		var elements := [WeaponData.Element.FIRE, WeaponData.Element.ICE,
						WeaponData.Element.ELECTRIC, WeaponData.Element.EXPLOSIVE]
		weapon.element = elements[randi() % elements.size()]

	# Element stats scale with rarity
	var rarity_mult: float = Rarity.STAT_MULTIPLIERS[weapon.rarity]
	weapon.element_chance = randf_range(0.15, 0.4) * rarity_mult
	weapon.element_damage = weapon.damage * randf_range(0.2, 0.4)
	weapon.element_duration = randf_range(2.0, 5.0)


static func _generate_name(weapon: WeaponData, mfr: ManufacturerData) -> String:
	var prefixes_by_element: Dictionary = {
		WeaponData.Element.NONE: ["Standard", "Classic", "Reliable", "Trusty"],
		WeaponData.Element.FIRE: ["Blazing", "Inferno", "Scorching", "Volcanic"],
		WeaponData.Element.ICE: ["Frozen", "Glacial", "Frostbite", "Arctic"],
		WeaponData.Element.ELECTRIC: ["Shocking", "Voltaic", "Thunder", "Storm"],
		WeaponData.Element.EXPLOSIVE: ["Volatile", "Detonating", "Blast", "Boom"],
	}

	var rarity_adj: Dictionary = {
		Rarity.Tier.COMMON: "",
		Rarity.Tier.UNCOMMON: "",
		Rarity.Tier.RARE: "Superior ",
		Rarity.Tier.EPIC: "Elite ",
		Rarity.Tier.LEGENDARY: "Legendary ",
	}

	var element_prefix: String = prefixes_by_element[weapon.element][randi() % prefixes_by_element[weapon.element].size()]
	var type_name: String = WeaponData.TYPE_NAMES[weapon.weapon_type]
	var rare_prefix: String = rarity_adj[weapon.rarity]

	if weapon.element == WeaponData.Element.NONE:
		return "%s%s %s" % [rare_prefix, mfr.prefix, type_name]
	else:
		return "%s%s %s" % [rare_prefix, element_prefix, type_name]
