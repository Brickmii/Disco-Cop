extends Control
## Game over / victory screen.

@onready var title_label: Label = $Title
@onready var subtitle_label: Label = $Subtitle

var _is_victory := false


func _ready() -> void:
	visible = false
	process_mode = Node.PROCESS_MODE_ALWAYS
	EventBus.game_over.connect(_show_game_over)
	EventBus.level_completed.connect(_show_victory)


func _show_game_over() -> void:
	_is_victory = false
	title_label.text = "GAME OVER"
	subtitle_label.text = "The disco died tonight..."
	visible = true
	get_tree().paused = true
	$VBox/ContinueButton.grab_focus()


func _show_victory() -> void:
	_is_victory = true
	title_label.text = "VICTORY!"
	subtitle_label.text = "The Disco King has fallen!"
	visible = true
	get_tree().paused = true
	$VBox/ContinueButton.grab_focus()


func _on_continue_pressed() -> void:
	get_tree().paused = false
	GameManager.reset_game()
	get_tree().change_scene_to_file("res://scenes/ui/main_menu.tscn")
