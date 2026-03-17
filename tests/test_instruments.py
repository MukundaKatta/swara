"""Tests for instrument synthesizers."""

import numpy as np
import pytest

from swara.models import Bol, Swara, SwaraNote, SwaraVariant
from swara.instruments.sitar import SitarSynthesizer
from swara.instruments.tabla import TablaSynthesizer, TAAL_REGISTRY, BOL_PATTERNS
from swara.instruments.veena import VeenaSynthesizer
from swara.instruments.tanpura import TanpuraDrone


class TestTablaSynthesizer:
    def setup_method(self):
        self.tabla = TablaSynthesizer(sample_rate=22050)

    def test_synthesize_na(self):
        signal = self.tabla.synthesize_bol(Bol.NA, duration=0.2)
        assert len(signal) > 0
        assert signal.dtype == np.float64

    def test_synthesize_all_bols(self):
        for bol in Bol:
            signal = self.tabla.synthesize_bol(bol, duration=0.15)
            assert len(signal) > 0, f"Failed for bol: {bol}"

    def test_empty_bol_is_silence(self):
        signal = self.tabla.synthesize_bol(Bol.EMPTY, duration=0.1)
        assert np.all(signal == 0)

    def test_amplitude_scaling(self):
        loud = self.tabla.synthesize_bol(Bol.DHA, duration=0.1, amplitude=1.0)
        quiet = self.tabla.synthesize_bol(Bol.DHA, duration=0.1, amplitude=0.1)
        assert np.max(np.abs(loud)) > np.max(np.abs(quiet))

    def test_synthesize_pattern(self):
        pattern = BOL_PATTERNS[0]
        signal = self.tabla.synthesize_pattern(pattern, tempo_bpm=120)
        assert len(signal) > 0

    def test_synthesize_theka(self):
        taal = TAAL_REGISTRY["teentaal"]
        signal = self.tabla.synthesize_theka(taal, cycles=1, tempo_bpm=120)
        assert len(signal) > 0

    def test_list_taals(self):
        taals = TablaSynthesizer.list_taals()
        assert "teentaal" in taals
        assert "jhaptaal" in taals
        assert len(taals) >= 10

    def test_get_taal(self):
        taal = TablaSynthesizer.get_taal("teentaal")
        assert taal.name == "Teentaal"
        assert taal.matra == 16

    def test_get_taal_invalid(self):
        with pytest.raises(ValueError):
            TablaSynthesizer.get_taal("nonexistent")

    def test_bol_patterns_count(self):
        patterns = TablaSynthesizer.get_bol_patterns()
        assert len(patterns) >= 30

    def test_taal_registry_count(self):
        assert len(TAAL_REGISTRY) >= 10


class TestSitarSynthesizer:
    def setup_method(self):
        self.sitar = SitarSynthesizer(sample_rate=22050)

    def test_synthesize_note(self):
        note = SwaraNote(swara=Swara.SA, duration=0.5)
        signal = self.sitar.synthesize_note(note)
        assert len(signal) > 0
        assert signal.dtype == np.float64

    def test_synthesize_with_meend(self):
        note = SwaraNote(
            swara=Swara.GA, duration=0.5,
            has_meend=True, meend_target=Swara.PA,
        )
        signal = self.sitar.synthesize_note(note)
        assert len(signal) > 0

    def test_synthesize_with_gamak(self):
        note = SwaraNote(swara=Swara.DHA, duration=0.5, has_gamak=True)
        signal = self.sitar.synthesize_note(note)
        assert len(signal) > 0

    def test_synthesize_phrase(self):
        notes = [
            SwaraNote(swara=Swara.SA, duration=0.3),
            SwaraNote(swara=Swara.RE, duration=0.3),
            SwaraNote(swara=Swara.GA, duration=0.3),
        ]
        signal = self.sitar.synthesize_phrase(notes)
        assert len(signal) > 0

    def test_empty_phrase(self):
        signal = self.sitar.synthesize_phrase([])
        assert len(signal) == 0

    def test_chikari(self):
        signal = self.sitar.synthesize_chikari(duration=1.0, tempo_bpm=120)
        assert len(signal) > 0

    def test_jawari_effect(self):
        sitar_no_jawari = SitarSynthesizer(sample_rate=22050, jawari_amount=0.0)
        sitar_jawari = SitarSynthesizer(sample_rate=22050, jawari_amount=0.5)
        note = SwaraNote(swara=Swara.PA, duration=0.3)
        sig1 = sitar_no_jawari.synthesize_note(note)
        sig2 = sitar_jawari.synthesize_note(note)
        # They should differ
        assert not np.allclose(sig1, sig2, atol=1e-6)


