"""Tabla synthesizer with bol patterns and taal support.

Implements synthesis of tabla sounds using additive synthesis and noise shaping
to approximate the characteristic sounds of dayan (right drum) and bayan (left drum).
Includes 30+ bol patterns across major taals.
"""

from __future__ import annotations

import numpy as np

from swara.models import Bol, BolPattern, TaalDefinition


# ── Taal Definitions with Thekas ─────────────────────────────────────────────

TAAL_REGISTRY: dict[str, TaalDefinition] = {
    "teentaal": TaalDefinition(
        name="Teentaal",
        matra=16,
        vibhag=[4, 4, 4, 4],
        sam=1,
        khali=[9],
        theka=[
            Bol.DHA, Bol.DHIN, Bol.DHIN, Bol.DHA,
            Bol.DHA, Bol.DHIN, Bol.DHIN, Bol.DHA,
            Bol.DHA, Bol.TIN, Bol.TIN, Bol.TA,
            Bol.TA, Bol.DHIN, Bol.DHIN, Bol.DHA,
        ],
    ),
    "jhaptaal": TaalDefinition(
        name="Jhaptaal",
        matra=10,
        vibhag=[2, 3, 2, 3],
        sam=1,
        khali=[6],
        theka=[
            Bol.DHIN, Bol.NA,
            Bol.DHIN, Bol.DHIN, Bol.NA,
            Bol.TIN, Bol.NA,
            Bol.DHIN, Bol.DHIN, Bol.NA,
        ],
    ),
    "ektaal": TaalDefinition(
        name="Ektaal",
        matra=12,
        vibhag=[2, 2, 2, 2, 2, 2],
        sam=1,
        khali=[3, 7],
        theka=[
            Bol.DHIN, Bol.DHIN,
            Bol.DHA, Bol.GE,
            Bol.TIRA, Bol.KITA,
            Bol.TIN, Bol.TIN,
            Bol.DHA, Bol.GE,
            Bol.DHERE, Bol.DHERE,
        ],
    ),
    "rupak": TaalDefinition(
        name="Rupak",
        matra=7,
        vibhag=[3, 2, 2],
        sam=1,
        khali=[1],
        theka=[
            Bol.TIN, Bol.TIN, Bol.NA,
            Bol.DHIN, Bol.NA,
            Bol.DHIN, Bol.NA,
        ],
    ),
    "dadra": TaalDefinition(
        name="Dadra",
        matra=6,
        vibhag=[3, 3],
        sam=1,
        khali=[4],
        theka=[
            Bol.DHA, Bol.DHIN, Bol.NA,
            Bol.DHA, Bol.TIN, Bol.NA,
        ],
    ),
    "keherwa": TaalDefinition(
        name="Keherwa",
        matra=8,
        vibhag=[4, 4],
        sam=1,
        khali=[5],
        theka=[
            Bol.DHA, Bol.GE, Bol.NA, Bol.TIN,
            Bol.NA, Bol.KE, Bol.DHIN, Bol.NA,
        ],
    ),
    "tilwada": TaalDefinition(
        name="Tilwada",
        matra=16,
        vibhag=[4, 4, 4, 4],
        sam=1,
        khali=[9],
        theka=[
            Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHIN,
            Bol.DHIN, Bol.DHA, Bol.DHA, Bol.TIN,
            Bol.TA, Bol.TIRA, Bol.KITA, Bol.DHIN,
            Bol.DHIN, Bol.DHA, Bol.DHA, Bol.DHIN,
        ],
    ),
    "dhamar": TaalDefinition(
        name="Dhamar",
        matra=14,
        vibhag=[5, 2, 3, 4],
        sam=1,
        khali=[6],
        theka=[
            Bol.KAT, Bol.DHIN, Bol.TA, Bol.DHIN, Bol.TA,
            Bol.DHA, Bol.EMPTY,
            Bol.GE, Bol.TIN, Bol.EMPTY,
            Bol.TA, Bol.TIRA, Bol.KITA, Bol.DHIN,
        ],
    ),
    "jhoomra": TaalDefinition(
        name="Jhoomra",
        matra=14,
        vibhag=[3, 4, 3, 4],
        sam=1,
        khali=[8],
        theka=[
            Bol.DHIN, Bol.EMPTY, Bol.DHIN,
            Bol.DHA, Bol.TRKT, Bol.DHIN, Bol.DHIN,
            Bol.DHA, Bol.DHA, Bol.TRKT,
            Bol.TIN, Bol.EMPTY, Bol.TIN, Bol.TA,
        ],
    ),
    "deepchandi": TaalDefinition(
        name="Deepchandi",
        matra=14,
        vibhag=[3, 4, 3, 4],
        sam=1,
        khali=[4, 11],
        theka=[
            Bol.DHA, Bol.DHIN, Bol.EMPTY,
            Bol.DHA, Bol.DHA, Bol.DHIN, Bol.EMPTY,
            Bol.TA, Bol.TIN, Bol.EMPTY,
            Bol.DHA, Bol.DHA, Bol.DHIN, Bol.EMPTY,
        ],
    ),
}


