extends Node
## Maps input devices to players. Keyboard = P1, gamepads = P2-P4.

const MAX_PLAYERS := 4

# Device ID -1 = keyboard, 0+ = gamepad index
var device_to_player: Dictionary = {}  # device_id -> player_index
var player_to_device: Dictionary = {}  # player_index -> device_id

# Event-driven "just pressed" tracking for gamepad buttons
var _joy_pressed_events: Dictionary = {}  # "device_button" -> true
var _trigger_was_active: Dictionary = {}  # device_id -> bool


func _ready() -> void:
	# Keyboard is always player 0
	assign_device_to_player(-1, 0)
	# Also claim first gamepad for player 0 (prevents lobby creating player 2)
	device_to_player[0] = 0
	Input.joy_connection_changed.connect(_on_joy_connection_changed)


func _input(event: InputEvent) -> void:
	# Track button press events for just-pressed detection
	if event is InputEventJoypadButton and event.pressed:
		var key := "%d_%d" % [event.device, event.button_index]
		_joy_pressed_events[key] = true

	# Track trigger crossing the activation threshold
	if event is InputEventJoypadMotion and event.axis == JOY_AXIS_TRIGGER_RIGHT:
		var now_active: bool = event.axis_value > 0.2
		var was_active: bool = _trigger_was_active.get(event.device, false)
		if now_active and not was_active:
			_joy_pressed_events["%d_rt" % event.device] = true
		_trigger_was_active[event.device] = now_active


func _physics_process(_delta: float) -> void:
	# Clear just-pressed flags AFTER all nodes have had a chance to read them
	call_deferred("_clear_joy_events")


func _clear_joy_events() -> void:
	_joy_pressed_events.clear()


func assign_device_to_player(device_id: int, player_index: int) -> void:
	device_to_player[device_id] = player_index
	player_to_device[player_index] = device_id


func get_player_for_device(device_id: int) -> int:
	return device_to_player.get(device_id, -1)


func get_device_for_player(player_index: int) -> int:
	return player_to_device.get(player_index, -1)


func is_action_pressed(player_index: int, action: String) -> bool:
	var device_id: int = player_to_device.get(player_index, -1)
	if device_id == -1:
		# Keyboard player — also check first gamepad
		if Input.is_action_pressed(action):
			return true
		if Input.get_connected_joypads().size() > 0:
			return _is_gamepad_action_pressed(0, action)
		return false
	else:
		return _is_gamepad_action_pressed(device_id, action)


func is_action_just_pressed(player_index: int, action: String) -> bool:
	var device_id: int = player_to_device.get(player_index, -1)
	if device_id == -1:
		if Input.is_action_just_pressed(action):
			return true
		if Input.get_connected_joypads().size() > 0:
			return _is_gamepad_action_just_pressed(0, action)
		return false
	else:
		return _is_gamepad_action_just_pressed(device_id, action)


func get_axis(player_index: int, negative_action: String, positive_action: String) -> float:
	var device_id: int = player_to_device.get(player_index, -1)
	if device_id == -1:
		var kb_axis := Input.get_axis(negative_action, positive_action)
		if absf(kb_axis) > 0.1:
			return kb_axis
		# Fall through to first gamepad
		if Input.get_connected_joypads().size() > 0:
			var neg := 1.0 if _is_gamepad_action_pressed(0, negative_action) else 0.0
			var pos := 1.0 if _is_gamepad_action_pressed(0, positive_action) else 0.0
			var gp_axis := pos - neg
			if absf(gp_axis) > 0.1:
				return gp_axis
		return kb_axis
	else:
		var neg := 1.0 if _is_gamepad_action_pressed(device_id, negative_action) else 0.0
		var pos := 1.0 if _is_gamepad_action_pressed(device_id, positive_action) else 0.0
		return pos - neg


func _is_gamepad_action_pressed(device_id: int, action: String) -> bool:
	match action:
		"move_left":
			return Input.get_joy_axis(device_id, JOY_AXIS_LEFT_X) < -0.2
		"move_right":
			return Input.get_joy_axis(device_id, JOY_AXIS_LEFT_X) > 0.2
		"aim_up":
			return Input.get_joy_axis(device_id, JOY_AXIS_LEFT_Y) < -0.2
		"aim_down":
			return Input.get_joy_axis(device_id, JOY_AXIS_LEFT_Y) > 0.2
		"jump":
			return Input.is_joy_button_pressed(device_id, JOY_BUTTON_A)
		"shoot":
			return Input.get_joy_axis(device_id, JOY_AXIS_TRIGGER_RIGHT) > 0.2
		"reload":
			return Input.is_joy_button_pressed(device_id, JOY_BUTTON_X)
		"interact":
			return Input.is_joy_button_pressed(device_id, JOY_BUTTON_B)
		"swap_weapon":
			return Input.is_joy_button_pressed(device_id, JOY_BUTTON_Y)
		"pause":
			return Input.is_joy_button_pressed(device_id, JOY_BUTTON_START)
	return false


func _is_gamepad_action_just_pressed(device_id: int, action: String) -> bool:
	var key := ""
	match action:
		"jump":
			key = "%d_%d" % [device_id, JOY_BUTTON_A]
		"shoot":
			key = "%d_rt" % device_id
		"reload":
			key = "%d_%d" % [device_id, JOY_BUTTON_X]
		"interact":
			key = "%d_%d" % [device_id, JOY_BUTTON_B]
		"swap_weapon":
			key = "%d_%d" % [device_id, JOY_BUTTON_Y]
		"pause":
			key = "%d_%d" % [device_id, JOY_BUTTON_START]
		"ui_join":
			key = "%d_%d" % [device_id, JOY_BUTTON_START]
	if key != "" and _joy_pressed_events.has(key):
		_joy_pressed_events.erase(key)
		return true
	return false


func try_join_player(device_id: int) -> int:
	## Attempts to assign a device to the next available player slot.
	## Returns player_index on success, -1 if full or already assigned.
	if device_id in device_to_player:
		return -1
	for i in MAX_PLAYERS:
		if i not in player_to_device:
			assign_device_to_player(device_id, i)
			GameManager.register_player(i, device_id)
			return i
	return -1


func _on_joy_connection_changed(device_id: int, connected: bool) -> void:
	if not connected and device_id in device_to_player:
		var player_index: int = device_to_player[device_id]
		device_to_player.erase(device_id)
		player_to_device.erase(player_index)
