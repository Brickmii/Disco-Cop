#!/usr/bin/env python3
"""Generate additional SFX for Disco Cop.

Creates:
  - rocket_explode.wav — big bassy boom for rocket AoE splash
  - combo_hit.wav — short ascending chime (pitch-shifted in code)
  - level_complete.wav — 2-3 second victory fanfare
  - game_over_sting.wav — dramatic 2 second death sting
  - landing_thud.wav — player landing from height
  - stuck_escape.wav — breaking free sound

Usage:
    python create_sfx_batch.py

Output: disco_cop/assets/audio/sfx/
"""

import wave
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "audio" / "sfx"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RATE = 44100


def save_wav(filename, data):
    """Save mono WAV file."""
    peak = np.max(np.abs(data))
    if peak > 0:
        data = data / peak * 0.75
    data = np.clip(data, -1, 1)
    samples = (data * 32767).astype(np.int16)
    stereo = np.column_stack([samples, samples]).flatten()

    path = OUTPUT_DIR / filename
    with wave.open(str(path), 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(stereo.tobytes())
    return path


def sine(freq, dur):
    t = np.linspace(0, dur, int(RATE * dur), False)
    return np.sin(2 * np.pi * freq * t)


def noise(dur):
    return np.random.uniform(-1, 1, int(RATE * dur))


def sweep(f0, f1, dur):
    t = np.linspace(0, dur, int(RATE * dur), False)
    freqs = np.linspace(f0, f1, len(t))
    return np.sin(2 * np.pi * np.cumsum(freqs) / RATE)


def env_decay(length, tau=0.15):
    t = np.linspace(0, length / RATE, length)
    return np.exp(-t / tau)


def env_ar(length, attack=0.01, release=0.02):
    e = np.ones(length)
    a = min(int(attack * RATE), length)
    r = min(int(release * RATE), length)
    if a > 0:
        e[:a] = np.linspace(0, 1, a)
    if r > 0:
        e[-r:] = np.linspace(1, 0, r)
    return e


def mix_at(target, source, offset):
    end = min(offset + len(source), len(target))
    if offset < 0 or offset >= len(target):
        return
    target[offset:end] += source[:end - offset]


# ── SFX Generators ───────────────────────────────────────────────────

def create_rocket_explode():
    """Big bassy boom — low frequency sweep + noise burst + sub rumble."""
    dur = 0.6
    nn = int(RATE * dur)
    mix = np.zeros(nn)

    # Sub-bass sweep (200Hz down to 30Hz)
    t = np.linspace(0, dur, nn, False)
    freq = 200 * np.exp(-t / 0.08) + 30
    sub = np.sin(2 * np.pi * np.cumsum(freq) / RATE) * 0.6
    mix += sub * env_decay(nn, 0.2)

    # Noise burst (explosion texture)
    mix += noise(dur) * 0.4 * env_decay(nn, 0.08)

    # Low rumble tail
    mix += sine(40, dur) * 0.3 * env_decay(nn, 0.25)

    # Mid crackle
    crackle = noise(dur) * 0.2
    # Low-pass by averaging
    for _ in range(5):
        crackle = np.convolve(crackle, [0.25, 0.5, 0.25], mode='same')
    mix += crackle * env_decay(nn, 0.15)

    return mix, "rocket_explode"


def create_combo_hit():
    """Short ascending chime — bright, clean, satisfying."""
    dur = 0.15
    nn = int(RATE * dur)
    mix = np.zeros(nn)

    # Main chime tone (ascending)
    freq = 880  # A5
    mix += sine(freq, dur) * 0.35
    mix += sine(freq * 2, dur) * 0.15  # Octave harmonic
    mix += sine(freq * 3, dur) * 0.08  # Shimmer

    # Bell-like envelope
    mix *= env_decay(nn, 0.06)

    # Add a tiny click at start for impact
    click = noise(0.003) * 0.2
    mix_at(mix, click, 0)

    return mix, "combo_hit"


def create_level_complete():
    """Victory fanfare — ascending major arpeggio + triumphant chord, ~2.5s."""
    bpm = 140
    beat = int(RATE * 60.0 / bpm)
    dur = 2.5
    nn = int(RATE * dur)
    mix = np.zeros(nn)

    # C major ascending arpeggio: C5 E5 G5 C6
    notes = [523.25, 659.25, 783.99, 1046.50]
    sixteenth = beat // 4

    for i, freq in enumerate(notes):
        pos = i * sixteenth * 2
        note_dur = 0.3
        tone = sine(freq, note_dur) * 0.3
        tone += sine(freq * 2, note_dur) * 0.12
        tone *= env_ar(len(tone), 0.005, 0.08)
        mix_at(mix, tone, pos)

    # Triumphant chord hit at beat 2
    chord_pos = beat
    chord_dur = 1.5
    chord_freqs = [523.25, 659.25, 783.99, 1046.50]  # C major
    for f in chord_freqs:
        tone = sine(f, chord_dur) * 0.2
        tone += sine(f * 2, chord_dur) * 0.08
        tone *= env_ar(len(tone), 0.01, 0.4)
        mix_at(mix, tone, chord_pos)

    # Sparkle shimmer overlay
    for i in range(8):
        pos = chord_pos + i * int(RATE * 0.08)
        freq = 2000 + i * 300
        sparkle = sine(freq, 0.05) * 0.06
        sparkle *= env_decay(len(sparkle), 0.02)
        mix_at(mix, sparkle, pos)

    # Little snare hit for punch
    snare_sig = noise(0.08) * 0.2 * env_decay(int(RATE * 0.08), 0.03)
    mix_at(mix, snare_sig, chord_pos)

    return mix, "level_complete"


def create_game_over_sting():
    """Dramatic death sting — descending minor, dark, final. ~2s."""
    dur = 2.0
    nn = int(RATE * dur)
    mix = np.zeros(nn)

    # Descending minor: E4 → C4 → A3 → E3
    notes = [(329.63, 0.0), (261.63, 0.3), (220.0, 0.6), (164.81, 0.9)]

    for freq, start in notes:
        pos = int(start * RATE)
        note_dur = 0.5
        # Dark tone: fundamental + sub
        tone = sine(freq, note_dur) * 0.3
        tone += sine(freq * 0.5, note_dur) * 0.15  # Sub octave
        tone += sine(freq * 1.5, note_dur) * 0.05   # Minor color
        tone *= env_ar(len(tone), 0.01, 0.2)
        mix_at(mix, tone, pos)

    # Final low chord at 1.2s
    final_pos = int(1.2 * RATE)
    final_dur = 0.8
    final_freqs = [82.41, 123.47, 164.81]  # E2, B2, E3 (low E power chord)
    for f in final_freqs:
        tone = sine(f, final_dur) * 0.25
        tone *= env_ar(len(tone), 0.02, 0.3)
        mix_at(mix, tone, final_pos)

    # Dark noise rumble
    rumble = noise(0.8) * 0.08
    for _ in range(8):
        rumble = np.convolve(rumble, [0.3, 0.4, 0.3], mode='same')
    rumble *= env_decay(len(rumble), 0.3)
    mix_at(mix, rumble, final_pos)

    return mix, "game_over_sting"


def create_landing_thud():
    """Player landing — short impactful thud with sub-bass."""
    dur = 0.15
    nn = int(RATE * dur)
    mix = np.zeros(nn)

    # Low thud (pitch sweep down)
    t = np.linspace(0, dur, nn, False)
    freq = 120 * np.exp(-t / 0.02) + 40
    thud = np.sin(2 * np.pi * np.cumsum(freq) / RATE) * 0.5
    mix += thud * env_decay(nn, 0.04)

    # Noise burst (impact texture)
    mix += noise(dur) * 0.15 * env_decay(nn, 0.02)

    # Sub body
    mix += sine(50, dur) * 0.3 * env_decay(nn, 0.05)

    return mix, "landing_thud"


def create_stuck_escape():
    """Breaking free sound — quick ascending scrape/burst."""
    dur = 0.25
    nn = int(RATE * dur)
    mix = np.zeros(nn)

    # Ascending sweep (scraping free)
    mix += sweep(200, 1200, dur) * 0.25 * env_ar(nn, 0.01, 0.05)

    # Quick noise burst
    burst_n = int(RATE * 0.08)
    mix_at(mix, noise(0.08) * 0.2 * env_decay(burst_n, 0.03), 0)

    # Snap/pop at the moment of release
    snap_pos = int(0.12 * RATE)
    snap = noise(0.02) * 0.35
    snap *= env_decay(len(snap), 0.008)
    mix_at(mix, snap, snap_pos)

    # Brief bright tone (freedom!)
    free_tone = sine(800, 0.08) * 0.15
    free_tone += sine(1200, 0.08) * 0.08
    free_tone *= env_ar(len(free_tone), 0.005, 0.03)
    mix_at(mix, free_tone, snap_pos)

    return mix, "stuck_escape"


def main():
    np.random.seed(99)
    print(f"Generating SFX to: {OUTPUT_DIR}")

    generators = [
        create_rocket_explode,
        create_combo_hit,
        create_level_complete,
        create_game_over_sting,
        create_landing_thud,
        create_stuck_escape,
    ]

    for gen_fn in generators:
        data, name = gen_fn()
        wav_name = f"{name}.wav"
        save_wav(wav_name, data)
        duration = len(data) / RATE
        print(f"  [OK] {wav_name} ({duration:.2f}s)")

    print(f"\nDone! {len(generators)} SFX generated.")


if __name__ == "__main__":
    main()
