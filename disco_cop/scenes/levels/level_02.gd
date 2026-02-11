extends LevelBase
## Level 02: Venice Beach. Outdoor boardwalk with weightlifters and skaters.

var _brute_scene: PackedScene = preload("res://scenes/enemies/brute.tscn")
var _skater_scene: PackedScene = preload("res://scenes/enemies/roller_skater.tscn")
var _beachbum_scene: PackedScene = preload("res://scenes/enemies/beach_bum.tscn")
var _seagull_scene: PackedScene = preload("res://scenes/enemies/seagull.tscn")
var _boss_scene: PackedScene = preload("res://scenes/bosses/boss_arnoldo.tscn")


func _ready() -> void:
	level_bounds = Rect2(0, 0, 5000, 720)
	spawn_points = [Vector2(200, 688), Vector2(260, 688), Vector2(320, 688), Vector2(380, 688)]

	_build_scroll_lock_zones()
	_spawn_boss()

	super._ready()
	GameManager.current_level = "level_02"


func _spawn_boss() -> void:
	var boss_node: Node2D = _boss_scene.instantiate() as Node2D
	boss_node.position = Vector2(4700, 688)
	if boss_node.has_signal("boss_defeated"):
		boss_node.connect("boss_defeated", _on_boss_victory)
	add_child(boss_node)


func _on_boss_victory() -> void:
	EventBus.level_completed.emit()


func _build_scroll_lock_zones() -> void:
	# Zone 1 (x:400-1200): warm-up — skaters + beach bum
	var zone1 := ScrollLockZone.new()
	zone1.position = Vector2(800, 450)
	zone1.zone_rect = Rect2(-500, -250, 1000, 550)
	var spawner1 := EnemySpawner.new()
	spawner1.enemy_scenes = [_skater_scene, _skater_scene, _beachbum_scene]
	spawner1.spawn_count = 4
	spawner1.spawn_radius = 150.0
	spawner1.position = Vector2(0, 238)
	zone1.add_child(spawner1)

	var zone1_shape := CollisionShape2D.new()
	var zone1_rect := RectangleShape2D.new()
	zone1_rect.size = Vector2(600, 400)
	zone1_shape.shape = zone1_rect
	zone1_shape.position = Vector2(0, 50)
	zone1.add_child(zone1_shape)
	add_child(zone1)

	# Zone 2 (x:1600-2600): escalation — brute + skaters + seagulls
	var zone2 := ScrollLockZone.new()
	zone2.position = Vector2(2100, 450)
	zone2.zone_rect = Rect2(-600, -250, 1200, 550)
	var spawner2 := EnemySpawner.new()
	spawner2.enemy_scenes = [_brute_scene, _skater_scene, _beachbum_scene, _seagull_scene]
	spawner2.spawn_count = 5
	spawner2.spawn_radius = 200.0
	spawner2.position = Vector2(0, 238)
	zone2.add_child(spawner2)

	var zone2_shape := CollisionShape2D.new()
	var zone2_rect := RectangleShape2D.new()
	zone2_rect.size = Vector2(800, 400)
	zone2_shape.shape = zone2_rect
	zone2_shape.position = Vector2(0, 50)
	zone2.add_child(zone2_shape)
	add_child(zone2)

	# Zone 3 (x:3000-4000): pre-boss gauntlet — heavy mix
	var zone3 := ScrollLockZone.new()
	zone3.position = Vector2(3500, 450)
	zone3.zone_rect = Rect2(-600, -250, 1200, 550)
	var spawner3 := EnemySpawner.new()
	spawner3.enemy_scenes = [_brute_scene, _brute_scene, _skater_scene, _beachbum_scene, _seagull_scene]
	spawner3.spawn_count = 7
	spawner3.spawn_radius = 200.0
	spawner3.position = Vector2(0, 238)
	zone3.add_child(spawner3)

	var zone3_shape := CollisionShape2D.new()
	var zone3_rect := RectangleShape2D.new()
	zone3_rect.size = Vector2(800, 400)
	zone3_shape.shape = zone3_rect
	zone3_shape.position = Vector2(0, 50)
	zone3.add_child(zone3_shape)
	add_child(zone3)
