"""Tests for composition engines."""

import pytest

from swara.models import CompositionSection, Laya, Swara
from swara.composition.raga_engine import RagaCompositionEngine, RAGA_REGISTRY
from swara.composition.tala_engine import TalaEngine
from swara.composition.jugalbandi import JugalbandiComposer
from swara.instruments.tabla import TAAL_REGISTRY


class TestRagaCompositionEngine:
    def setup_method(self):
        self.engine = RagaCompositionEngine(seed=42)

    def test_compose_basic(self):
        comp = self.engine.compose("yaman", duration=10.0)
        assert comp.raga.name == "Yaman"
        assert comp.total_duration > 0
        assert comp.note_count > 0

    def test_compose_all_sections(self):
        comp = self.engine.compose(
            "bhairav",
            sections=["alap", "jor", "jhala", "gat"],
            duration=20.0,
        )
        assert len(comp.sections) == 4
        section_types = {s.section_type for s in comp.sections}
        assert CompositionSection.ALAP in section_types
        assert CompositionSection.JOR in section_types
        assert CompositionSection.JHALA in section_types
        assert CompositionSection.GAT in section_types

    def test_compose_single_section(self):
        comp = self.engine.compose("todi", sections=["alap"], duration=10.0)
        assert len(comp.sections) == 1
        assert comp.sections[0].section_type == CompositionSection.ALAP

    def test_compose_different_layas(self):
        for laya in [Laya.VILAMBIT, Laya.MADHYA, Laya.DRUT]:
            comp = self.engine.compose("yaman", duration=5.0, laya=laya)
            assert comp.note_count > 0

    def test_get_raga(self):
        raga = RagaCompositionEngine.get_raga("yaman")
        assert raga.name == "Yaman"
        assert raga.vadi == Swara.GA

    def test_get_raga_invalid(self):
        with pytest.raises(ValueError):
            RagaCompositionEngine.get_raga("nonexistent")

    def test_list_ragas(self):
        ragas = RagaCompositionEngine.list_ragas()
        assert len(ragas) >= 20
        assert "yaman" in ragas
        assert "bhairav" in ragas

    def test_raga_registry_count(self):
        assert len(RAGA_REGISTRY) >= 20

    def test_all_ragas_composable(self):
        """Every registered raga should be composable."""
        for raga_name in RAGA_REGISTRY:
            comp = self.engine.compose(raga_name, duration=3.0, sections=["alap"])
            assert comp.note_count > 0, f"Failed for raga: {raga_name}"

    def test_reproducible_with_seed(self):
        engine1 = RagaCompositionEngine(seed=123)
        engine2 = RagaCompositionEngine(seed=123)
        comp1 = engine1.compose("yaman", sections=["gat"], duration=5.0)
        comp2 = engine2.compose("yaman", sections=["gat"], duration=5.0)
        assert comp1.note_count == comp2.note_count

    def test_raga_definitions_have_aroh_avroh(self):
        for name, raga in RAGA_REGISTRY.items():
            assert len(raga.aroh) > 0, f"Raga {name} missing aroh"
            assert len(raga.avroh) > 0, f"Raga {name} missing avroh"


class TestTalaEngine:
    def test_init_defaults(self):
        engine = TalaEngine()
        assert engine.taal_def.name == "Teentaal"
        assert engine.laya == Laya.MADHYA

    def test_beat_duration(self):
        engine = TalaEngine(laya=Laya.MADHYA, bpm=120)
        assert abs(engine.beat_duration - 0.5) < 0.01

    def test_cycle_duration(self):
        engine = TalaEngine(taal="teentaal", bpm=120)
        assert abs(engine.cycle_duration - 8.0) < 0.01  # 16 beats * 0.5s

    def test_generate_theka(self):
        engine = TalaEngine(taal="teentaal")
        theka = engine.generate_theka(cycles=2)
        assert len(theka) == 32  # 16 * 2

    def test_generate_accompaniment(self):
        engine = TalaEngine(taal="dadra", bpm=120, seed=42)
        bols = engine.generate_accompaniment(duration=5.0)
        assert len(bols) > 0

    def test_layakari_dugun(self):
        engine = TalaEngine(seed=42)
        original = engine.generate_theka(cycles=1)
        doubled = engine.apply_layakari(original, subdivision=2)
        assert len(doubled) == len(original) * 2

    def test_layakari_tigun(self):
        engine = TalaEngine(seed=42)
        original = engine.generate_theka(cycles=1)
        tripled = engine.apply_layakari(original, subdivision=3)
        assert len(tripled) == len(original) * 3

    def test_generate_tihai(self):
        engine = TalaEngine()
        tihai = engine.generate_tihai()
        assert len(tihai) > 0
        # Tihai should have the pattern 3 times

    def test_generate_chakradar(self):
        engine = TalaEngine()
        chakradar = engine.generate_chakradar()
        assert len(chakradar) > 0

    def test_vibhag_markers(self):
        engine = TalaEngine(taal="teentaal")
        markers = engine.get_vibhag_markers()
        assert len(markers) == 4
        assert markers[0][1] == "sam"

    def test_laya_bpm_clamping(self):
        # Vilambit should clamp to 30-60
        engine = TalaEngine(laya=Laya.VILAMBIT, bpm=200)
        assert engine.bpm <= 60

    def test_string_laya(self):
        engine = TalaEngine(laya="madhya")
        assert engine.laya == Laya.MADHYA

    def test_list_layas(self):
        layas = TalaEngine.list_layas()
        assert len(layas) >= 3

    def test_all_taals(self):
        for taal_name in TAAL_REGISTRY:
            engine = TalaEngine(taal=taal_name)
            theka = engine.generate_theka()
            assert len(theka) > 0, f"Failed for taal: {taal_name}"


class TestJugalbandiComposer:
    def setup_method(self):
        self.composer = JugalbandiComposer(seed=42)

    def test_sawal_jawab(self):
        comp = self.composer.compose_duet(
            "yaman", duration=10.0, interaction_style="sawal_jawab",
        )
        assert comp.total_duration > 0
        assert comp.total_notes_a > 0

    def test_parallel(self):
        comp = self.composer.compose_duet(
            "bhairav", duration=10.0, interaction_style="parallel",
        )
        assert len(comp.instrument_a_phrases) > 0
        assert len(comp.instrument_b_phrases) > 0

    def test_layakari_style(self):
        comp = self.composer.compose_duet(
            "todi", duration=10.0, interaction_style="layakari",
        )
        assert comp.total_notes_a > 0
        assert comp.total_notes_b > 0

    def test_different_layas(self):
        for laya in [Laya.VILAMBIT, Laya.MADHYA, Laya.DRUT]:
            comp = self.composer.compose_duet("yaman", duration=5.0, laya=laya)
            assert comp.total_notes_a > 0
