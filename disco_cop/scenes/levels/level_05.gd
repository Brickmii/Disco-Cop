extends LevelBase
## Level 05: Bee Gees Disco Floor. Triple simultaneous boss fight.

var _disco_dancer_scene: PackedScene = preload("res://scenes/enemies/disco_dancer.tscn")
var _mirror_ball_scene: PackedScene = preload("res://scenes/enemies/mirror_ball.tscn")
var _floor_bouncer_scene: PackedScene = preload("res://scenes/enemies/floor_bouncer.tscn")
var _groupie_scene: PackedScene = preload("res://scenes/enemies/groupie.tscn")
var _roadie_scene: PackedScene = preload("res://scenes/enemies/roadie.tscn")
var _boss_barry_scene: PackedScene = preload("res://scenes/bosses/boss_barry_gibb.tscn")
var _boss_robin_scene: PackedScene = preload("res://scenes/bosses/boss_robin_gibb.tscn")
var _boss_maurice_scene: PackedScene = preload("res://scenes/bosses/boss_maurice_gibb.tscn")

var _bosses_defeated := 0


func _ready() -> void:
	level_bounds = Rect2(0, 0, 5500, 720)
	spawn_points = [Vector2(200, 688), Vector2(260, 688), Vector2(320, 688), Vector2(380, 688)]

	_build_scroll_lock_zones()
	_spawn_bosses()

	super._ready()
	GameManager.current_level = "level_05"


func _spawn_bosses() -> void:
	# Barry Gibb — flyer, starts airborne
	var barry: Node2D = _boss_barry_scene.instantiate() as Node2D
	barry.position = Vector2(5100, 500)
	if barry.has_signal("boss_defeated"):
		barry.connect("boss_defeated", _on_triple_boss_killed)
	add_child(barry)

	# Robin Gibb — ground
	var robin: Node2D = _boss_robin_scene.instantiate() as Node2D
	robin.position = Vector2(5200, 688)
	if robin.has_signal("boss_defeated"):
		robin.connect("boss_defeated", _on_triple_boss_killed)
	add_child(robin)

	# Maurice Gibb — starts invisible
	var maurice: Node2D = _boss_maurice_scene.instantiate() as Node2D
	maurice.position = Vector2(5300, 688)
	if maurice.has_signal("boss_defeated"):
		maurice.connect("boss_defeated", _on_triple_boss_killed)
	add_child(maurice)


func _on_triple_boss_killed() -> void:
	_bosses_defeated += 1
	if _bosses_defeated >= 3:
		EventBus.level_completed.emit()


func _build_scroll_lock_zones() -> void:
	# Zone 1 (x:800): 2 disco_dancer + 1 mirror_ball + 1 groupie
	var zone1 := ScrollLockZone.new()
	zone1.position = Vector2(800, 450)
	zone1.zone_rect = Rect2(-500, -250, 1000, 550)
	var spawner1 := EnemySpawner.new()
	spawner1.enemy_scenes = [_disco_dancer_scene, _disco_dancer_scene, _mirror_ball_scene, _groupie_scene]
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

	# Zone 2 (x:1900): 1 floor_bouncer + 2 disco_dancer + 1 roadie + 1 mirror_ball
	var zone2 := ScrollLockZone.new()
	zone2.position = Vector2(1900, 450)
	zone2.zone_rect = Rect2(-600, -250, 1200, 550)
	var spawner2 := EnemySpawner.new()
	spawner2.enemy_scenes = [_floor_bouncer_scene, _disco_dancer_scene, _disco_dancer_scene, _roadie_scene, _mirror_ball_scene]
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

	# Zone 3 (x:3000): 2 floor_bouncer + 2 mirror_ball + 1 disco_dancer + 1 groupie
	var zone3 := ScrollLockZone.new()
	zone3.position = Vector2(3000, 450)
	zone3.zone_rect = Rect2(-700, -250, 1400, 550)
	var spawner3 := EnemySpawner.new()
	spawner3.enemy_scenes = [_floor_bouncer_scene, _floor_bouncer_scene, _mirror_ball_scene, _mirror_ball_scene, _disco_dancer_scene, _groupie_scene]
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

	# Zone 4 (x:4200): 2 floor_bouncer + 2 disco_dancer + 2 mirror_ball + 1 roadie
	var zone4 := ScrollLockZone.new()
	zone4.position = Vector2(4200, 450)
	zone4.zone_rect = Rect2(-700, -250, 1400, 550)
	var spawner4 := EnemySpawner.new()
	spawner4.enemy_scenes = [_floor_bouncer_scene, _floor_bouncer_scene, _disco_dancer_scene, _disco_dancer_scene, _mirror_ball_scene, _mirror_ball_scene, _roadie_scene]
	spawner4.spawn_count = 9
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
