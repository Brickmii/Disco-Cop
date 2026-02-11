extends LevelBase
## Level 03: Sex Pistols Concert. Concert stage with roadies, groupies, pyro techs, and speakers.

var _roadie_scene: PackedScene = preload("res://scenes/enemies/roadie.tscn")
var _groupie_scene: PackedScene = preload("res://scenes/enemies/groupie.tscn")
var _pyrotech_scene: PackedScene = preload("res://scenes/enemies/pyro_tech.tscn")
var _speaker_scene: PackedScene = preload("res://scenes/enemies/speaker_stack.tscn")
var _boss_johnny_scene: PackedScene = preload("res://scenes/bosses/boss_johnny_rotten.tscn")
var _boss_sid_scene: PackedScene = preload("res://scenes/bosses/boss_sid_vicious.tscn")

var _bosses_defeated := 0


func _ready() -> void:
	level_bounds = Rect2(0, 0, 6000, 720)
	spawn_points = [Vector2(200, 688), Vector2(260, 688), Vector2(320, 688), Vector2(380, 688)]

	_build_scroll_lock_zones()
	_spawn_bosses()

	super._ready()
	GameManager.current_level = "level_03"


func _spawn_bosses() -> void:
	var johnny: Node2D = _boss_johnny_scene.instantiate() as Node2D
	johnny.position = Vector2(5600, 688)
	if johnny.has_signal("boss_defeated"):
		johnny.connect("boss_defeated", _on_dual_boss_killed)
	add_child(johnny)

	var sid: Node2D = _boss_sid_scene.instantiate() as Node2D
	sid.position = Vector2(5800, 688)
	if sid.has_signal("boss_defeated"):
		sid.connect("boss_defeated", _on_dual_boss_killed)
	add_child(sid)


func _on_dual_boss_killed() -> void:
	_bosses_defeated += 1
	if _bosses_defeated >= 2:
		EventBus.level_completed.emit()


func _build_scroll_lock_zones() -> void:
	# Zone 1 (x:600-1400): "Opening" — 3 groupie + 1 pyro_tech
	var zone1 := ScrollLockZone.new()
	zone1.position = Vector2(1000, 450)
	zone1.zone_rect = Rect2(-500, -250, 1000, 550)
	var spawner1 := EnemySpawner.new()
	spawner1.enemy_scenes = [_groupie_scene, _groupie_scene, _groupie_scene, _pyrotech_scene]
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

	# Zone 2 (x:1800-2800): "Crowd Surge" — 1 roadie + 2 groupie + 1 speaker + 1 pyro_tech
	var zone2 := ScrollLockZone.new()
	zone2.position = Vector2(2300, 450)
	zone2.zone_rect = Rect2(-600, -250, 1200, 550)
	var spawner2 := EnemySpawner.new()
	spawner2.enemy_scenes = [_roadie_scene, _groupie_scene, _groupie_scene, _speaker_scene, _pyrotech_scene]
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

	# Zone 3 (x:3200-4400): "Backstage" — 2 roadie + 1 speaker + 2 pyro_tech + 2 groupie
	var zone3 := ScrollLockZone.new()
	zone3.position = Vector2(3800, 450)
	zone3.zone_rect = Rect2(-700, -250, 1400, 550)
	var spawner3 := EnemySpawner.new()
	spawner3.enemy_scenes = [_roadie_scene, _roadie_scene, _speaker_scene, _pyrotech_scene, _pyrotech_scene, _groupie_scene, _groupie_scene]
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
