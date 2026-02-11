extends Control
## Pause menu overlay.

func _ready() -> void:
	visible = false
	process_mode = Node.PROCESS_MODE_ALWAYS


func _process(_delta: float) -> void:
	# Poll Input — _input() doesn't fire while tree is paused
	if Input.is_action_just_pressed("pause"):
		toggle_pause()


func toggle_pause() -> void:
	visible = not visible
	get_tree().paused = visible
	if visible:
		$VBox/ResumeButton.grab_focus()
		EventBus.game_paused.emit()
	else:
		EventBus.game_resumed.emit()


func _on_resume_pressed() -> void:
	toggle_pause()


func _on_quit_pressed() -> void:
	GameManager.reset_game()
	Transition.change_scene("res://scenes/ui/main_menu.tscn")
