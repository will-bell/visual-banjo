import queue
import sounddevice as sd
from rich.live import Live

from .audio import start_audio_stream, FREQ_MIN, FREQ_MAX, CONFIDENCE_THRESHOLD
from .theory import freq_to_note
from .display import render_detection, render_listening


def run() -> None:
    result_queue: queue.Queue[tuple[float, float]] = queue.Queue(maxsize=10)

    try:
        stream = start_audio_stream(result_queue)
    except sd.PortAudioError as e:
        print(f"Could not open microphone: {e}")
        print("Check that your microphone is connected and macOS has granted access.")
        return

    last_panel = render_listening()

    with stream, Live(last_panel, refresh_per_second=20) as live:
        try:
            while True:
                item = None
                try:
                    while True:
                        item = result_queue.get_nowait()
                except queue.Empty:
                    pass

                if item is None:
                    try:
                        item = result_queue.get(timeout=0.1)
                    except queue.Empty:
                        live.update(last_panel)
                        continue

                freq, confidence = item

                if confidence < CONFIDENCE_THRESHOLD or not (FREQ_MIN <= freq <= FREQ_MAX):
                    live.update(last_panel)
                    continue

                try:
                    note, octave, cents, _ = freq_to_note(freq)
                except ValueError:
                    live.update(last_panel)
                    continue

                last_panel = render_detection(note, octave, freq, cents)
                live.update(last_panel)

        except KeyboardInterrupt:
            pass
