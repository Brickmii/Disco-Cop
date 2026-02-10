extends Node
## Manages audio playback for SFX and music, wired to EventBus signals.

const MAX_SFX_PLAYERS := 16

var _sfx_players: Array[AudioStreamPlayer] = []
var _music_player: AudioStreamPlayer = null
var _sfx_index := 0

# Preloaded SFX
var _shoot_sfx: Dictionary = {}
var _impact_hit: AudioStream
var _impact_crit: AudioStream
var _explosion: AudioStream
var _enemy_death: AudioStream
var _player_hurt: AudioStream
var _player_death: AudioStream
var _shield_break: AudioStream
var _shield_recharge: AudioStream
var _loot_pickup: AudioStream
var _weapon_swap: AudioStream
var _menu_select: AudioStream

# Music
var _menu_theme: AudioStream
var _level_theme: AudioStream
var _boss_theme: AudioStream

# Player health tracking (for hurt sound)
var _player_health: Dictionary = {}


func _ready() -> void:
	# Create SFX pool
	for i in MAX_SFX_PLAYERS:
		var player := AudioStreamPlayer.new()
		player.bus = "SFX" if AudioServer.get_bus_index("SFX") >= 0 else "Master"
		add_child(player)
		_sfx_players.append(player)

	# Create music player
	_music_player = AudioStreamPlayer.new()
	_music_player.bus = "Music" if AudioServer.get_bus_index("Music") >= 0 else "Master"
	_music_player.finished.connect(_on_music_finished)
	add_child(_music_player)

	_load_audio_assets()
	_connect_signals()


func _load_audio_assets() -> void:
	_shoot_sfx = {
		WeaponData.WeaponType.PISTOL: _load("res://assets/audio/sfx/shoot_pistol.wav"),
		WeaponData.WeaponType.SMG: _load("res://assets/audio/sfx/shoot_smg.wav"),
		WeaponData.WeaponType.SHOTGUN: _load("res://assets/audio/sfx/shoot_shotgun.wav"),
		WeaponData.WeaponType.ASSAULT_RIFLE: _load("res://assets/audio/sfx/shoot_rifle.wav"),
		WeaponData.WeaponType.SNIPER: _load("res://assets/audio/sfx/shoot_sniper.wav"),
		WeaponData.WeaponType.ROCKET_LAUNCHER: _load("res://assets/audio/sfx/shoot_launcher.wav"),
	}
	_impact_hit = _load("res://assets/audio/sfx/impact_hit.wav")
	_impact_crit = _load("res://assets/audio/sfx/impact_crit.wav")
	_explosion = _load("res://assets/audio/sfx/explosion.wav")
	_enemy_death = _load("res://assets/audio/sfx/enemy_death.wav")
	_player_hurt = _load("res://assets/audio/sfx/player_hurt.wav")
	_player_death = _load("res://assets/audio/sfx/player_death.wav")
	_shield_break = _load("res://assets/audio/sfx/shield_break.wav")
	_shield_recharge = _load("res://assets/audio/sfx/shield_recharge.wav")
	_loot_pickup = _load("res://assets/audio/sfx/loot_pickup.wav")
	_weapon_swap = _load("res://assets/audio/sfx/weapon_swap.wav")
	_menu_select = _load("res://assets/audio/sfx/menu_select.wav")
	_menu_theme = _load("res://assets/audio/music/menu_theme.wav")
	_level_theme = _load("res://assets/audio/music/level_theme.wav")
	_boss_theme = _load("res://assets/audio/music/boss_theme.wav")


func _load(path: String) -> AudioStream:
	if ResourceLoader.exists(path):
		return load(path)
	return null


func _connect_signals() -> void:
	EventBus.weapon_fired.connect(_on_weapon_fired)
	EventBus.damage_dealt.connect(_on_damage_dealt)
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.player_health_changed.connect(_on_player_health_changed)
	EventBus.player_died.connect(_on_player_died)
	EventBus.shield_broken.connect(_on_shield_broken)
	EventBus.shield_recharged.connect(_on_shield_recharged)
	EventBus.loot_picked_up.connect(_on_loot_picked_up)
	EventBus.weapon_swapped.connect(_on_weapon_swapped)
	EventBus.boss_spawned.connect(_on_boss_spawned)
	EventBus.boss_defeated.connect(_on_boss_defeated)
	EventBus.level_started.connect(_on_level_started)


# --- Signal handlers ---

func _on_weapon_fired(_player_index: int, weapon_data: Resource) -> void:
	if weapon_data is WeaponData:
		var sfx: AudioStream = _shoot_sfx.get(weapon_data.weapon_type)
		play_sfx(sfx, -6.0)


func _on_damage_dealt(_position: Vector2, _amount: float, is_crit: bool, element: int) -> void:
	if element == WeaponData.Element.EXPLOSIVE:
		play_sfx(_explosion, -3.0)
	elif is_crit:
		play_sfx(_impact_crit, -3.0)
	else:
		play_sfx(_impact_hit, -6.0)


func _on_enemy_died(_enemy_node: Node, _position: Vector2) -> void:
	play_sfx(_enemy_death, -3.0)


func _on_player_health_changed(player_index: int, current: float, max_hp: float) -> void:
	var prev: float = _player_health.get(player_index, max_hp)
	if current < prev:
		play_sfx(_player_hurt, -3.0)
	_player_health[player_index] = current


func _on_player_died(_player_index: int) -> void:
	play_sfx(_player_death)


func _on_shield_broken(_position: Vector2) -> void:
	play_sfx(_shield_break)


func _on_shield_recharged(_player_index: int) -> void:
	play_sfx(_shield_recharge, -6.0)


func _on_loot_picked_up(_player_index: int, _item: Resource) -> void:
	play_sfx(_loot_pickup)


func _on_weapon_swapped(_player_index: int, _weapon_data: Resource) -> void:
	play_sfx(_weapon_swap, -3.0)


func _on_boss_spawned(_boss_node: Node) -> void:
	play_music(_boss_theme, -8.0)


func _on_boss_defeated(_boss_node: Node) -> void:
	play_music(_level_theme, -10.0)


func _on_level_started() -> void:
	play_music(_level_theme, -10.0)


func _on_music_finished() -> void:
	_music_player.play()


# --- Public API ---

func play_sfx(stream: AudioStream, volume_db: float = 0.0) -> void:
	if stream == null:
		return
	var player := _sfx_players[_sfx_index]
	player.stream = stream
	player.volume_db = volume_db
	player.play()
	_sfx_index = (_sfx_index + 1) % MAX_SFX_PLAYERS


func play_music(stream: AudioStream, volume_db: float = -10.0) -> void:
	if stream == null:
		return
	_music_player.stream = stream
	_music_player.volume_db = volume_db
	_music_player.play()


func stop_music() -> void:
	_music_player.stop()


func set_sfx_volume(volume_db: float) -> void:
	for player in _sfx_players:
		player.volume_db = volume_db


func set_music_volume(volume_db: float) -> void:
	_music_player.volume_db = volume_db
