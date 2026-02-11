extends Control
## Credits screen shown after beating the final level.

const SCROLL_SPEED := 40.0

@onready var stats_label: Label = $StatsLabel
@onready var credits_label: Label = $CreditsLabel

var _scroll_offset := 0.0
var _accept_cooldown := 1.5
var _done := false


func _ready() -> void:
	var mode_name: String = GameManager.MODE_NAMES[GameManager.play_mode]
	var stats := GameManager.run_stats

	stats_label.text = "CONGRATULATIONS!\n\nYou beat Disco Cop on %s!\n\nEnemies defeated: %d\nBosses defeated: %d\nLoot collected: %d" % [
		mode_name,
		stats["enemies_killed"],
		stats["bosses_defeated"],
		stats["loot_collected"],
	]

	# Check if a new mode was unlocked
	var unlock_text := ""
	match GameManager.play_mode:
		GameManager.PlayMode.NORMAL:
			unlock_text = "\n\nDisco Fever mode unlocked!"
		GameManager.PlayMode.DISCO_FEVER:
			unlock_text = "\n\nSaturday Night Slaughter mode unlocked!"
		GameManager.PlayMode.SATURDAY_NIGHT_SLAUGHTER:
			unlock_text = "\n\nYou conquered every mode. True Disco Cop."
	stats_label.text += unlock_text

	credits_label.text = "\n\n\n\nDISCO COP\n\nA game by Brickmii\n\nBuilt with Godot Engine\n\n\n\nThank you for playing!"

	# Position credits below stats for scrolling
	credits_label.position.y = 720.0


func _process(delta: float) -> void:
	if _accept_cooldown > 0:
		_accept_cooldown -= delta

	# Scroll credits up
	if not _done:
		_scroll_offset += SCROLL_SPEED * delta
		credits_label.position.y = 720.0 - _scroll_offset
		# Stop scrolling when credits are centered
		if credits_label.position.y <= 300.0:
			credits_label.position.y = 300.0
			_done = true

	if _accept_cooldown > 0:
		return

	# Accept input to return to menu
	if Input.is_key_pressed(KEY_ENTER) or Input.is_key_pressed(KEY_SPACE) or Input.is_key_pressed(KEY_KP_ENTER):
		_return_to_menu()
		return
	for i in Input.get_connected_joypads().size():
		if Input.is_joy_button_pressed(i, JOY_BUTTON_A) or Input.is_joy_button_pressed(i, JOY_BUTTON_START):
			_return_to_menu()
			return


func _return_to_menu() -> void:
	GameManager.reset_game()
	Transition.change_scene("res://scenes/ui/main_menu.tscn")
