"""Raga composition engine with 20+ raga definitions.

Generates alap, jor, jhala, and gat sections following the melodic
grammar and mood of each raga.
"""

from __future__ import annotations

import random
from typing import Optional

import numpy as np

from swara.models import (
    Bol,
    Composition,
    CompositionConfig,
    CompositionSection,
    GeneratedSection,
    Laya,
    RagaDefinition,
    Swara,
    SwaraNote,
    SwaraVariant,
)


def _n(
    swara: Swara,
    variant: SwaraVariant = SwaraVariant.SHUDDHA,
    octave: int = 0,
    duration: float = 0.5,
) -> SwaraNote:
    """Shorthand for creating a SwaraNote."""
    return SwaraNote(swara=swara, variant=variant, octave=octave, duration=duration)


# ── 20+ Raga Definitions ────────────────────────────────────────────────────

RAGA_REGISTRY: dict[str, RagaDefinition] = {
    "yaman": RagaDefinition(
        name="Yaman",
        thaat="Kalyan",
        aroh=[_n(Swara.SA), _n(Swara.RE), _n(Swara.GA), _n(Swara.MA, SwaraVariant.TIVRA),
              _n(Swara.PA), _n(Swara.DHA), _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.DHA), _n(Swara.PA),
               _n(Swara.MA, SwaraVariant.TIVRA), _n(Swara.GA), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.GA,
        samvadi=Swara.NI,
        pakad=[_n(Swara.NI, octave=-1), _n(Swara.RE), _n(Swara.GA), _n(Swara.RE),
               _n(Swara.SA), _n(Swara.NI, octave=-1), _n(Swara.RE), _n(Swara.SA)],
        time_of_day="Evening (1st prahar of night)",
        rasa="Shringara (romantic), devotional",
        tivra_swaras=[Swara.MA],
    ),
    "bhairav": RagaDefinition(
        name="Bhairav",
        thaat="Bhairav",
        aroh=[_n(Swara.SA), _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.GA),
              _n(Swara.MA), _n(Swara.PA), _n(Swara.DHA, SwaraVariant.KOMAL),
              _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.DHA, SwaraVariant.KOMAL),
               _n(Swara.PA), _n(Swara.MA), _n(Swara.GA),
               _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.SA)],
        vadi=Swara.DHA,
        samvadi=Swara.RE,
        pakad=[_n(Swara.GA), _n(Swara.MA), _n(Swara.DHA, SwaraVariant.KOMAL), _n(Swara.PA),
               _n(Swara.MA), _n(Swara.GA), _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.SA)],
        time_of_day="Early morning (sandhiprakash)",
        rasa="Bhakti (devotion), Shanta (peace)",
        komal_swaras=[Swara.RE, Swara.DHA],
    ),
    "todi": RagaDefinition(
        name="Todi",
        thaat="Todi",
        aroh=[_n(Swara.SA), _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.GA, SwaraVariant.KOMAL),
              _n(Swara.MA, SwaraVariant.TIVRA), _n(Swara.PA),
              _n(Swara.DHA, SwaraVariant.KOMAL), _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.DHA, SwaraVariant.KOMAL),
               _n(Swara.PA), _n(Swara.MA, SwaraVariant.TIVRA),
               _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.SA)],
        vadi=Swara.DHA,
        samvadi=Swara.GA,
        time_of_day="Late morning",
        rasa="Karuna (pathos), viraha (longing)",
        komal_swaras=[Swara.RE, Swara.GA, Swara.DHA],
        tivra_swaras=[Swara.MA],
    ),
    "marwa": RagaDefinition(
        name="Marwa",
        thaat="Marwa",
        aroh=[_n(Swara.SA), _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.GA),
              _n(Swara.MA, SwaraVariant.TIVRA), _n(Swara.DHA), _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.DHA),
               _n(Swara.MA, SwaraVariant.TIVRA), _n(Swara.GA),
               _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.SA)],
        vadi=Swara.DHA,
        samvadi=Swara.RE,
        time_of_day="Evening (sunset)",
        rasa="Serious, contemplative",
        komal_swaras=[Swara.RE],
        tivra_swaras=[Swara.MA],
    ),
    "puriya": RagaDefinition(
        name="Puriya",
        thaat="Marwa",
        aroh=[_n(Swara.SA), _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.GA),
              _n(Swara.MA, SwaraVariant.TIVRA), _n(Swara.DHA), _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.DHA),
               _n(Swara.MA, SwaraVariant.TIVRA), _n(Swara.GA),
               _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.SA)],
        vadi=Swara.GA,
        samvadi=Swara.NI,
        time_of_day="Early evening",
        rasa="Serious, profound",
        komal_swaras=[Swara.RE],
        tivra_swaras=[Swara.MA],
    ),
    "bilawal": RagaDefinition(
        name="Bilawal",
        thaat="Bilawal",
        aroh=[_n(Swara.SA), _n(Swara.RE), _n(Swara.GA), _n(Swara.MA),
              _n(Swara.PA), _n(Swara.DHA), _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.DHA), _n(Swara.PA),
               _n(Swara.MA), _n(Swara.GA), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.DHA,
        samvadi=Swara.GA,
        time_of_day="Late morning to afternoon",
        rasa="Shringara (romantic), joyful",
    ),
    "khamaj": RagaDefinition(
        name="Khamaj",
        thaat="Khamaj",
        aroh=[_n(Swara.SA), _n(Swara.GA), _n(Swara.MA), _n(Swara.PA),
              _n(Swara.DHA), _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI, SwaraVariant.KOMAL), _n(Swara.DHA),
               _n(Swara.PA), _n(Swara.MA), _n(Swara.GA), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.GA,
        samvadi=Swara.NI,
        time_of_day="Night (2nd prahar)",
        rasa="Shringara, light romantic",
        komal_swaras=[Swara.NI],  # Ni komal in avroh
    ),
    "kafi": RagaDefinition(
        name="Kafi",
        thaat="Kafi",
        aroh=[_n(Swara.SA), _n(Swara.RE), _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.MA),
              _n(Swara.PA), _n(Swara.DHA), _n(Swara.NI, SwaraVariant.KOMAL), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI, SwaraVariant.KOMAL), _n(Swara.DHA),
               _n(Swara.PA), _n(Swara.MA), _n(Swara.GA, SwaraVariant.KOMAL),
               _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.PA,
        samvadi=Swara.SA,
        time_of_day="Night",
        rasa="Shringara, karuna",
        komal_swaras=[Swara.GA, Swara.NI],
    ),
    "asavari": RagaDefinition(
        name="Asavari",
        thaat="Asavari",
        aroh=[_n(Swara.SA), _n(Swara.RE), _n(Swara.MA), _n(Swara.PA),
              _n(Swara.DHA, SwaraVariant.KOMAL), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI, SwaraVariant.KOMAL),
               _n(Swara.DHA, SwaraVariant.KOMAL), _n(Swara.PA), _n(Swara.MA),
               _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.DHA,
        samvadi=Swara.GA,
        time_of_day="Late morning",
        rasa="Karuna, peaceful",
        komal_swaras=[Swara.GA, Swara.DHA, Swara.NI],
    ),
    "bhairavi": RagaDefinition(
        name="Bhairavi",
        thaat="Bhairavi",
        aroh=[_n(Swara.SA), _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.GA, SwaraVariant.KOMAL),
              _n(Swara.MA), _n(Swara.PA), _n(Swara.DHA, SwaraVariant.KOMAL),
              _n(Swara.NI, SwaraVariant.KOMAL), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI, SwaraVariant.KOMAL),
               _n(Swara.DHA, SwaraVariant.KOMAL), _n(Swara.PA), _n(Swara.MA),
               _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.SA)],
        vadi=Swara.MA,
        samvadi=Swara.SA,
        time_of_day="Morning (traditionally concluding raga)",
        rasa="Karuna (pathos), bhakti (devotion)",
        komal_swaras=[Swara.RE, Swara.GA, Swara.DHA, Swara.NI],
    ),
    "darbari_kanada": RagaDefinition(
        name="Darbari Kanada",
        thaat="Asavari",
        aroh=[_n(Swara.SA), _n(Swara.RE), _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.MA),
              _n(Swara.PA), _n(Swara.DHA, SwaraVariant.KOMAL), _n(Swara.NI, SwaraVariant.KOMAL),
              _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.DHA, SwaraVariant.KOMAL), _n(Swara.NI, SwaraVariant.KOMAL),
               _n(Swara.PA), _n(Swara.MA), _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.RE,
        samvadi=Swara.PA,
        time_of_day="Night (2nd prahar)",
        rasa="Gambhir (serious), majestic",
        komal_swaras=[Swara.GA, Swara.DHA, Swara.NI],
    ),
    "malkauns": RagaDefinition(
        name="Malkauns",
        thaat="Bhairavi",
        aroh=[_n(Swara.SA), _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.MA),
              _n(Swara.DHA, SwaraVariant.KOMAL), _n(Swara.NI, SwaraVariant.KOMAL), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI, SwaraVariant.KOMAL),
               _n(Swara.DHA, SwaraVariant.KOMAL), _n(Swara.MA),
               _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.SA)],
        vadi=Swara.MA,
        samvadi=Swara.SA,
        time_of_day="Late night (3rd prahar)",
        rasa="Gambhir, meditative, mystical",
        komal_swaras=[Swara.GA, Swara.DHA, Swara.NI],
    ),
    "bageshree": RagaDefinition(
        name="Bageshree",
        thaat="Kafi",
        aroh=[_n(Swara.SA), _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.MA),
              _n(Swara.DHA), _n(Swara.NI, SwaraVariant.KOMAL), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI, SwaraVariant.KOMAL), _n(Swara.DHA),
               _n(Swara.MA), _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.MA,
        samvadi=Swara.SA,
        time_of_day="Night (2nd prahar)",
        rasa="Shringara, romantic, tender",
        komal_swaras=[Swara.GA, Swara.NI],
    ),
    "des": RagaDefinition(
        name="Des",
        thaat="Khamaj",
        aroh=[_n(Swara.SA), _n(Swara.RE), _n(Swara.MA), _n(Swara.PA),
              _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI, SwaraVariant.KOMAL), _n(Swara.DHA),
               _n(Swara.PA), _n(Swara.MA), _n(Swara.GA), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.RE,
        samvadi=Swara.PA,
        time_of_day="Night",
        rasa="Light romantic, playful",
        komal_swaras=[Swara.NI],
    ),
    "pilu": RagaDefinition(
        name="Pilu",
        thaat="Kafi",
        aroh=[_n(Swara.SA), _n(Swara.RE), _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.MA),
              _n(Swara.PA), _n(Swara.GA), _n(Swara.RE), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI, SwaraVariant.KOMAL), _n(Swara.DHA),
               _n(Swara.PA), _n(Swara.MA), _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.GA,
        samvadi=Swara.NI,
        time_of_day="Any time (mishra raga)",
        rasa="Shringara, playful, light",
        komal_swaras=[Swara.GA, Swara.NI],
    ),
    "bihag": RagaDefinition(
        name="Bihag",
        thaat="Bilawal",
        aroh=[_n(Swara.SA), _n(Swara.GA), _n(Swara.MA), _n(Swara.PA),
              _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.DHA), _n(Swara.PA),
               _n(Swara.MA), _n(Swara.GA), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.GA,
        samvadi=Swara.NI,
        time_of_day="Night (2nd prahar)",
        rasa="Shringara, romantic",
    ),
    "kedar": RagaDefinition(
        name="Kedar",
        thaat="Kalyan",
        aroh=[_n(Swara.SA), _n(Swara.MA), _n(Swara.MA, SwaraVariant.TIVRA), _n(Swara.PA),
              _n(Swara.DHA), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.DHA), _n(Swara.PA),
               _n(Swara.MA), _n(Swara.GA), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.MA,
        samvadi=Swara.SA,
        time_of_day="Night (1st prahar)",
        rasa="Bhakti, devotional",
        tivra_swaras=[Swara.MA],
    ),
    "hansadhwani": RagaDefinition(
        name="Hansadhwani",
        thaat="Bilawal",
        aroh=[_n(Swara.SA), _n(Swara.RE), _n(Swara.GA), _n(Swara.PA),
              _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.PA),
               _n(Swara.GA), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.RE,
        samvadi=Swara.PA,
        time_of_day="Night (1st prahar)",
        rasa="Joyful, auspicious",
    ),
    "durga": RagaDefinition(
        name="Durga",
        thaat="Bilawal",
        aroh=[_n(Swara.SA), _n(Swara.RE), _n(Swara.MA), _n(Swara.PA),
              _n(Swara.DHA), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.DHA), _n(Swara.PA),
               _n(Swara.MA), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.MA,
        samvadi=Swara.SA,
        time_of_day="Night",
        rasa="Veer (valorous), strong",
    ),
    "shankara": RagaDefinition(
        name="Shankara",
        thaat="Bilawal",
        aroh=[_n(Swara.SA), _n(Swara.RE), _n(Swara.GA), _n(Swara.PA),
              _n(Swara.DHA), _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.DHA), _n(Swara.PA),
               _n(Swara.GA), _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.PA,
        samvadi=Swara.SA,
        time_of_day="Night (3rd prahar)",
        rasa="Shanta (peace), devotional",
    ),
    "puriya_dhanashree": RagaDefinition(
        name="Puriya Dhanashree",
        thaat="Purvi",
        aroh=[_n(Swara.SA), _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.GA),
              _n(Swara.MA, SwaraVariant.TIVRA), _n(Swara.PA),
              _n(Swara.DHA), _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.DHA), _n(Swara.PA),
               _n(Swara.MA, SwaraVariant.TIVRA), _n(Swara.GA),
               _n(Swara.RE, SwaraVariant.KOMAL), _n(Swara.SA)],
        vadi=Swara.PA,
        samvadi=Swara.SA,
        time_of_day="Evening",
        rasa="Serious, emotional",
        komal_swaras=[Swara.RE],
        tivra_swaras=[Swara.MA],
    ),
    "jaunpuri": RagaDefinition(
        name="Jaunpuri",
        thaat="Asavari",
        aroh=[_n(Swara.SA), _n(Swara.RE), _n(Swara.GA, SwaraVariant.KOMAL), _n(Swara.MA),
              _n(Swara.PA), _n(Swara.DHA, SwaraVariant.KOMAL), _n(Swara.NI), _n(Swara.SA, octave=1)],
        avroh=[_n(Swara.SA, octave=1), _n(Swara.NI), _n(Swara.DHA, SwaraVariant.KOMAL),
               _n(Swara.PA), _n(Swara.MA), _n(Swara.GA, SwaraVariant.KOMAL),
               _n(Swara.RE), _n(Swara.SA)],
        vadi=Swara.DHA,
        samvadi=Swara.RE,
        time_of_day="Late morning",
        rasa="Shringara, gentle",
        komal_swaras=[Swara.GA, Swara.DHA],
    ),
}


