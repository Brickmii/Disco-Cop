extends Node2D
## Stress test: ramps up objects until FPS drops below 60, finds the breaking point.

var _elapsed := 0.0
var _phase := 0
var _phase_timer := 0.0
var _fps_samples: Array[float] = []
var _phase_start_time := 0.0

var _grunt_scene: PackedScene = preload("res://scenes/enemies/grunt.tscn")
var _shooter_scene: PackedScene = preload("res://scenes/enemies/shooter.tscn")
var _flyer_scene: PackedScene = preload("res://scenes/enemies/flyer.tscn")
var _projectile_scene: PackedScene = preload("res://scenes/weapons/projectile.tscn")
var _loot_scene: PackedScene = preload("res://scenes/loot/loot_drop.tscn")
var _player_scene: PackedScene = preload("res://scenes/player/player.tscn")

var _spawned_enemies: Array[Node] = []
var _spawned_projectiles: Array[Node] = []
var _spawned_loot: Array[Node] = []
var _spawned_players: Array[Node] = []
var _damage_labels: Array[Node] = []

var _enemy_count := 0
var _projectile_count := 0
var _loot_count := 0
var _player_count := 0
var _label_count := 0

const PHASE_DURATION := 4.0
const TOTAL_PHASES := 9

# Phase plan:
# 0: Baseline (just level geometry)
# 1: 4 players
# 2: +10 enemies
# 3: +20 enemies (30 total)
# 4: +50 projectiles flying
# 5: +100 projectiles (150 total)
# 6: +20 loot drops
# 7: +50 damage number labels
# 8: Everything at once + 50 more enemies


func _ready() -> void:
	# Build floor
	_add_platform(Vector2(2500, 900), Vector2(5000, 32))
	_add_platform(Vector2(2500, 600), Vector2(3000, 16))
	_add_platform(Vector2(2500, 400), Vector2(2000, 16))

	# Pre-fill projectile pool
	if ObjectPool.get_pool_size("stress_projectiles") == 0:
		ObjectPool.preload_pool("stress_projectiles", _projectile_scene, 200)

	# Register P1 so player scenes work
	if GameManager.get_active_player_count() == 0:
		GameManager.register_player(0, -1)

	_start_phase(0)
	print("")
	print("====== STRESS TEST STARTING ======")
	print("Ramping objects over %d phases (%ds each)" % [TOTAL_PHASES, PHASE_DURATION])
	print("")


func _process(delta: float) -> void:
	_elapsed += delta
	_phase_timer += delta

	# Collect FPS every frame for current phase
	var fps := Performance.get_monitor(Performance.TIME_FPS)

	# Print stats every second
	if fmod(_elapsed, 1.0) < delta:
		var draw_calls := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
		var objects := Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)
		var nodes := get_tree().get_node_count()
		var mem := Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0
		print("Phase %d | FPS: %5.1f | Draws: %3d | Objects: %4d | Nodes: %4d | Mem: %.1fMB | E:%d P:%d L:%d Lab:%d Pl:%d" % [
			_phase, fps, draw_calls, objects, nodes, mem,
			_enemy_count, _projectile_count, _loot_count, _label_count, _player_count
		])
		_fps_samples.append(fps)

	# Keep projectiles alive by recycling them
	_recycle_projectiles()

	# Phase transition
	if _phase_timer >= PHASE_DURATION:
		_phase_timer = 0.0
		_phase += 1
		if _phase >= TOTAL_PHASES:
			_finish()
			return
		_start_phase(_phase)


func _start_phase(phase: int) -> void:
	print("--- Phase %d ---" % phase)
	match phase:
		0:
			print("  Baseline: level geometry only")
		1:
			print("  Adding 4 players")
			_spawn_players(4)
		2:
			print("  Adding 10 enemies")
			_spawn_enemies(10)
		3:
			print("  Adding 20 more enemies (30 total)")
			_spawn_enemies(20)
		4:
			print("  Adding 50 projectiles")
			_spawn_projectiles(50)
		5:
			print("  Adding 100 more projectiles (150 total)")
			_spawn_projectiles(100)
		6:
			print("  Adding 20 loot drops")
			_spawn_loot(20)
		7:
			print("  Adding 50 damage labels")
			_spawn_damage_labels(50)
		8:
			print("  MAXIMUM: +50 enemies, +50 projectiles, +30 loot, +50 labels")
			_spawn_enemies(50)
			_spawn_projectiles(50)
			_spawn_loot(30)
			_spawn_damage_labels(50)


func _spawn_players(count: int) -> void:
	for i in count:
		var player: Node2D = _player_scene.instantiate() as Node2D
		player.set("player_index", mini(i, 3))
		player.global_position = Vector2(200 + i * 60, 800)
		add_child(player)
		_spawned_players.append(player)
		_player_count += 1


