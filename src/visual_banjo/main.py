from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from . import tuner, fretboard

_MENU_ITEMS = [
    ("1", "Tuner", "detect notes in real time"),
    ("2", "Fretboard explorer", "map notes and chord tones in Open G or Double C"),
]

console = Console()


def _render_menu() -> Panel:
    body = Text("\n")
    for key, name, desc in _MENU_ITEMS:
        body.append(f"  [{key}] ", style="bold cyan")
        body.append(f"{name}", style="bold")
        body.append(f"  —  {desc}\n", style="dim")
    body.append("\n")
    return Panel(body, title=Text("visual-banjo", style="bold dim"), box=box.ROUNDED, border_style="dim")


def main() -> None:
    console.clear()
    while True:
        console.print(_render_menu())
        try:
            choice = input("  > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            try:
                tuner.run()
            except KeyboardInterrupt:
                pass
            console.clear()
        elif choice == "2":
            try:
                fretboard.run()
            except (KeyboardInterrupt, EOFError):
                pass
            console.clear()
        elif choice in ("q", "Q", ""):
            break
        else:
            console.print(f"  [dim]Unknown option '{choice}' — try 1, 2, or q to quit.[/dim]\n")


if __name__ == "__main__":
    main()
