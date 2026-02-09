class_name ShieldGenerator
## Procedurally generates shields.

const BASE_CAPACITY := 50.0
const BASE_RECHARGE_RATE := 10.0
const BASE_RECHARGE_DELAY := 4.0

const SHIELD_PREFIXES: Array[String] = [
	"Disco", "Neon", "Groove", "Funky", "Soul",
	"Mirror Ball", "Strobe", "Velvet", "Chrome", "Glitter"
]

const SHIELD_SUFFIXES: Array[String] = [
	"Barrier", "Ward", "Aegis", "Buckler", "Guard",
	"Deflector", "Plate", "Shell", "Dome", "Field"
]


static func generate(level: int = 1, forced_rarity: Rarity.Tier = -1) -> ShieldData:
	var shield := ShieldData.new()

	# Roll rarity
	if forced_rarity >= 0:
		shield.rarity = forced_rarity as Rarity.Tier
	else:
		shield.rarity = _roll_rarity()

	shield.item_level = level

	var rarity_mult: float = Rarity.STAT_MULTIPLIERS[shield.rarity]
	var level_scale := 1.0 + (level - 1) * 0.05

	# Base stats with scaling
	shield.capacity = BASE_CAPACITY * rarity_mult * level_scale * randf_range(0.9, 1.1)
	shield.recharge_rate = BASE_RECHARGE_RATE * rarity_mult * randf_range(0.85, 1.15)
	shield.recharge_delay = BASE_RECHARGE_DELAY / lerpf(1.0, rarity_mult, 0.3)

	# Element resistances (higher rarity = more/better)
	var resist_count := 0
	match shield.rarity:
		Rarity.Tier.COMMON: resist_count = randi_range(0, 1)
		Rarity.Tier.UNCOMMON: resist_count = randi_range(0, 2)
		Rarity.Tier.RARE: resist_count = randi_range(1, 2)
		Rarity.Tier.EPIC: resist_count = randi_range(1, 3)
		Rarity.Tier.LEGENDARY: resist_count = randi_range(2, 4)

	var elements := [&"fire", &"ice", &"electric", &"explosive"]
	elements.shuffle()
	for i in mini(resist_count, elements.size()):
		var resist_value := randf_range(0.1, 0.4) * rarity_mult
		resist_value = clampf(resist_value, 0.0, 0.8)
		match elements[i]:
			&"fire": shield.fire_resistance = resist_value
			&"ice": shield.ice_resistance = resist_value
			&"electric": shield.electric_resistance = resist_value
			&"explosive": shield.explosive_resistance = resist_value

	# Damage reduction (rare+)
	if shield.rarity >= Rarity.Tier.RARE:
		shield.damage_reduction = randf_range(0.02, 0.08) * rarity_mult

	# Nova on break (epic+)
	if shield.rarity >= Rarity.Tier.EPIC and randf() < 0.3:
		shield.nova_on_break = true
		var nova_elements := [WeaponData.Element.FIRE, WeaponData.Element.ICE,
							WeaponData.Element.ELECTRIC, WeaponData.Element.EXPLOSIVE]
		shield.nova_element = nova_elements[randi() % nova_elements.size()]
		shield.nova_damage = shield.capacity * randf_range(0.3, 0.6)

	# Name generation
	shield.shield_name = _generate_name(shield)

	return shield


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


static func _generate_name(shield: ShieldData) -> String:
	var prefix: String = SHIELD_PREFIXES[randi() % SHIELD_PREFIXES.size()]
	var suffix: String = SHIELD_SUFFIXES[randi() % SHIELD_SUFFIXES.size()]

	var rarity_adj: Dictionary = {
		Rarity.Tier.COMMON: "",
		Rarity.Tier.UNCOMMON: "",
		Rarity.Tier.RARE: "Reinforced ",
		Rarity.Tier.EPIC: "Fortified ",
		Rarity.Tier.LEGENDARY: "Legendary ",
	}

	return "%s%s %s" % [rarity_adj[shield.rarity], prefix, suffix]
