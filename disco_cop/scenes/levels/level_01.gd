extends LevelBase
## Level 01: Disco Dungeon. Sections built in _ready().

var _grunt_scene: PackedScene = preload("res://scenes/enemies/grunt.tscn")
var _shooter_scene: PackedScene = preload("res://scenes/enemies/shooter.tscn")
var _flyer_scene: PackedScene = preload("res://scenes/enemies/flyer.tscn")
var _boss_scene: PackedScene = preload("res://scenes/bosses/boss_disco_king.tscn")


func _ready() -> void:
	level_bounds = Rect2(0, -200, 5200, 1200)
	spawn_points = [Vector2(200, 800), Vector2(260, 800), Vector2(320, 800), Vector2(380, 800)]

	_build_terrain()
	_build_parallax()
	_build_scroll_lock_zones()
	_spawn_boss()

	super._ready()


func _spawn_boss() -> void:
	var boss_node: Node2D = _boss_scene.instantiate() as Node2D
	boss_node.position = Vector2(4700, 830)
	if boss_node.has_signal("boss_defeated"):
		boss_node.connect("boss_defeated", _on_boss_defeated)
	add_child(boss_node)


func _on_boss_defeated() -> void:
	EventBus.level_completed.emit()


func _build_terrain() -> void:
	# --- Section 1: Landing Zone (x: 0-1000) ---
	_add_platform(Vector2(500, 900), Vector2(1000, 32))  # Ground
	_add_platform(Vector2(300, 750), Vector2(150, 16))
	_add_platform(Vector2(600, 650), Vector2(150, 16))
	_add_platform(Vector2(850, 550), Vector2(150, 16))

	# --- Section 2: Vertical Climb (x: 1000-1800) ---
	_add_platform(Vector2(1300, 900), Vector2(600, 32))  # Ground continues
	_add_platform(Vector2(1100, 750), Vector2(120, 16))
	_add_platform(Vector2(1350, 600), Vector2(120, 16))
	_add_platform(Vector2(1150, 450), Vector2(120, 16))
	_add_platform(Vector2(1400, 300), Vector2(120, 16))
	_add_platform(Vector2(1600, 200), Vector2(200, 16))

	# --- Section 3: Bridge Gauntlet (x: 1800-2800) ---
	_add_platform(Vector2(2000, 250), Vector2(150, 16))
	_add_platform(Vector2(2200, 250), Vector2(150, 16))
	_add_platform(Vector2(2400, 250), Vector2(150, 16))
	_add_platform(Vector2(2600, 250), Vector2(150, 16))
	# Gap platforms below (death gap)
	_add_kill_zone(Vector2(2300, 950), Vector2(800, 100))

	# --- Section 4: Mid-Boss Arena (x: 2800-3400) ---
	_add_platform(Vector2(3100, 300), Vector2(600, 32))
	_add_platform(Vector2(3100, 500), Vector2(200, 16))  # Center platform

	# --- Section 5: Descent (x: 3400-4200) ---
	_add_platform(Vector2(3600, 400), Vector2(150, 16))
	_add_platform(Vector2(3800, 500), Vector2(150, 16))
	_add_platform(Vector2(3600, 650), Vector2(150, 16))
	_add_platform(Vector2(3900, 750), Vector2(150, 16))
	_add_platform(Vector2(4100, 900), Vector2(300, 32))

	# --- Section 6: Boss Arena (x: 4200-5200) ---
	_add_platform(Vector2(4700, 900), Vector2(1000, 32))  # Large floor
	_add_platform(Vector2(4500, 700), Vector2(150, 16))  # Side platforms
	_add_platform(Vector2(4900, 700), Vector2(150, 16))
	_add_platform(Vector2(4700, 500), Vector2(200, 16))  # Center high

	# Hazard spikes in various places
	_add_hazard(Vector2(700, 880), Vector2(60, 16))
	_add_hazard(Vector2(2300, 230), Vector2(40, 16))


