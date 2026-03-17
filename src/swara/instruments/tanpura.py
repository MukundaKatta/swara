"""Tanpura drone synthesizer providing Sa-Pa-Sa continuous drone.

Models the tanpura's unique buzzing drone produced by the jawari bridge
and cotton thread (jiva) that creates the rich harmonic texture
fundamental to Indian classical music performance.
"""

from __future__ import annotations

import numpy as np


class TanpuraDrone:
    """Synthesizer for tanpura drone with Sa-Pa-Sa tuning.

    Features:
    - Standard Sa-Pa-Sa-Sa (or Sa-Ma-Sa-Sa) four-string tuning
    - Jawari bridge simulation for characteristic buzz
    - Jiva thread modeling for harmonic enrichment
    - Continuous cyclical drone generation
    - Natural string pluck timing variation
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        sa_frequency: float = 261.63,
        tuning: str = "sa_pa",
        jawari_amount: float = 0.4,
        jiva_amount: float = 0.3,
    ) -> None:
        """Initialize tanpura drone.

        Args:
            sample_rate: Audio sample rate.
            sa_frequency: Frequency of Sa (default middle C).
            tuning: Tuning scheme - 'sa_pa' for Sa-Pa-Sa-Sa or 'sa_ma' for Sa-Ma-Sa-Sa.
            jawari_amount: Amount of bridge buzz (0-1).
            jiva_amount: Amount of jiva thread effect (0-1).
        """
        self.sample_rate = sample_rate
        self.sa_frequency = sa_frequency
        self.jawari_amount = jawari_amount
        self.jiva_amount = jiva_amount

        # String frequencies based on tuning
        if tuning == "sa_ma":
            self.string_freqs = [
                sa_frequency,       # Pa string (low octave) - actually first string is Pa/Ma
                sa_frequency * 4 / 3,  # Ma
                sa_frequency,       # Sa
                sa_frequency / 2,   # Sa (low octave)
            ]
        else:  # sa_pa (default)
            self.string_freqs = [
                sa_frequency,       # First string - Sa
                sa_frequency * 3 / 2,  # Pa
                sa_frequency,       # Sa
                sa_frequency / 2,   # Sa (low octave, mandra saptak)
            ]

    def generate_drone(self, duration: float, amplitude: float = 0.6) -> np.ndarray:
        """Generate a continuous tanpura drone for the given duration.

        The four strings are plucked in sequence with natural timing
        to create the characteristic cyclical drone.
        """
        n_samples = int(self.sample_rate * duration)
        signal = np.zeros(n_samples)

        # Each string cycle takes about 0.8-1.2 seconds
        string_interval = 0.9  # seconds between string plucks
        cycle_duration = string_interval * 4  # one full cycle

        current_time = 0.0
        string_idx = 0

        while current_time < duration:
            freq = self.string_freqs[string_idx % 4]
            # Natural timing variation
            jitter = np.random.uniform(-0.05, 0.05)
            pluck_time = current_time + jitter

            if pluck_time < 0:
                pluck_time = 0.0

            start_idx = int(pluck_time * self.sample_rate)
            if start_idx >= n_samples:
                break

            # Each string rings for about 3-4 seconds
            ring_duration = min(3.5, duration - pluck_time)
            ring_samples = int(ring_duration * self.sample_rate)
            end_idx = min(start_idx + ring_samples, n_samples)
            actual_samples = end_idx - start_idx

            if actual_samples <= 0:
                break

            t = np.linspace(0, ring_duration, actual_samples, endpoint=False)

            # Generate string sound
            string_sound = self._tanpura_string(t, freq, ring_duration, amplitude)

            signal[start_idx:end_idx] += string_sound[:actual_samples]

            current_time += string_interval
            string_idx += 1

        # Normalize to prevent clipping
        peak = np.max(np.abs(signal))
        if peak > 0:
            signal = signal / peak * amplitude

        return signal

    def generate_single_cycle(self, amplitude: float = 0.6) -> np.ndarray:
        """Generate one complete pluck cycle of all four strings."""
        return self.generate_drone(duration=4.0, amplitude=amplitude)

    def _tanpura_string(
        self, t: np.ndarray, freq: float, duration: float, amplitude: float
    ) -> np.ndarray:
        """Synthesize a single tanpura string pluck.

        Models the slow attack, long sustain, and rich harmonic content
        characteristic of the tanpura.
        """
        # Soft attack (tanpura strings are plucked gently)
        attack_time = 0.05
        attack = np.clip(t / attack_time, 0, 1)
        # Very slow decay (strings ring long)
        decay = np.exp(-0.5 * t / duration)
        envelope = attack * decay * amplitude

        # Fundamental and harmonics
        signal = np.zeros_like(t)
        n_harmonics = min(20, int(self.sample_rate / (2 * freq)))

        for n in range(1, n_harmonics + 1):
            harmonic_freq = freq * n
            if harmonic_freq >= self.sample_rate / 2:
                break

            # Tanpura has a unique harmonic profile due to jawari
            # Even harmonics are relatively strong
            if n == 1:
                amp = 1.0
            elif n <= 4:
                amp = 0.6 / n
            else:
                amp = 0.3 / (n ** 0.5)

            # Each harmonic decays at its own rate
            h_decay = np.exp(-(0.3 + 0.15 * n) * t / duration)
            # Slight phase randomization for natural sound
            phase = np.random.uniform(0, 2 * np.pi)
            signal += amp * np.sin(2 * np.pi * harmonic_freq * t + phase) * h_decay

        signal *= envelope

        # Apply jawari effect
        signal = self._apply_jawari(signal, t, freq, duration)

        # Apply jiva thread effect
        signal = self._apply_jiva(signal, t, freq, duration)

        return signal

    def _apply_jawari(
        self, signal: np.ndarray, t: np.ndarray, freq: float, duration: float
    ) -> np.ndarray:
        """Apply jawari (bridge buzz) effect.

        The tanpura bridge is carefully curved so strings buzz against it,
        creating the rich, shimmering harmonic wash.
        """
        if self.jawari_amount <= 0:
            return signal

        # Asymmetric soft clipping (string lifts off bridge on one side)
        threshold = 0.6 * (1 - self.jawari_amount * 0.4)
        buzzed = np.copy(signal)
        mask = signal > threshold
        buzzed[mask] = threshold + (signal[mask] - threshold) * 0.2

        # This clipping generates additional harmonics naturally
        # Add a subtle time-varying buzz
        buzz_freq = freq * 0.5  # Sub-harmonic buzz
        buzz = (
            self.jawari_amount
            * 0.03
            * np.sin(2 * np.pi * buzz_freq * t)
            * np.exp(-1.0 * t / duration)
        )

        return buzzed + buzz

    def _apply_jiva(
        self, signal: np.ndarray, t: np.ndarray, freq: float, duration: float
    ) -> np.ndarray:
        """Apply jiva (cotton thread) effect.

        A cotton thread placed between the string and bridge modifies
        the buzzing pattern, creating a richer, more diffuse harmonic
        wash that is the signature tanpura sound.
        """
        if self.jiva_amount <= 0:
            return signal

        # The jiva creates a shimmering effect by modulating harmonics
        shimmer_rate = 2.0 + self.jiva_amount * 2.0  # 2-4 Hz
        shimmer = 1.0 + self.jiva_amount * 0.1 * np.sin(2 * np.pi * shimmer_rate * t)

        # Add subtle harmonic reinforcement
        reinforcement = (
            self.jiva_amount
            * 0.02
            * np.sin(2 * np.pi * freq * 2 * t)
            * np.exp(-0.8 * t / duration)
        )

        return signal * shimmer + reinforcement
