extends Node
class_name ShieldComponent
## Reusable shield component. Absorbs damage before health, recharges after delay.

signal shield_changed(current: float, maximum: float)
signal shield_broken()
signal shield_full()

var shield_data: ShieldData = null
var current_shield: float = 0.0
var _recharge_timer: float = 0.0
var _is_recharging := false


func equip_shield(data: ShieldData) -> void:
	shield_data = data
	current_shield = data.capacity
	_recharge_timer = 0.0
	_is_recharging = false
	shield_changed.emit(current_shield, data.capacity)


func _process(delta: float) -> void:
	if shield_data == null:
		return

	if current_shield < shield_data.capacity:
		if _recharge_timer > 0:
			_recharge_timer -= delta
			if _recharge_timer <= 0:
				_is_recharging = true
		if _is_recharging:
			current_shield = minf(
				current_shield + shield_data.recharge_rate * delta,
				shield_data.capacity
			)
			shield_changed.emit(current_shield, shield_data.capacity)
			if current_shield >= shield_data.capacity:
				_is_recharging = false
				shield_full.emit()


func absorb_damage(amount: float, element: WeaponData.Element = WeaponData.Element.NONE) -> float:
	## Absorbs damage, returns remaining damage that passes through to health.
	if shield_data == null or current_shield <= 0:
		return amount

	# Apply element resistance
	var resistance := shield_data.get_resistance(element)
	var reduced_amount := amount * (1.0 - resistance)

	# Apply flat damage reduction
	if shield_data.damage_reduction > 0 and current_shield > 0:
		reduced_amount *= (1.0 - shield_data.damage_reduction)

	# Shield absorbs damage
	var absorbed := minf(reduced_amount, current_shield)
	current_shield -= absorbed
	var overflow := reduced_amount - absorbed

	# Reset recharge
	_recharge_timer = shield_data.recharge_delay
	_is_recharging = false
	shield_changed.emit(current_shield, shield_data.capacity)

	if current_shield <= 0:
		current_shield = 0.0
		shield_broken.emit()
		# Nova on break
		if shield_data.nova_on_break:
			_trigger_nova()

	return overflow


func _trigger_nova() -> void:
	EventBus.shield_broken.emit(get_parent().global_position if get_parent() else Vector2.ZERO)


func get_shield_percent() -> float:
	if shield_data == null or shield_data.capacity <= 0:
		return 0.0
	return current_shield / shield_data.capacity


func has_shield() -> bool:
	return shield_data != null and current_shield > 0
