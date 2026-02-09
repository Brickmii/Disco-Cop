extends Node
## Global event bus for decoupled communication between systems.

# Player events
signal player_spawned(player_index: int, player_node: Node)
signal player_died(player_index: int)
signal player_respawned(player_index: int)
signal player_health_changed(player_index: int, current: float, max_hp: float)
signal player_shield_changed(player_index: int, current: float, max_shield: float)

# Weapon events
signal weapon_fired(player_index: int, weapon_data: Resource)
signal weapon_reloading(player_index: int, duration: float)
signal weapon_reload_complete(player_index: int)
signal weapon_swapped(player_index: int, weapon_data: Resource)
signal weapon_picked_up(player_index: int, weapon_data: Resource)

# Enemy events
signal enemy_spawned(enemy_node: Node)
signal enemy_died(enemy_node: Node, position: Vector2)
signal enemy_hit(enemy_node: Node, damage: float, element: int)

# Loot events
signal loot_dropped(loot_node: Node, position: Vector2)
signal loot_picked_up(player_index: int, item: Resource)

# Boss events
signal boss_spawned(boss_node: Node)
signal boss_phase_changed(boss_node: Node, phase: int)
signal boss_defeated(boss_node: Node)

# Game flow events
signal level_started()
signal level_completed()
signal scroll_lock_entered(zone: Node)
signal scroll_lock_cleared(zone: Node)
signal game_over()
signal game_paused()
signal game_resumed()

# Combat events
signal damage_dealt(position: Vector2, amount: float, is_crit: bool, element: int)
signal shield_broken(position: Vector2)
signal shield_recharged(player_index: int)

# Camera events
signal camera_shake_requested(intensity: float, duration: float)

# Multiplayer events
signal player_joined(player_index: int, device_id: int)
signal player_left(player_index: int)
