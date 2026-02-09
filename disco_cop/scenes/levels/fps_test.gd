extends Node
## Temporary FPS measurement script. Prints FPS every second, quits after 10s.

var _elapsed := 0.0
var _frame_count := 0
var _fps_samples: Array[float] = []
const TEST_DURATION := 10.0


func _process(delta: float) -> void:
	_elapsed += delta
	_frame_count += 1

	if fmod(_elapsed, 1.0) < delta:
		var fps := Performance.get_monitor(Performance.TIME_FPS)
		var draw_calls := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
		var objects := Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)
		var mem := Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0
		_fps_samples.append(fps)
		print("FPS: %.1f | Draw calls: %d | Objects: %d | Static mem: %.1f MB | Time: %.0fs" % [fps, draw_calls, objects, mem, _elapsed])

	if _elapsed >= TEST_DURATION:
		_print_summary()
		get_tree().quit()


func _print_summary() -> void:
	if _fps_samples.is_empty():
		print("No FPS samples collected.")
		return

	var min_fps := _fps_samples[0]
	var max_fps := _fps_samples[0]
	var total := 0.0
	for s in _fps_samples:
		total += s
		if s < min_fps:
			min_fps = s
		if s > max_fps:
			max_fps = s
	var avg := total / _fps_samples.size()

	print("========== FPS SUMMARY ==========")
	print("  Avg FPS:  %.1f" % avg)
	print("  Min FPS:  %.1f" % min_fps)
	print("  Max FPS:  %.1f" % max_fps)
	print("  Samples:  %d" % _fps_samples.size())
	print("  Duration: %.1fs" % _elapsed)
	print("  Target:   60 FPS → %s" % ("PASS" if avg >= 58.0 else "FAIL"))
	print("=================================")
