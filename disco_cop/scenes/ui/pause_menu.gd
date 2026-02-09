extends Control
## Pause menu overlay.

func _ready() -> void:
	visible = false
	process_mode = Node.PROCESS_MODE_ALWAYS


func _input(event: InputEvent) -> void:
	if event.is_action_pressed("pause"):
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
	get_tree().paused = false
	GameManager.reset_game()
	get_tree().change_scene_to_file("res://scenes/ui/main_menu.tscn")
