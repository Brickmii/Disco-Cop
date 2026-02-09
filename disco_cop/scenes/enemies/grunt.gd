extends BaseEnemy
class_name EnemyGrunt
## Melee walker enemy — charges at players and attacks up close.

func _ready() -> void:
	if enemy_data == null:
		enemy_data = EnemyData.new()
		enemy_data.enemy_name = "Grunt"
		enemy_data.enemy_type = EnemyData.EnemyType.GRUNT
		enemy_data.max_health = 30.0
		enemy_data.move_speed = 120.0
		enemy_data.damage = 15.0
		enemy_data.attack_range = 45.0
		enemy_data.detection_range = 250.0
		enemy_data.attack_cooldown = 0.8
		enemy_data.loot_chance = 0.25
	super._ready()


func _perform_attack() -> void:
	if _target and _distance_to_target() < enemy_data.attack_range:
		if _target.has_method("take_damage"):
			_target.take_damage(enemy_data.damage, global_position)
