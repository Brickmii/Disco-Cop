extends Node2D
## Side-scrolling test level — camera tracks the player horizontally.

@onready var camera: Camera2D = $Camera2D
@onready var player: CharacterBody2D = $Player

const KILL_Y := 900.0


func _physics_process(_delta: float) -> void:
	if player and camera:
		camera.position.x = player.position.x
		# Kill zone — fall death
		if player.position.y > KILL_Y:
			if player.has_method("take_damage"):
				player.take_damage(9999.0, player.global_position)
