"""Tests for SWARA data models."""

import pytest

from swara.models import (
    Bol,
    BolPattern,
    Composition,
    CompositionConfig,
    CompositionSection,
    GeneratedSection,
    Laya,
    RagaDefinition,
    Swara,
    SwaraNote,
    SwaraVariant,
    TaalDefinition,
)


class TestSwaraNote:
    def test_default_note(self):
        note = SwaraNote(swara=Swara.SA)
        assert note.swara == Swara.SA
        assert note.variant == SwaraVariant.SHUDDHA
        assert note.octave == 0
        assert note.duration == 0.5
        assert note.amplitude == 0.8

    def test_frequency_sa(self):
        note = SwaraNote(swara=Swara.SA)
        assert abs(note.frequency - 261.63) < 0.01

    def test_frequency_pa(self):
        note = SwaraNote(swara=Swara.PA)
        expected = 261.63 * 3 / 2
        assert abs(note.frequency - expected) < 0.01

    def test_frequency_octave(self):
        note_low = SwaraNote(swara=Swara.SA, octave=-1)
        note_mid = SwaraNote(swara=Swara.SA, octave=0)
        note_high = SwaraNote(swara=Swara.SA, octave=1)
        assert abs(note_high.frequency - note_mid.frequency * 2) < 0.01
        assert abs(note_low.frequency - note_mid.frequency / 2) < 0.01

    def test_komal_re(self):
        note = SwaraNote(swara=Swara.RE, variant=SwaraVariant.KOMAL)
        expected = 261.63 * 256 / 243
        assert abs(note.frequency - expected) < 0.01

    def test_tivra_ma(self):
        note = SwaraNote(swara=Swara.MA, variant=SwaraVariant.TIVRA)
        expected = 261.63 * 729 / 512
        assert abs(note.frequency - expected) < 0.01

    def test_meend_fields(self):
        note = SwaraNote(swara=Swara.GA, has_meend=True, meend_target=Swara.PA)
        assert note.has_meend is True
        assert note.meend_target == Swara.PA

    def test_gamak_field(self):
        note = SwaraNote(swara=Swara.DHA, has_gamak=True)
        assert note.has_gamak is True


class TestBolPattern:
    def test_create_pattern(self):
        pattern = BolPattern(
            name="test",
            bols=[Bol.DHA, Bol.DHIN, Bol.DHA],
            matra_count=3,
        )
        assert len(pattern.bols) == 3
        assert pattern.matra_count == 3

    def test_pattern_validation(self):
        with pytest.raises(Exception):
            BolPattern(name="bad", bols=[], matra_count=0)


class TestTaalDefinition:
    def test_teentaal_structure(self):
        taal = TaalDefinition(
            name="Teentaal",
            matra=16,
            vibhag=[4, 4, 4, 4],
            sam=1,
            khali=[9],
        )
        assert taal.matra == 16
        assert sum(taal.vibhag) == 16
        assert taal.sam == 1


class TestComposition:
    def test_note_count(self):
        config = CompositionConfig(raga_name="yaman")
        raga = RagaDefinition(name="Yaman")
        taal = TaalDefinition(name="Teentaal", matra=16)

        section = GeneratedSection(
            section_type=CompositionSection.ALAP,
            notes=[SwaraNote(swara=Swara.SA), SwaraNote(swara=Swara.RE)],
            duration_seconds=2.0,
        )

        comp = Composition(
            config=config, raga=raga, taal=taal,
            sections=[section], total_duration=2.0,
        )
        assert comp.note_count == 2
        assert comp.bol_count == 0


class TestLaya:
    def test_laya_values(self):
        assert Laya.VILAMBIT.value == "vilambit"
        assert Laya.MADHYA.value == "madhya"
        assert Laya.DRUT.value == "drut"