func _build_parallax() -> void:
	var parallax_bg := ParallaxBackground.new()
	parallax_bg.name = "ParallaxBackground"
	add_child(parallax_bg)

	# Layer 1 (far) - dark city skyline
	var layer1 := ParallaxLayer.new()
	layer1.motion_scale = Vector2(0.1, 0.05)
	var bg1 := ColorRect.new()
	bg1.size = Vector2(6000, 1200)
	bg1.position = Vector2(-500, -200)
	bg1.color = Color(0.05, 0.02, 0.08)
	bg1.z_index = -30
	layer1.add_child(bg1)
	parallax_bg.add_child(layer1)

	# Layer 2 (mid) - buildings
	var layer2 := ParallaxLayer.new()
	layer2.motion_scale = Vector2(0.3, 0.15)
	var bg2 := ColorRect.new()
	bg2.size = Vector2(6000, 800)
	bg2.position = Vector2(-500, 200)
	bg2.color = Color(0.08, 0.04, 0.12)
	bg2.z_index = -20
	layer2.add_child(bg2)
	parallax_bg.add_child(layer2)

	# Layer 3 (near) - foreground detail
	var layer3 := ParallaxLayer.new()
	layer3.motion_scale = Vector2(0.6, 0.3)
	var bg3 := ColorRect.new()
	bg3.size = Vector2(6000, 400)
	bg3.position = Vector2(-500, 600)
	bg3.color = Color(0.12, 0.06, 0.18)
	bg3.z_index = -10
	layer3.add_child(bg3)
	parallax_bg.add_child(layer3)


func _build_scroll_lock_zones() -> void:
	# Zone 1: Landing Zone combat
	var zone1 := ScrollLockZone.new()
	zone1.position = Vector2(300, 500)
	zone1.zone_rect = Rect2(-200, -200, 600, 500)
	var spawner1 := EnemySpawner.new()
	spawner1.enemy_scenes = [_grunt_scene, _grunt_scene]
	spawner1.spawn_count = 3
	spawner1.position = Vector2(200, 0)
	zone1.add_child(spawner1)

	var zone1_shape := CollisionShape2D.new()
	var zone1_rect := RectangleShape2D.new()
	zone1_rect.size = Vector2(600, 500)
	zone1_shape.shape = zone1_rect
	zone1.add_child(zone1_shape)
	add_child(zone1)

	# Zone 2: Bridge Gauntlet
	var zone2 := ScrollLockZone.new()
	zone2.position = Vector2(2300, 100)
	zone2.zone_rect = Rect2(-300, -150, 600, 400)
	var spawner2 := EnemySpawner.new()
	spawner2.enemy_scenes = [_shooter_scene, _flyer_scene]
	spawner2.spawn_count = 4
	spawner2.position = Vector2(0, -50)
	zone2.add_child(spawner2)

	var zone2_shape := CollisionShape2D.new()
	var zone2_rect := RectangleShape2D.new()
	zone2_rect.size = Vector2(600, 400)
	zone2_shape.shape = zone2_rect
	zone2.add_child(zone2_shape)
	add_child(zone2)

	# Zone 3: Pre-boss
	var zone3 := ScrollLockZone.new()
	zone3.position = Vector2(4100, 600)
	zone3.zone_rect = Rect2(-200, -300, 400, 500)
	var spawner3 := EnemySpawner.new()
	spawner3.enemy_scenes = [_grunt_scene, _shooter_scene, _flyer_scene]
	spawner3.spawn_count = 5
	spawner3.position = Vector2(0, 0)
	zone3.add_child(spawner3)

	var zone3_shape := CollisionShape2D.new()
	var zone3_rect := RectangleShape2D.new()
	zone3_rect.size = Vector2(400, 500)
	zone3_shape.shape = zone3_rect
	zone3.add_child(zone3_shape)
	add_child(zone3)


func _add_platform(pos: Vector2, size: Vector2) -> void:
	var body := StaticBody2D.new()
	body.position = pos
	body.collision_layer = 1

	var col := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = size
	col.shape = shape
	body.add_child(col)

	var visual := ColorRect.new()
	visual.position = -size / 2.0
	visual.size = size
	visual.color = Color(0.35, 0.25, 0.2) if size.y > 20 else Color(0.45, 0.35, 0.3)
	body.add_child(visual)

	add_child(body)


func _add_kill_zone(pos: Vector2, size: Vector2) -> void:
	var area := Area2D.new()
	area.position = pos
	area.collision_layer = 10  # Hazards
	area.collision_mask = 2    # Players

	var col := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = size
	col.shape = shape
	area.add_child(col)

	area.body_entered.connect(func(body: Node2D) -> void:
		if body.has_method("take_damage"):
			body.take_damage(9999.0, pos)
	)

	add_child(area)


func _add_hazard(pos: Vector2, size: Vector2) -> void:
	var area := Area2D.new()
	area.position = pos
	area.collision_layer = 10
	area.collision_mask = 2

	var col := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = size
	col.shape = shape
	area.add_child(col)

	var visual := ColorRect.new()
	visual.position = -size / 2.0
	visual.size = size
	visual.color = Color(0.9, 0.1, 0.1)
	area.add_child(visual)

	area.body_entered.connect(func(body: Node2D) -> void:
		if body.has_method("take_damage"):
			body.take_damage(20.0, pos)
	)

	add_child(area)
