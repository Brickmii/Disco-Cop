#!/usr/bin/env python3
"""Generate retro 8-bit style sound effects for Disco Cop.

Synthesizes 17 SFX files using numpy waveform generation:
square waves, noise, frequency sweeps, and envelopes for
a chunky retro arcade feel.

Usage:
    python create_sfx.py

Output: disco_cop/assets/audio/sfx/
"""

import struct
import wave
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "disco_cop" / "assets" / "audio" / "sfx"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RATE = 44100
MAX_AMP = 0.8


# ── Waveform Primitives ───────────────────────────────────────────────

def sine(freq: float, duration: float, rate: int = RATE) -> np.ndarray:
    t = np.linspace(0, duration, int(rate * duration), endpoint=False)
    return np.sin(2 * np.pi * freq * t)


def square(freq: float, duration: float, rate: int = RATE) -> np.ndarray:
    return np.sign(sine(freq, duration, rate))


def noise(duration: float, rate: int = RATE) -> np.ndarray:
    return np.random.uniform(-1, 1, int(rate * duration))


def saw(freq: float, duration: float, rate: int = RATE) -> np.ndarray:
    t = np.linspace(0, duration, int(rate * duration), endpoint=False)
    return 2.0 * (t * freq - np.floor(0.5 + t * freq))


def sweep(f_start: float, f_end: float, duration: float, wave_fn=sine, rate: int = RATE) -> np.ndarray:
    """Frequency sweep from f_start to f_end."""
    t = np.linspace(0, duration, int(rate * duration), endpoint=False)
    freqs = np.linspace(f_start, f_end, len(t))
    phase = 2 * np.pi * np.cumsum(freqs) / rate
    if wave_fn == sine:
        return np.sin(phase)
    else:
        return np.sign(np.sin(phase))


# ── Envelopes ─────────────────────────────────────────────────────────

def env_adsr(length: int, attack: float = 0.01, decay: float = 0.05,
             sustain: float = 0.6, release: float = 0.1) -> np.ndarray:
    """ADSR envelope."""
    a = min(int(attack * RATE), length)
    remaining = length - a
    d = min(int(decay * RATE), remaining)
    remaining -= d
    r = min(int(release * RATE), remaining)
    s = remaining - r

    envelope = np.zeros(length)
    pos = 0
    if a > 0:
        envelope[pos:pos + a] = np.linspace(0, 1, a)
        pos += a
    if d > 0:
        envelope[pos:pos + d] = np.linspace(1, sustain, d)
        pos += d
    if s > 0:
        envelope[pos:pos + s] = sustain
        pos += s
    if r > 0:
        envelope[pos:pos + r] = np.linspace(sustain, 0, r)

    return envelope


def env_decay(length: int, decay_time: float = 0.3) -> np.ndarray:
    """Simple exponential decay."""
    t = np.linspace(0, decay_time * (length / (RATE * decay_time)), length)
    return np.exp(-t / decay_time)


def env_punch(length: int) -> np.ndarray:
    """Sharp attack, fast decay — for impacts."""
    return env_adsr(length, attack=0.002, decay=0.03, sustain=0.3, release=0.08)


# ── Helper ────────────────────────────────────────────────────────────

