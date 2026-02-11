extends LevelBase
## Level 04: Blondie Concert at CBGB. Stage divers, pogo punks, bottle throwers, and bouncers.

var _stage_diver_scene: PackedScene = preload("res://scenes/enemies/stage_diver.tscn")
var _pogo_punk_scene: PackedScene = preload("res://scenes/enemies/pogo_punk.tscn")
var _bottle_thrower_scene: PackedScene = preload("res://scenes/enemies/bottle_thrower.tscn")
var _bouncer_scene: PackedScene = preload("res://scenes/enemies/bouncer.tscn")
var _boss_scene: PackedScene = preload("res://scenes/bosses/boss_debbie_harry.tscn")


func _ready() -> void:
	level_bounds = Rect2(0, 0, 7000, 720)
	spawn_points = [Vector2(200, 688), Vector2(260, 688), Vector2(320, 688), Vector2(380, 688)]

	_build_scroll_lock_zones()
	_spawn_boss()

	super._ready()
	GameManager.current_level = "level_04"


func _spawn_boss() -> void:
	var boss_node: Node2D = _boss_scene.instantiate() as Node2D
	boss_node.position = Vector2(6700, 688)
	if boss_node.has_signal("boss_defeated"):
		boss_node.connect("boss_defeated", _on_boss_victory)
	add_child(boss_node)


func _on_boss_victory() -> void:
	EventBus.level_completed.emit()


func _build_scroll_lock_zones() -> void:
	# Zone 1 (x:800): 2 pogo_punk + 1 stage_diver + 1 bottle_thrower
	var zone1 := ScrollLockZone.new()
	zone1.position = Vector2(800, 450)
	zone1.zone_rect = Rect2(-500, -250, 1000, 550)
	var spawner1 := EnemySpawner.new()
	spawner1.enemy_scenes = [_pogo_punk_scene, _pogo_punk_scene, _stage_diver_scene, _bottle_thrower_scene]
	spawner1.spawn_count = 5
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

	# Zone 2 (x:2200): 1 bouncer + 2 stage_diver + 1 pogo_punk + 1 bottle_thrower
	var zone2 := ScrollLockZone.new()
	zone2.position = Vector2(2200, 450)
	zone2.zone_rect = Rect2(-600, -250, 1200, 550)
	var spawner2 := EnemySpawner.new()
	spawner2.enemy_scenes = [_bouncer_scene, _stage_diver_scene, _stage_diver_scene, _pogo_punk_scene, _bottle_thrower_scene]
	spawner2.spawn_count = 6
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

	# Zone 3 (x:3800): 1 bouncer + 2 bottle_thrower + 2 pogo_punk + 1 stage_diver
	var zone3 := ScrollLockZone.new()
	zone3.position = Vector2(3800, 450)
	zone3.zone_rect = Rect2(-700, -250, 1400, 550)
	var spawner3 := EnemySpawner.new()
	spawner3.enemy_scenes = [_bouncer_scene, _bottle_thrower_scene, _bottle_thrower_scene, _pogo_punk_scene, _pogo_punk_scene, _stage_diver_scene]
	spawner3.spawn_count = 8
	spawner3.spawn_radius = 250.0
	spawner3.position = Vector2(0, 238)
	zone3.add_child(spawner3)

	var zone3_shape := CollisionShape2D.new()
	var zone3_rect := RectangleShape2D.new()
	zone3_rect.size = Vector2(900, 400)
	zone3_shape.shape = zone3_rect
	zone3_shape.position = Vector2(0, 50)
	zone3.add_child(zone3_shape)
	add_child(zone3)

	# Zone 4 (x:5200): 2 bouncer + 2 stage_diver + 2 bottle_thrower + 2 pogo_punk
	var zone4 := ScrollLockZone.new()
	zone4.position = Vector2(5200, 450)
	zone4.zone_rect = Rect2(-700, -250, 1400, 550)
	var spawner4 := EnemySpawner.new()
	spawner4.enemy_scenes = [_bouncer_scene, _bouncer_scene, _stage_diver_scene, _stage_diver_scene, _bottle_thrower_scene, _bottle_thrower_scene, _pogo_punk_scene, _pogo_punk_scene]
	spawner4.spawn_count = 10
	spawner4.spawn_radius = 300.0
	spawner4.position = Vector2(0, 238)
	zone4.add_child(spawner4)

	var zone4_shape := CollisionShape2D.new()
	var zone4_rect := RectangleShape2D.new()
	zone4_rect.size = Vector2(900, 400)
	zone4_shape.shape = zone4_rect
	zone4_shape.position = Vector2(0, 50)
	zone4.add_child(zone4_shape)
	add_child(zone4)
