"""Sitar synthesizer with string resonance, meend, and gamak.

Models the sitar's main playing string, sympathetic strings (taraf), jaw bridge
(jawari) buzz, and characteristic ornamental techniques.
"""

from __future__ import annotations

import numpy as np

from swara.models import SwaraNote


class SitarSynthesizer:
    """Sitar sound synthesis using physical-modeling-inspired additive synthesis.

    Features:
    - String resonance with jawari (bridge buzz) simulation
    - Meend (glissando/pitch bend between notes)
    - Gamak (rapid oscillation around a note)
    - Sympathetic string resonance (taraf)
    - Chikari (rhythmic drone strings)
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        sa_frequency: float = 261.63,
        jawari_amount: float = 0.3,
        sympathetic_gain: float = 0.15,
    ) -> None:
        self.sample_rate = sample_rate
        self.sa_frequency = sa_frequency
        self.jawari_amount = jawari_amount
        self.sympathetic_gain = sympathetic_gain
        # Sympathetic string tuning ratios (13 taraf strings typical)
        self._taraf_ratios = [
            1.0, 9 / 8, 81 / 64, 4 / 3, 3 / 2, 27 / 16, 243 / 128,
            2.0, 9 / 4, 81 / 32, 8 / 3, 3.0, 27 / 8,
        ]

    def synthesize_note(self, note: SwaraNote) -> np.ndarray:
        """Synthesize a single sitar note with optional ornaments."""
        n_samples = int(self.sample_rate * note.duration)
        t = np.linspace(0, note.duration, n_samples, endpoint=False)
        freq = note.frequency

        # Main string sound
        signal = self._plucked_string(t, freq, note.duration, note.amplitude)

        # Add jawari buzz
        signal = self._apply_jawari(signal, t, freq)

        # Add sympathetic string resonance
        signal += self._sympathetic_resonance(t, freq, note.duration)

        # Apply meend if specified
        if note.has_meend and note.meend_target is not None:
            signal = self._apply_meend(t, freq, note, signal)

        # Apply gamak if specified
        if note.has_gamak:
            signal = self._apply_gamak(t, freq, signal)

        return signal

    def synthesize_phrase(self, notes: list[SwaraNote]) -> np.ndarray:
        """Synthesize a sequence of notes as a continuous phrase."""
        segments: list[np.ndarray] = []
        for i, note in enumerate(notes):
            seg = self.synthesize_note(note)
            # Apply slight crossfade between consecutive notes
            if segments and len(segments[-1]) > 200 and len(seg) > 200:
                fade_len = min(200, len(segments[-1]), len(seg))
                fade_out = np.linspace(1.0, 0.0, fade_len)
                fade_in = np.linspace(0.0, 1.0, fade_len)
                segments[-1][-fade_len:] *= fade_out
                seg[:fade_len] *= fade_in
            segments.append(seg)
        return np.concatenate(segments) if segments else np.array([], dtype=np.float64)

    def synthesize_chikari(self, duration: float, tempo_bpm: float = 120.0) -> np.ndarray:
        """Synthesize chikari (rhythmic drone string) strokes."""
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        beat_interval = 60.0 / tempo_bpm
        signal = np.zeros(n_samples)

        # Sa and Pa drone frequencies
        sa_freq = self.sa_frequency * 2  # High octave Sa
        pa_freq = self.sa_frequency * 3  # High octave Pa

        current_time = 0.0
        while current_time < duration:
            start_idx = int(current_time * self.sample_rate)
            stroke_dur = min(0.08, duration - current_time)
            stroke_samples = int(stroke_dur * self.sample_rate)
            if start_idx + stroke_samples > n_samples:
                break
            st = np.linspace(0, stroke_dur, stroke_samples, endpoint=False)
            env = np.exp(-15 * st / stroke_dur)
            stroke = 0.3 * (np.sin(2 * np.pi * sa_freq * st) + 0.5 * np.sin(2 * np.pi * pa_freq * st)) * env
            signal[start_idx : start_idx + stroke_samples] += stroke
            current_time += beat_interval

        return signal * 0.4

    def _plucked_string(
        self, t: np.ndarray, freq: float, duration: float, amplitude: float
    ) -> np.ndarray:
        """Model a plucked string with Karplus-Strong-inspired harmonic series."""
        # Attack transient
        attack_env = 1.0 - np.exp(-50 * t)
        # Decay envelope
        decay_env = np.exp(-2.5 * t / duration)
        envelope = attack_env * decay_env * amplitude

        # Harmonic series with inharmonicity (characteristic of sitar)
        signal = np.zeros_like(t)
        n_harmonics = min(15, int(self.sample_rate / (2 * freq)))
        for n in range(1, n_harmonics + 1):
            # Slight inharmonicity factor
            inharmonicity = 1.0 + 0.0003 * n * n
            harmonic_freq = freq * n * inharmonicity
            if harmonic_freq >= self.sample_rate / 2:
                break
            # Higher harmonics decay faster
            harmonic_amp = 1.0 / (n ** 0.8)
            harmonic_decay = np.exp(-(1.0 + 0.5 * n) * t / duration)
            signal += harmonic_amp * np.sin(2 * np.pi * harmonic_freq * t) * harmonic_decay

        return signal * envelope

    def _apply_jawari(self, signal: np.ndarray, t: np.ndarray, freq: float) -> np.ndarray:
        """Apply jawari (bridge buzz) effect.

        The flat bridge of the sitar causes strings to buzz against it,
        creating the characteristic bright, buzzy timbre.
        """
        if self.jawari_amount <= 0:
            return signal
        # Soft clipping to simulate bridge contact
        threshold = 1.0 - self.jawari_amount * 0.5
        buzzed = np.where(
            np.abs(signal) > threshold,
            np.sign(signal) * (threshold + (np.abs(signal) - threshold) * 0.3),
            signal,
        )
        # Add high-frequency buzz harmonics
        buzz = self.jawari_amount * 0.1 * np.sin(2 * np.pi * freq * 4 * t) * np.abs(signal)
        return buzzed + buzz

    def _sympathetic_resonance(
        self, t: np.ndarray, played_freq: float, duration: float
    ) -> np.ndarray:
        """Simulate sympathetic string (taraf) resonance."""
        resonance = np.zeros_like(t)
        for ratio in self._taraf_ratios:
            taraf_freq = self.sa_frequency * ratio
            # Sympathetic strings resonate when close to a harmonic of the played note
            for harmonic in range(1, 6):
                freq_diff = abs(played_freq * harmonic - taraf_freq)
                if freq_diff < 5.0:  # Within 5 Hz
                    coupling = max(0, 1.0 - freq_diff / 5.0)
                    env = coupling * np.exp(-3.0 * t / duration)
                    resonance += (
                        self.sympathetic_gain
                        * coupling
                        * np.sin(2 * np.pi * taraf_freq * t)
                        * env
                    )
        return resonance

    def _apply_meend(
        self, t: np.ndarray, start_freq: float, note: SwaraNote, signal: np.ndarray
    ) -> np.ndarray:
        """Apply meend (glissando) from current note to target note.

        Meend is a smooth glide between notes, a defining ornament of sitar playing.
        """
        if note.meend_target is None:
            return signal

        target_note = SwaraNote(swara=note.meend_target, octave=note.octave)
        end_freq = target_note.frequency

        # Create pitch glide envelope (starts after 30% of the note)
        glide_start = 0.3
        glide_portion = np.clip((t / note.duration - glide_start) / (1 - glide_start), 0, 1)
        # Smooth S-curve
        glide = glide_portion ** 2 * (3 - 2 * glide_portion)

        freq_envelope = start_freq + (end_freq - start_freq) * glide
        phase = np.cumsum(2 * np.pi * freq_envelope / self.sample_rate)

        amplitude_env = np.exp(-2.0 * t / note.duration) * note.amplitude
        meend_signal = np.sin(phase) * amplitude_env

        # Blend: original for first 30%, then transition to meend
        blend = np.clip(t / note.duration / glide_start, 0, 1)
        return signal * (1 - blend * 0.7) + meend_signal * blend * 0.7

    def _apply_gamak(self, t: np.ndarray, freq: float, signal: np.ndarray) -> np.ndarray:
        """Apply gamak (rapid oscillation) to a note.

        Gamak is a rapid oscillation between adjacent notes, giving intensity
        and expressiveness.
        """
        # Oscillation rate: ~5-8 Hz
        gamak_rate = 6.0
        # Depth: about a quarter tone
        gamak_depth = freq * 0.03
        modulation = gamak_depth * np.sin(2 * np.pi * gamak_rate * t)

        # Apply frequency modulation
        phase_mod = np.cumsum(2 * np.pi * modulation / self.sample_rate)
        gamak_signal = signal * np.cos(phase_mod)

        return gamak_signal
