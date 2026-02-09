extends Node
## Spawns pooled VFX effects. Autoload: VFXSpawner

const VFX_POOL_NAME := "vfx"

var _vfx_scene: PackedScene = null


func _ready() -> void:
	_vfx_scene = preload("res://scenes/effects/vfx.tscn")
	ObjectPool.preload_pool(VFX_POOL_NAME, _vfx_scene, 10)

	EventBus.shield_broken.connect(_on_shield_broken)
	EventBus.enemy_died.connect(_on_enemy_died)


func spawn(effect_name: String, pos: Vector2, effect_scale: float = 1.0, angle: float = 0.0) -> void:
	var vfx: VFX = ObjectPool.get_instance(VFX_POOL_NAME) as VFX
	if vfx:
		vfx.play_effect(effect_name, pos, effect_scale, angle)


func _on_shield_broken(pos: Vector2) -> void:
	spawn("shield_break", pos, 1.5)


func _on_enemy_died(_enemy_node: Node, pos: Vector2) -> void:
	spawn("explosion", pos)
