extends Control
## Game over / victory screen.

@onready var title_label: Label = $Title
@onready var subtitle_label: Label = $Subtitle

var _is_victory := false
var _is_showing := false
var _accept_cooldown := 0.0


func _ready() -> void:
	visible = false
	EventBus.game_over.connect(_show_game_over)
	EventBus.level_completed.connect(_show_victory)


func _process(delta: float) -> void:
	if not _is_showing:
		return

	# Brief cooldown so held buttons don't instantly dismiss
	if _accept_cooldown > 0:
		_accept_cooldown -= delta
		return

	# Keyboard
	if Input.is_key_pressed(KEY_ENTER) or Input.is_key_pressed(KEY_SPACE) or Input.is_key_pressed(KEY_KP_ENTER):
		_on_continue_pressed()
		return
	# Gamepad: A or Start
	for i in Input.get_connected_joypads().size():
		if Input.is_joy_button_pressed(i, JOY_BUTTON_A) or Input.is_joy_button_pressed(i, JOY_BUTTON_START):
			_on_continue_pressed()
			return


func _show_game_over() -> void:
	if _is_showing:
		return
	_is_showing = true
	_is_victory = false
	_accept_cooldown = 0.5
	title_label.text = "GAME OVER"
	subtitle_label.text = "The disco died tonight...\n\nPress ENTER to continue"
	visible = true


func _show_victory() -> void:
	if _is_showing:
		return
	_is_showing = true
	_is_victory = true
	_accept_cooldown = 0.5
	title_label.text = "VICTORY!"
	subtitle_label.text = "The Disco King has fallen!\n\nPress ENTER to continue"
	visible = true


func _on_continue_pressed() -> void:
	if not _is_showing:
		return
	_is_showing = false
	visible = false
	if _is_victory and GameManager.current_level == "tutorial":
		# Tutorial complete — proceed to Level 1
		get_tree().call_deferred("change_scene_to_file", "res://scenes/levels/level_01.tscn")
	else:
		GameManager.reset_game()
		get_tree().call_deferred("change_scene_to_file", "res://scenes/ui/main_menu.tscn")
