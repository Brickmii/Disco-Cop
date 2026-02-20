#!/usr/bin/env python3
"""Generate disco music loops for Disco Cop.

Creates 3 tracks with authentic disco elements:
  - Four-on-the-floor kick with open hi-hat off-beats
  - Octave-bouncing disco bass lines
  - Rhythm guitar stabs (wah-style filtered chords)
  - Lush string/synth pads
  - Funky lead melodies

  - menu_theme.wav  — smooth disco groove (120 BPM, ~16s)
  - level_theme.wav — upbeat disco funk (126 BPM, ~15s)
  - boss_theme.wav  — intense dark disco (132 BPM, ~14s)

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

# ── Note Frequencies ──────────────────────────────────────────────────
NOTE_FREQS = {}
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
for _oct in range(1, 8):
    for _i, _nm in enumerate(NOTE_NAMES):
        _midi = (_oct + 1) * 12 + _i
        NOTE_FREQS[f"{_nm}{_oct}"] = 440.0 * 2 ** ((_midi - 69) / 12.0)


def n(name: str) -> float:
    return NOTE_FREQS.get(name, 0)


# ── Waveforms ─────────────────────────────────────────────────────────

def sine(freq, dur):
    t = np.linspace(0, dur, int(RATE * dur), False)
    return np.sin(2 * np.pi * freq * t)


def square(freq, dur, duty=0.5):
    t = np.linspace(0, dur, int(RATE * dur), False)
    return np.where((t * freq) % 1.0 < duty, 1.0, -1.0)


def saw(freq, dur):
    t = np.linspace(0, dur, int(RATE * dur), False)
    return 2.0 * (t * freq - np.floor(0.5 + t * freq))


def noise(dur):
    return np.random.uniform(-1, 1, int(RATE * dur))


def sweep_sin(f0, f1, dur):
    t = np.linspace(0, dur, int(RATE * dur), False)
    freqs = np.linspace(f0, f1, len(t))
    return np.sin(2 * np.pi * np.cumsum(freqs) / RATE)


# ── Envelopes ─────────────────────────────────────────────────────────

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


def env_swell(length, attack=0.08):
    """Slow attack for strings."""
    e = np.ones(length)
    a = min(int(attack * RATE), length)
    r = min(int(0.05 * RATE), length)
    if a > 0:
        e[:a] = np.linspace(0, 1, a)
    if r > 0:
        e[-r:] = np.linspace(1, 0, r)
    return e


# ── Instruments ───────────────────────────────────────────────────────

def kick(dur=0.15):
    nn = int(RATE * dur)
    t = np.linspace(0, dur, nn, False)
    freq = 160 * np.exp(-t / 0.035) + 45
    sig = np.sin(2 * np.pi * np.cumsum(freq) / RATE) * 0.65
    return sig * env_decay(nn, 0.08)


def snare(dur=0.12):
    nn = int(RATE * dur)
    sig = noise(dur) * 0.3 + square(180, dur) * 0.12
    return sig * env_decay(nn, 0.05)


def hihat_closed(dur=0.04):
    nn = int(RATE * dur)
    return noise(dur) * 0.18 * env_decay(nn, 0.02)


def hihat_open(dur=0.12):
    """Open hi-hat — THE disco signature sound on every off-beat."""
    nn = int(RATE * dur)
    return noise(dur) * 0.16 * env_decay(nn, 0.08)


def disco_bass(freq, dur, decay=0.12):
    """Punchy disco bass — fundamental + sub octave."""
    sig = square(freq, dur, 0.3) * 0.35
    sig += sine(freq, dur) * 0.3
    sig += sine(freq * 0.5, dur) * 0.15  # Sub
    return sig * env_decay(len(sig), decay)


def guitar_stab(freqs, dur=0.08):
    """Rhythm guitar chord stab — filtered square, quick decay.
    Simulates the classic disco wah-guitar 'chucka' sound."""
    sig = np.zeros(int(RATE * dur))
    for f in freqs:
        # Slightly detuned for width
        sig += square(f, dur, 0.4) * 0.06
        sig += square(f * 1.003, dur, 0.4) * 0.04
    # Simple low-pass simulation: average adjacent samples
    for _ in range(3):
        sig = np.convolve(sig, [0.25, 0.5, 0.25], mode='same')
    return sig * env_decay(len(sig), 0.04)


def guitar_mute(freqs, dur=0.04):
    """Muted guitar hit — shorter, more percussive."""
    sig = np.zeros(int(RATE * dur))
    for f in freqs:
        sig += square(f, dur, 0.35) * 0.05
    for _ in range(4):
        sig = np.convolve(sig, [0.25, 0.5, 0.25], mode='same')
    return sig * env_decay(len(sig), 0.02)


def string_note(freq, dur):
    """Disco string — lush saw with slow swell."""
    sig = saw(freq, dur) * 0.07
    sig += saw(freq * 1.004, dur) * 0.05  # Detune
    sig += saw(freq * 0.998, dur) * 0.04  # More detune
    sig += sine(freq * 2, dur) * 0.03     # Octave shimmer
    # Soften with averaging
    for _ in range(2):
        sig = np.convolve(sig, [0.3, 0.4, 0.3], mode='same')
    return sig * env_swell(len(sig), 0.1)


def string_chord(freqs, dur):
    """Multi-note string pad."""
    sig = np.zeros(int(RATE * dur))
    for f in freqs:
        sig += string_note(f, dur)
    return sig


def lead_synth(freq, dur):
    """Bright synth lead — square + octave sine."""
    sig = square(freq, dur, 0.5) * 0.18
    sig += sine(freq * 2, dur) * 0.08
    sig += sine(freq, dur) * 0.06
    return sig * env_ar(len(sig), 0.005, 0.03)


# ── Helpers ───────────────────────────────────────────────────────────

def mix_at(target, source, offset):
    end = min(offset + len(source), len(target))
    if offset < 0 or offset >= len(target):
        return
    target[offset:end] += source[:end - offset]


def bts(beats, bpm):
    """Beats to samples."""
    return int(RATE * 60.0 / bpm * beats)


# ── DISCO DRUM PATTERN ────────────────────────────────────────────────

def disco_drums(mix, bpm, total_bars, variation=0):
    """Classic disco drum pattern:
    - Kick on every quarter (four-on-the-floor)
    - Open hi-hat on every off-beat (the defining disco element)
    - Snare on 2 and 4
    - Closed hi-hat 16ths for groove
    """
    beat = bts(1, bpm)
    bar = beat * 4
    sixteenth = beat // 4

    for b in range(total_bars):
        for i in range(4):
            pos = b * bar + i * beat

            # KICK — every beat, four-on-the-floor
            mix_at(mix, kick(), pos)

            # SNARE — beats 2 and 4
            if i in [1, 3]:
                mix_at(mix, snare(), pos)

            # OPEN HI-HAT — every off-beat (between kicks)
            # This is THE disco sound
            mix_at(mix, hihat_open(), pos + beat // 2)

            # CLOSED HI-HAT — 16th notes for groove
            for s in range(4):
                if s == 2:  # Skip where open hat is
                    continue
                vol = 0.8 if s == 0 else 0.5
                mix_at(mix, hihat_closed() * vol, pos + s * sixteenth)

            # Variation: extra snare ghost notes
            if variation >= 1 and i == 0 and b % 2 == 1:
                mix_at(mix, snare(0.06) * 0.4, pos + 3 * sixteenth)
            if variation >= 2 and i == 3:
                mix_at(mix, snare(0.06) * 0.5, pos + beat // 2)


# ── TRACK 1: MENU THEME ──────────────────────────────────────────────

def create_menu_theme():
    """Smooth disco groove — 120 BPM, 8 bars.
    Think: Donna Summer 'I Feel Love' meets chillout.
    Progression: Am7 - Dm9 - Gmaj7 - Cmaj7 (2 bars each)
    """
    bpm = 120
    beat = bts(1, bpm)
    bar = beat * 4
    total_bars = 8
    total = bar * total_bars
    mix = np.zeros(total)

    # Drums
    disco_drums(mix, bpm, total_bars, variation=0)

    # ── Disco bass: octave bounce pattern ──
    bass_prog = [
        ('A2', 'A3'),   # Am7
        ('D2', 'D3'),   # Dm9
        ('G2', 'G3'),   # Gmaj7
        ('C2', 'C3'),   # Cmaj7
    ]
    eighth = beat // 2
    for ci, (lo, hi) in enumerate(bass_prog):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            # Classic disco octave pattern: low-high-low-high per beat
            for i in range(4):
                bp = pos + i * beat
                mix_at(mix, disco_bass(n(lo), 0.18, 0.12), bp)
                mix_at(mix, disco_bass(n(hi), 0.12, 0.08), bp + eighth)

    # ── Rhythm guitar: off-beat stabs ──
    guitar_chords = [
        [n('A3'), n('C4'), n('E4'), n('G4')],   # Am7
        [n('D3'), n('F4'), n('A4'), n('C5')],   # Dm9
        [n('G3'), n('B3'), n('D4'), n('F#4')],  # Gmaj7
        [n('C3'), n('E4'), n('G4'), n('B4')],   # Cmaj7
    ]
    for ci, chord in enumerate(guitar_chords):
        for rep in range(2):
            b = ci * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                # Stab on off-beat (between kicks)
                mix_at(mix, guitar_stab(chord), pos + eighth)
                # Ghost mute on the 'a' of each beat
                mix_at(mix, guitar_mute(chord), pos + 3 * (beat // 4))

    # ── Strings: lush sustained pads ──
    str_chords = [
        [n('A3'), n('C4'), n('E4'), n('G4')],
        [n('D4'), n('F4'), n('A4'), n('C5')],
        [n('G3'), n('B3'), n('D4'), n('F#4')],
        [n('C4'), n('E4'), n('G4'), n('B4')],
    ]
    for ci, chord in enumerate(str_chords):
        dur = 60.0 / bpm * 8  # 2 bars
        pos = ci * 2 * bar
        mix_at(mix, string_chord(chord, dur), pos)

    # ── Lead: smooth melody ──
    melody = [
        (0, 0, 'E5', 1), (0, 1, 'D5', 0.5), (0, 1.5, 'C5', 0.5),
        (0, 2, 'A4', 1.5), (0, 3.5, 'G4', 0.5),
        (1, 0, 'A4', 2), (1, 2, 'G4', 1), (1, 3, 'E4', 1),
        (2, 0, 'D5', 0.5), (2, 0.5, 'E5', 0.5), (2, 1, 'D5', 1),
        (2, 2, 'B4', 1), (2, 3, 'A4', 1),
        (3, 0, 'G4', 1.5), (3, 1.5, 'A4', 0.5), (3, 2, 'B4', 2),
        # Second half: variation
        (4, 0, 'C5', 1), (4, 1, 'B4', 0.5), (4, 1.5, 'A4', 0.5),
        (4, 2, 'G4', 1), (4, 3, 'A4', 0.5), (4, 3.5, 'B4', 0.5),
        (5, 0, 'C5', 2), (5, 2, 'A4', 2),
        (6, 0, 'F5', 0.5), (6, 0.5, 'E5', 0.5), (6, 1, 'D5', 0.5),
        (6, 1.5, 'C5', 0.5), (6, 2, 'D5', 1), (6, 3, 'E5', 1),
        (7, 0, 'C5', 2), (7, 2, 'B4', 1), (7, 3, 'A4', 1),
    ]
    for m_bar, beat_off, note_name, dur_beats in melody:
        pos = m_bar * bar + int(beat_off * beat)
        dur = 60.0 / bpm * dur_beats * 0.85
        mix_at(mix, lead_synth(n(note_name), dur), pos)

    return mix, "menu_theme"


# ── TRACK 2: LEVEL THEME ─────────────────────────────────────────────

def create_level_theme():
    """Upbeat disco funk — 126 BPM, 8 bars.
    Think: Bee Gees 'Stayin Alive' energy.
    Progression: Em7 - A7 - Dm7 - G7 (2 bars each)
    """
    bpm = 126
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    sixteenth = beat // 4
    total_bars = 8
    total = bar * total_bars
    mix = np.zeros(total)

    # Drums with ghost notes
    disco_drums(mix, bpm, total_bars, variation=1)

    # ── Disco bass: syncopated octave bounce ──
    bass_prog = [
        ('E2', 'E3'),  # Em7
        ('A2', 'A3'),  # A7
        ('D2', 'D3'),  # Dm7
        ('G2', 'G3'),  # G7
    ]
    for ci, (lo, hi) in enumerate(bass_prog):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            # Syncopated funk pattern
            mix_at(mix, disco_bass(n(lo), 0.15, 0.1), pos)                    # 1
            mix_at(mix, disco_bass(n(hi), 0.1, 0.06), pos + eighth)           # &
            mix_at(mix, disco_bass(n(lo), 0.08, 0.06), pos + beat + sixteenth * 3)  # a of 2
            mix_at(mix, disco_bass(n(hi), 0.12, 0.08), pos + beat * 2)        # 3
            mix_at(mix, disco_bass(n(lo), 0.1, 0.06), pos + beat * 2 + eighth) # & of 3
            mix_at(mix, disco_bass(n(hi), 0.15, 0.1), pos + beat * 3)          # 4
            mix_at(mix, disco_bass(n(lo), 0.08, 0.06), pos + beat * 3 + eighth) # & of 4

    # ── Rhythm guitar: classic 16th-note disco chucka ──
    gtr_chords = [
        [n('E3'), n('G4'), n('B4'), n('D5')],   # Em7
        [n('A3'), n('C#4'), n('E4'), n('G4')],  # A7
        [n('D3'), n('F4'), n('A4'), n('C5')],   # Dm7
        [n('G3'), n('B3'), n('D4'), n('F4')],   # G7
    ]
    for ci, chord in enumerate(gtr_chords):
        for rep in range(2):
            b = ci * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                # 16th note rhythm: X.x.X.x. (stab-mute-stab-mute)
                mix_at(mix, guitar_stab(chord, 0.07), pos + eighth)
                mix_at(mix, guitar_mute(chord, 0.04), pos + eighth + sixteenth)
                mix_at(mix, guitar_stab(chord, 0.06), pos + 3 * sixteenth)

    # ── Strings ──
    str_chords = [
        [n('E4'), n('G4'), n('B4'), n('D5')],
        [n('A3'), n('C#4'), n('E4'), n('G4')],
        [n('D4'), n('F4'), n('A4'), n('C5')],
        [n('G3'), n('B3'), n('D4'), n('F4')],
    ]
    for ci, chord in enumerate(str_chords):
        dur = 60.0 / bpm * 8
        pos = ci * 2 * bar
        mix_at(mix, string_chord(chord, dur) * 0.8, pos)

    # ── Lead: energetic disco riff ──
    riff_a = [
        (0, 'E5', 0.5), (0.5, 'D5', 0.25), (0.75, 'E5', 0.25),
        (1, 'G5', 0.5), (1.5, 'E5', 0.5),
        (2, 'D5', 0.5), (2.5, 'B4', 0.5),
        (3, 'A4', 0.75), (3.75, 'B4', 0.25),
    ]
    riff_b = [
        (0, 'A4', 0.5), (0.5, 'B4', 0.25), (0.75, 'C5', 0.25),
        (1, 'D5', 0.5), (1.5, 'E5', 0.5),
        (2, 'D5', 1),
        (3, 'B4', 0.5), (3.5, 'A4', 0.5),
    ]
    for rep in range(2):
        for m_bar_off, riff in [(0, riff_a), (1, riff_b)]:
            b = rep * 4 + m_bar_off * 2
            for beat_off, note_name, dur_beats in riff:
                # Play in bars b and b+1
                for sub in range(2):
                    pos = (b + sub) * bar + int(beat_off * beat)
                    dur = 60.0 / bpm * dur_beats * 0.8
                    mix_at(mix, lead_synth(n(note_name), dur), pos)

    return mix, "level_theme"


# ── TRACK 3: BOSS THEME ──────────────────────────────────────────────

def create_boss_theme():
    """Dark intense disco — 132 BPM, 8 bars.
    Think: Giorgio Moroder 'Chase' / Cerrone 'Supernature'.
    Progression: Am - F - Dm - E7 (2 bars each, minor key tension)
    """
    bpm = 132
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    sixteenth = beat // 4
    total_bars = 8
    total = bar * total_bars
    mix = np.zeros(total)

    # Intense drums
    disco_drums(mix, bpm, total_bars, variation=2)

    # ── Bass: driving octave eighths ──
    bass_prog = [
        ('A2', 'A3'),  # Am
        ('F2', 'F3'),  # F
        ('D2', 'D3'),  # Dm
        ('E2', 'E3'),  # E7
    ]
    for ci, (lo, hi) in enumerate(bass_prog):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            # Relentless eighth-note octave pumping
            for i in range(8):
                f = n(lo) if i % 2 == 0 else n(hi)
                mix_at(mix, disco_bass(f, 0.12, 0.08), pos + i * eighth)

    # ── Rhythm guitar: aggressive stabs ──
    gtr_chords = [
        [n('A3'), n('C4'), n('E4')],        # Am
        [n('F3'), n('A3'), n('C4')],        # F
        [n('D3'), n('F4'), n('A4')],        # Dm
        [n('E3'), n('G#3'), n('B3'), n('D4')],  # E7
    ]
    for ci, chord in enumerate(gtr_chords):
        for rep in range(2):
            b = ci * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                # Aggressive off-beat stabs
                mix_at(mix, guitar_stab(chord, 0.09) * 1.2, pos + eighth)
                # Extra stab on "a" for intensity
                mix_at(mix, guitar_stab(chord, 0.06) * 0.8, pos + 3 * sixteenth)

    # ── Strings: dramatic sustained ──
    str_chords = [
        [n('A3'), n('C4'), n('E4'), n('A4')],
        [n('F3'), n('A3'), n('C4'), n('F4')],
        [n('D3'), n('F4'), n('A4'), n('D5')],
        [n('E3'), n('G#3'), n('B3'), n('E4')],
    ]
    for ci, chord in enumerate(str_chords):
        dur = 60.0 / bpm * 8
        pos = ci * 2 * bar
        mix_at(mix, string_chord(chord, dur) * 1.1, pos)

    # ── Lead: intense minor key descending patterns ──
    patterns = [
        # Bar 0-1: Am — dramatic descending
        [(0, 'A5', 0.5), (0.5, 'G5', 0.5), (1, 'F5', 0.5), (1.5, 'E5', 0.5),
         (2, 'C5', 1), (3, 'B4', 0.5), (3.5, 'A4', 0.5)],
        # Bar 2-3: F — ascending counter
        [(0, 'F4', 0.5), (0.5, 'A4', 0.5), (1, 'C5', 0.5), (1.5, 'F5', 0.5),
         (2, 'E5', 1), (3, 'C5', 0.5), (3.5, 'A4', 0.5)],
        # Bar 4-5: Dm — syncopated
        [(0, 'D5', 0.75), (0.75, 'E5', 0.25), (1, 'F5', 0.5), (1.5, 'E5', 0.5),
         (2, 'D5', 0.5), (2.5, 'C5', 0.5), (3, 'A4', 1)],
        # Bar 6-7: E7 — tension, chromatic
        [(0, 'E5', 0.5), (0.5, 'F5', 0.5), (1, 'G#5', 0.5), (1.5, 'A5', 0.5),
         (2, 'G#5', 1), (3, 'E5', 0.75), (3.75, 'D5', 0.25)],
    ]
    for pi, pattern in enumerate(patterns):
        for rep in range(2):
            b = pi * 2 + rep
            for beat_off, note_name, dur_beats in pattern:
                pos = b * bar + int(beat_off * beat)
                dur = 60.0 / bpm * dur_beats * 0.8
                mix_at(mix, lead_synth(n(note_name), dur) * 1.2, pos)

    # ── Disco stab accents (brass-like hits) ──
    stab_notes = [
        (0, [n('A4'), n('C5'), n('E5')]),
        (2, [n('F4'), n('A4'), n('C5')]),
        (4, [n('D4'), n('F4'), n('A4')]),
        (6, [n('E4'), n('G#4'), n('B4')]),
    ]
    for b, chord in stab_notes:
        for sub in range(2):  # 2 bars per chord
            # Hit on beat 1 of each bar
            pos = (b + sub) * bar
            for f in chord:
                hit = square(f, 0.06, 0.5) * 0.1
                hit *= env_decay(len(hit), 0.03)
                mix_at(mix, hit, pos)
            # Hit on the "and" of beat 3
            pos2 = (b + sub) * bar + beat * 2 + eighth
            for f in chord:
                hit = square(f, 0.04, 0.5) * 0.08
                hit *= env_decay(len(hit), 0.02)
                mix_at(mix, hit, pos2)

    return mix, "boss_theme"


# ── Additional Instruments (punk/rock/new-wave) ──────────────────────

def power_chord(freq, dur, gain=0.22):
    """Distorted power chord — root + fifth, squared for crunch."""
    sig = saw(freq, dur) * 0.4
    sig += saw(freq * 1.5, dur) * 0.3  # Fifth
    sig += saw(freq * 2, dur) * 0.15   # Octave
    # Distortion: hard clip
    sig = np.clip(sig * 3, -1, 1) * gain
    for _ in range(2):
        sig = np.convolve(sig, [0.3, 0.4, 0.3], mode='same')
    return sig * env_ar(len(sig), 0.003, 0.02)


def punk_bass(freq, dur, decay=0.1):
    """Aggressive punk bass — square wave with bite."""
    sig = square(freq, dur, 0.4) * 0.4
    sig += saw(freq, dur) * 0.2
    return sig * env_decay(len(sig), decay)


def crash_cymbal(dur=0.4):
    """Crash cymbal for punk fills."""
    nn = int(RATE * dur)
    sig = noise(dur) * 0.25
    # Add some metallic ring
    sig += sine(3200, dur) * 0.03 + sine(5100, dur) * 0.02
    return sig * env_decay(nn, 0.2)


def ride_bell(dur=0.06):
    """Ride bell ping."""
    nn = int(RATE * dur)
    sig = sine(4800, dur) * 0.12 + sine(7200, dur) * 0.05
    return sig * env_decay(nn, 0.03)


def tom(freq=120, dur=0.15):
    """Floor/rack tom."""
    nn = int(RATE * dur)
    t = np.linspace(0, dur, nn, False)
    f = freq * 1.5 * np.exp(-t / 0.05) + freq
    sig = np.sin(2 * np.pi * np.cumsum(f) / RATE) * 0.4
    return sig * env_decay(nn, 0.06)


def brass_stab(freqs, dur=0.1):
    """Brass section stab for disco/funk accents."""
    sig = np.zeros(int(RATE * dur))
    for f in freqs:
        sig += square(f, dur, 0.45) * 0.08
        sig += sine(f, dur) * 0.06
    for _ in range(3):
        sig = np.convolve(sig, [0.25, 0.5, 0.25], mode='same')
    return sig * env_ar(len(sig), 0.005, 0.015)


def falsetto_lead(freq, dur):
    """Falsetto-style lead — bright sine + octave shimmer (Bee Gees)."""
    sig = sine(freq, dur) * 0.2
    sig += sine(freq * 2, dur) * 0.12
    sig += sine(freq * 3, dur) * 0.04  # Extra brightness
    # Vibrato
    t = np.linspace(0, dur, len(sig), False)
    vib = np.sin(2 * np.pi * 5.5 * t) * 0.008
    sig2 = sine(freq * (1 + vib.mean()), dur) * 0.05
    mix_buf = sig + sig2[:len(sig)]
    return mix_buf * env_ar(len(mix_buf), 0.01, 0.04)


def synth_arp(freq, dur):
    """Arpeggiated synth note for new-wave shimmer."""
    sig = square(freq, dur, 0.3) * 0.12
    sig += sine(freq * 2, dur) * 0.08
    sig += sine(freq * 4, dur) * 0.03
    return sig * env_ar(len(sig), 0.002, 0.02)


# ── Additional Drum Patterns ─────────────────────────────────────────

def punk_drums(mix, bpm, total_bars, intensity=1):
    """Punk drum pattern — fast, aggressive, snare-heavy."""
    beat = bts(1, bpm)
    bar = beat * 4
    sixteenth = beat // 4

    for b in range(total_bars):
        for i in range(4):
            pos = b * bar + i * beat
            # Kick on 1 and 3
            if i in [0, 2]:
                mix_at(mix, kick(0.12), pos)
            # Snare on 2 and 4
            if i in [1, 3]:
                mix_at(mix, snare(0.1), pos)
            # Hi-hat 8ths
            mix_at(mix, hihat_closed(0.03) * 1.2, pos)
            mix_at(mix, hihat_closed(0.03) * 0.7, pos + beat // 2)

        # Crash on bar 1 of every 4
        if b % 4 == 0:
            mix_at(mix, crash_cymbal(), b * bar)

        # Extra kick patterns for intensity
        if intensity >= 2:
            pos = b * bar
            mix_at(mix, kick(0.1), pos + beat + beat // 2)  # & of 2
            mix_at(mix, kick(0.1), pos + beat * 3 + beat // 2)  # & of 4
        # Fill every 4 bars
        if intensity >= 1 and b % 4 == 3:
            for s in range(4):
                mix_at(mix, snare(0.06) * 0.6, b * bar + beat * 3 + s * sixteenth)


def new_wave_drums(mix, bpm, total_bars):
    """New wave drum pattern — tight, driving, with ride bell."""
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2

    for b in range(total_bars):
        for i in range(4):
            pos = b * bar + i * beat
            # Kick on 1, &2, 3
            if i in [0, 2]:
                mix_at(mix, kick(0.13), pos)
            if i == 1:
                mix_at(mix, kick(0.1), pos + eighth)
            # Snare on 2 and 4
            if i in [1, 3]:
                mix_at(mix, snare(0.1), pos)
            # Ride 8ths with off-beat accent
            mix_at(mix, ride_bell() * 0.7, pos)
            mix_at(mix, ride_bell(), pos + eighth)
            # Ghost hi-hat
            mix_at(mix, hihat_closed(0.03) * 0.4, pos + beat // 4)

        if b % 4 == 3:
            # Tom fill
            for s in range(3):
                mix_at(mix, tom(140 - s * 20, 0.1), b * bar + beat * 3 + s * (beat // 3))


def bee_gees_drums(mix, bpm, total_bars):
    """Tight Bee Gees disco drums — emphasis on off-beat hi-hat and groove."""
    beat = bts(1, bpm)
    bar = beat * 4
    sixteenth = beat // 4

    for b in range(total_bars):
        for i in range(4):
            pos = b * bar + i * beat
            # Four-on-the-floor kick
            mix_at(mix, kick(0.14), pos)
            # Snare on 2 and 4 with extra body
            if i in [1, 3]:
                mix_at(mix, snare(0.13), pos)
            # Strong open hat on off-beats — the Bee Gees signature
            mix_at(mix, hihat_open(0.14) * 1.1, pos + beat // 2)
            # Tight closed hats on 16ths
            for s in range(4):
                if s == 2:
                    continue
                vol = 0.9 if s == 0 else 0.5
                mix_at(mix, hihat_closed(0.035) * vol, pos + s * sixteenth)
        # Syncopated ghost snares for Gibb groove
        if b % 2 == 1:
            mix_at(mix, snare(0.05) * 0.3, b * bar + beat * 2 + 3 * sixteenth)


# ── LEVEL 1: SKATING RINK ──────────────────────────────────────────────

def create_level_01_theme():
    """Roller rink disco funk — 124 BPM, 8 bars.
    Think: classic roller disco, funky and groovy.
    Progression: Gm7 - C9 - Fm7 - Bb7 (2 bars each)
    """
    bpm = 124
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    sixteenth = beat // 4
    total_bars = 8
    mix = np.zeros(bar * total_bars)

    disco_drums(mix, bpm, total_bars, variation=1)

    # Bass: bouncy roller rink groove
    bass_prog = [('G2', 'G3'), ('C2', 'C3'), ('F2', 'F3'), ('A#2', 'A#3')]
    for ci, (lo, hi) in enumerate(bass_prog):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            for i in range(4):
                bp = pos + i * beat
                mix_at(mix, disco_bass(n(lo), 0.15, 0.1), bp)
                mix_at(mix, disco_bass(n(hi), 0.1, 0.07), bp + eighth)
                # Extra syncopation on 'a'
                if i % 2 == 1:
                    mix_at(mix, disco_bass(n(lo), 0.06, 0.04), bp + 3 * sixteenth)

    # Guitar: funky wah stabs
    gtr = [
        [n('G3'), n('A#3'), n('D4'), n('F4')],   # Gm7
        [n('C3'), n('E4'), n('G4'), n('A#4')],   # C9
        [n('F3'), n('G#3'), n('C4'), n('D#4')],  # Fm7
        [n('A#3'), n('D4'), n('F4'), n('G#4')],  # Bb7
    ]
    for ci, chord in enumerate(gtr):
        for rep in range(2):
            b = ci * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                mix_at(mix, guitar_stab(chord, 0.07), pos + eighth)
                mix_at(mix, guitar_mute(chord), pos + 3 * sixteenth)

    # Strings: warm pads
    strs = [
        [n('G3'), n('A#3'), n('D4'), n('F4')],
        [n('C4'), n('E4'), n('G4'), n('A#4')],
        [n('F3'), n('G#3'), n('C4'), n('D#4')],
        [n('A#3'), n('D4'), n('F4'), n('G#4')],
    ]
    for ci, chord in enumerate(strs):
        dur = 60.0 / bpm * 8
        mix_at(mix, string_chord(chord, dur), ci * 2 * bar)

    # Lead: cheerful roller rink melody
    melody = [
        (0, 0, 'D5', 0.5), (0, 0.5, 'F5', 0.5), (0, 1, 'G5', 1),
        (0, 2, 'F5', 0.5), (0, 2.5, 'D5', 0.5), (0, 3, 'A#4', 1),
        (1, 0, 'C5', 0.5), (1, 0.5, 'D5', 0.5), (1, 1, 'F5', 1),
        (1, 2, 'D5', 1.5), (1, 3.5, 'C5', 0.5),
        (2, 0, 'G4', 0.5), (2, 0.5, 'A#4', 0.5), (2, 1, 'C5', 0.5),
        (2, 1.5, 'D5', 0.5), (2, 2, 'F5', 1), (2, 3, 'D5', 1),
        (3, 0, 'A#4', 1.5), (3, 1.5, 'C5', 0.5), (3, 2, 'D5', 2),
        (4, 0, 'F5', 0.5), (4, 0.5, 'G5', 0.5), (4, 1, 'A#5', 1),
        (4, 2, 'G5', 0.5), (4, 2.5, 'F5', 0.5), (4, 3, 'D5', 1),
        (5, 0, 'C5', 1), (5, 1, 'D5', 0.5), (5, 1.5, 'F5', 0.5),
        (5, 2, 'G5', 2),
        (6, 0, 'A#5', 0.5), (6, 0.5, 'G5', 0.5), (6, 1, 'F5', 0.5),
        (6, 1.5, 'D5', 0.5), (6, 2, 'C5', 1), (6, 3, 'D5', 1),
        (7, 0, 'G4', 2), (7, 2, 'A#4', 1), (7, 3, 'D5', 1),
    ]
    for m_bar, beat_off, note_name, dur_beats in melody:
        pos = m_bar * bar + int(beat_off * beat)
        dur = 60.0 / bpm * dur_beats * 0.85
        mix_at(mix, lead_synth(n(note_name), dur), pos)

    return mix, "level_01_theme"


def create_level_01_boss():
    """Disco King boss — dark roller rink showdown, 130 BPM, 8 bars.
    Progression: Gm - Eb - Cm - D7
    """
    bpm = 130
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    total_bars = 8
    mix = np.zeros(bar * total_bars)

    disco_drums(mix, bpm, total_bars, variation=2)

    bass_prog = [('G2', 'G3'), ('D#2', 'D#3'), ('C2', 'C3'), ('D2', 'D3')]
    for ci, (lo, hi) in enumerate(bass_prog):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            for i in range(8):
                f = n(lo) if i % 2 == 0 else n(hi)
                mix_at(mix, disco_bass(f, 0.12, 0.08), pos + i * eighth)

    gtr = [
        [n('G3'), n('A#3'), n('D4')],
        [n('D#3'), n('G3'), n('A#3')],
        [n('C3'), n('D#3'), n('G3')],
        [n('D3'), n('F#3'), n('A3'), n('C4')],
    ]
    for ci, chord in enumerate(gtr):
        for rep in range(2):
            b = ci * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                mix_at(mix, guitar_stab(chord, 0.09) * 1.2, pos + eighth)

    strs = [
        [n('G3'), n('A#3'), n('D4')],
        [n('D#3'), n('G3'), n('A#3')],
        [n('C3'), n('D#4'), n('G4')],
        [n('D3'), n('F#3'), n('A3')],
    ]
    for ci, chord in enumerate(strs):
        dur = 60.0 / bpm * 8
        mix_at(mix, string_chord(chord, dur) * 1.1, ci * 2 * bar)

    # Menacing lead
    patterns = [
        [(0, 'G5', 0.5), (0.5, 'F5', 0.5), (1, 'D#5', 0.5), (1.5, 'D5', 0.5),
         (2, 'A#4', 1), (3, 'D5', 0.5), (3.5, 'D#5', 0.5)],
        [(0, 'G4', 0.5), (0.5, 'A#4', 0.5), (1, 'D#5', 1),
         (2, 'D5', 0.5), (2.5, 'A#4', 0.5), (3, 'G4', 1)],
        [(0, 'C5', 0.75), (0.75, 'D5', 0.25), (1, 'D#5', 1),
         (2, 'G5', 0.5), (2.5, 'F5', 0.5), (3, 'D#5', 1)],
        [(0, 'D5', 0.5), (0.5, 'F#5', 0.5), (1, 'A5', 1),
         (2, 'F#5', 0.5), (2.5, 'D5', 0.5), (3, 'A4', 1)],
    ]
    for pi, pattern in enumerate(patterns):
        for rep in range(2):
            b = pi * 2 + rep
            for beat_off, note_name, dur_beats in pattern:
                pos = b * bar + int(beat_off * beat)
                dur = 60.0 / bpm * dur_beats * 0.8
                mix_at(mix, lead_synth(n(note_name), dur) * 1.2, pos)

    return mix, "level_01_boss"


# ── LEVEL 2: VENICE BEACH ──────────────────────────────────────────────

def create_level_02_theme():
    """Venice Beach bombastic 80s action — 128 BPM, 8 bars.
    Arnold Schwarzenegger vibe: larger-than-life, driving.
    Progression: Cm - Ab - Fm - G7 (2 bars each)
    """
    bpm = 128
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    sixteenth = beat // 4
    total_bars = 8
    mix = np.zeros(bar * total_bars)

    disco_drums(mix, bpm, total_bars, variation=2)

    # Heavy bass: pumping 80s action
    bass_prog = [('C2', 'C3'), ('G#2', 'G#3'), ('F2', 'F3'), ('G2', 'G3')]
    for ci, (lo, hi) in enumerate(bass_prog):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            for i in range(4):
                bp = pos + i * beat
                mix_at(mix, disco_bass(n(lo), 0.18, 0.12), bp)
                mix_at(mix, disco_bass(n(hi), 0.1, 0.06), bp + eighth)

    # Guitar: power stabs (more aggressive)
    gtr = [
        [n('C3'), n('D#3'), n('G3'), n('C4')],
        [n('G#3'), n('C4'), n('D#4')],
        [n('F3'), n('G#3'), n('C4')],
        [n('G3'), n('B3'), n('D4'), n('F4')],
    ]
    for ci, chord in enumerate(gtr):
        for rep in range(2):
            b = ci * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                mix_at(mix, guitar_stab(chord, 0.09) * 1.1, pos + eighth)
                mix_at(mix, guitar_stab(chord, 0.06) * 0.7, pos + 3 * sixteenth)

    # Brass stabs for Arnold bombast
    brass = [
        [n('C4'), n('D#4'), n('G4')],
        [n('G#3'), n('C4'), n('D#4')],
        [n('F3'), n('G#3'), n('C4')],
        [n('G3'), n('B3'), n('D4')],
    ]
    for ci, chord in enumerate(brass):
        for rep in range(2):
            b = ci * 2 + rep
            # Brass hits on beat 1 and &3
            mix_at(mix, brass_stab(chord, 0.12), b * bar)
            mix_at(mix, brass_stab(chord, 0.08), b * bar + beat * 2 + eighth)

    # Strings: dramatic cinematic pads
    strs = [
        [n('C4'), n('D#4'), n('G4'), n('C5')],
        [n('G#3'), n('C4'), n('D#4'), n('G#4')],
        [n('F3'), n('G#3'), n('C4'), n('F4')],
        [n('G3'), n('B3'), n('D4'), n('G4')],
    ]
    for ci, chord in enumerate(strs):
        dur = 60.0 / bpm * 8
        mix_at(mix, string_chord(chord, dur) * 1.0, ci * 2 * bar)

    # Lead: heroic action melody
    melody = [
        (0, 0, 'G5', 0.5), (0, 0.5, 'G5', 0.25), (0, 0.75, 'G5', 0.25),
        (0, 1, 'D#5', 1), (0, 2, 'F5', 0.5), (0, 2.5, 'G5', 0.5),
        (0, 3, 'C6', 1),
        (1, 0, 'G5', 0.5), (1, 0.5, 'F5', 0.5), (1, 1, 'D#5', 1),
        (1, 2, 'C5', 2),
        (2, 0, 'G#5', 0.5), (2, 0.5, 'G5', 0.5), (2, 1, 'F5', 1),
        (2, 2, 'D#5', 0.5), (2, 2.5, 'F5', 0.5), (2, 3, 'G5', 1),
        (3, 0, 'G#5', 2), (3, 2, 'G5', 2),
        (4, 0, 'C5', 0.5), (4, 0.5, 'D5', 0.5), (4, 1, 'D#5', 0.5),
        (4, 1.5, 'F5', 0.5), (4, 2, 'G5', 1.5), (4, 3.5, 'F5', 0.5),
        (5, 0, 'D#5', 1), (5, 1, 'C5', 1), (5, 2, 'D5', 1), (5, 3, 'D#5', 1),
        (6, 0, 'F5', 0.5), (6, 0.5, 'G5', 0.5), (6, 1, 'G#5', 1),
        (6, 2, 'G5', 0.5), (6, 2.5, 'F5', 0.5), (6, 3, 'D#5', 1),
        (7, 0, 'G5', 2), (7, 2, 'C5', 2),
    ]
    for m_bar, beat_off, note_name, dur_beats in melody:
        pos = m_bar * bar + int(beat_off * beat)
        dur = 60.0 / bpm * dur_beats * 0.85
        mix_at(mix, lead_synth(n(note_name), dur) * 1.1, pos)

    return mix, "level_02_theme"


def create_level_02_boss():
    """Arnoldo boss — bombastic muscle beach showdown, 134 BPM.
    Progression: Cm - G - Ab - Bb
    """
    bpm = 134
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    total_bars = 8
    mix = np.zeros(bar * total_bars)

    disco_drums(mix, bpm, total_bars, variation=2)

    bass_prog = [('C2', 'C3'), ('G2', 'G3'), ('G#2', 'G#3'), ('A#2', 'A#3')]
    for ci, (lo, hi) in enumerate(bass_prog):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            for i in range(8):
                f = n(lo) if i % 2 == 0 else n(hi)
                mix_at(mix, disco_bass(f, 0.12, 0.08), pos + i * eighth)

    # Heavy brass for Arnold
    brass = [
        [n('C4'), n('D#4'), n('G4')],
        [n('G3'), n('B3'), n('D4')],
        [n('G#3'), n('C4'), n('D#4')],
        [n('A#3'), n('D4'), n('F4')],
    ]
    for ci, chord in enumerate(brass):
        for rep in range(2):
            b = ci * 2 + rep
            mix_at(mix, brass_stab(chord, 0.15) * 1.3, b * bar)
            mix_at(mix, brass_stab(chord, 0.1) * 1.0, b * bar + beat * 2)
            mix_at(mix, brass_stab(chord, 0.08) * 0.8, b * bar + beat * 2 + eighth)

    strs = [
        [n('C4'), n('D#4'), n('G4')],
        [n('G3'), n('B3'), n('D4')],
        [n('G#3'), n('C4'), n('D#4')],
        [n('A#3'), n('D4'), n('F4')],
    ]
    for ci, chord in enumerate(strs):
        dur = 60.0 / bpm * 8
        mix_at(mix, string_chord(chord, dur) * 1.2, ci * 2 * bar)

    # Powerful lead
    patterns = [
        [(0, 'C5', 0.5), (0.5, 'D#5', 0.5), (1, 'G5', 1),
         (2, 'G5', 0.5), (2.5, 'F5', 0.5), (3, 'D#5', 1)],
        [(0, 'D5', 0.5), (0.5, 'G5', 1), (1.5, 'F5', 0.5),
         (2, 'D5', 1), (3, 'B4', 1)],
        [(0, 'G#4', 0.5), (0.5, 'C5', 0.5), (1, 'D#5', 1),
         (2, 'F5', 0.5), (2.5, 'D#5', 0.5), (3, 'C5', 1)],
        [(0, 'A#4', 0.5), (0.5, 'D5', 0.5), (1, 'F5', 1),
         (2, 'D5', 1.5), (3.5, 'C5', 0.5)],
    ]
    for pi, pattern in enumerate(patterns):
        for rep in range(2):
            b = pi * 2 + rep
            for beat_off, note_name, dur_beats in pattern:
                pos = b * bar + int(beat_off * beat)
                dur = 60.0 / bpm * dur_beats * 0.8
                mix_at(mix, lead_synth(n(note_name), dur) * 1.3, pos)

    return mix, "level_02_boss"


# ── LEVEL 3: PUNK CONCERT (SEX PISTOLS) ─────────────────────────────

def create_level_03_theme():
    """Raw punk aggression — 160 BPM, 8 bars.
    Sex Pistols: abrasive, anarchic, fast.
    Progression: E5 - A5 - B5 - E5 (power chords, 2 bars each)
    """
    bpm = 160
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    sixteenth = beat // 4
    total_bars = 8
    mix = np.zeros(bar * total_bars)

    punk_drums(mix, bpm, total_bars, intensity=2)

    # Punk bass: driving root notes
    bass_notes = [('E2',), ('A2',), ('B2',), ('E2',)]
    for ci, (root,) in enumerate(bass_notes):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            for i in range(4):
                bp = pos + i * beat
                mix_at(mix, punk_bass(n(root), 0.15, 0.08), bp)
                mix_at(mix, punk_bass(n(root) * 2, 0.08, 0.04), bp + eighth)

    # Power chords: raw and loud
    chords = [n('E3'), n('A3'), n('B3'), n('E3')]
    for ci, root in enumerate(chords):
        for rep in range(2):
            b = ci * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                # Down-strums on every beat
                mix_at(mix, power_chord(root, 0.18, 0.25), pos)
                # Up-strums on off-beats
                mix_at(mix, power_chord(root, 0.1, 0.15), pos + eighth)

    # Aggressive lead: angular punk melody
    melody = [
        (0, 0, 'E5', 0.25), (0, 0.25, 'E5', 0.25), (0, 0.5, 'G5', 0.5),
        (0, 1, 'A5', 0.5), (0, 1.5, 'G5', 0.5),
        (0, 2, 'E5', 0.5), (0, 2.5, 'D5', 0.5), (0, 3, 'E5', 1),
        (1, 0, 'B4', 0.5), (1, 0.5, 'D5', 0.5), (1, 1, 'E5', 0.5),
        (1, 1.5, 'G5', 0.5), (1, 2, 'E5', 2),
        (2, 0, 'A5', 0.5), (2, 0.5, 'A5', 0.25), (2, 0.75, 'G5', 0.25),
        (2, 1, 'E5', 0.5), (2, 1.5, 'D5', 0.5),
        (2, 2, 'C5', 0.5), (2, 2.5, 'D5', 0.5), (2, 3, 'E5', 1),
        (3, 0, 'A4', 1), (3, 1, 'B4', 0.5), (3, 1.5, 'D5', 0.5),
        (3, 2, 'E5', 2),
        (4, 0, 'B5', 0.5), (4, 0.5, 'A5', 0.5), (4, 1, 'G5', 0.5),
        (4, 1.5, 'E5', 0.5), (4, 2, 'D5', 1), (4, 3, 'E5', 1),
        (5, 0, 'B4', 0.5), (5, 0.5, 'E5', 0.5), (5, 1, 'G5', 0.5),
        (5, 1.5, 'A5', 0.5), (5, 2, 'B5', 2),
        (6, 0, 'E5', 0.25), (6, 0.25, 'E5', 0.25), (6, 0.5, 'G5', 0.5),
        (6, 1, 'A5', 0.5), (6, 1.5, 'B5', 0.5),
        (6, 2, 'A5', 0.5), (6, 2.5, 'G5', 0.5), (6, 3, 'E5', 1),
        (7, 0, 'E5', 1), (7, 1, 'D5', 0.5), (7, 1.5, 'E5', 0.5),
        (7, 2, 'E5', 2),
    ]
    for m_bar, beat_off, note_name, dur_beats in melody:
        pos = m_bar * bar + int(beat_off * beat)
        dur = 60.0 / bpm * dur_beats * 0.8
        mix_at(mix, lead_synth(n(note_name), dur) * 1.2, pos)

    return mix, "level_03_theme"


def create_level_03_boss():
    """Johnny Rotten + Sid Vicious boss — chaotic punk fury, 170 BPM.
    Progression: Am - F5 - C5 - G5
    """
    bpm = 170
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    total_bars = 8
    mix = np.zeros(bar * total_bars)

    punk_drums(mix, bpm, total_bars, intensity=2)
    # Extra crash chaos
    for b in range(total_bars):
        if b % 2 == 0:
            mix_at(mix, crash_cymbal(0.3), b * bar)

    bass_notes = [('A2',), ('F2',), ('C2',), ('G2',)]
    for ci, (root,) in enumerate(bass_notes):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            for i in range(8):
                mix_at(mix, punk_bass(n(root), 0.1, 0.06), pos + i * eighth)

    chords = [n('A3'), n('F3'), n('C3'), n('G3')]
    for ci, root in enumerate(chords):
        for rep in range(2):
            b = ci * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                mix_at(mix, power_chord(root, 0.2, 0.28), pos)
                mix_at(mix, power_chord(root, 0.12, 0.18), pos + eighth)

    # Chaotic lead
    patterns = [
        [(0, 'A5', 0.25), (0.25, 'G5', 0.25), (0.5, 'A5', 0.5),
         (1, 'C6', 0.5), (1.5, 'A5', 0.5), (2, 'G5', 1), (3, 'E5', 1)],
        [(0, 'F5', 0.5), (0.5, 'G5', 0.5), (1, 'A5', 0.5), (1.5, 'C6', 0.5),
         (2, 'A5', 1), (3, 'F5', 1)],
        [(0, 'C5', 0.5), (0.5, 'E5', 0.5), (1, 'G5', 0.5), (1.5, 'C6', 0.5),
         (2, 'G5', 0.5), (2.5, 'E5', 0.5), (3, 'C5', 1)],
        [(0, 'G5', 0.25), (0.25, 'A5', 0.25), (0.5, 'B5', 0.5),
         (1, 'D6', 0.5), (1.5, 'B5', 0.5), (2, 'G5', 1), (3, 'E5', 1)],
    ]
    for pi, pattern in enumerate(patterns):
        for rep in range(2):
            b = pi * 2 + rep
            for beat_off, note_name, dur_beats in pattern:
                pos = b * bar + int(beat_off * beat)
                dur = 60.0 / bpm * dur_beats * 0.75
                mix_at(mix, lead_synth(n(note_name), dur) * 1.4, pos)

    return mix, "level_03_boss"


# ── LEVEL 4: BLONDIE CONCERT AT CBGB ────────────────────────────────

def create_level_04_theme():
    """New wave punk-pop — 138 BPM, 8 bars.
    Blondie: cool + dangerous, driving beat, pop hooks.
    Progression: Dm - Bb - F - C (2 bars each)
    """
    bpm = 138
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    sixteenth = beat // 4
    total_bars = 8
    mix = np.zeros(bar * total_bars)

    new_wave_drums(mix, bpm, total_bars)

    # Bass: punchy new wave
    bass_prog = [('D2', 'D3'), ('A#2', 'A#3'), ('F2', 'F3'), ('C2', 'C3')]
    for ci, (lo, hi) in enumerate(bass_prog):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            for i in range(4):
                bp = pos + i * beat
                mix_at(mix, punk_bass(n(lo), 0.15, 0.1), bp)
                if i % 2 == 0:
                    mix_at(mix, punk_bass(n(hi), 0.08, 0.05), bp + eighth)

    # Synth arpeggios — new wave signature
    arp_chords = [
        [n('D4'), n('F4'), n('A4'), n('D5')],
        [n('A#3'), n('D4'), n('F4'), n('A#4')],
        [n('F3'), n('A3'), n('C4'), n('F4')],
        [n('C4'), n('E4'), n('G4'), n('C5')],
    ]
    for ci, chord in enumerate(arp_chords):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            for i in range(16):  # 16th note arps
                note = chord[i % len(chord)]
                npos = pos + i * sixteenth
                mix_at(mix, synth_arp(note, 0.06), npos)

    # Guitar: choppy new wave stabs
    gtr = [
        [n('D3'), n('F3'), n('A3')],
        [n('A#3'), n('D4'), n('F4')],
        [n('F3'), n('A3'), n('C4')],
        [n('C3'), n('E3'), n('G3')],
    ]
    for ci, chord in enumerate(gtr):
        for rep in range(2):
            b = ci * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                mix_at(mix, guitar_stab(chord, 0.06) * 0.9, pos + eighth)

    # Strings: minimal, cool
    strs = [
        [n('D4'), n('F4'), n('A4')],
        [n('A#3'), n('D4'), n('F4')],
        [n('F4'), n('A4'), n('C5')],
        [n('C4'), n('E4'), n('G4')],
    ]
    for ci, chord in enumerate(strs):
        dur = 60.0 / bpm * 8
        mix_at(mix, string_chord(chord, dur) * 0.6, ci * 2 * bar)

    # Lead: catchy Blondie-style melody
    melody = [
        (0, 0, 'A4', 0.5), (0, 0.5, 'D5', 0.5), (0, 1, 'F5', 1),
        (0, 2, 'E5', 0.5), (0, 2.5, 'D5', 0.5), (0, 3, 'C5', 1),
        (1, 0, 'D5', 1.5), (1, 1.5, 'C5', 0.5), (1, 2, 'A4', 2),
        (2, 0, 'A#4', 0.5), (2, 0.5, 'D5', 0.5), (2, 1, 'F5', 0.5),
        (2, 1.5, 'G5', 0.5), (2, 2, 'F5', 1), (2, 3, 'D5', 1),
        (3, 0, 'A#4', 1), (3, 1, 'C5', 0.5), (3, 1.5, 'D5', 0.5),
        (3, 2, 'F5', 2),
        (4, 0, 'F5', 0.5), (4, 0.5, 'G5', 0.5), (4, 1, 'A5', 1),
        (4, 2, 'G5', 0.5), (4, 2.5, 'F5', 0.5), (4, 3, 'D5', 1),
        (5, 0, 'C5', 1), (5, 1, 'D5', 0.5), (5, 1.5, 'F5', 0.5),
        (5, 2, 'D5', 2),
        (6, 0, 'A5', 0.5), (6, 0.5, 'G5', 0.5), (6, 1, 'F5', 0.5),
        (6, 1.5, 'D5', 0.5), (6, 2, 'C5', 1), (6, 3, 'D5', 1),
        (7, 0, 'A4', 2), (7, 2, 'D5', 2),
    ]
    for m_bar, beat_off, note_name, dur_beats in melody:
        pos = m_bar * bar + int(beat_off * beat)
        dur = 60.0 / bpm * dur_beats * 0.85
        mix_at(mix, lead_synth(n(note_name), dur), pos)

    return mix, "level_04_theme"


def create_level_04_boss():
    """Debbie Harry boss — intense new wave showdown, 142 BPM.
    Progression: Dm - Am - Bb - A7
    """
    bpm = 142
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    sixteenth = beat // 4
    total_bars = 8
    mix = np.zeros(bar * total_bars)

    new_wave_drums(mix, bpm, total_bars)
    # Extra intensity: crashes every 2 bars
    for b in range(0, total_bars, 2):
        mix_at(mix, crash_cymbal(0.3), b * bar)

    bass_prog = [('D2', 'D3'), ('A2', 'A3'), ('A#2', 'A#3'), ('A2', 'A3')]
    for ci, (lo, hi) in enumerate(bass_prog):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            for i in range(8):
                f = n(lo) if i % 2 == 0 else n(hi)
                mix_at(mix, punk_bass(f, 0.1, 0.06), pos + i * eighth)

    # Intense synth arps
    arp_chords = [
        [n('D4'), n('F4'), n('A4'), n('D5')],
        [n('A3'), n('C4'), n('E4'), n('A4')],
        [n('A#3'), n('D4'), n('F4'), n('A#4')],
        [n('A3'), n('C#4'), n('E4'), n('G4')],
    ]
    for ci, chord in enumerate(arp_chords):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            for i in range(16):
                note = chord[i % len(chord)]
                mix_at(mix, synth_arp(note, 0.05) * 1.2, pos + i * sixteenth)

    strs = [
        [n('D4'), n('F4'), n('A4')],
        [n('A3'), n('C4'), n('E4')],
        [n('A#3'), n('D4'), n('F4')],
        [n('A3'), n('C#4'), n('E4')],
    ]
    for ci, chord in enumerate(strs):
        dur = 60.0 / bpm * 8
        mix_at(mix, string_chord(chord, dur) * 0.9, ci * 2 * bar)

    patterns = [
        [(0, 'D5', 0.5), (0.5, 'F5', 0.5), (1, 'A5', 1),
         (2, 'G5', 0.5), (2.5, 'F5', 0.5), (3, 'D5', 1)],
        [(0, 'C5', 0.5), (0.5, 'E5', 0.5), (1, 'A5', 1),
         (2, 'G5', 0.5), (2.5, 'E5', 0.5), (3, 'C5', 1)],
        [(0, 'A#4', 0.5), (0.5, 'D5', 0.5), (1, 'F5', 1),
         (2, 'G5', 0.5), (2.5, 'F5', 0.5), (3, 'D5', 1)],
        [(0, 'A4', 0.5), (0.5, 'C#5', 0.5), (1, 'E5', 1),
         (2, 'G5', 0.5), (2.5, 'E5', 0.5), (3, 'C#5', 1)],
    ]
    for pi, pattern in enumerate(patterns):
        for rep in range(2):
            b = pi * 2 + rep
            for beat_off, note_name, dur_beats in pattern:
                pos = b * bar + int(beat_off * beat)
                dur = 60.0 / bpm * dur_beats * 0.8
                mix_at(mix, lead_synth(n(note_name), dur) * 1.2, pos)

    return mix, "level_04_boss"


# ── LEVEL 5: BEE GEES DISCO FLOOR ───────────────────────────────────

def create_level_05_theme():
    """Ultimate Bee Gees disco — 110 BPM, 8 bars.
    Tight disco grooves, falsetto energy, dance floor momentum.
    Progression: Fm7 - Bbm7 - Eb7 - Ab (2 bars each)
    """
    bpm = 110
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    sixteenth = beat // 4
    total_bars = 8
    mix = np.zeros(bar * total_bars)

    bee_gees_drums(mix, bpm, total_bars)

    # Bass: classic Bee Gees octave disco bounce
    bass_prog = [('F2', 'F3'), ('A#2', 'A#3'), ('D#2', 'D#3'), ('G#2', 'G#3')]
    for ci, (lo, hi) in enumerate(bass_prog):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            # Smooth octave bounce
            mix_at(mix, disco_bass(n(lo), 0.2, 0.14), pos)
            mix_at(mix, disco_bass(n(hi), 0.12, 0.08), pos + eighth)
            mix_at(mix, disco_bass(n(lo), 0.1, 0.06), pos + beat)
            mix_at(mix, disco_bass(n(hi), 0.15, 0.1), pos + beat + eighth)
            mix_at(mix, disco_bass(n(lo), 0.18, 0.12), pos + beat * 2)
            mix_at(mix, disco_bass(n(hi), 0.1, 0.06), pos + beat * 2 + eighth)
            mix_at(mix, disco_bass(n(lo), 0.08, 0.05), pos + beat * 3)
            mix_at(mix, disco_bass(n(hi), 0.12, 0.08), pos + beat * 3 + eighth)

    # Guitar: tight disco chucka
    gtr = [
        [n('F3'), n('G#3'), n('C4'), n('D#4')],
        [n('A#3'), n('C#4'), n('F4'), n('G#4')],
        [n('D#3'), n('G3'), n('A#3'), n('D4')],
        [n('G#3'), n('C4'), n('D#4'), n('G4')],
    ]
    for ci, chord in enumerate(gtr):
        for rep in range(2):
            b = ci * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                mix_at(mix, guitar_stab(chord, 0.07), pos + eighth)
                mix_at(mix, guitar_mute(chord), pos + 3 * sixteenth)

    # Lush strings — big Bee Gees production
    strs = [
        [n('F3'), n('G#3'), n('C4'), n('D#4'), n('F4')],
        [n('A#3'), n('C#4'), n('F4'), n('G#4')],
        [n('D#3'), n('G3'), n('A#3'), n('D4')],
        [n('G#3'), n('C4'), n('D#4'), n('G4'), n('C5')],
    ]
    for ci, chord in enumerate(strs):
        dur = 60.0 / bpm * 8
        mix_at(mix, string_chord(chord, dur) * 1.1, ci * 2 * bar)

    # Falsetto lead: Bee Gees signature
    melody = [
        (0, 0, 'C5', 0.5), (0, 0.5, 'D#5', 0.5), (0, 1, 'F5', 1),
        (0, 2, 'G5', 0.5), (0, 2.5, 'F5', 0.5), (0, 3, 'D#5', 1),
        (1, 0, 'C5', 1.5), (1, 1.5, 'D#5', 0.5), (1, 2, 'F5', 2),
        (2, 0, 'G5', 0.5), (2, 0.5, 'A#5', 0.5), (2, 1, 'G5', 1),
        (2, 2, 'F5', 0.5), (2, 2.5, 'D#5', 0.5), (2, 3, 'C5', 1),
        (3, 0, 'D#5', 1), (3, 1, 'F5', 0.5), (3, 1.5, 'G5', 0.5),
        (3, 2, 'A#5', 2),
        (4, 0, 'G#5', 0.5), (4, 0.5, 'G5', 0.5), (4, 1, 'F5', 1),
        (4, 2, 'D#5', 0.5), (4, 2.5, 'F5', 0.5), (4, 3, 'G5', 1),
        (5, 0, 'G#5', 1.5), (5, 1.5, 'G5', 0.5), (5, 2, 'F5', 2),
        (6, 0, 'C5', 0.5), (6, 0.5, 'D#5', 0.5), (6, 1, 'F5', 0.5),
        (6, 1.5, 'G5', 0.5), (6, 2, 'A#5', 1), (6, 3, 'G5', 1),
        (7, 0, 'F5', 1.5), (7, 1.5, 'D#5', 0.5), (7, 2, 'C5', 2),
    ]
    for m_bar, beat_off, note_name, dur_beats in melody:
        pos = m_bar * bar + int(beat_off * beat)
        dur = 60.0 / bpm * dur_beats * 0.85
        mix_at(mix, falsetto_lead(n(note_name), dur), pos)

    return mix, "level_05_theme"


def create_level_05_boss():
    """Bee Gees trio boss — ultimate disco showdown, 118 BPM.
    Progression: Fm - Db - Ab - Eb
    """
    bpm = 118
    beat = bts(1, bpm)
    bar = beat * 4
    eighth = beat // 2
    sixteenth = beat // 4
    total_bars = 8
    mix = np.zeros(bar * total_bars)

    bee_gees_drums(mix, bpm, total_bars)
    # Extra groove: double hi-hat intensity
    for b in range(total_bars):
        for i in range(8):
            mix_at(mix, hihat_closed(0.03) * 0.3, b * bar + i * eighth + sixteenth)

    bass_prog = [('F2', 'F3'), ('C#2', 'C#3'), ('G#2', 'G#3'), ('D#2', 'D#3')]
    for ci, (lo, hi) in enumerate(bass_prog):
        for rep in range(2):
            b = ci * 2 + rep
            pos = b * bar
            for i in range(8):
                f = n(lo) if i % 2 == 0 else n(hi)
                mix_at(mix, disco_bass(f, 0.13, 0.09), pos + i * eighth)

    gtr = [
        [n('F3'), n('G#3'), n('C4')],
        [n('C#3'), n('F3'), n('G#3')],
        [n('G#3'), n('C4'), n('D#4')],
        [n('D#3'), n('G3'), n('A#3')],
    ]
    for ci, chord in enumerate(gtr):
        for rep in range(2):
            b = ci * 2 + rep
            for i in range(4):
                pos = b * bar + i * beat
                mix_at(mix, guitar_stab(chord, 0.08) * 1.1, pos + eighth)
                mix_at(mix, guitar_mute(chord), pos + 3 * sixteenth)

    # Big strings
    strs = [
        [n('F3'), n('G#3'), n('C4'), n('F4')],
        [n('C#3'), n('F3'), n('G#3'), n('C#4')],
        [n('G#3'), n('C4'), n('D#4'), n('G#4')],
        [n('D#3'), n('G3'), n('A#3'), n('D#4')],
    ]
    for ci, chord in enumerate(strs):
        dur = 60.0 / bpm * 8
        mix_at(mix, string_chord(chord, dur) * 1.2, ci * 2 * bar)

    # Brass stabs for drama
    brass = [
        [n('F4'), n('G#4'), n('C5')],
        [n('C#4'), n('F4'), n('G#4')],
        [n('G#4'), n('C5'), n('D#5')],
        [n('D#4'), n('G4'), n('A#4')],
    ]
    for ci, chord in enumerate(brass):
        for rep in range(2):
            b = ci * 2 + rep
            mix_at(mix, brass_stab(chord, 0.12) * 1.2, b * bar)
            mix_at(mix, brass_stab(chord, 0.08) * 0.9, b * bar + beat * 2 + eighth)

    # Falsetto lead: intense, high
    patterns = [
        [(0, 'F5', 0.5), (0.5, 'G5', 0.5), (1, 'G#5', 1),
         (2, 'G5', 0.5), (2.5, 'F5', 0.5), (3, 'C5', 1)],
        [(0, 'C#5', 0.5), (0.5, 'F5', 0.5), (1, 'G#5', 1),
         (2, 'F5', 1), (3, 'C#5', 1)],
        [(0, 'G#5', 0.5), (0.5, 'A#5', 0.5), (1, 'C6', 1),
         (2, 'A#5', 0.5), (2.5, 'G#5', 0.5), (3, 'D#5', 1)],
        [(0, 'D#5', 0.5), (0.5, 'G5', 0.5), (1, 'A#5', 1),
         (2, 'G5', 0.5), (2.5, 'D#5', 0.5), (3, 'A#4', 1)],
    ]
    for pi, pattern in enumerate(patterns):
        for rep in range(2):
            b = pi * 2 + rep
            for beat_off, note_name, dur_beats in pattern:
                pos = b * bar + int(beat_off * beat)
                dur = 60.0 / bpm * dur_beats * 0.8
                mix_at(mix, falsetto_lead(n(note_name), dur) * 1.3, pos)

    return mix, "level_05_boss"


# ── Save ──────────────────────────────────────────────────────────────

def save_wav_stereo(filename, data):
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


# ── Main ──────────────────────────────────────────────────────────────

def main():
    np.random.seed(42)  # Reproducible noise
    print(f"Generating disco music to: {OUTPUT_DIR}")

    tracks = [
        create_menu_theme, create_level_theme, create_boss_theme,
        # Per-level themes
        create_level_01_theme, create_level_02_theme, create_level_03_theme,
        create_level_04_theme, create_level_05_theme,
        # Per-level boss themes
        create_level_01_boss, create_level_02_boss, create_level_03_boss,
        create_level_04_boss, create_level_05_boss,
    ]
    for gen_fn in tracks:
        data, name = gen_fn()
        wav_name = f"{name}.wav"
        save_wav_stereo(wav_name, data)
        duration = len(data) / RATE
        print(f"  [OK] {wav_name} ({duration:.1f}s)")

    print(f"\nDone! {len(tracks)} disco tracks generated.")


if __name__ == "__main__":
    main()
