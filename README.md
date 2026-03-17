# SWARA - Indian Classical Music Composer

SWARA is a Python-based Indian classical music composition and synthesis engine featuring authentic tabla, sitar, veena, and tanpura synthesis with raga-aware composition capabilities.

## Features

- **Sitar Synthesis** - String resonance modeling, meend (glissando), gamak (oscillation), and sympathetic string simulation
- **Tabla Synthesis** - 30+ bol patterns across common taals (Teentaal, Jhaptaal, Ektaal, Rupak, Dadra, Keherwa, and more)
- **Veena Synthesis** - Sustained note generation with gamakas and characteristic veena timbre
- **Tanpura Drone** - Continuous Sa-Pa-Sa drone with rich harmonic content
- **Raga Engine** - 20+ raga definitions with automatic alap, jor, jhala, and gat composition
- **Tala Engine** - Layakari support for vilambit (slow), madhya (medium), and drut (fast) tempos
- **Jugalbandi** - Instrument duet composition with call-and-response patterns

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from swara.composition.raga_engine import RagaCompositionEngine
from swara.composition.tala_engine import TalaEngine
from swara.instruments.sitar import SitarSynthesizer
from swara.instruments.tabla import TablaSynthesizer

# Create a composition in Raga Yaman
engine = RagaCompositionEngine()
composition = engine.compose("yaman", sections=["alap", "jor", "gat"])

# Synthesize tabla accompaniment
tabla = TablaSynthesizer(sample_rate=44100)
tala = TalaEngine(taal="teentaal", laya="madhya")
```

## CLI Usage

```bash
# List available ragas
swara list-ragas

# List available taals
swara list-taals

# Compose a piece
swara compose --raga yaman --taal teentaal --laya madhya --duration 60

# Generate a report
swara report --raga yaman --taal teentaal
```

## Project Structure

```
src/swara/
  instruments/
    sitar.py      - Sitar synthesis with string resonance
    tabla.py      - Tabla synthesis with bol patterns
    veena.py      - Veena synthesis with gamakas
    tanpura.py    - Tanpura drone generation
  composition/
    raga_engine.py  - Raga-based composition (alap/jor/jhala/gat)
    tala_engine.py  - Tala and layakari management
    jugalbandi.py   - Instrument duet composition
  models.py       - Pydantic data models
  report.py       - Rich-formatted composition reports
  cli.py          - Click-based CLI interface
```

## Supported Ragas

Yaman, Bhairav, Todi, Marwa, Puriya, Bilawal, Khamaj, Kafi, Asavari, Bhairavi,
Darbari Kanada, Malkauns, Bageshree, Des, Pilu, Bihag, Kedar, Hansadhwani,
Hamsadhwani, Durga, Shankara, and more.

## Supported Taals

Teentaal (16 beats), Jhaptaal (10 beats), Ektaal (12 beats), Rupak (7 beats),
Dadra (6 beats), Keherwa (8 beats), Tilwada (16 beats), Dhamar (14 beats),
Jhoomra (14 beats), Deepchandi (14 beats), and more.

## License

MIT
