extends Node2D
## Side-scrolling test level — camera tracks the player horizontally.

@onready var camera: Camera2D = $Camera2D
@onready var player: CharacterBody2D = $Player


func _physics_process(_delta: float) -> void:
	if player and camera:
		camera.position.x = player.position.x
