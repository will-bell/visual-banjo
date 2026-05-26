from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Group
from rich import box

_BAR_WIDTH = 41  # must be odd so there's a true center character
_CENTER = _BAR_WIDTH // 2

_TITLE = Text("visual-banjo", style="bold dim")


def _tune_color(cents: float) -> str:
    abs_c = abs(cents)
    if abs_c <= 10:
        return "green"
    if abs_c <= 30:
        return "yellow"
    return "red"


def _cents_bar(cents: float) -> Text:
    """41-char meter: ♭ on left, ♯ on right, cursor shows deviation."""
    clamped = max(-50.0, min(50.0, cents))
    cursor = int(round((clamped + 50) / 100 * (_BAR_WIDTH - 1)))
    color = _tune_color(cents)

    bar = Text()
    bar.append("♭ [", style="dim")
    for i in range(_BAR_WIDTH):
        if i == cursor:
            bar.append("█", style=f"bold {color}")
        elif i == _CENTER:
            bar.append("|", style="dim")
        else:
            bar.append("░", style="dim")
    bar.append("]  ♯", style="dim")
    return bar


def _tune_label(cents: float) -> Text:
    color = _tune_color(cents)
    direction = "in tune" if abs(cents) <= 5 else ("sharp" if cents > 0 else "flat")
    label = Text()
    label.append(f"{cents:+.1f} cents  ", style=color)
    label.append(direction, style=f"bold {color}")
    return label


def render_detection(note: str, octave: int, freq: float, cents: float) -> Panel:
    color = _tune_color(cents)

    body = Text(justify="center")
    body.append(f"\n{note}{octave}\n", style=f"bold {color}")
    body.append(f"{freq:.1f} Hz\n\n", style="dim")

    content = Group(
        Align(body, align="center"),
        Align(_cents_bar(cents), align="center"),
        Align(_tune_label(cents), align="center"),
    )
    return Panel(content, title=_TITLE, border_style="dim", box=box.ROUNDED, padding=(0, 2))


def render_listening() -> Panel:
    body = Text("\n\nListening...\n\n", style="dim italic", justify="center")
    return Panel(Align(body, align="center"), title=_TITLE, border_style="dim", box=box.ROUNDED, padding=(0, 2))
