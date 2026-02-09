extends Control
## Main menu screen.

func _ready() -> void:
	GameManager.change_state(GameManager.GameState.MENU)
	$VBox/StartButton.grab_focus()


func _on_start_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/ui/lobby.tscn")


func _on_quit_pressed() -> void:
	get_tree().quit()
