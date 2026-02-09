extends Node2D
class_name WeaponHolder
## Manages weapon firing, reloading, and ammo for a player.

signal ammo_changed(current: int, max_ammo: int)
signal reload_started(duration: float)
signal reload_finished()
signal weapon_changed(weapon: WeaponData)

@export var player_index := 0

var current_weapon: WeaponData = null
var weapons: Array[WeaponData] = []  # inventory slots (max 2)
var current_slot := 0
var current_ammo := 0
var is_reloading := false

var _fire_timer := 0.0
var _reload_timer := 0.0
var _burst_remaining := 0
var _burst_timer := 0.0

const MAX_WEAPON_SLOTS := 2
const PROJECTILE_POOL_NAME := "projectiles"

var _projectile_scene: PackedScene = null
var _player: CharacterBody2D = null


func _ready() -> void:
	_projectile_scene = preload("res://scenes/weapons/projectile.tscn")
	_player = get_parent() as CharacterBody2D

	# Pre-fill pool
	if ObjectPool.get_pool_size(PROJECTILE_POOL_NAME) == 0:
		ObjectPool.preload_pool(PROJECTILE_POOL_NAME, _projectile_scene, 30)

	# Give a starter weapon
	var starter := WeaponGenerator.generate(1, Rarity.Tier.COMMON, WeaponData.WeaponType.PISTOL)
	equip_weapon(starter)


func _process(delta: float) -> void:
	if current_weapon == null:
		return

	# Fire cooldown
	if _fire_timer > 0:
		_fire_timer -= delta

	# Reload timer
	if is_reloading:
		_reload_timer -= delta
		if _reload_timer <= 0:
			_finish_reload()

	# Burst fire
	if _burst_remaining > 0:
		_burst_timer -= delta
		if _burst_timer <= 0:
			_fire_single_projectile()
			_burst_remaining -= 1
			_burst_timer = current_weapon.burst_delay

	# Input
	if InputManager.is_action_pressed(player_index, "shoot"):
		try_fire()
	if InputManager.is_action_just_pressed(player_index, "reload"):
		try_reload()
	if InputManager.is_action_just_pressed(player_index, "swap_weapon"):
		swap_weapon()


func equip_weapon(weapon: WeaponData) -> void:
	if weapons.size() < MAX_WEAPON_SLOTS:
		weapons.append(weapon)
		current_slot = weapons.size() - 1
	else:
		weapons[current_slot] = weapon

	current_weapon = weapon
	current_ammo = weapon.magazine_size
	is_reloading = false
	_fire_timer = 0.0
	ammo_changed.emit(current_ammo, weapon.magazine_size)
	weapon_changed.emit(weapon)
	EventBus.weapon_swapped.emit(player_index, weapon)


func swap_weapon() -> void:
	if weapons.size() <= 1:
		return
	current_slot = (current_slot + 1) % weapons.size()
	current_weapon = weapons[current_slot]
	current_ammo = current_weapon.magazine_size  # Simplified: full mag on swap
	is_reloading = false
	ammo_changed.emit(current_ammo, current_weapon.magazine_size)
	weapon_changed.emit(current_weapon)
	EventBus.weapon_swapped.emit(player_index, current_weapon)


func try_fire() -> void:
	if current_weapon == null or is_reloading or _fire_timer > 0 or _burst_remaining > 0:
		return
	if current_ammo <= 0:
		try_reload()
		return

	# Fire rate: convert shots/sec to cooldown
	_fire_timer = 1.0 / current_weapon.fire_rate

	if current_weapon.burst_count > 1:
		_burst_remaining = current_weapon.burst_count
		_burst_timer = 0.0  # Fire first shot immediately
	else:
		_fire_single_projectile()

	EventBus.weapon_fired.emit(player_index, current_weapon)

	# Screen shake based on weapon type
	var shake_intensity := 1.0
	match current_weapon.weapon_type:
		WeaponData.WeaponType.SHOTGUN: shake_intensity = 4.0
		WeaponData.WeaponType.SNIPER: shake_intensity = 3.0
		WeaponData.WeaponType.ROCKET_LAUNCHER: shake_intensity = 5.0
		WeaponData.WeaponType.ASSAULT_RIFLE: shake_intensity = 1.5
	EventBus.camera_shake_requested.emit(shake_intensity, 0.1)


func _fire_single_projectile() -> void:
	if current_ammo <= 0:
		return

	current_ammo -= 1
	ammo_changed.emit(current_ammo, current_weapon.magazine_size)

	var aim_angle: float = _player.get_aim_angle() if _player else 0.0
	var aim_vector := Vector2.from_angle(aim_angle)

	# Spawn projectiles (multiple for shotgun)
	for i in current_weapon.projectile_count:
		var proj: Projectile = ObjectPool.get_instance(PROJECTILE_POOL_NAME) as Projectile
		if proj == null:
			continue

		# Apply accuracy spread
		var spread := (1.0 - current_weapon.accuracy) * PI * 0.25
		var angle_offset := randf_range(-spread, spread)
		if current_weapon.projectile_count > 1:
			# Shotgun spread: fan pattern
			var fan_range := (1.0 - current_weapon.accuracy) * PI * 0.3
			var fan_offset := lerpf(-fan_range, fan_range, float(i) / maxf(current_weapon.projectile_count - 1, 1))
			angle_offset = fan_offset + randf_range(-spread * 0.3, spread * 0.3)

		var final_dir := aim_vector.rotated(angle_offset)

		# Crit roll
		var is_crit := randf() < current_weapon.crit_chance

		var spawn_pos := global_position + aim_vector * 20.0
		proj.activate(spawn_pos, final_dir, current_weapon, player_index, is_crit)

	if current_ammo <= 0:
		try_reload()


func try_reload() -> void:
	if is_reloading or current_weapon == null:
		return
	if current_ammo >= current_weapon.magazine_size:
		return

	is_reloading = true
	_reload_timer = current_weapon.reload_time
	reload_started.emit(current_weapon.reload_time)
	EventBus.weapon_reloading.emit(player_index, current_weapon.reload_time)


func _finish_reload() -> void:
	is_reloading = false
	current_ammo = current_weapon.magazine_size
	ammo_changed.emit(current_ammo, current_weapon.magazine_size)
	reload_finished.emit()
	EventBus.weapon_reload_complete.emit(player_index)
