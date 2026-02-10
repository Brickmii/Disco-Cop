#!/usr/bin/env python3
"""Generate placeholder disco/funk music loops for Disco Cop.

Creates 3 music tracks using numpy synthesis:
  - menu_theme.wav  — chill disco groove (4 bars, ~8 sec loop)
  - level_theme.wav — upbeat funk (4 bars, ~6 sec loop)
  - boss_theme.wav  — intense disco (4 bars, ~5 sec loop)

These are intentionally lo-fi / chiptune-adjacent placeholder tracks.
Convert to OGG with: ffmpeg -i track.wav -c:a libvorbis -q:a 4 track.ogg

Usage:
    python create_music.py

Output: disco_cop/assets/audio/music/
"""

import wave
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "audio" / "music"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RATE = 44100

# ── Note Frequencies (A4 = 440 Hz) ───────────────────────────────────
NOTE_FREQS = {}
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
for octave in range(1, 8):
    for i, name in enumerate(NOTE_NAMES):
        midi = (octave + 1) * 12 + i
        NOTE_FREQS[f"{name}{octave}"] = 440.0 * 2 ** ((midi - 69) / 12.0)


def note(name: str) -> float:
    return NOTE_FREQS.get(name, 0)


# ── Waveforms ─────────────────────────────────────────────────────────

def sine_wave(freq: float, duration: float) -> np.ndarray:
    t = np.linspace(0, duration, int(RATE * duration), endpoint=False)
    return np.sin(2 * np.pi * freq * t)


def square_wave(freq: float, duration: float, duty: float = 0.5) -> np.ndarray:
    t = np.linspace(0, duration, int(RATE * duration), endpoint=False)
    return np.where((t * freq) % 1.0 < duty, 1.0, -1.0)


def saw_wave(freq: float, duration: float) -> np.ndarray:
    t = np.linspace(0, duration, int(RATE * duration), endpoint=False)
    return 2.0 * (t * freq - np.floor(0.5 + t * freq))


def noise_burst(duration: float) -> np.ndarray:
    return np.random.uniform(-1, 1, int(RATE * duration))


def silence(duration: float) -> np.ndarray:
    return np.zeros(int(RATE * duration))


# ── Envelopes ─────────────────────────────────────────────────────────

def env_pluck(length: int, decay: float = 0.15) -> np.ndarray:
    t = np.linspace(0, length / RATE, length)
    return np.exp(-t / decay)


def env_sustain(length: int, attack: float = 0.01, release: float = 0.02) -> np.ndarray:
    env = np.ones(length)
    a = min(int(attack * RATE), length)
    r = min(int(release * RATE), length)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    if r > 0:
        env[-r:] = np.linspace(1, 0, r)
    return env


def env_kick(length: int) -> np.ndarray:
    t = np.linspace(0, length / RATE, length)
    return np.exp(-t / 0.08)


# ── Instrument Voices ─────────────────────────────────────────────────

def bass_note(freq: float, duration: float, decay: float = 0.2) -> np.ndarray:
    sig = square_wave(freq, duration, 0.25) * 0.4 + sine_wave(freq, duration) * 0.3
    return sig * env_pluck(len(sig), decay)


def lead_note(freq: float, duration: float) -> np.ndarray:
    sig = square_wave(freq, duration, 0.5) * 0.25 + sine_wave(freq * 2, duration) * 0.1
    return sig * env_sustain(len(sig), 0.005, 0.02)


def pad_note(freq: float, duration: float) -> np.ndarray:
    sig = sine_wave(freq, duration) * 0.12
    sig += sine_wave(freq * 1.005, duration) * 0.08  # Slight detune for width
    sig += sine_wave(freq * 2, duration) * 0.05
    return sig * env_sustain(len(sig), 0.05, 0.05)


