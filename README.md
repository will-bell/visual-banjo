# visual-banjo

A terminal app for exploring banjo music theory and detecting notes from a microphone.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- [just](https://just.systems) (optional convenience commands)
- macOS microphone access for the tuner (the fretboard explorer requires no microphone)

## Setup

```bash
uv sync
```

On macOS, `brew install uv just` installs the tools. On first tuner use, allow the microphone permission prompt.

## Running

```bash
just run
# or: uv run visual-banjo
```

From the menu:

- **1 — Tuner:** detect notes, frequency and intonation from microphone input. Ctrl+C returns to menu.
- **2 — Fretboard explorer:** choose Open G (`gDGBD`) or Double C (`gCGCD`), then optionally a chord root and major/minor quality. The display covers frets 0–17; chord roots are green, other chord tones yellow, and non-chord tones dimmed. Leave the root blank to show all notes. The fifth string has no positions at frets 0–4: its open G sounds at physical fret 5.
- **q — Quit.**

When the fretboard explorer is open, enter `q` at the tuning or root prompt to return to the menu. `Ctrl+C` also returns to the menu.

## Tests

```bash
uv run python -m unittest discover -s tests
```

## Development

```bash
just dev
```

See [algorithms.md](algorithms.md) for the music and signal-processing algorithms.
