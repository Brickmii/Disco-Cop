extends LevelBase
## Tutorial level — 2 scroll-lock zones, auto-transitions to Level 1.

var _skating_grunt_scene: PackedScene = preload("res://scenes/enemies/skating_grunt.tscn")
var _skating_shooter_scene: PackedScene = preload("res://scenes/enemies/skating_shooter.tscn")
var _flyer_scene: PackedScene = preload("res://scenes/enemies/flyer.tscn")
var _transitioning := false


func _ready() -> void:
	level_bounds = Rect2(0, 0, 2000, 720)
	spawn_points = [Vector2(100, 688), Vector2(160, 688), Vector2(220, 688), Vector2(280, 688)]

	_build_scroll_lock_zones()

	super._ready()
	GameManager.current_level = "tutorial"


func _build_scroll_lock_zones() -> void:
	# Zone 1 (x:300-800): 3 skating grunts
	# zone_rect 100px wider on each side so walls are behind player when trigger fires
	var zone1 := ScrollLockZone.new()
	zone1.position = Vector2(550, 450)
	zone1.zone_rect = Rect2(-350, -250, 700, 550)
	var spawner1 := EnemySpawner.new()
	spawner1.enemy_scenes = [_skating_grunt_scene]
	spawner1.spawn_count = 3
	spawner1.spawn_radius = 80.0
	spawner1.position = Vector2(100, 238)
	zone1.add_child(spawner1)

	var zone1_shape := CollisionShape2D.new()
	var zone1_rect := RectangleShape2D.new()
	zone1_rect.size = Vector2(400, 400)
	zone1_shape.shape = zone1_rect
	zone1_shape.position = Vector2(0, 50)
	zone1.add_child(zone1_shape)
	add_child(zone1)

	# Zone 2 (x:1000-1800): 2 grunts + 1 shooter + 1 flyer
	var zone2 := ScrollLockZone.new()
	zone2.position = Vector2(1400, 450)
	zone2.zone_rect = Rect2(-500, -250, 1000, 550)
	var spawner2 := EnemySpawner.new()
	spawner2.enemy_scenes = [_skating_grunt_scene, _skating_grunt_scene, _skating_shooter_scene, _flyer_scene]
	spawner2.spawn_count = 4
	spawner2.spawn_radius = 100.0
	spawner2.position = Vector2(0, 238)
	zone2.add_child(spawner2)

	var zone2_shape := CollisionShape2D.new()
	var zone2_rect := RectangleShape2D.new()
	zone2_rect.size = Vector2(700, 400)
	zone2_shape.shape = zone2_rect
	zone2_shape.position = Vector2(0, 50)
	zone2.add_child(zone2_shape)
	add_child(zone2)

	zone2.zone_cleared.connect(_on_tutorial_complete)


func _on_tutorial_complete() -> void:
	if _transitioning:
		return
	_transitioning = true

	# Save each player's weapons for carry-over to Level 1
	for pd in GameManager.player_data:
		if pd["active"] and pd["node"] != null:
			var player_node: Node = pd["node"]
			var holder: WeaponHolder = player_node.get_node("WeaponHolder") as WeaponHolder
			if holder:
				GameManager.save_player_weapons(pd["index"], holder.weapons)
	get_tree().call_deferred("change_scene_to_file", "res://scenes/levels/level_01.tscn")