class TestVeenaSynthesizer:
    def setup_method(self):
        self.veena = VeenaSynthesizer(sample_rate=22050)

    def test_synthesize_note(self):
        note = SwaraNote(swara=Swara.SA, duration=0.5)
        signal = self.veena.synthesize_note(note)
        assert len(signal) > 0

    def test_gamaka_kampita(self):
        note = SwaraNote(swara=Swara.GA, duration=0.5)
        signal = self.veena.synthesize_note(note, gamaka_type="kampita")
        assert len(signal) > 0

    def test_gamaka_jaru(self):
        note = SwaraNote(swara=Swara.PA, duration=0.5)
        signal = self.veena.synthesize_note(note, gamaka_type="jaru")
        assert len(signal) > 0

    def test_gamaka_sphurita(self):
        note = SwaraNote(swara=Swara.DHA, duration=0.5)
        signal = self.veena.synthesize_note(note, gamaka_type="sphurita")
        assert len(signal) > 0

    def test_gamaka_pratyahata(self):
        note = SwaraNote(swara=Swara.NI, duration=0.5)
        signal = self.veena.synthesize_note(note, gamaka_type="pratyahata")
        assert len(signal) > 0

    def test_synthesize_phrase(self):
        notes = [
            SwaraNote(swara=Swara.SA, duration=0.3),
            SwaraNote(swara=Swara.GA, duration=0.3),
            SwaraNote(swara=Swara.PA, duration=0.3),
        ]
        signal = self.veena.synthesize_phrase(notes, gamakas=["none", "kampita", "jaru"])
        assert len(signal) > 0

    def test_sustained_note(self):
        note = SwaraNote(swara=Swara.MA, duration=0.5)
        signal = self.veena.synthesize_sustained(note, sustain_factor=2.0)
        expected_len = int(22050 * 0.5 * 2.0)
        assert abs(len(signal) - expected_len) < 10

    def test_gamak_flag(self):
        note = SwaraNote(swara=Swara.RE, duration=0.5, has_gamak=True)
        signal = self.veena.synthesize_note(note)
        assert len(signal) > 0


class TestTanpuraDrone:
    def setup_method(self):
        self.tanpura = TanpuraDrone(sample_rate=22050)

    def test_generate_drone(self):
        signal = self.tanpura.generate_drone(duration=2.0)
        assert len(signal) > 0
        assert len(signal) == int(22050 * 2.0)

    def test_drone_amplitude(self):
        signal = self.tanpura.generate_drone(duration=1.0, amplitude=0.5)
        assert np.max(np.abs(signal)) <= 0.5 + 0.01

    def test_single_cycle(self):
        signal = self.tanpura.generate_single_cycle()
        assert len(signal) == int(22050 * 4.0)

    def test_sa_pa_tuning(self):
        tanpura = TanpuraDrone(sample_rate=22050, tuning="sa_pa")
        assert tanpura.string_freqs[1] == tanpura.sa_frequency * 3 / 2

    def test_sa_ma_tuning(self):
        tanpura = TanpuraDrone(sample_rate=22050, tuning="sa_ma")
        assert tanpura.string_freqs[1] == tanpura.sa_frequency * 4 / 3

    def test_jawari_parameter(self):
        tanpura_buzz = TanpuraDrone(sample_rate=22050, jawari_amount=0.8)
        tanpura_clean = TanpuraDrone(sample_rate=22050, jawari_amount=0.0)
        sig1 = tanpura_buzz.generate_drone(duration=1.0)
        sig2 = tanpura_clean.generate_drone(duration=1.0)
        # Different jawari should produce different signals
        assert not np.allclose(sig1, sig2, atol=1e-6)