# ── 30+ Bol Patterns ────────────────────────────────────────────────────────

BOL_PATTERNS: list[BolPattern] = [
    # Basic thekas
    BolPattern(
        name="teentaal_theka",
        bols=[Bol.DHA, Bol.DHIN, Bol.DHIN, Bol.DHA, Bol.DHA, Bol.DHIN, Bol.DHIN, Bol.DHA,
              Bol.DHA, Bol.TIN, Bol.TIN, Bol.TA, Bol.TA, Bol.DHIN, Bol.DHIN, Bol.DHA],
        matra_count=16,
        description="Basic teentaal theka",
    ),
    BolPattern(
        name="jhaptaal_theka",
        bols=[Bol.DHIN, Bol.NA, Bol.DHIN, Bol.DHIN, Bol.NA,
              Bol.TIN, Bol.NA, Bol.DHIN, Bol.DHIN, Bol.NA],
        matra_count=10,
        description="Basic jhaptaal theka",
    ),
    # Kayda patterns
    BolPattern(
        name="kayda_1",
        bols=[Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHA, Bol.GE, Bol.NA, Bol.TIRA, Bol.KITA],
        matra_count=8,
        description="Kayda opening pattern",
    ),
    BolPattern(
        name="kayda_2",
        bols=[Bol.DHIN, Bol.NA, Bol.GE, Bol.NA, Bol.DHIN, Bol.NA, Bol.KE, Bol.NA],
        matra_count=8,
        description="Kayda with ge-na",
    ),
    BolPattern(
        name="kayda_3",
        bols=[Bol.DHA, Bol.TIRA, Bol.KITA, Bol.TETE, Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHIN],
        matra_count=8,
        description="Kayda with tete",
    ),
    # Tukda patterns (fixed compositions)
    BolPattern(
        name="tukda_1",
        bols=[Bol.DHA, Bol.TI, Bol.DHA, Bol.GE, Bol.NA, Bol.DHA, Bol.TIRA, Bol.KITA,
              Bol.TA, Bol.KE, Bol.DHIN, Bol.NA, Bol.DHA, Bol.GE, Bol.TIRA, Bol.KITA],
        matra_count=16,
        description="Tukda in teentaal",
    ),
    BolPattern(
        name="tukda_2",
        bols=[Bol.DHIN, Bol.TA, Bol.DHIN, Bol.TA, Bol.DHA, Bol.DHA, Bol.DHIN, Bol.TA],
        matra_count=8,
        description="Short tukda",
    ),
    BolPattern(
        name="tukda_3",
        bols=[Bol.TA, Bol.KITA, Bol.GE, Bol.NA, Bol.TA, Bol.KITA, Bol.DHA, Bol.TIRA,
              Bol.KITA, Bol.DHA, Bol.GE, Bol.TIRA, Bol.KITA, Bol.DHIN, Bol.NA, Bol.DHA],
        matra_count=16,
        description="Extended tukda pattern",
    ),
    # Tihai patterns (triple-repeat cadential patterns)
    BolPattern(
        name="tihai_1",
        bols=[Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHA, Bol.EMPTY,
              Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHA, Bol.EMPTY,
              Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHA],
        matra_count=14,
        description="Simple tihai",
    ),
    BolPattern(
        name="tihai_2",
        bols=[Bol.DHA, Bol.GE, Bol.TIN, Bol.NA, Bol.KE, Bol.EMPTY,
              Bol.DHA, Bol.GE, Bol.TIN, Bol.NA, Bol.KE, Bol.EMPTY,
              Bol.DHA, Bol.GE, Bol.TIN, Bol.NA, Bol.KE],
        matra_count=17,
        description="Chakradar tihai",
    ),
    BolPattern(
        name="tihai_3",
        bols=[Bol.DHIN, Bol.NA, Bol.DHA, Bol.EMPTY,
              Bol.DHIN, Bol.NA, Bol.DHA, Bol.EMPTY,
              Bol.DHIN, Bol.NA, Bol.DHA],
        matra_count=11,
        description="Short tihai on sam",
    ),
    # Peshkar patterns (slow, elaborate)
    BolPattern(
        name="peshkar_1",
        bols=[Bol.DHA, Bol.EMPTY, Bol.GE, Bol.EMPTY, Bol.TIRA, Bol.KITA,
              Bol.TIN, Bol.EMPTY, Bol.KE, Bol.EMPTY, Bol.TIRA, Bol.KITA],
        matra_count=12,
        description="Peshkar opening",
    ),
    BolPattern(
        name="peshkar_2",
        bols=[Bol.DHA, Bol.EMPTY, Bol.TRKT, Bol.DHA, Bol.GE, Bol.DHIN,
              Bol.NA, Bol.GE, Bol.DHIN, Bol.EMPTY, Bol.DHA, Bol.GE],
        matra_count=12,
        description="Peshkar elaboration",
    ),
    # Rela (fast, continuous patterns)
    BolPattern(
        name="rela_1",
        bols=[Bol.DHERE, Bol.DHERE, Bol.TETE, Bol.TETE,
              Bol.DHERE, Bol.DHERE, Bol.TETE, Bol.TETE],
        matra_count=8,
        description="Rela pattern",
    ),
    BolPattern(
        name="rela_2",
        bols=[Bol.TIRA, Bol.KITA, Bol.TIRA, Bol.KITA,
              Bol.DHERE, Bol.DHERE, Bol.TIRA, Bol.KITA],
        matra_count=8,
        description="Fast rela",
    ),
    BolPattern(
        name="rela_3",
        bols=[Bol.DHIN, Bol.TIRA, Bol.KITA, Bol.DHIN, Bol.TIRA, Bol.KITA,
              Bol.TETE, Bol.KITA, Bol.GE, Bol.NA, Bol.TIRA, Bol.KITA],
        matra_count=12,
        description="Extended rela",
    ),
    # Kaida paltas (variations)
    BolPattern(
        name="palta_1",
        bols=[Bol.DHA, Bol.GE, Bol.TIRA, Bol.KITA, Bol.DHA, Bol.GE, Bol.NA, Bol.DHA],
        matra_count=8,
        description="Palta variation 1",
    ),
    BolPattern(
        name="palta_2",
        bols=[Bol.DHIN, Bol.GE, Bol.DHIN, Bol.GE, Bol.NA, Bol.DHIN, Bol.GE, Bol.NA],
        matra_count=8,
        description="Palta variation 2",
    ),
    BolPattern(
        name="palta_3",
        bols=[Bol.DHA, Bol.TIRA, Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHA, Bol.GE, Bol.NA],
        matra_count=8,
        description="Palta variation 3",
    ),
    BolPattern(
        name="palta_4",
        bols=[Bol.TA, Bol.KE, Bol.TIRA, Bol.KITA, Bol.TA, Bol.KE, Bol.NA, Bol.TA],
        matra_count=8,
        description="Palta on khali",
    ),
    # Laggi patterns (fast patterns for light music)
    BolPattern(
        name="laggi_1",
        bols=[Bol.DHA, Bol.GE, Bol.NA, Bol.GE, Bol.DHA, Bol.GE, Bol.NA, Bol.GE],
        matra_count=8,
        description="Laggi pattern 1",
    ),
    BolPattern(
        name="laggi_2",
        bols=[Bol.DHA, Bol.TI, Bol.NA, Bol.KE, Bol.DHA, Bol.TI, Bol.NA, Bol.KE],
        matra_count=8,
        description="Laggi pattern 2",
    ),
    BolPattern(
        name="laggi_3",
        bols=[Bol.DHIN, Bol.TA, Bol.KDA, Bol.TIRA, Bol.KITA, Bol.DHA, Bol.GE, Bol.NA],
        matra_count=8,
        description="Laggi with kda",
    ),
    # Chakradar patterns
    BolPattern(
        name="chakradar_1",
        bols=[Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHA, Bol.DHIN, Bol.NA,
              Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHA, Bol.DHIN, Bol.NA,
              Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHA, Bol.DHIN, Bol.NA],
        matra_count=18,
        description="Chakradar composition (3x repeat)",
    ),
    # Mohra patterns (closing patterns before tihai)
    BolPattern(
        name="mohra_1",
        bols=[Bol.DHA, Bol.TIRA, Bol.KITA, Bol.DHIN, Bol.NA, Bol.GE, Bol.NA, Bol.DHIN],
        matra_count=8,
        description="Mohra before tihai",
    ),
    BolPattern(
        name="mohra_2",
        bols=[Bol.TA, Bol.TIRA, Bol.KITA, Bol.TIN, Bol.NA, Bol.KE, Bol.NA, Bol.TIN],
        matra_count=8,
        description="Mohra on khali side",
    ),
    # Additional theka patterns
    BolPattern(
        name="dadra_theka",
        bols=[Bol.DHA, Bol.DHIN, Bol.NA, Bol.DHA, Bol.TIN, Bol.NA],
        matra_count=6,
        description="Dadra theka",
    ),
    BolPattern(
        name="keherwa_theka",
        bols=[Bol.DHA, Bol.GE, Bol.NA, Bol.TIN, Bol.NA, Bol.KE, Bol.DHIN, Bol.NA],
        matra_count=8,
        description="Keherwa theka",
    ),
    BolPattern(
        name="rupak_theka",
        bols=[Bol.TIN, Bol.TIN, Bol.NA, Bol.DHIN, Bol.NA, Bol.DHIN, Bol.NA],
        matra_count=7,
        description="Rupak theka",
    ),
    BolPattern(
        name="ektaal_theka",
        bols=[Bol.DHIN, Bol.DHIN, Bol.DHA, Bol.GE, Bol.TIRA, Bol.KITA,
              Bol.TIN, Bol.TIN, Bol.DHA, Bol.GE, Bol.DHERE, Bol.DHERE],
        matra_count=12,
        description="Ektaal theka",
    ),
    # Uthaan patterns (opening/pickup)
    BolPattern(
        name="uthaan_1",
        bols=[Bol.DHA, Bol.EMPTY, Bol.DHIN, Bol.EMPTY, Bol.DHA, Bol.GE, Bol.TIRA, Bol.KITA],
        matra_count=8,
        description="Uthaan opening pickup",
    ),
    BolPattern(
        name="uthaan_2",
        bols=[Bol.DHA, Bol.TRKT, Bol.DHA, Bol.GE, Bol.DHIN, Bol.NA, Bol.GE, Bol.DHIN],
        matra_count=8,
        description="Uthaan with trkt",
    ),
]


