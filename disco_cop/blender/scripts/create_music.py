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

    tracks = [create_menu_theme, create_level_theme, create_boss_theme]
    for gen_fn in tracks:
        data, name = gen_fn()
        wav_name = f"{name}.wav"
        save_wav_stereo(wav_name, data)
        duration = len(data) / RATE
        print(f"  [OK] {wav_name} ({duration:.1f}s)")

    print(f"\nDone! {len(tracks)} disco tracks generated.")


if __name__ == "__main__":
    main()
