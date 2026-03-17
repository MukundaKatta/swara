"""Pydantic data models for SWARA."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Swara(str, Enum):
    """The seven swaras (notes) of Indian classical music."""

    SA = "Sa"
    RE = "Re"
    GA = "Ga"
    MA = "Ma"
    PA = "Pa"
    DHA = "Dha"
    NI = "Ni"


class SwaraVariant(str, Enum):
    """Variants of swaras (komal, shuddha, tivra)."""

    KOMAL = "komal"
    SHUDDHA = "shuddha"
    TIVRA = "tivra"


class Laya(str, Enum):
    """Tempo classifications in Indian classical music."""

    VILAMBIT = "vilambit"  # Slow (~30-60 BPM)
    MADHYA = "madhya"  # Medium (~60-120 BPM)
    DRUT = "drut"  # Fast (~120-240 BPM)
    ATI_DRUT = "ati_drut"  # Very fast (~240+ BPM)


class CompositionSection(str, Enum):
    """Sections of a classical composition."""

    ALAP = "alap"
    JOR = "jor"
    JHALA = "jhala"
    GAT = "gat"


class Bol(str, Enum):
    """Tabla bol (syllable) types."""

    NA = "Na"
    TIN = "Tin"
    DHA = "Dha"
    DHIN = "Dhin"
    TA = "Ta"
    TI = "Ti"
    GE = "Ge"
    KE = "Ke"
    GHE = "Ghe"
    DHE = "Dhe"
    TE = "Te"
    RE = "Re"
    KAT = "Kat"
    GA = "Ga"
    KDA = "Kda"
    TIRA = "Tira"
    KITA = "Kita"
    DHERE = "Dhere"
    TETE = "Tete"
    TRKT = "Trkt"
    EMPTY = "-"


class SwaraNote(BaseModel):
    """A single note with pitch, duration, and ornamental information."""

    swara: Swara
    variant: SwaraVariant = SwaraVariant.SHUDDHA
    octave: int = Field(default=0, ge=-2, le=2)
    duration: float = Field(default=0.5, gt=0)
    amplitude: float = Field(default=0.8, ge=0, le=1.0)
    has_meend: bool = False
    has_gamak: bool = False
    meend_target: Optional[Swara] = None

    @property
    def frequency(self) -> float:
        """Get the frequency in Hz for this note (Sa = 261.63 Hz / middle C)."""
        base_sa = 261.63
        ratios = {
            (Swara.SA, SwaraVariant.SHUDDHA): 1.0,
            (Swara.RE, SwaraVariant.KOMAL): 256 / 243,
            (Swara.RE, SwaraVariant.SHUDDHA): 9 / 8,
            (Swara.GA, SwaraVariant.KOMAL): 32 / 27,
            (Swara.GA, SwaraVariant.SHUDDHA): 81 / 64,
            (Swara.MA, SwaraVariant.SHUDDHA): 4 / 3,
            (Swara.MA, SwaraVariant.TIVRA): 729 / 512,
            (Swara.PA, SwaraVariant.SHUDDHA): 3 / 2,
            (Swara.DHA, SwaraVariant.KOMAL): 128 / 81,
            (Swara.DHA, SwaraVariant.SHUDDHA): 27 / 16,
            (Swara.NI, SwaraVariant.KOMAL): 16 / 9,
            (Swara.NI, SwaraVariant.SHUDDHA): 243 / 128,
        }
        ratio = ratios.get((self.swara, self.variant), 1.0)
        # If variant not found, try shuddha
        if (self.swara, self.variant) not in ratios:
            ratio = ratios.get((self.swara, SwaraVariant.SHUDDHA), 1.0)
        return base_sa * ratio * (2 ** self.octave)


class BolPattern(BaseModel):
    """A tabla bol pattern with timing."""

    name: str
    bols: list[Bol]
    matra_count: int = Field(gt=0)
    description: str = ""


class TaalDefinition(BaseModel):
    """Definition of a taal (rhythmic cycle)."""

    name: str
    matra: int = Field(gt=0)
    vibhag: list[int] = Field(default_factory=list)
    sam: int = 1
    khali: list[int] = Field(default_factory=list)
    theka: list[Bol] = Field(default_factory=list)
    bol_patterns: list[BolPattern] = Field(default_factory=list)


class RagaDefinition(BaseModel):
    """Definition of a raga with aroh, avroh, and characteristic phrases."""

    name: str
    thaat: str = ""
    aroh: list[SwaraNote] = Field(default_factory=list)
    avroh: list[SwaraNote] = Field(default_factory=list)
    vadi: Optional[Swara] = None
    samvadi: Optional[Swara] = None
    pakad: list[SwaraNote] = Field(default_factory=list)
    time_of_day: str = ""
    rasa: str = ""
    komal_swaras: list[Swara] = Field(default_factory=list)
    tivra_swaras: list[Swara] = Field(default_factory=list)


class CompositionConfig(BaseModel):
    """Configuration for generating a composition."""

    raga_name: str
    taal_name: str = "teentaal"
    laya: Laya = Laya.MADHYA
    duration_seconds: float = Field(default=60.0, gt=0)
    sections: list[CompositionSection] = Field(
        default_factory=lambda: [
            CompositionSection.ALAP,
            CompositionSection.JOR,
            CompositionSection.JHALA,
            CompositionSection.GAT,
        ]
    )
    sample_rate: int = Field(default=44100, gt=0)
    sa_frequency: float = Field(default=261.63, gt=0)
    include_tanpura: bool = True


class GeneratedSection(BaseModel):
    """A generated section of a composition."""

    section_type: CompositionSection
    notes: list[SwaraNote] = Field(default_factory=list)
    duration_seconds: float = 0.0
    bol_sequence: list[Bol] = Field(default_factory=list)


class Composition(BaseModel):
    """A complete generated composition."""

    config: CompositionConfig
    raga: RagaDefinition
    taal: TaalDefinition
    sections: list[GeneratedSection] = Field(default_factory=list)
    total_duration: float = 0.0

    @property
    def note_count(self) -> int:
        return sum(len(s.notes) for s in self.sections)

    @property
    def bol_count(self) -> int:
        return sum(len(s.bol_sequence) for s in self.sections)
