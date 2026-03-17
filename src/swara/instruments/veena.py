"""Veena (Saraswati Veena) synthesizer with sustained notes and gamakas.

Models the Saraswati Veena's warm, sustained tone with characteristic
fret-pull gamakas and the resonance of the twin gourd resonators.
"""

from __future__ import annotations

import numpy as np

from swara.models import SwaraNote, Swara, SwaraVariant


class VeenaSynthesizer:
    """Synthesizer for Saraswati Veena using harmonic synthesis.

    Features:
    - Warm, sustained tone with rich harmonics
    - Gamaka (oscillatory ornaments unique to Carnatic music)
    - Kampita (shake/vibrato)
    - Jaru (slide between notes)
    - Nokku (hammer-on)
    - Dual-gourd resonance modeling
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        sa_frequency: float = 261.63,
        resonance_factor: float = 0.4,
    ) -> None:
        self.sample_rate = sample_rate
        self.sa_frequency = sa_frequency
        self.resonance_factor = resonance_factor

    def synthesize_note(
        self,
        note: SwaraNote,
        gamaka_type: str = "none",
        gamaka_depth: float = 0.5,
    ) -> np.ndarray:
        """Synthesize a veena note with optional gamaka.

        Args:
            note: The swara note to synthesize.
            gamaka_type: One of 'none', 'kampita', 'jaru', 'sphurita', 'pratyahata'.
            gamaka_depth: Intensity of the gamaka (0-1).
        """
        n_samples = int(self.sample_rate * note.duration)
        t = np.linspace(0, note.duration, n_samples, endpoint=False)
        freq = note.frequency

        # Base veena tone
        signal = self._veena_tone(t, freq, note.duration, note.amplitude)

        # Apply gamaka
        gamaka_map = {
            "kampita": self._gamaka_kampita,
            "jaru": self._gamaka_jaru,
            "sphurita": self._gamaka_sphurita,
            "pratyahata": self._gamaka_pratyahata,
        }
        if gamaka_type in gamaka_map:
            signal = gamaka_map[gamaka_type](signal, t, freq, note.duration, gamaka_depth)

        # General gamak flag from model
        if note.has_gamak and gamaka_type == "none":
            signal = self._gamaka_kampita(signal, t, freq, note.duration, 0.4)

        # Add gourd resonance
        signal = self._apply_gourd_resonance(signal, t, freq, note.duration)

        return signal

    def synthesize_phrase(
        self, notes: list[SwaraNote], gamakas: list[str] | None = None
    ) -> np.ndarray:
        """Synthesize a phrase of veena notes with optional gamakas per note."""
        if gamakas is None:
            gamakas = ["none"] * len(notes)

        segments: list[np.ndarray] = []
        for note, gam in zip(notes, gamakas):
            seg = self.synthesize_note(note, gamaka_type=gam)
            # Crossfade between notes for legato feel
            if segments and len(segments[-1]) > 300 and len(seg) > 300:
                fade_len = min(300, len(segments[-1]), len(seg))
                segments[-1][-fade_len:] *= np.linspace(1.0, 0.0, fade_len)
                seg[:fade_len] *= np.linspace(0.0, 1.0, fade_len)
            segments.append(seg)
        return np.concatenate(segments) if segments else np.array([], dtype=np.float64)

    def synthesize_sustained(
        self, note: SwaraNote, sustain_factor: float = 1.5
    ) -> np.ndarray:
        """Synthesize a long, sustained veena note (for alap-style playing)."""
        extended = SwaraNote(
            swara=note.swara,
            variant=note.variant,
            octave=note.octave,
            duration=note.duration * sustain_factor,
            amplitude=note.amplitude,
            has_gamak=note.has_gamak,
        )
        return self.synthesize_note(extended, gamaka_type="kampita", gamaka_depth=0.25)

    def _veena_tone(
        self, t: np.ndarray, freq: float, duration: float, amplitude: float
    ) -> np.ndarray:
        """Generate the core veena timbre.

        The veena has a warmer, rounder tone than sitar, with strong
        fundamentals and gentler upper harmonics.
        """
        # Soft attack, long sustain
        attack_time = min(0.02, duration * 0.1)
        attack = np.clip(t / attack_time, 0, 1)
        # Gentle decay
        decay = np.exp(-0.8 * t / duration)
        envelope = attack * decay * amplitude

        signal = np.zeros_like(t)
        n_harmonics = min(12, int(self.sample_rate / (2 * freq)))

        for n in range(1, n_harmonics + 1):
            harmonic_freq = freq * n
            if harmonic_freq >= self.sample_rate / 2:
                break
            # Veena has strong even harmonics and gentle rolloff
            if n % 2 == 0:
                amp = 0.7 / (n ** 0.6)
            else:
                amp = 1.0 / (n ** 0.7)
            harmonic_decay = np.exp(-(0.3 + 0.2 * n) * t / duration)
            signal += amp * np.sin(2 * np.pi * harmonic_freq * t) * harmonic_decay

        return signal * envelope

    def _gamaka_kampita(
        self,
        signal: np.ndarray,
        t: np.ndarray,
        freq: float,
        duration: float,
        depth: float,
    ) -> np.ndarray:
        """Kampita gamaka - oscillatory shake around the note.

        This is the most common veena gamaka, involving rapid pulling
        and releasing of the string on the fret.
        """
        rate = 5.0 + depth * 3.0  # 5-8 Hz
        mod_depth = freq * 0.04 * depth
        modulation = mod_depth * np.sin(2 * np.pi * rate * t)
        # Gradually increase gamaka intensity
        ramp = np.clip(t / (duration * 0.2), 0, 1)
        phase_mod = np.cumsum(2 * np.pi * modulation * ramp / self.sample_rate)
        return signal * np.cos(phase_mod)

    def _gamaka_jaru(
        self,
        signal: np.ndarray,
        t: np.ndarray,
        freq: float,
        duration: float,
        depth: float,
    ) -> np.ndarray:
        """Jaru gamaka - smooth slide to the note from below or above."""
        slide_duration = min(duration * 0.3, 0.2)
        slide_depth = freq * 0.1 * depth
        slide = slide_depth * np.exp(-t / slide_duration)
        phase_mod = np.cumsum(2 * np.pi * slide / self.sample_rate)
        return signal * np.cos(phase_mod)

    def _gamaka_sphurita(
        self,
        signal: np.ndarray,
        t: np.ndarray,
        freq: float,
        duration: float,
        depth: float,
    ) -> np.ndarray:
        """Sphurita gamaka - a single deflection and return."""
        peak_time = duration * 0.2
        deflection = depth * freq * 0.05 * np.exp(-((t - peak_time) ** 2) / (2 * (duration * 0.1) ** 2))
        phase_mod = np.cumsum(2 * np.pi * deflection / self.sample_rate)
        return signal * np.cos(phase_mod)

    def _gamaka_pratyahata(
        self,
        signal: np.ndarray,
        t: np.ndarray,
        freq: float,
        duration: float,
        depth: float,
    ) -> np.ndarray:
        """Pratyahata gamaka - touch upper note and return."""
        # Brief upward deflection followed by return
        peak_time = duration * 0.15
        width = duration * 0.08
        deflection = depth * freq * 0.08 * np.exp(-((t - peak_time) ** 2) / (2 * width ** 2))
        phase_mod = np.cumsum(2 * np.pi * deflection / self.sample_rate)
        return signal * np.cos(phase_mod)

    def _apply_gourd_resonance(
        self, signal: np.ndarray, t: np.ndarray, freq: float, duration: float
    ) -> np.ndarray:
        """Model the resonance of the veena's twin gourd chambers.

        The main gourd at the base and the secondary gourd at the scroll
        add body resonance and sustain.
        """
        # Primary resonance around 100-200 Hz
        res_freq_1 = 130.0
        # Secondary around 250-400 Hz
        res_freq_2 = 300.0

        res1 = (
            self.resonance_factor
            * 0.05
            * np.sin(2 * np.pi * res_freq_1 * t)
            * np.exp(-1.0 * t / duration)
            * np.abs(signal)
        )
        res2 = (
            self.resonance_factor
            * 0.03
            * np.sin(2 * np.pi * res_freq_2 * t)
            * np.exp(-1.5 * t / duration)
            * np.abs(signal)
        )

        return signal + res1 + res2
