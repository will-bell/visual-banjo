# Algorithms

## Pitch detection (`audio.py`)

### Normalized autocorrelation

**Used for:** Identifying the fundamental frequency (pitch) of a note played into the microphone.

A periodic signal with period T0 looks similar to itself when shifted by T0 samples. The autocorrelation function (ACF) measures this self-similarity at each possible shift (lag). The first strong peak above lag 0 corresponds to T0, and the fundamental frequency follows as f0 = sample_rate / T0. The ACF is normalized so that a perfectly periodic signal scores 1.0 at its peak and noise scores near 0 — this normalized peak value is used directly as the confidence score.

**Primary reference:** Rabiner, L.R. (1977). On the use of autocorrelation analysis for pitch detection. *IEEE Transactions on Acoustics, Speech, and Signal Processing*, 25(1), 24–33.
https://doi.org/10.1109/TASSP.1977.1162905

---

### FFT acceleration of autocorrelation (Wiener–Khinchin theorem)

**Used for:** Computing the autocorrelation efficiently — O(n log n) instead of O(n²).

The Wiener–Khinchin theorem states that the autocorrelation of a signal equals the inverse Fourier transform of its power spectral density:

```
ACF(τ) = IFFT( |FFT(x)|² )
```

The signal is zero-padded to 2n samples before the FFT to prevent circular aliasing that would otherwise cause the tail of the correlation to wrap around and corrupt the result.

**Primary reference:** Wiener, N. (1930). Generalized harmonic analysis. *Acta Mathematica*, 55, 117–258.
https://doi.org/10.1007/BF02546511

**Accessible explanation:** NumPy FFT documentation — https://numpy.org/doc/stable/reference/routines.fft.html

---

### Parabolic interpolation of the ACF peak

**Used for:** Refining the detected period to sub-sample precision, improving frequency accuracy beyond the discrete sample grid.

The discrete ACF peak is the sample closest to the true peak, but the true maximum lies somewhere between samples. Fitting a parabola through the three samples surrounding the peak (α, β, γ) and solving for its vertex gives a fractional lag adjustment:

```
adjustment = 0.5 * (α - γ) / (α - 2β + γ)
```

This typically reduces frequency error from ~2 cents to ~0.5 cents without any additional computation.

**Primary reference:** Smith, J.O. (2011). *Spectral Audio Signal Processing*. W3K Publishing.
Chapter: "Quadratic Interpolation of Spectral Peaks".
https://ccrma.stanford.edu/~jos/sasp/Quadratic_Interpolation_Spectral_Peaks.html

---

## Note identification (`theory.py`)

### MIDI note number formula

**Used for:** Converting a detected frequency in Hz to the nearest named musical note (e.g., G3, D4).

The MIDI standard assigns integer note numbers to each semitone, with A4 = 440 Hz = note 69. In equal temperament, frequency doubles every octave (12 semitones), so the mapping from frequency to MIDI note is:

```
midi = 12 * log2(f / 440) + 69
```

Rounding to the nearest integer gives the closest note. The note name comes from `midi % 12` (position within the octave) and the octave from `midi // 12 - 1`.

**Primary reference:** MIDI Tuning Standard, MIDI Manufacturers Association (MMA).
https://midi.org/midi-tuning-standard

**Accessible explanation:** https://en.wikipedia.org/wiki/MIDI_tuning_standard

---

### Cents deviation

**Used for:** Measuring how sharp or flat a detected pitch is relative to the nearest equal-tempered note, displayed on the tuner meter.

A cent is 1/100 of a semitone. Because frequency ratios are logarithmic, the cent deviation from an ideal frequency f_ideal is:

```
cents = 1200 * log2(f / f_ideal)
```

The result ranges from −50 to +50 cents before the pitch would round to the adjacent note. Positive = sharp, negative = flat.

**Primary reference:** Ellis, A.J. (1885). Appendix XX to Helmholtz, H. *On the Sensations of Tone*. Dover reprint 1954. (Original definition of the cent as a unit.)

**Accessible explanation:** https://en.wikipedia.org/wiki/Cent_(music)

---

## Fretboard note mapping (`fretboard.py`)

**Used for:** Displaying note locations in Open G and Double C, including the short fifth string.

Each fret raises a pitch by one equal-tempered semitone. For the four long strings, the sounding MIDI pitch is the open-string MIDI pitch plus the physical fret number. The short fifth string begins at *physical fret 5*, where its open pitch is G4; positions 0–4 are absent and fret 6 raises it to G#4. Pitch names are obtained using MIDI pitch modulo 12.

**Primary reference:** Earl Scruggs, *Earl Scruggs and the 5-String Banjo*, revised edition (2005), banjo tuning and fifth-string setup.

**Accessible explanation:** https://en.wikipedia.org/wiki/Five-string_banjo

### Chord tone highlighting

**Used for:** Coloring every major or minor triad tone on the fretboard.

Major triads use pitch-class offsets 0, 4 and 7 semitones above their root; minor triads use 0, 3 and 7. Octaves do not change chord membership. This marks *potential tones*, not complete fingerable chord grips, which will require separate fingering constraints.

**Primary reference:** Kostka, Payne & Almén, *Tonal Harmony*, 8th edition, chapters on triads.

**Accessible explanation:** https://en.wikipedia.org/wiki/Triad_(music)
