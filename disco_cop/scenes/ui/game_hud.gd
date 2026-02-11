extends CanvasLayer
## Game HUD that shows per-player HUDs in corners and boss health bar.

var _player_hud_scene: PackedScene = preload("res://scenes/player/player_hud.tscn")
var _player_huds: Array[PlayerHUD] = []

@onready var boss_health_bar: ProgressBar = $BossHealthBar
@onready var boss_name_label: Label = $BossNameLabel

# HUD corner positions (for 1-4 players)
const HUD_POSITIONS := [
	Vector2(10, 10),       # Top-left (P1)
	Vector2(1070, 10),     # Top-right (P2)
	Vector2(10, 590),      # Bottom-left (P3)
	Vector2(1070, 590),    # Bottom-right (P4)
]


var _toast_container: VBoxContainer


func _ready() -> void:
	EventBus.player_spawned.connect(_on_player_spawned)
	EventBus.boss_spawned.connect(_on_boss_spawned)
	EventBus.boss_defeated.connect(_on_boss_defeated)
	EventBus.boss_phase_changed.connect(_on_boss_phase_changed)
	EventBus.damage_dealt.connect(_on_damage_dealt)
	EventBus.weapon_picked_up.connect(_on_weapon_picked_up)

	_toast_container = VBoxContainer.new()
	_toast_container.position = Vector2(440, 620)
	_toast_container.size = Vector2(400, 100)
	_toast_container.alignment = BoxContainer.ALIGNMENT_END
	add_child(_toast_container)

	set_process(false)  # Only process when boss is active
	if boss_health_bar:
		boss_health_bar.visible = false
	if boss_name_label:
		boss_name_label.visible = false


func _on_player_spawned(player_index: int, _player_node: Node) -> void:
	if player_index >= HUD_POSITIONS.size():
		return

	var hud: PlayerHUD = _player_hud_scene.instantiate() as PlayerHUD
	hud.player_index = player_index
	hud.position = HUD_POSITIONS[player_index]
	add_child(hud)

	while _player_huds.size() <= player_index:
		_player_huds.append(null)
	_player_huds[player_index] = hud


func _on_boss_spawned(boss_node: Node) -> void:
	if boss_health_bar:
		boss_health_bar.visible = true
		boss_health_bar.max_value = 100
		boss_health_bar.value = 100
	if boss_name_label and boss_node is BossBase:
		boss_name_label.visible = true
		boss_name_label.text = boss_node.boss_name

	# Update boss health bar every frame
	if boss_node is BossBase:
		set_process(true)
		set_meta("boss_ref", boss_node)


func _process(_delta: float) -> void:
	if not has_meta("boss_ref"):
		set_process(false)
		return
	var boss_variant: Variant = get_meta("boss_ref")
	if boss_variant is BossBase and is_instance_valid(boss_variant) and boss_health_bar:
		var boss: BossBase = boss_variant as BossBase
		boss_health_bar.value = boss.get_health_percent() * 100.0
	else:
		set_process(false)


func _on_boss_defeated(_boss_node: Node) -> void:
	if boss_health_bar:
		boss_health_bar.visible = false
	if boss_name_label:
		boss_name_label.visible = false
	set_process(false)


func _on_boss_phase_changed(boss_node: Node, phase: int) -> void:
	if boss_name_label and boss_node is BossBase:
		boss_name_label.text = "%s - Phase %d" % [(boss_node as BossBase).boss_name, phase]


func _on_damage_dealt(pos: Vector2, amount: float, is_crit: bool, element: int) -> void:
	_spawn_damage_number(pos, amount, is_crit, element)


func _spawn_damage_number(pos: Vector2, amount: float, is_crit: bool, element: int) -> void:
	var label := Label.new()
	label.text = str(roundi(amount))
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	# Color by element
	var color := Color.WHITE
	match element:
		WeaponData.Element.FIRE: color = Color.ORANGE_RED
		WeaponData.Element.ICE: color = Color.LIGHT_BLUE
		WeaponData.Element.ELECTRIC: color = Color.YELLOW
		WeaponData.Element.EXPLOSIVE: color = Color.DARK_RED

	if is_crit:
		label.text += "!"
		color = Color.GOLD
		label.add_theme_font_size_override("font_size", 24)
	else:
		label.add_theme_font_size_override("font_size", 16)

	label.modulate = color
	label.z_index = 100

	# Convert world pos to screen pos (approximate)
	label.position = pos - Vector2(20, 30)
	get_parent().add_child(label)

	# Float up and fade
	var tween := label.create_tween()
	tween.set_parallel(true)
	tween.tween_property(label, "position:y", label.position.y - 40, 0.8)
	tween.tween_property(label, "modulate:a", 0.0, 0.8).set_delay(0.3)
	tween.chain().tween_callback(label.queue_free)


func _on_weapon_picked_up(_player_index: int, weapon_data: Resource) -> void:
	if not weapon_data is WeaponData:
		return
	var wd: WeaponData = weapon_data as WeaponData
	var toast := Label.new()
	toast.text = wd.get_display_name()
	toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	toast.modulate = wd.get_rarity_color()
	toast.add_theme_font_size_override("font_size", 18)
	_toast_container.add_child(toast)

	var tw := toast.create_tween()
	tw.tween_property(toast, "modulate:a", 0.0, 0.5).set_delay(1.5)
	tw.tween_callback(toast.queue_free)
