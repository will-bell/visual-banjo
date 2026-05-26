from math import log2

_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

OPEN_STRINGS_G_TUNING = {
    "D3": 146.83,
    "G3": 196.00,
    "B3": 246.94,
    "D4": 293.66,
    "G4": 392.00,
}


def freq_to_note(freq: float) -> tuple[str, int, float, float]:
    """Return (note_name, octave, cents_deviation, ideal_freq) for a frequency in Hz.

    cents_deviation is positive for sharp, negative for flat.
    Raises ValueError if freq is out of the audible instrument range.

    MIDI note number
    ----------------
    The MIDI standard maps A4 = 440 Hz to note number 69. The formula
        midi = 12 * log2(f / 440) + 69
    follows directly from equal temperament: each octave doubles the
    frequency, so each semitone multiplies by 2^(1/12). Rounding to the
    nearest integer gives the closest note.

    Reference: MIDI Tuning Standard, MIDI Manufacturers Association (MMA).
    https://midi.org/midi-tuning-standard
    Accessible derivation: https://en.wikipedia.org/wiki/MIDI_tuning_standard

    Equal temperament & cents
    -------------------------
    In 12-tone equal temperament every semitone is exactly 2^(1/12) ≈ 1.0595
    times the previous one. A cent is 1/100 of a semitone, so 1200 cents = 1
    octave. The deviation from ideal is:
        cents = 1200 * log2(f / f_ideal)
    ±50 cents is the maximum before the note rounds to the adjacent semitone.

    Reference: Ellis, A.J. (1885). Appendix to Helmholtz, H. "On the
    Sensations of Tone". Dover reprint 1954. (Original definition of the cent.)
    Accessible: https://en.wikipedia.org/wiki/Cent_(music)
    """
    if freq < 20 or freq > 20000:
        raise ValueError(f"Frequency {freq:.1f} Hz is out of range")

    midi = 12 * log2(freq / 440.0) + 69
    midi_rounded = round(midi)
    note_name = _NOTE_NAMES[midi_rounded % 12]
    octave = (midi_rounded // 12) - 1
    ideal_freq = 440.0 * 2 ** ((midi_rounded - 69) / 12)
    cents = 1200 * log2(freq / ideal_freq)

    return note_name, octave, cents, ideal_freq
