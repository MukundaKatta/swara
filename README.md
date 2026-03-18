# swara

**Swara — Indian Classical Music Composer. AI raga composition with tabla, sitar, and veena synthesis.**

![Build](https://img.shields.io/badge/build-passing-brightgreen) ![License](https://img.shields.io/badge/license-proprietary-red)

## Install
```bash
pip install -e ".[dev]"
```

## Quick Start
```python
from src.core import Swara
 instance = Swara()
r = instance.compose(input="test")
```

## CLI
```bash
python -m src status
python -m src run --input "data"
```

## API
| Method | Description |
|--------|-------------|
| `compose()` | Compose |
| `synthesize()` | Synthesize |
| `render()` | Render |
| `adjust_params()` | Adjust params |
| `export_audio()` | Export audio |
| `get_presets()` | Get presets |
| `get_stats()` | Get stats |
| `reset()` | Reset |

## Test
```bash
pytest tests/ -v
```

## License
(c) 2026 Officethree Technologies. All Rights Reserved.
