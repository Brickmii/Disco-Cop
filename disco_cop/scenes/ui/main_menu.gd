extends Control
## Main menu screen.

func _ready() -> void:
	GameManager.change_state(GameManager.GameState.MENU)
	$VBox/StartButton.grab_focus()


func _input(event: InputEvent) -> void:
	# Accept Start or A button on gamepad to begin
	if event is InputEventJoypadButton and event.pressed:
		if event.button_index == JOY_BUTTON_A or event.button_index == JOY_BUTTON_START:
			_on_start_pressed()


func _on_start_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/ui/lobby.tscn")


func _on_quit_pressed() -> void:
	get_tree().quit()
