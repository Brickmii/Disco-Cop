class_name LootTable
## Manages weighted loot drops.

enum DropType { WEAPON, SHIELD, HEALTH, AMMO }

const DROP_WEIGHTS: Dictionary = {
	DropType.WEAPON: 40.0,
	DropType.SHIELD: 20.0,
	DropType.HEALTH: 30.0,
	DropType.AMMO: 10.0,
}


static func roll_drop(loot_chance: float, level: int = 1, rarity_bonus: int = 0) -> Dictionary:
	## Returns {type: DropType, data: Resource} or empty dict if no drop.
	if randf() > loot_chance:
		return {}

	var drop_type := _roll_type()
	var result := {"type": drop_type, "data": null}

	match drop_type:
		DropType.WEAPON:
			result["data"] = WeaponGenerator.generate(level)
		DropType.SHIELD:
			result["data"] = ShieldGenerator.generate(level)
		DropType.HEALTH:
			result["data"] = null  # Health pickup doesn't need data
		DropType.AMMO:
			result["data"] = null  # Ammo pickup doesn't need data

	return result


static func roll_boss_drop(level: int = 1) -> Array[Dictionary]:
	## Boss always drops Epic+ weapon and shield.
	var drops: Array[Dictionary] = []

	# Guaranteed Epic+ weapon
	var rarity: Rarity.Tier = Rarity.Tier.EPIC if randf() < 0.7 else Rarity.Tier.LEGENDARY
	drops.append({
		"type": DropType.WEAPON,
		"data": WeaponGenerator.generate(level, rarity),
	})

	# Guaranteed Rare+ shield
	var shield_rarity: Rarity.Tier = Rarity.Tier.RARE
	if randf() < 0.3:
		shield_rarity = Rarity.Tier.EPIC
	if randf() < 0.1:
		shield_rarity = Rarity.Tier.LEGENDARY
	drops.append({
		"type": DropType.SHIELD,
		"data": ShieldGenerator.generate(level, shield_rarity),
	})

	return drops


static func _roll_type() -> DropType:
	var total := 0.0
	for t in DROP_WEIGHTS:
		total += DROP_WEIGHTS[t]

	var roll := randf() * total
	var cumulative := 0.0
	for t in DROP_WEIGHTS:
		cumulative += DROP_WEIGHTS[t]
		if roll <= cumulative:
			return t as DropType
	return DropType.HEALTH
