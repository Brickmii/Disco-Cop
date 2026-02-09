extends Node
## Manages audio playback for SFX and music.

const MAX_SFX_PLAYERS := 16

var _sfx_players: Array[AudioStreamPlayer] = []
var _music_player: AudioStreamPlayer = null
var _sfx_index := 0


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
	add_child(_music_player)


func play_sfx(stream: AudioStream, volume_db: float = 0.0) -> void:
	if stream == null:
		return
	# Round-robin through SFX players
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
