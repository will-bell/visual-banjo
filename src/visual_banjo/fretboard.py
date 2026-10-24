"""Banjo fretboard positions and chord-tone visualization.

String 5 is the short drone string, beginning at physical fret 5.
MIDI numbers preserve octaves so the short string is displayed correctly.
"""
from rich import box
from rich.console import Console
from rich.table import Table

NOTES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
TUNINGS = {
    "g": ("Open G (gDGBD)", (67, 50, 55, 59, 62)),
    "c": ("Double C (gCGCD)", (67, 48, 55, 60, 62)),
}
CHORD_INTERVALS = {"major": (0, 4, 7), "minor": (0, 3, 7)}
STRING_START_FRETS = (5, 0, 0, 0, 0)


def note_name(midi: int) -> str:
    """Convert a MIDI semitone to a pitch class.

    Reference: MIDI 1.0 Detailed Specification, note-number convention.
    Accessible: https://en.wikipedia.org/wiki/MIDI_tuning_standard
    """
    return NOTES[midi % 12]


def fretboard_notes(tuning: str, max_fret: int = 17) -> list[list[str | None]]:
    """List sounding note names at each physical fret, with absent drone frets blank.

    On the fifth string, the open note sounds at physical fret 5; the first
    stopped note is at fret 6. The other four strings begin at the nut.

    Reference: Earl Scruggs, *Earl Scruggs and the 5-String Banjo*,
    revised edition (2005), tuning and fifth-string layout.
    Accessible: https://en.wikipedia.org/wiki/Five-string_banjo
    """
    if tuning not in TUNINGS:
        raise ValueError(f"Unknown tuning: {tuning}")
    if max_fret < 0:
        raise ValueError("max_fret must be nonnegative")
    pitches = TUNINGS[tuning][1]
    return [
        [
            None if fret < start else note_name(midi + fret - start)
            for fret in range(max_fret + 1)
        ]
        for midi, start in zip(pitches, STRING_START_FRETS)
    ]


def chord_notes(root: str, quality: str = "major") -> set[str]:
    """Return the pitch classes of a major or minor triad.

    A major triad contains semitone intervals 0, 4, 7; a minor triad
    contains 0, 3, 7, counted upward from the root.

    Reference: Kostka, Payne & Almén, *Tonal Harmony*, 8th ed., triads.
    Accessible: https://en.wikipedia.org/wiki/Triad_(music)
    """
    root = root.upper().replace("♯", "#")
    if root not in NOTES:
        raise ValueError(f"Unknown root: {root}")
    if quality not in CHORD_INTERVALS:
        raise ValueError(f"Unknown chord quality: {quality}")
    return {NOTES[(NOTES.index(root) + step) % 12] for step in CHORD_INTERVALS[quality]}


def render_fretboard(tuning: str, root: str | None = None,
                     quality: str = "major", max_fret: int = 17) -> Table:
    """Draw a fretboard with all notes, optionally emphasizing chord tones."""
    name, pitches = TUNINGS[tuning]
    wanted = chord_notes(root, quality) if root is not None else None
    table = Table(
        title=f"{name}" + (f"  —  {root} {quality}" if root else ""),
        box=box.SIMPLE, show_edge=False, pad_edge=False,
        caption="5th string begins at fret 5; dots mark chord tones." if wanted else
                "5th string begins at fret 5.",
    )
    table.add_column("String", style="cyan", no_wrap=True)
    for fret in range(max_fret + 1):
        table.add_column(str(fret), justify="center", min_width=3, no_wrap=True)
    for string_number, (midi, notes) in enumerate(
        zip(pitches, fretboard_notes(tuning, max_fret)), start=1
    ):
        cells = []
        for note in notes:
            if note is None:
                cells.append(" ")
            elif wanted is None:
                cells.append(note)
            elif note in wanted:
                style = "bold green" if note == root else "bold yellow"
                cells.append(f"[{style}]●{note}[/{style}]")
            else:
                cells.append(f"[dim]{note}[/dim]")
        table.add_row(f"{6 - string_number} ({note_name(midi)})", *cells)
    return table


def run() -> None:
    """Terminal fretboard explorer, with no microphone required."""
    console = Console()
    while True:
        console.print("\n[bold]Fretboard explorer[/bold]  [dim](Enter or q to return)[/dim]")
        tuning = input("  Tuning [g] Open G / [c] Double C (default g): ").strip().lower()
        if tuning in ("q", "quit"):
            return
        tuning = tuning or "g"
        if tuning not in TUNINGS:
            console.print("[red]Choose g or c.[/red]")
            continue
        root = input("  Chord root (C, C#, D ... or blank for all notes): ").strip().upper()
        if root in ("Q", "QUIT"):
            return
        quality = "major"
        if root:
            quality = input("  Chord quality [major/minor] (default major): ").strip().lower() or "major"
            if quality in ("q", "quit"):
                return
        try:
            table = render_fretboard(tuning, root or None, quality)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            continue
        console.print(table)
        console.print("[dim]Green = root; yellow = other chord tones; dim = outside chord.[/dim]" if root else
                      "[dim]All chromatic note positions shown.[/dim]")