def kick(duration: float = 0.15) -> np.ndarray:
    n = int(RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    freq = 150 * np.exp(-t / 0.04) + 40
    sig = np.sin(2 * np.pi * np.cumsum(freq) / RATE) * 0.6
    return sig * env_kick(n)


def snare(duration: float = 0.12) -> np.ndarray:
    n = int(RATE * duration)
    sig = noise_burst(duration) * 0.35 + square_wave(200, duration) * 0.15
    return sig * env_pluck(n, 0.06)


def hihat(duration: float = 0.05) -> np.ndarray:
    n = int(RATE * duration)
    sig = noise_burst(duration) * 0.2
    return sig * env_pluck(n, 0.03)


def hihat_open(duration: float = 0.15) -> np.ndarray:
    n = int(RATE * duration)
    sig = noise_burst(duration) * 0.15
    return sig * env_pluck(n, 0.1)


# ── Pattern Helpers ───────────────────────────────────────────────────

def mix_at(target: np.ndarray, source: np.ndarray, offset: int):
    """Mix source into target at sample offset."""
    end = min(offset + len(source), len(target))
    target[offset:end] += source[:end - offset]


def beats_to_samples(beats: float, bpm: float) -> int:
    return int(RATE * 60.0 / bpm * beats)


# ── Track Generators ──────────────────────────────────────────────────

def create_menu_theme():
    """Chill disco groove — 120 BPM, 8 bars (~16 sec loop)."""
    bpm = 120
    beat = beats_to_samples(1, bpm)
    sixteenth = beat // 4
    bar = beat * 4
    total_bars = 8
    total = bar * total_bars
    mix = np.zeros(total)

    # ── Drums: classic disco pattern ──
    for b in range(total_bars):
        for i in range(4):  # 4 beats per bar
            pos = b * bar + i * beat
            # Kick on every beat (four-on-the-floor)
            mix_at(mix, kick(), pos)
            # Snare on 2 and 4
            if i in [1, 3]:
                mix_at(mix, snare(), pos)
            # Hi-hat on every eighth
            mix_at(mix, hihat(), pos)
            mix_at(mix, hihat(), pos + beat // 2)
            # Open hi-hat on off-beats
            if i in [1, 3]:
                mix_at(mix, hihat_open(), pos + beat // 2)

    # ── Bass: disco octave pattern ──
    # Chord progression: Am - Dm - G - C (2 bars each)
    bass_prog = [
        (note('A2'), note('A3')),  # Am
        (note('D2'), note('D3')),  # Dm
        (note('G2'), note('G3')),  # G
        (note('C2'), note('C3')),  # C
    ]
    for chord_idx, (low, high) in enumerate(bass_prog):
        for rep in range(2):  # 2 bars per chord
            b = chord_idx * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                # Octave bounce: low-high-low-high
                f = low if i % 2 == 0 else high
                mix_at(mix, bass_note(f, 60.0 / bpm * 0.8, 0.15), pos)

    # ── Pad: sustained chords ──
    pad_chords = [
        [note('A3'), note('C4'), note('E4')],   # Am
        [note('D3'), note('F4'), note('A4')],   # Dm
        [note('G3'), note('B3'), note('D4')],   # G
        [note('C3'), note('E4'), note('G4')],   # C
    ]
    for chord_idx, chord in enumerate(pad_chords):
        dur = 60.0 / bpm * 8  # 2 bars
        pos = chord_idx * 2 * bar
        for f in chord:
            mix_at(mix, pad_note(f, dur), pos)

    # ── Lead: simple melody ──
    melody = [
        # (bar, beat_offset, note_name, duration_beats)
        (0, 0, 'E4', 1), (0, 1, 'C4', 0.5), (0, 1.5, 'D4', 0.5),
        (0, 2, 'E4', 1), (0, 3, 'G4', 1),
        (1, 0, 'A4', 2), (1, 2, 'G4', 1), (1, 3, 'E4', 1),
        (2, 0, 'D4', 1), (2, 1, 'E4', 0.5), (2, 1.5, 'D4', 0.5),
        (2, 2, 'B3', 1), (2, 3, 'D4', 1),
        (3, 0, 'C4', 2), (3, 2, 'E4', 1), (3, 3, 'G4', 1),
        # Repeat with variation
        (4, 0, 'E4', 1), (4, 1, 'C4', 0.5), (4, 1.5, 'D4', 0.5),
        (4, 2, 'E4', 0.5), (4, 2.5, 'G4', 0.5), (4, 3, 'A4', 1),
        (5, 0, 'G4', 1.5), (5, 1.5, 'E4', 0.5), (5, 2, 'D4', 2),
        (6, 0, 'D4', 1), (6, 1, 'F4', 1), (6, 2, 'E4', 1), (6, 3, 'D4', 1),
        (7, 0, 'C4', 3), (7, 3, 'E4', 1),
    ]
    for m_bar, beat_off, n, dur_beats in melody:
        pos = m_bar * bar + int(beat_off * beat)
        dur = 60.0 / bpm * dur_beats * 0.9
        mix_at(mix, lead_note(note(n), dur), pos)

    return mix, "menu_theme"


def create_level_theme():
    """Upbeat funk — 140 BPM, 8 bars (~14 sec loop)."""
    bpm = 140
    beat = beats_to_samples(1, bpm)
    bar = beat * 4
    total_bars = 8
    total = bar * total_bars
    mix = np.zeros(total)

    # ── Drums: driving funk beat ──
    for b in range(total_bars):
        for i in range(4):
            pos = b * bar + i * beat
            # Kick: 1, "and of 2", 3
            if i in [0, 2]:
                mix_at(mix, kick(), pos)
            if i == 1:
                mix_at(mix, kick(), pos + beat // 2)
            # Snare on 2 and 4
            if i in [1, 3]:
                mix_at(mix, snare(), pos)
            # 16th note hi-hats
            for s in range(4):
                vol = 0.7 if s == 0 else 0.4
                hh = hihat(0.04)
                mix_at(mix, hh * vol, pos + s * (beat // 4))

    # ── Bass: funky syncopated ──
    bass_prog = [
        (note('E2'), note('E3')),
        (note('A2'), note('A3')),
        (note('D2'), note('D3')),
        (note('A2'), note('A3')),
    ]
    for chord_idx, (low, high) in enumerate(bass_prog):
        for rep in range(2):
            b = chord_idx * 2 + rep
            pos = b * bar
            # Funky rhythm: 1, and-of-2, 3, and-of-3, 4
            mix_at(mix, bass_note(low, 0.15, 0.1), pos)
            mix_at(mix, bass_note(high, 0.1, 0.08), pos + beat + beat // 2)
            mix_at(mix, bass_note(low, 0.15, 0.1), pos + beat * 2)
            mix_at(mix, bass_note(high, 0.08, 0.06), pos + beat * 2 + beat // 2)
            mix_at(mix, bass_note(low, 0.12, 0.1), pos + beat * 3)

    # ── Lead: energetic riff ──
    riff = [
        (0, 0, 'E4', 0.5), (0, 0.5, 'G4', 0.5), (0, 1, 'A4', 0.5),
        (0, 1.5, 'B4', 0.5), (0, 2, 'A4', 1), (0, 3, 'G4', 0.5), (0, 3.5, 'E4', 0.5),
        (1, 0, 'D4', 1), (1, 1, 'E4', 0.5), (1, 1.5, 'G4', 0.5),
        (1, 2, 'A4', 1.5), (1, 3.5, 'G4', 0.5),
    ]
    for rep in range(4):  # Repeat riff 4 times
        for m_bar, beat_off, n, dur_beats in riff:
            pos = (rep * 2 + m_bar) * bar + int(beat_off * beat)
            dur = 60.0 / bpm * dur_beats * 0.85
            mix_at(mix, lead_note(note(n), dur), pos)

    # ── Pad: power chords ──
    pad_chords = [
        [note('E3'), note('B3')],
        [note('A3'), note('E4')],
        [note('D3'), note('A3')],
        [note('A3'), note('E4')],
    ]
    for chord_idx, chord in enumerate(pad_chords):
        dur = 60.0 / bpm * 8
        pos = chord_idx * 2 * bar
        for f in chord:
            mix_at(mix, pad_note(f, dur) * 0.7, pos)

    return mix, "level_theme"


def create_boss_theme():
    """Intense disco — 160 BPM, 8 bars (~12 sec loop)."""
    bpm = 160
    beat = beats_to_samples(1, bpm)
    bar = beat * 4
    total_bars = 8
    total = bar * total_bars
    mix = np.zeros(total)

    # ── Drums: intense four-on-the-floor + double-time hats ──
    for b in range(total_bars):
        for i in range(4):
            pos = b * bar + i * beat
            # Kick on every beat
            mix_at(mix, kick(0.12), pos)
            # Snare on 2 and 4 with extra hit on and-of-4
            if i in [1, 3]:
                mix_at(mix, snare(0.1), pos)
            if i == 3:
                mix_at(mix, snare(0.08) * 0.7, pos + beat // 2)
            # 16th note hats
            for s in range(4):
                vol = 0.8 if s == 0 else 0.5 if s == 2 else 0.3
                mix_at(mix, hihat(0.03) * vol, pos + s * (beat // 4))
            # Open hat on off-beats every other bar
            if b % 2 == 1 and i in [1, 3]:
                mix_at(mix, hihat_open(0.1), pos + beat // 2)

    # ── Bass: driving minor key ──
    bass_prog = [
        (note('A2'), note('A3')),
        (note('F2'), note('F3')),
        (note('G2'), note('G3')),
        (note('E2'), note('E3')),
    ]
    for chord_idx, (low, high) in enumerate(bass_prog):
        for rep in range(2):
            b = chord_idx * 2 + rep
            pos = b * bar
            # Driving eighths
            for i in range(8):
                f = low if i % 2 == 0 else high
                mix_at(mix, bass_note(f, 0.1, 0.08), pos + i * (beat // 2))

    # ── Lead: intense descending pattern ──
    patterns = [
        [(0, 'A4', 0.5), (0.5, 'G4', 0.5), (1, 'F4', 0.5), (1.5, 'E4', 0.5),
         (2, 'F4', 1), (3, 'E4', 0.5), (3.5, 'D4', 0.5)],
        [(0, 'C5', 0.5), (0.5, 'A4', 0.5), (1, 'G4', 0.5), (1.5, 'F4', 0.5),
         (2, 'E4', 1.5), (3.5, 'D4', 0.5)],
        [(0, 'D4', 0.5), (0.5, 'E4', 0.5), (1, 'F4', 0.5), (1.5, 'G4', 0.5),
         (2, 'A4', 1), (3, 'G4', 0.5), (3.5, 'F4', 0.5)],
        [(0, 'E4', 1), (1, 'F4', 0.5), (1.5, 'E4', 0.5),
         (2, 'D4', 1), (3, 'E4', 1)],
    ]
    for pat_idx, pattern in enumerate(patterns):
        for rep in range(2):
            b = pat_idx * 2 + rep
            for beat_off, n, dur_beats in pattern:
                pos = b * bar + int(beat_off * beat)
                dur = 60.0 / bpm * dur_beats * 0.8
                mix_at(mix, lead_note(note(n), dur) * 1.1, pos)

    # ── Stab chords (disco stabs on off-beats) ──
    stab_chords = [
        [note('A3'), note('C4'), note('E4')],
        [note('F3'), note('A3'), note('C4')],
        [note('G3'), note('B3'), note('D4')],
        [note('E3'), note('G3'), note('B3')],
    ]
    for chord_idx, chord in enumerate(stab_chords):
        for rep in range(2):
            b = chord_idx * 2 + rep
            for i in [1, 3]:  # Off-beats
                pos = b * bar + i * beat + beat // 2
                for f in chord:
                    stab = square_wave(f, 0.08, 0.5) * 0.12
                    stab *= env_pluck(len(stab), 0.04)
                    mix_at(mix, stab, pos)

    return mix, "boss_theme"


# ── Save as WAV ───────────────────────────────────────────────────────

def save_wav_stereo(filename: str, data: np.ndarray):
    """Save as 16-bit stereo WAV (duplicate mono to both channels)."""
    peak = np.max(np.abs(data))
    if peak > 0:
        data = data / peak * 0.75
    data = np.clip(data, -1, 1)
    samples = (data * 32767).astype(np.int16)
    # Interleave for stereo
    stereo = np.column_stack([samples, samples]).flatten()

    path = OUTPUT_DIR / filename
    with wave.open(str(path), 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(stereo.tobytes())


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print(f"Generating music to: {OUTPUT_DIR}")

    tracks = [create_menu_theme, create_level_theme, create_boss_theme]
    for gen_fn in tracks:
        data, name = gen_fn()
        wav_name = f"{name}.wav"
        save_wav_stereo(wav_name, data)
        duration = len(data) / RATE
        print(f"  [OK] {wav_name} ({duration:.1f}s)")

    print(f"\nDone! {len(tracks)} music tracks generated.")
    print("\nTo convert to OGG (optional, smaller files):")
    print("  ffmpeg -i menu_theme.wav -c:a libvorbis -q:a 4 menu_theme.ogg")


if __name__ == "__main__":
    main()
