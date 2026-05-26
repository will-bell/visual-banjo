# visual-banjo

A terminal app for real-time banjo note detection. Play a note into your microphone and see the note name, frequency, and how sharp or flat you are.

## Requirements

- macOS (uses the system microphone)
- [Homebrew](https://brew.sh)
- [uv](https://docs.astral.sh/uv/) — installed in the setup step below
- [just](https://just.systems) — installed in the setup step below

## Setup

```bash
# Install uv and just
brew install uv just

# Install Python dependencies
uv sync
```

On first run, macOS will show a permission dialog asking for microphone access — allow it.

## Running

```bash
# Run the app
just run

# Run with auto-reload on source file changes (for development)
just dev
```

From the menu, press `1` to open the tuner. Press `Ctrl+C` to return to the menu. Press `Ctrl+C` again (or `q`) to exit.

> In `just dev` mode, `Ctrl+C` stops the file watcher and exits completely.
