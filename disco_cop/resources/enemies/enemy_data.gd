class_name EnemyData
extends Resource
## Data definition for enemy types.

enum EnemyType { GRUNT, SHOOTER, FLYER, SKATING_GRUNT, SKATING_SHOOTER, BRUTE, ROLLER_SKATER, BEACH_BUM, SEAGULL, ROADIE, GROUPIE, PYRO_TECH, SPEAKER_STACK }

@export var enemy_name: String = "Grunt"
@export var enemy_type: EnemyType = EnemyType.GRUNT
@export var max_health: float = 30.0
@export var move_speed: float = 100.0
@export var damage: float = 10.0
@export var attack_range: float = 40.0
@export var detection_range: float = 300.0
@export var attack_cooldown: float = 1.0
@export var score_value: int = 100
@export var xp_value: int = 10

# Loot
@export var loot_chance: float = 0.3  # chance to drop anything
@export var rarity_bonus: int = 0  # added to rarity roll