func _spawn_enemies(count: int) -> void:
	var scenes: Array[PackedScene] = [_grunt_scene, _shooter_scene, _flyer_scene]
	for i in count:
		var scene: PackedScene = scenes[randi() % scenes.size()]
		var enemy: Node2D = scene.instantiate() as Node2D
		enemy.global_position = Vector2(
			randf_range(100, 4900),
			randf_range(300, 850)
		)
		add_child(enemy)
		_spawned_enemies.append(enemy)
		_enemy_count += 1


func _spawn_projectiles(count: int) -> void:
	var weapon := WeaponData.new()
	weapon.damage = 1.0
	weapon.projectile_speed = 300.0
	weapon.knockback = 0.0
	weapon.crit_chance = 0.0
	weapon.crit_multiplier = 1.0
	weapon.projectile_size = 1.0
	weapon.element = WeaponData.Element.NONE

	for i in count:
		var proj: Node = ObjectPool.get_instance("stress_projectiles")
		if proj == null:
			continue
		if proj.has_method("activate"):
			var pos := Vector2(randf_range(100, 4900), randf_range(200, 800))
			var dir := Vector2.from_angle(randf() * TAU)
			proj.call("activate", pos, dir, weapon, -1, false)
			# Override collision so they don't hit anything and deactivate
			proj.set("collision_layer", 0)
			proj.set("collision_mask", 0)
			proj.set("max_lifetime", 999.0)
		_spawned_projectiles.append(proj)
		_projectile_count += 1


func _spawn_loot(count: int) -> void:
	for i in count:
		var loot: Node = _loot_scene.instantiate()
		var pos := Vector2(randf_range(100, 4900), randf_range(600, 850))
		loot.call("setup", {"type": 2, "data": null}, pos)  # HEALTH type
		add_child(loot)
		_spawned_loot.append(loot)
		_loot_count += 1


func _spawn_damage_labels(count: int) -> void:
	for i in count:
		var label := Label.new()
		label.text = str(randi_range(10, 999))
		label.position = Vector2(randf_range(100, 4900), randf_range(200, 800))
		label.add_theme_font_size_override("font_size", randi_range(14, 24))
		label.modulate = [Color.WHITE, Color.ORANGE_RED, Color.YELLOW, Color.LIGHT_BLUE][randi() % 4]
		add_child(label)
		_damage_labels.append(label)
		_label_count += 1

		# Animate
		var tween := label.create_tween()
		tween.set_loops()
		tween.tween_property(label, "position:y", label.position.y - 30, 1.0)
		tween.tween_property(label, "position:y", label.position.y, 1.0)


func _recycle_projectiles() -> void:
	# Keep projectiles in bounds by wrapping them
	for proj in _spawned_projectiles:
		if is_instance_valid(proj) and proj.visible:
			var pos: Vector2 = proj.global_position
			if pos.x < -100 or pos.x > 5100 or pos.y < -200 or pos.y > 1100:
				proj.global_position = Vector2(randf_range(100, 4900), randf_range(200, 800))


func _finish() -> void:
	print("")
	print("====== STRESS TEST RESULTS ======")

	if _fps_samples.is_empty():
		print("  No samples collected!")
		get_tree().quit()
		return

	var min_fps := _fps_samples[0]
	var max_fps := _fps_samples[0]
	var total := 0.0
	var below_60 := 0
	for s in _fps_samples:
		total += s
		if s < min_fps:
			min_fps = s
		if s > max_fps:
			max_fps = s
		if s < 60.0:
			below_60 += 1

	var avg := total / _fps_samples.size()

	print("  Total objects spawned:")
	print("    Players:      %d" % _player_count)
	print("    Enemies:      %d" % _enemy_count)
	print("    Projectiles:  %d" % _projectile_count)
	print("    Loot drops:   %d" % _loot_count)
	print("    Dmg labels:   %d" % _label_count)
	print("    TOTAL:        %d" % (_player_count + _enemy_count + _projectile_count + _loot_count + _label_count))
	print("")
	print("  FPS Results:")
	print("    Avg:          %.1f" % avg)
	print("    Min:          %.1f" % min_fps)
	print("    Max:          %.1f" % max_fps)
	print("    Below 60:     %d / %d samples (%.0f%%)" % [below_60, _fps_samples.size(), float(below_60) / _fps_samples.size() * 100])
	print("")

	if avg >= 60:
		print("  VERDICT: PASS — averaging above 60 FPS under stress")
	elif avg >= 45:
		print("  VERDICT: MARGINAL — playable but needs optimization")
	else:
		print("  VERDICT: FAIL — needs significant optimization")

	print("=================================")
	get_tree().quit()


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
	visual.color = Color(0.35, 0.25, 0.2)
	body.add_child(visual)

	add_child(body)
