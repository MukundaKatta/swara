"""Jugalbandi - instrument duet composition engine.

Generates call-and-response patterns between two instruments,
a hallmark of Indian classical music performance.
"""

from __future__ import annotations

import random
from typing import Optional

import numpy as np

from swara.models import (
    Composition,
    CompositionSection,
    GeneratedSection,
    Laya,
    RagaDefinition,
    Swara,
    SwaraNote,
    SwaraVariant,
)
from swara.composition.raga_engine import RagaCompositionEngine


class JugalbandiComposer:
    """Compose duet passages for two instruments in call-and-response style.

    In jugalbandi, two musicians take turns playing phrases, gradually
    building intensity and complexity, sometimes converging on
    simultaneous passages (sawal-jawab).
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self._raga_engine = RagaCompositionEngine(seed=seed)

    def compose_duet(
        self,
        raga_name: str,
        duration: float = 60.0,
        laya: Laya = Laya.MADHYA,
        phrase_length: float = 4.0,
        interaction_style: str = "sawal_jawab",
    ) -> JugalbandiComposition:
        """Generate a duet composition.

        Args:
            raga_name: Name of the raga.
            duration: Total duration in seconds.
            laya: Tempo classification.
            phrase_length: Average phrase duration in seconds.
            interaction_style: One of 'sawal_jawab' (call-response),
                             'parallel' (simultaneous), 'layakari' (rhythmic interplay).
        """
        raga = self._raga_engine.get_raga(raga_name)

        phrases_a: list[DuetPhrase] = []
        phrases_b: list[DuetPhrase] = []
        elapsed = 0.0
        turn = 0  # 0 = instrument A, 1 = instrument B

        while elapsed < duration:
            remaining = duration - elapsed
            p_dur = min(phrase_length + self._rng.uniform(-1, 1), remaining)
            if p_dur <= 0:
                break

            if interaction_style == "parallel":
                # Both instruments play simultaneously
                notes_a = self._generate_phrase(raga, p_dur, laya, lead=True)
                notes_b = self._generate_response(raga, notes_a, p_dur, laya)
                phrases_a.append(DuetPhrase(notes=notes_a, start_time=elapsed, duration=p_dur, is_call=True))
                phrases_b.append(DuetPhrase(notes=notes_b, start_time=elapsed, duration=p_dur, is_call=False))
                elapsed += p_dur

            elif interaction_style == "layakari":
                # Rhythmic interplay - interlocking patterns
                notes_a = self._generate_phrase(raga, p_dur, laya, lead=True)
                notes_b = self._generate_interlock(raga, notes_a, p_dur, laya)
                phrases_a.append(DuetPhrase(notes=notes_a, start_time=elapsed, duration=p_dur, is_call=True))
                phrases_b.append(DuetPhrase(notes=notes_b, start_time=elapsed, duration=p_dur, is_call=False))
                elapsed += p_dur

            else:  # sawal_jawab
                notes = self._generate_phrase(raga, p_dur, laya, lead=(turn == 0))
                phrase = DuetPhrase(
                    notes=notes,
                    start_time=elapsed,
                    duration=p_dur,
                    is_call=(turn == 0),
                )
                if turn == 0:
                    phrases_a.append(phrase)
                else:
                    # Response should echo and develop the call
                    call_notes = phrases_a[-1].notes if phrases_a else []
                    response = self._generate_response(raga, call_notes, p_dur, laya)
                    phrases_b.append(DuetPhrase(
                        notes=response, start_time=elapsed, duration=p_dur, is_call=False,
                    ))
                elapsed += p_dur
                turn = 1 - turn

        return JugalbandiComposition(
            raga=raga,
            laya=laya,
            instrument_a_phrases=phrases_a,
            instrument_b_phrases=phrases_b,
            total_duration=elapsed,
            interaction_style=interaction_style,
        )

    def _generate_phrase(
        self, raga: RagaDefinition, duration: float, laya: Laya, lead: bool
    ) -> list[SwaraNote]:
        """Generate a melodic phrase within the raga."""
        notes: list[SwaraNote] = []
        elapsed = 0.0
        source = raga.aroh if lead else raga.avroh
        if not source:
            source = [SwaraNote(swara=Swara.SA)]

        laya_dur = {Laya.VILAMBIT: 0.8, Laya.MADHYA: 0.4, Laya.DRUT: 0.2, Laya.ATI_DRUT: 0.12}
        base_dur = laya_dur.get(laya, 0.4)

        while elapsed < duration:
            template = self._rng.choice(source)
            note_dur = base_dur * self._rng.uniform(0.7, 1.5)
            note_dur = min(note_dur, duration - elapsed)
            if note_dur <= 0:
                break
            note = SwaraNote(
                swara=template.swara,
                variant=template.variant,
                octave=template.octave,
                duration=note_dur,
                amplitude=self._rng.uniform(0.6, 0.95),
                has_gamak=self._rng.random() < 0.2,
                has_meend=self._rng.random() < 0.15,
            )
            notes.append(note)
            elapsed += note_dur

        return notes

    def _generate_response(
        self, raga: RagaDefinition, call_notes: list[SwaraNote], duration: float, laya: Laya
    ) -> list[SwaraNote]:
        """Generate a response that echoes and develops the call phrase."""
        if not call_notes:
            return self._generate_phrase(raga, duration, laya, lead=False)

        response: list[SwaraNote] = []
        elapsed = 0.0

        # Echo some of the call notes, then develop
        echo_count = max(1, len(call_notes) // 2)
        for note in call_notes[:echo_count]:
            if elapsed >= duration:
                break
            # Slight variation on the echoed note
            resp_note = SwaraNote(
                swara=note.swara,
                variant=note.variant,
                octave=note.octave,
                duration=note.duration * self._rng.uniform(0.8, 1.2),
                amplitude=note.amplitude * 0.9,
                has_gamak=self._rng.random() < 0.3,
            )
            response.append(resp_note)
            elapsed += resp_note.duration

        # Continue with development using avroh
        remaining = duration - elapsed
        if remaining > 0:
            development = self._generate_phrase(raga, remaining, laya, lead=False)
            response.extend(development)

        return response

    def _generate_interlock(
        self, raga: RagaDefinition, partner_notes: list[SwaraNote], duration: float, laya: Laya
    ) -> list[SwaraNote]:
        """Generate interlocking patterns that complement the partner's rhythm."""
        notes: list[SwaraNote] = []
        elapsed = 0.0
        source = raga.avroh if raga.avroh else [SwaraNote(swara=Swara.SA)]

        for pn in partner_notes:
            if elapsed >= duration:
                break
            # Play in the gaps - offset by half a beat
            rest_dur = pn.duration * 0.4
            if elapsed + rest_dur < duration:
                # Short rest
                notes.append(SwaraNote(
                    swara=Swara.SA, duration=rest_dur, amplitude=0.0,
                ))
                elapsed += rest_dur

            # Complementary note
            template = self._rng.choice(source)
            note_dur = pn.duration * 0.6
            note_dur = min(note_dur, duration - elapsed)
            if note_dur <= 0:
                break
            notes.append(SwaraNote(
                swara=template.swara,
                variant=template.variant,
                octave=template.octave,
                duration=note_dur,
                amplitude=0.75,
            ))
            elapsed += note_dur

        return notes


class DuetPhrase:
    """A single phrase in a jugalbandi duet."""

    def __init__(
        self,
        notes: list[SwaraNote],
        start_time: float,
        duration: float,
        is_call: bool,
    ) -> None:
        self.notes = notes
        self.start_time = start_time
        self.duration = duration
        self.is_call = is_call

    @property
    def note_count(self) -> int:
        return len(self.notes)


class JugalbandiComposition:
    """A complete jugalbandi (duet) composition."""

    def __init__(
        self,
        raga: RagaDefinition,
        laya: Laya,
        instrument_a_phrases: list[DuetPhrase],
        instrument_b_phrases: list[DuetPhrase],
        total_duration: float,
        interaction_style: str,
    ) -> None:
        self.raga = raga
        self.laya = laya
        self.instrument_a_phrases = instrument_a_phrases
        self.instrument_b_phrases = instrument_b_phrases
        self.total_duration = total_duration
        self.interaction_style = interaction_style

    @property
    def total_notes_a(self) -> int:
        return sum(p.note_count for p in self.instrument_a_phrases)

    @property
    def total_notes_b(self) -> int:
        return sum(p.note_count for p in self.instrument_b_phrases)