def save_wav(filename: str, data: np.ndarray, rate: int = RATE):
    """Save float array as 16-bit WAV."""
    # Normalize and clamp
    peak = np.max(np.abs(data))
    if peak > 0:
        data = data / peak * MAX_AMP
    data = np.clip(data, -1, 1)
    samples = (data * 32767).astype(np.int16)

    path = OUTPUT_DIR / filename
    with wave.open(str(path), 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(samples.tobytes())


# ── SFX Generators ────────────────────────────────────────────────────

def sfx_shoot_pistol():
    """Short snappy pop."""
    dur = 0.12
    sig = square(800, dur) * 0.5 + noise(dur) * 0.3
    sig += sweep(1200, 200, dur, square) * 0.3
    env = env_adsr(len(sig), attack=0.001, decay=0.02, sustain=0.2, release=0.06)
    save_wav("shoot_pistol.wav", sig * env)


def sfx_shoot_shotgun():
    """Wide boom, bass-heavy."""
    dur = 0.2
    sig = noise(dur) * 0.6 + square(150, dur) * 0.4
    sig += sweep(600, 80, dur, square) * 0.3
    env = env_adsr(len(sig), attack=0.001, decay=0.04, sustain=0.3, release=0.12)
    save_wav("shoot_shotgun.wav", sig * env)


def sfx_shoot_smg():
    """Rapid staccato tap."""
    dur = 0.06
    sig = square(1000, dur) * 0.5 + noise(dur) * 0.4
    sig += sweep(1500, 600, dur, square) * 0.2
    env = env_adsr(len(sig), attack=0.001, decay=0.01, sustain=0.3, release=0.02)
    save_wav("shoot_smg.wav", sig * env)


def sfx_shoot_sniper():
    """Sharp crack with echo tail."""
    dur = 0.35
    # Sharp crack
    crack = noise(0.02) * 0.8
    # Descending tone
    tail = sweep(2000, 200, 0.33, square) * 0.3
    tail_env = env_decay(len(tail), 0.25)
    tail = tail * tail_env
    sig = np.concatenate([crack, tail])
    env = env_adsr(len(sig), attack=0.001, decay=0.01, sustain=0.25, release=0.2)
    save_wav("shoot_sniper.wav", sig * env)


def sfx_shoot_rifle():
    """Medium punch."""
    dur = 0.1
    sig = square(600, dur) * 0.5 + noise(dur) * 0.35
    sig += sweep(900, 300, dur, square) * 0.25
    env = env_adsr(len(sig), attack=0.001, decay=0.02, sustain=0.3, release=0.05)
    save_wav("shoot_rifle.wav", sig * env)


def sfx_shoot_launcher():
    """Deep thud/whomp."""
    dur = 0.3
    sig = sweep(300, 50, dur, sine) * 0.6 + noise(dur) * 0.3
    sig += square(80, dur) * 0.3
    env = env_adsr(len(sig), attack=0.005, decay=0.06, sustain=0.3, release=0.15)
    save_wav("shoot_launcher.wav", sig * env)


def sfx_impact_hit():
    """Metallic ping."""
    dur = 0.1
    sig = sine(1200, dur) * 0.4 + square(800, dur) * 0.3 + noise(dur) * 0.2
    env = env_punch(len(sig))
    save_wav("impact_hit.wav", sig * env)


def sfx_impact_crit():
    """Louder ping + crunch."""
    dur = 0.15
    sig = sine(1600, dur) * 0.4 + square(1000, dur) * 0.3 + noise(dur) * 0.4
    sig += sweep(2000, 500, dur, square) * 0.2
    env = env_punch(len(sig))
    save_wav("impact_crit.wav", sig * env)


def sfx_explosion():
    """Bass boom with crackle."""
    dur = 0.5
    boom = sweep(200, 30, 0.3, sine) * 0.7
    boom_env = env_decay(len(boom), 0.2)
    crackle = noise(0.4) * 0.4
    crackle_env = env_decay(len(crackle), 0.3)
    # Pad to same length
    total = int(RATE * dur)
    sig = np.zeros(total)
    sig[:len(boom)] += boom * boom_env
    sig[:len(crackle)] += crackle * crackle_env
    sig += square(60, dur) * 0.2 * env_decay(total, 0.15)
    save_wav("explosion.wav", sig)


def sfx_enemy_death():
    """Short descending tone."""
    dur = 0.25
    sig = sweep(800, 100, dur, square) * 0.5
    sig += noise(dur) * 0.15
    env = env_adsr(len(sig), attack=0.001, decay=0.05, sustain=0.3, release=0.1)
    save_wav("enemy_death.wav", sig * env)


def sfx_player_hurt():
    """Grunt/thud — low frequency punch."""
    dur = 0.15
    sig = sweep(400, 150, dur, square) * 0.5 + noise(dur) * 0.3
    sig += sine(100, dur) * 0.3
    env = env_punch(len(sig))
    save_wav("player_hurt.wav", sig * env)


def sfx_player_death():
    """Longer descending tone."""
    dur = 0.6
    sig = sweep(600, 50, dur, square) * 0.4
    sig += sweep(400, 30, dur, sine) * 0.3
    sig += noise(dur) * 0.1
    env = env_adsr(len(sig), attack=0.005, decay=0.1, sustain=0.3, release=0.3)
    save_wav("player_death.wav", sig * env)


def sfx_shield_break():
    """Glass shatter + electric zap."""
    dur = 0.3
    # Shatter: high noise burst
    shatter = noise(0.08) * 0.7
    shatter_env = env_decay(len(shatter), 0.06)
    # Zap: descending square chirp
    zap = sweep(3000, 200, 0.22, square) * 0.4
    zap_env = env_decay(len(zap), 0.15)
    total = int(RATE * dur)
    sig = np.zeros(total)
    sig[:len(shatter)] += shatter * shatter_env
    sig[:len(zap)] += zap * zap_env
    # Tinkle: high sine hits
    for i in range(5):
        offset = int(RATE * i * 0.04)
        freq = 2000 + i * 500
        tone_dur = 0.03
        tone = sine(freq, tone_dur) * 0.2
        tone_len = len(tone)
        if offset + tone_len <= total:
            sig[offset:offset + tone_len] += tone * env_decay(tone_len, 0.02)
    save_wav("shield_break.wav", sig)


def sfx_shield_recharge():
    """Rising hum."""
    dur = 0.4
    sig = sweep(200, 1200, dur, sine) * 0.4
    sig += sweep(300, 1800, dur, sine) * 0.2  # Harmonic
    env = env_adsr(len(sig), attack=0.05, decay=0.05, sustain=0.7, release=0.15)
    save_wav("shield_recharge.wav", sig * env)


def sfx_loot_pickup():
    """Bright ascending chime."""
    dur = 0.3
    # Two-note chime: C5 then E5
    note1 = sine(523, 0.12) * 0.5  # C5
    note2 = sine(659, 0.18) * 0.5  # E5
    sig = np.concatenate([note1, note2])
    # Add sparkle
    sig += sweep(1000, 3000, dur, sine)[:len(sig)] * 0.15
    env = env_adsr(len(sig), attack=0.005, decay=0.03, sustain=0.6, release=0.1)
    save_wav("loot_pickup.wav", sig * env)


def sfx_weapon_swap():
    """Click/rack sound."""
    dur = 0.08
    sig = noise(dur) * 0.5 + square(600, dur) * 0.3
    env = env_adsr(len(sig), attack=0.001, decay=0.015, sustain=0.2, release=0.03)
    save_wav("weapon_swap.wav", sig * env)


def sfx_menu_select():
    """UI blip."""
    dur = 0.08
    sig = sine(880, dur) * 0.4 + square(880, dur) * 0.2
    env = env_adsr(len(sig), attack=0.002, decay=0.01, sustain=0.5, release=0.03)
    save_wav("menu_select.wav", sig * env)


# ── Main ──────────────────────────────────────────────────────────────

GENERATORS = [
    ("shoot_pistol", sfx_shoot_pistol),
    ("shoot_shotgun", sfx_shoot_shotgun),
    ("shoot_smg", sfx_shoot_smg),
    ("shoot_sniper", sfx_shoot_sniper),
    ("shoot_rifle", sfx_shoot_rifle),
    ("shoot_launcher", sfx_shoot_launcher),
    ("impact_hit", sfx_impact_hit),
    ("impact_crit", sfx_impact_crit),
    ("explosion", sfx_explosion),
    ("enemy_death", sfx_enemy_death),
    ("player_hurt", sfx_player_hurt),
    ("player_death", sfx_player_death),
    ("shield_break", sfx_shield_break),
    ("shield_recharge", sfx_shield_recharge),
    ("loot_pickup", sfx_loot_pickup),
    ("weapon_swap", sfx_weapon_swap),
    ("menu_select", sfx_menu_select),
]


def main():
    print(f"Generating {len(GENERATORS)} SFX to: {OUTPUT_DIR}")
    for name, gen_fn in GENERATORS:
        gen_fn()
        print(f"  [OK] {name}.wav")
    print(f"\nDone! {len(GENERATORS)} SFX files generated.")


if __name__ == "__main__":
    main()
