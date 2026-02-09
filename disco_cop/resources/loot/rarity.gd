class_name Rarity
## Shared rarity definitions used by weapons, armor, and loot.

enum Tier { COMMON, UNCOMMON, RARE, EPIC, LEGENDARY }

const COLORS: Dictionary = {
	Tier.COMMON: Color.WHITE,
	Tier.UNCOMMON: Color.GREEN,
	Tier.RARE: Color.CORNFLOWER_BLUE,
	Tier.EPIC: Color.MEDIUM_PURPLE,
	Tier.LEGENDARY: Color.ORANGE,
}

const NAMES: Dictionary = {
	Tier.COMMON: "Common",
	Tier.UNCOMMON: "Uncommon",
	Tier.RARE: "Rare",
	Tier.EPIC: "Epic",
	Tier.LEGENDARY: "Legendary",
}

# Stat multipliers per rarity tier
const STAT_MULTIPLIERS: Dictionary = {
	Tier.COMMON: 1.0,
	Tier.UNCOMMON: 1.2,
	Tier.RARE: 1.5,
	Tier.EPIC: 1.8,
	Tier.LEGENDARY: 2.2,
}

# Drop weight (higher = more common)
const DROP_WEIGHTS: Dictionary = {
	Tier.COMMON: 50.0,
	Tier.UNCOMMON: 30.0,
	Tier.RARE: 14.0,
	Tier.EPIC: 5.0,
	Tier.LEGENDARY: 1.0,
}