class RagaCompositionEngine:
    """Engine for generating compositions based on raga grammar.

    Generates musically coherent sequences of notes following raga rules
    for each section: alap, jor, jhala, gat.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def compose(
        self,
        raga_name: str,
        sections: list[str] | None = None,
        duration: float = 60.0,
        laya: Laya = Laya.MADHYA,
    ) -> Composition:
        """Generate a full composition in the given raga.

        Args:
            raga_name: Name of the raga.
            sections: List of section names (alap, jor, jhala, gat).
            duration: Total duration in seconds.
            laya: Tempo classification.
        """
        raga = self.get_raga(raga_name)

        if sections is None:
            section_types = [
                CompositionSection.ALAP,
                CompositionSection.JOR,
                CompositionSection.JHALA,
                CompositionSection.GAT,
            ]
        else:
            section_types = [CompositionSection(s) for s in sections]

        config = CompositionConfig(
            raga_name=raga_name,
            laya=laya,
            duration_seconds=duration,
            sections=section_types,
        )

        # Distribute duration across sections
        section_weights = {
            CompositionSection.ALAP: 0.35,
            CompositionSection.JOR: 0.25,
            CompositionSection.JHALA: 0.15,
            CompositionSection.GAT: 0.25,
        }
        total_weight = sum(section_weights.get(s, 0.25) for s in section_types)

        generated_sections: list[GeneratedSection] = []
        for sec_type in section_types:
            weight = section_weights.get(sec_type, 0.25) / total_weight
            sec_duration = duration * weight
            section = self._generate_section(raga, sec_type, sec_duration, laya)
            generated_sections.append(section)

        from swara.instruments.tabla import TablaSynthesizer

        taal = TablaSynthesizer.get_taal(config.taal_name)

        return Composition(
            config=config,
            raga=raga,
            taal=taal,
            sections=generated_sections,
            total_duration=sum(s.duration_seconds for s in generated_sections),
        )

    def _generate_section(
        self,
        raga: RagaDefinition,
        section_type: CompositionSection,
        duration: float,
        laya: Laya,
    ) -> GeneratedSection:
        """Generate notes for a specific section."""
        generators = {
            CompositionSection.ALAP: self._generate_alap,
            CompositionSection.JOR: self._generate_jor,
            CompositionSection.JHALA: self._generate_jhala,
            CompositionSection.GAT: self._generate_gat,
        }
        gen_fn = generators[section_type]
        notes = gen_fn(raga, duration, laya)
        return GeneratedSection(
            section_type=section_type,
            notes=notes,
            duration_seconds=sum(n.duration for n in notes),
        )

    def _generate_alap(self, raga: RagaDefinition, duration: float, laya: Laya) -> list[SwaraNote]:
        """Generate alap (slow, free-rhythm introduction).

        Alap is unmetered and explores the raga note by note,
        starting from the lower octave and gradually ascending.
        """
        notes: list[SwaraNote] = []
        total_dur = 0.0
        aroh = raga.aroh if raga.aroh else [_n(Swara.SA)]
        avroh = raga.avroh if raga.avroh else [_n(Swara.SA)]

        # Start with Sa
        sa = _n(Swara.SA, duration=2.0)
        notes.append(sa)
        total_dur += sa.duration

        # Gradually introduce notes of the raga
        max_note_idx = 1
        while total_dur < duration and max_note_idx <= len(aroh):
            available = aroh[:max_note_idx]
            # Choose notes with emphasis on vadi
            for _ in range(self._rng.randint(2, 5)):
                if total_dur >= duration:
                    break
                note_template = self._rng.choice(available)
                note_dur = self._rng.uniform(1.0, 3.0)
                note = SwaraNote(
                    swara=note_template.swara,
                    variant=note_template.variant,
                    octave=note_template.octave,
                    duration=note_dur,
                    amplitude=self._rng.uniform(0.5, 0.9),
                    has_meend=self._rng.random() < 0.3,
                    has_gamak=self._rng.random() < 0.15,
                )
                # Add meend target occasionally
                if note.has_meend and len(available) > 1:
                    target_idx = self._rng.randint(0, len(available) - 1)
                    note.meend_target = available[target_idx].swara
                notes.append(note)
                total_dur += note.duration

            # Return to Sa periodically
            if self._rng.random() < 0.3:
                sa_return = _n(Swara.SA, duration=self._rng.uniform(0.8, 1.5))
                notes.append(sa_return)
                total_dur += sa_return.duration

            max_note_idx = min(max_note_idx + 1, len(aroh))

        return notes

    def _generate_jor(self, raga: RagaDefinition, duration: float, laya: Laya) -> list[SwaraNote]:
        """Generate jor (rhythmic pulse introduced, no taal).

        Jor introduces a steady pulse while continuing melodic exploration.
        """
        notes: list[SwaraNote] = []
        total_dur = 0.0
        all_notes = raga.aroh + raga.avroh

        pulse_duration = 0.5  # Steady pulse

        while total_dur < duration:
            # Alternate between aroh and avroh phrases
            if self._rng.random() < 0.5:
                phrase_source = raga.aroh if raga.aroh else [_n(Swara.SA)]
            else:
                phrase_source = raga.avroh if raga.avroh else [_n(Swara.SA)]

            phrase_len = self._rng.randint(3, 6)
            start_idx = self._rng.randint(0, max(0, len(phrase_source) - phrase_len))
            phrase = phrase_source[start_idx : start_idx + phrase_len]

            for note_template in phrase:
                if total_dur >= duration:
                    break
                note = SwaraNote(
                    swara=note_template.swara,
                    variant=note_template.variant,
                    octave=note_template.octave,
                    duration=pulse_duration,
                    amplitude=self._rng.uniform(0.6, 0.9),
                    has_gamak=self._rng.random() < 0.2,
                )
                notes.append(note)
                total_dur += note.duration

        return notes

    def _generate_jhala(self, raga: RagaDefinition, duration: float, laya: Laya) -> list[SwaraNote]:
        """Generate jhala (fast, rhythmic section with chikari strokes).

        Jhala features rapid alternation between melody notes and the
        high Sa drone string (chikari).
        """
        notes: list[SwaraNote] = []
        total_dur = 0.0
        all_notes = raga.aroh if raga.aroh else [_n(Swara.SA)]

        note_dur = 0.15  # Fast notes
        chikari = _n(Swara.SA, octave=1, duration=note_dur)

        note_idx = 0
        while total_dur < duration:
            # Melody note
            template = all_notes[note_idx % len(all_notes)]
            melody = SwaraNote(
                swara=template.swara,
                variant=template.variant,
                octave=template.octave,
                duration=note_dur,
                amplitude=0.8,
            )
            notes.append(melody)
            total_dur += note_dur

            # Chikari stroke
            if total_dur < duration:
                notes.append(SwaraNote(
                    swara=Swara.SA, octave=1, duration=note_dur, amplitude=0.6,
                ))
                total_dur += note_dur

            note_idx += 1

        return notes

    def _generate_gat(self, raga: RagaDefinition, duration: float, laya: Laya) -> list[SwaraNote]:
        """Generate gat (fixed composition within taal cycle).

        Gat is a composed melody set to a taal, forming the basis
        for improvisational elaboration.
        """
        notes: list[SwaraNote] = []
        total_dur = 0.0

        # Note duration based on laya
        laya_durations = {
            Laya.VILAMBIT: 0.8,
            Laya.MADHYA: 0.4,
            Laya.DRUT: 0.2,
            Laya.ATI_DRUT: 0.12,
        }
        note_dur = laya_durations.get(laya, 0.4)

        # Compose sthayi (first section of gat)
        all_notes = raga.aroh + raga.avroh
        pakad = raga.pakad if raga.pakad else all_notes

        # Create a basic gat composition using the pakad
        while total_dur < duration:
            # Play through pakad
            for template in pakad:
                if total_dur >= duration:
                    break
                note = SwaraNote(
                    swara=template.swara,
                    variant=template.variant,
                    octave=template.octave,
                    duration=note_dur,
                    amplitude=self._rng.uniform(0.7, 0.95),
                    has_gamak=self._rng.random() < 0.25,
                )
                notes.append(note)
                total_dur += note.duration

            # Add improvised taans between pakad repetitions
            if total_dur < duration and self._rng.random() < 0.5:
                taan_notes = self._generate_taan(raga, note_dur)
                for tn in taan_notes:
                    if total_dur >= duration:
                        break
                    notes.append(tn)
                    total_dur += tn.duration

        return notes

    def _generate_taan(self, raga: RagaDefinition, base_dur: float) -> list[SwaraNote]:
        """Generate a taan (fast melodic run)."""
        all_notes = raga.aroh + list(reversed(raga.avroh)) if raga.avroh else raga.aroh
        if not all_notes:
            return []

        taan_len = self._rng.randint(8, 16)
        fast_dur = base_dur * 0.5
        notes: list[SwaraNote] = []

        # Ascending run
        for i in range(taan_len):
            template = all_notes[i % len(all_notes)]
            notes.append(SwaraNote(
                swara=template.swara,
                variant=template.variant,
                octave=template.octave,
                duration=fast_dur,
                amplitude=0.85,
            ))

        return notes

    @staticmethod
    def get_raga(name: str) -> RagaDefinition:
        """Get a raga definition by name."""
        key = name.lower().replace(" ", "_")
        if key not in RAGA_REGISTRY:
            available = ", ".join(sorted(RAGA_REGISTRY.keys()))
            raise ValueError(f"Unknown raga '{name}'. Available: {available}")
        return RAGA_REGISTRY[key]

    @staticmethod
    def list_ragas() -> list[str]:
        """List all available raga names."""
        return sorted(RAGA_REGISTRY.keys())
