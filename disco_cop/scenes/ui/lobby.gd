extends Control
## Lobby screen — "Press button to join" with 4 player slots.

const PLAYER_COLORS: Array[Color] = [
	Color(0.2, 0.8, 0.3),   # P1 Green
	Color(0.3, 0.5, 1.0),   # P2 Blue
	Color(1.0, 0.4, 0.2),   # P3 Orange
	Color(0.8, 0.2, 0.8),   # P4 Purple
]

var _slot_labels: Array[Label] = []
var _joined: Array[bool] = [false, false, false, false]

@onready var start_label: Label = $StartLabel


func _ready() -> void:
	# Find slot labels from scene tree
	var slots_container := $Slots
	for i in 4:
		var slot_node: Label = slots_container.get_node("Slot%d" % i) as Label
		_slot_labels.append(slot_node)

	# Register keyboard as P1 automatically
	GameManager.register_player(0, -1)
	_joined[0] = true

	for i in 4:
		_update_slot(i)

	EventBus.player_joined.connect(_on_player_joined)
	_update_start_label()


func _input(event: InputEvent) -> void:
	# Gamepad join
	if event is InputEventJoypadButton and event.pressed:
		var device_id: int = event.device
		var result := InputManager.try_join_player(device_id)
		if result >= 0:
			_joined[result] = true
			_update_slot(result)
			_update_start_label()

	# Start game
	if event.is_action_pressed("ui_join") or event.is_action_pressed("jump"):
		if GameManager.get_active_player_count() >= 1:
			_start_game()


func _update_slot(index: int) -> void:
	if index >= _slot_labels.size():
		return
	if _joined[index]:
		_slot_labels[index].text = "P%d - READY" % (index + 1)
		_slot_labels[index].modulate = PLAYER_COLORS[index]
	else:
		_slot_labels[index].text = "P%d - Press to join" % (index + 1)
		_slot_labels[index].modulate = Color(0.5, 0.5, 0.5)


func _update_start_label() -> void:
	var count := GameManager.get_active_player_count()
	if start_label:
		start_label.text = "%d Player(s) - Press ENTER/START to begin" % count


func _on_player_joined(player_index: int, _device_id: int) -> void:
	if player_index < 4:
		_joined[player_index] = true
		_update_slot(player_index)
		_update_start_label()


func _start_game() -> void:
	get_tree().change_scene_to_file("res://scenes/levels/level_01.tscn")