class TablaSynthesizer:
    """Synthesizer for tabla sounds using additive synthesis and noise shaping.

    Models the dayan (right, higher-pitched drum) and bayan (left, bass drum)
    to produce characteristic tabla bol sounds.
    """

    def __init__(self, sample_rate: int = 44100, base_pitch: float = 260.0) -> None:
        self.sample_rate = sample_rate
        self.base_pitch = base_pitch

    def synthesize_bol(self, bol: Bol, duration: float = 0.15, amplitude: float = 0.8) -> np.ndarray:
        """Synthesize a single tabla bol sound."""
        if bol == Bol.EMPTY:
            return np.zeros(int(self.sample_rate * duration))

        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        synthesis_map = {
            Bol.NA: self._synth_na,
            Bol.TIN: self._synth_tin,
            Bol.DHA: self._synth_dha,
            Bol.DHIN: self._synth_dhin,
            Bol.TA: self._synth_ta,
            Bol.TI: self._synth_ti,
            Bol.GE: self._synth_ge,
            Bol.KE: self._synth_ke,
            Bol.GHE: self._synth_ghe,
            Bol.DHE: self._synth_dhe,
            Bol.TE: self._synth_te,
            Bol.RE: self._synth_re,
            Bol.KAT: self._synth_kat,
            Bol.GA: self._synth_ga,
            Bol.KDA: self._synth_kda,
            Bol.TIRA: self._synth_tira,
            Bol.KITA: self._synth_kita,
            Bol.DHERE: self._synth_dhere,
            Bol.TETE: self._synth_tete,
            Bol.TRKT: self._synth_trkt,
        }

        synth_fn = synthesis_map.get(bol, self._synth_na)
        signal = synth_fn(t, duration)
        return (signal * amplitude).astype(np.float64)

    def synthesize_pattern(self, pattern: BolPattern, tempo_bpm: float = 120.0) -> np.ndarray:
        """Synthesize a complete bol pattern at a given tempo."""
        beat_duration = 60.0 / tempo_bpm
        segments: list[np.ndarray] = []
        for bol in pattern.bols:
            seg = self.synthesize_bol(bol, duration=beat_duration * 0.8)
            silence = np.zeros(int(self.sample_rate * beat_duration * 0.2))
            segments.append(np.concatenate([seg, silence]))
        return np.concatenate(segments) if segments else np.array([], dtype=np.float64)

    def synthesize_theka(self, taal: TaalDefinition, cycles: int = 1, tempo_bpm: float = 120.0) -> np.ndarray:
        """Synthesize the theka (basic pattern) of a taal for given cycles."""
        beat_duration = 60.0 / tempo_bpm
        segments: list[np.ndarray] = []
        for _ in range(cycles):
            for bol in taal.theka:
                seg = self.synthesize_bol(bol, duration=beat_duration * 0.8)
                silence = np.zeros(int(self.sample_rate * beat_duration * 0.2))
                segments.append(np.concatenate([seg, silence]))
        return np.concatenate(segments) if segments else np.array([], dtype=np.float64)

    # ── Individual bol synthesis methods ─────────────────────────────────

    def _decay_envelope(self, t: np.ndarray, duration: float, decay_rate: float = 8.0) -> np.ndarray:
        return np.exp(-decay_rate * t / duration)

    def _synth_na(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Na - sharp dayan stroke, open."""
        env = self._decay_envelope(t, duration, 6.0)
        f = self.base_pitch
        signal = (
            0.5 * np.sin(2 * np.pi * f * t)
            + 0.3 * np.sin(2 * np.pi * 2 * f * t)
            + 0.1 * np.sin(2 * np.pi * 3 * f * t)
        )
        noise = 0.05 * np.random.randn(len(t)) * self._decay_envelope(t, duration, 20.0)
        return (signal + noise) * env

    def _synth_tin(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Tin - resonant dayan stroke."""
        env = self._decay_envelope(t, duration, 5.0)
        f = self.base_pitch * 1.2
        signal = (
            0.6 * np.sin(2 * np.pi * f * t)
            + 0.25 * np.sin(2 * np.pi * 2.01 * f * t)
            + 0.15 * np.sin(2 * np.pi * 3.03 * f * t)
        )
        return signal * env

    def _synth_dha(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Dha - bayan + dayan combined, open resonant."""
        env = self._decay_envelope(t, duration, 4.5)
        f_dayan = self.base_pitch
        f_bayan = self.base_pitch * 0.4
        dayan = 0.4 * np.sin(2 * np.pi * f_dayan * t) + 0.15 * np.sin(2 * np.pi * 2 * f_dayan * t)
        bayan = 0.3 * np.sin(2 * np.pi * f_bayan * t) + 0.1 * np.sin(2 * np.pi * 1.5 * f_bayan * t)
        # Bayan pitch bend
        bend = np.exp(-3.0 * t / duration)
        bayan_bent = 0.2 * np.sin(2 * np.pi * f_bayan * (1 + 0.3 * bend) * t)
        return (dayan + bayan + bayan_bent) * env

    def _synth_dhin(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Dhin - bayan + dayan, closed/muted bayan."""
        env = self._decay_envelope(t, duration, 5.0)
        f_dayan = self.base_pitch * 1.1
        f_bayan = self.base_pitch * 0.35
        dayan = 0.45 * np.sin(2 * np.pi * f_dayan * t) + 0.2 * np.sin(2 * np.pi * 2 * f_dayan * t)
        bayan = 0.25 * np.sin(2 * np.pi * f_bayan * t) * self._decay_envelope(t, duration, 8.0)
        return (dayan + bayan) * env

    def _synth_ta(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Ta - crisp dayan edge stroke."""
        env = self._decay_envelope(t, duration, 10.0)
        f = self.base_pitch * 1.5
        signal = 0.5 * np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2.5 * f * t)
        noise = 0.15 * np.random.randn(len(t)) * self._decay_envelope(t, duration, 25.0)
        return (signal + noise) * env

    def _synth_ti(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Ti - light dayan tap."""
        env = self._decay_envelope(t, duration, 12.0)
        f = self.base_pitch * 1.8
        signal = 0.4 * np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 3 * f * t)
        return signal * env

    def _synth_ge(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Ge (Ga) - open bayan bass stroke."""
        env = self._decay_envelope(t, duration, 3.5)
        f = self.base_pitch * 0.3
        signal = (
            0.6 * np.sin(2 * np.pi * f * t)
            + 0.2 * np.sin(2 * np.pi * 2 * f * t)
        )
        # Pitch modulation for bayan characteristic
        mod = 0.15 * np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-2 * t / duration)
        return (signal + mod) * env

    def _synth_ke(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Ke - closed/muted bayan."""
        env = self._decay_envelope(t, duration, 15.0)
        f = self.base_pitch * 0.4
        signal = 0.4 * np.sin(2 * np.pi * f * t)
        noise = 0.2 * np.random.randn(len(t)) * self._decay_envelope(t, duration, 30.0)
        return (signal + noise) * env

    def _synth_ghe(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Ghe - heavy open bayan."""
        env = self._decay_envelope(t, duration, 3.0)
        f = self.base_pitch * 0.25
        signal = 0.7 * np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 1.5 * f * t)
        bend = np.exp(-2.0 * t / duration)
        bent = 0.15 * np.sin(2 * np.pi * f * (1 + 0.5 * bend) * t)
        return (signal + bent) * env

    def _synth_dhe(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Dhe - combination stroke."""
        return 0.5 * self._synth_dha(t, duration) + 0.5 * self._synth_te(t, duration)

    def _synth_te(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Te - sharp dayan rim stroke."""
        env = self._decay_envelope(t, duration, 14.0)
        f = self.base_pitch * 2.0
        signal = 0.3 * np.sin(2 * np.pi * f * t)
        noise = 0.25 * np.random.randn(len(t)) * self._decay_envelope(t, duration, 20.0)
        return (signal + noise) * env

    def _synth_re(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Re - gliding dayan stroke."""
        env = self._decay_envelope(t, duration, 8.0)
        f = self.base_pitch * 1.3
        glide = 1 + 0.2 * np.exp(-5 * t / duration)
        signal = 0.4 * np.sin(2 * np.pi * f * glide * t)
        return signal * env

    def _synth_kat(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Kat - dry, muted dayan slap."""
        env = self._decay_envelope(t, duration, 20.0)
        noise = 0.6 * np.random.randn(len(t))
        return noise * env

    def _synth_ga(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Ga - soft bayan tap."""
        env = self._decay_envelope(t, duration, 10.0)
        f = self.base_pitch * 0.35
        signal = 0.35 * np.sin(2 * np.pi * f * t)
        return signal * env

    def _synth_kda(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Kda - quick flick on dayan."""
        env = self._decay_envelope(t, duration, 16.0)
        f = self.base_pitch * 1.6
        signal = 0.35 * np.sin(2 * np.pi * f * t) + 0.15 * np.sin(2 * np.pi * 3 * f * t)
        noise = 0.1 * np.random.randn(len(t)) * self._decay_envelope(t, duration, 30.0)
        return (signal + noise) * env

    def _synth_tira(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Tira - fast double stroke (ti-ra)."""
        half = len(t) // 2
        t1, t2 = t[:half], t[half:]
        s1 = self._synth_ti(t1, duration / 2)
        env2 = self._decay_envelope(t2 - t2[0] if len(t2) > 0 else t2, duration / 2, 10.0)
        f = self.base_pitch * 1.4
        s2 = 0.35 * np.sin(2 * np.pi * f * (t2 - t2[0])) * env2 if len(t2) > 0 else np.array([])
        return np.concatenate([s1, s2])

    def _synth_kita(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Kita - fast double stroke (ki-ta)."""
        half = len(t) // 2
        t1, t2 = t[:half], t[half:]
        s1 = self._synth_ke(t1, duration / 2)
        s2 = self._synth_ta(t2 - t2[0] if len(t2) > 0 else t2, duration / 2) if len(t2) > 0 else np.array([])
        return np.concatenate([s1, s2])

    def _synth_dhere(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Dhere - rolling bayan stroke."""
        env = self._decay_envelope(t, duration, 5.0)
        f = self.base_pitch * 0.35
        signal = 0.4 * np.sin(2 * np.pi * f * t)
        roll = 0.15 * np.sin(2 * np.pi * 8 * t) * np.exp(-4 * t / duration)
        return (signal + roll) * env

    def _synth_tete(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Tete - fast double te stroke."""
        half = len(t) // 2
        t1, t2 = t[:half], t[half:]
        s1 = self._synth_te(t1, duration / 2)
        s2 = self._synth_te(t2 - t2[0] if len(t2) > 0 else t2, duration / 2) if len(t2) > 0 else np.array([])
        return np.concatenate([s1, s2])

    def _synth_trkt(self, t: np.ndarray, duration: float) -> np.ndarray:
        """Trkt - fast quadruple stroke."""
        q = len(t) // 4
        parts: list[np.ndarray] = []
        for i in range(4):
            start = i * q
            end = (i + 1) * q if i < 3 else len(t)
            seg_t = t[start:end] - t[start]
            seg_dur = duration / 4
            if i % 2 == 0:
                parts.append(self._synth_ti(seg_t, seg_dur))
            else:
                parts.append(self._synth_re(seg_t, seg_dur))
        return np.concatenate(parts)

    @staticmethod
    def get_taal(name: str) -> TaalDefinition:
        """Get a taal definition by name."""
        key = name.lower().replace(" ", "")
        if key not in TAAL_REGISTRY:
            available = ", ".join(sorted(TAAL_REGISTRY.keys()))
            raise ValueError(f"Unknown taal '{name}'. Available: {available}")
        return TAAL_REGISTRY[key]

    @staticmethod
    def list_taals() -> list[str]:
        """List all available taal names."""
        return sorted(TAAL_REGISTRY.keys())

    @staticmethod
    def get_bol_patterns() -> list[BolPattern]:
        """Return all registered bol patterns."""
        return BOL_PATTERNS
