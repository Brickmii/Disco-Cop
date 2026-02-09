extends Node
## Object pool for projectiles and effects to avoid allocation hitches on Pi.

var _pools: Dictionary = {}  # String -> Array[Node]
var _scenes: Dictionary = {}  # String -> PackedScene


func preload_pool(pool_name: String, scene: PackedScene, count: int) -> void:
	_scenes[pool_name] = scene
	if pool_name not in _pools:
		_pools[pool_name] = []
	for i in count:
		var instance: Node = scene.instantiate()
		instance.set_meta("pool_name", pool_name)
		instance.process_mode = Node.PROCESS_MODE_DISABLED
		instance.visible = false
		add_child(instance)
		_pools[pool_name].append(instance)


func get_instance(pool_name: String) -> Node:
	if pool_name not in _pools:
		push_warning("Pool '%s' does not exist" % pool_name)
		return null

	var pool: Array = _pools[pool_name]
	for instance in pool:
		if instance.process_mode == Node.PROCESS_MODE_DISABLED:
			instance.process_mode = Node.PROCESS_MODE_INHERIT
			instance.visible = true
			return instance

	# Pool exhausted — grow by 1
	if pool_name in _scenes:
		var scene: PackedScene = _scenes[pool_name]
		var instance: Node = scene.instantiate()
		instance.set_meta("pool_name", pool_name)
		add_child(instance)
		pool.append(instance)
		return instance

	push_warning("Pool '%s' exhausted and has no scene to grow" % pool_name)
	return null


func release_instance(instance: Node) -> void:
	instance.process_mode = Node.PROCESS_MODE_DISABLED
	instance.visible = false


func get_pool_size(pool_name: String) -> int:
	if pool_name in _pools:
		return _pools[pool_name].size()
	return 0


func get_active_count(pool_name: String) -> int:
	if pool_name not in _pools:
		return 0
	var count := 0
	for instance in _pools[pool_name]:
		if instance.process_mode != Node.PROCESS_MODE_DISABLED:
			count += 1
	return count
