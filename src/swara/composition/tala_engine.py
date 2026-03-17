"""Tala engine with layakari support: vilambit, madhya, drut.

Manages rhythmic cycles and tempo, providing bol sequences
aligned to taal structures at various speeds.
"""

from __future__ import annotations

import random
from typing import Optional

from swara.models import Bol, BolPattern, Laya, TaalDefinition
from swara.instruments.tabla import BOL_PATTERNS, TAAL_REGISTRY, TablaSynthesizer


# Tempo BPM ranges for each laya
LAYA_BPM: dict[Laya, tuple[float, float]] = {
    Laya.VILAMBIT: (30.0, 60.0),
    Laya.MADHYA: (60.0, 120.0),
    Laya.DRUT: (120.0, 240.0),
    Laya.ATI_DRUT: (240.0, 360.0),
}


class TalaEngine:
    """Engine for managing taal cycles and generating bol sequences.

    Supports layakari (rhythmic variations) at vilambit (slow),
    madhya (medium), and drut (fast) tempos with proper subdivision.
    """

    def __init__(
        self,
        taal: str = "teentaal",
        laya: Laya | str = Laya.MADHYA,
        bpm: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> None:
        if isinstance(laya, str):
            laya = Laya(laya)

        self.taal_def = TablaSynthesizer.get_taal(taal)
        self.laya = laya
        self._rng = random.Random(seed)

        # Set BPM within laya range
        bpm_range = LAYA_BPM[laya]
        if bpm is not None:
            self.bpm = max(bpm_range[0], min(bpm, bpm_range[1]))
        else:
            self.bpm = (bpm_range[0] + bpm_range[1]) / 2

    @property
    def beat_duration(self) -> float:
        """Duration of one matra (beat) in seconds."""
        return 60.0 / self.bpm

    @property
    def cycle_duration(self) -> float:
        """Duration of one complete taal cycle in seconds."""
        return self.beat_duration * self.taal_def.matra

    def generate_theka(self, cycles: int = 1) -> list[Bol]:
        """Generate the basic theka pattern for the given number of cycles."""
        return self.taal_def.theka * cycles

    def generate_accompaniment(
        self, duration: float, variation: float = 0.2
    ) -> list[Bol]:
        """Generate tabla accompaniment for a given duration.

        Args:
            duration: Total duration in seconds.
            variation: Probability of inserting a variation pattern (0-1).
        """
        bols: list[Bol] = []
        elapsed = 0.0
        cycle_dur = self.cycle_duration

        while elapsed < duration:
            if self._rng.random() < variation:
                # Insert a variation pattern
                pattern = self._select_pattern()
                bols.extend(pattern.bols)
                elapsed += len(pattern.bols) * self.beat_duration
            else:
                # Play basic theka
                bols.extend(self.taal_def.theka)
                elapsed += cycle_dur

        return bols

    def apply_layakari(self, bols: list[Bol], subdivision: int = 2) -> list[Bol]:
        """Apply layakari (rhythmic subdivision) to a bol sequence.

        subdivision=2 doubles the speed (dugun), 3 triples (tigun),
        4 quadruples (chaugun).
        """
        if subdivision <= 1:
            return bols

        expanded: list[Bol] = []
        for bol in bols:
            if bol == Bol.EMPTY:
                expanded.extend([Bol.EMPTY] * subdivision)
            else:
                # Fill subdivisions with the bol and filler strokes
                expanded.append(bol)
                fillers = self._get_filler_bols(bol, subdivision - 1)
                expanded.extend(fillers)
        return expanded

    def generate_tihai(self, pattern: list[Bol] | None = None) -> list[Bol]:
        """Generate a tihai (triple-repeat cadential pattern ending on sam)."""
        if pattern is None:
            # Default short pattern
            pattern = [Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHA]

        # Tihai = pattern + gap + pattern + gap + pattern (landing on sam)
        gap_len = max(1, (self.taal_def.matra - 3 * len(pattern)) // 2)
        gap = [Bol.EMPTY] * gap_len

        tihai = pattern + gap + pattern + gap + pattern
        return tihai

    def generate_chakradar(self) -> list[Bol]:
        """Generate a chakradar (tihai where each element is itself a tihai)."""
        inner = [Bol.DHA, Bol.GE, Bol.TIN, Bol.NA, Bol.KE]
        inner_tihai = inner + [Bol.EMPTY] + inner + [Bol.EMPTY] + inner
        outer = inner_tihai + [Bol.EMPTY] + inner_tihai + [Bol.EMPTY] + inner_tihai
        return outer

    def get_vibhag_markers(self) -> list[tuple[int, str]]:
        """Get the position and type (sam/taali/khali) of each vibhag."""
        markers: list[tuple[int, str]] = []
        pos = 1
        for i, count in enumerate(self.taal_def.vibhag):
            if pos == self.taal_def.sam:
                markers.append((pos, "sam"))
            elif pos in self.taal_def.khali:
                markers.append((pos, "khali"))
            else:
                markers.append((pos, "taali"))
            pos += count
        return markers

    def _select_pattern(self) -> BolPattern:
        """Select an appropriate bol pattern based on current taal and laya."""
        # Filter patterns that fit the taal's matra count
        compatible = [
            p for p in BOL_PATTERNS
            if p.matra_count <= self.taal_def.matra
        ]
        if not compatible:
            compatible = BOL_PATTERNS[:5]
        return self._rng.choice(compatible)

    def _get_filler_bols(self, bol: Bol, count: int) -> list[Bol]:
        """Generate filler bols for layakari subdivisions."""
        # Choose appropriate fillers based on the main bol type
        dayan_bols = {Bol.NA, Bol.TIN, Bol.TA, Bol.TI, Bol.TE, Bol.RE}
        bayan_bols = {Bol.GE, Bol.KE, Bol.GHE, Bol.GA}

        if bol in dayan_bols:
            fillers = [Bol.TI, Bol.RE, Bol.KE, Bol.NA]
        elif bol in bayan_bols:
            fillers = [Bol.GE, Bol.KE, Bol.NA, Bol.GE]
        else:
            fillers = [Bol.TIRA, Bol.KITA, Bol.GE, Bol.NA]

        return [fillers[i % len(fillers)] for i in range(count)]

    @staticmethod
    def list_layas() -> list[str]:
        """List all available laya names with BPM ranges."""
        return [f"{l.value} ({bpm[0]:.0f}-{bpm[1]:.0f} BPM)" for l, bpm in LAYA_BPM.items()]
