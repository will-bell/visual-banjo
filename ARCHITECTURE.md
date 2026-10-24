# Architecture: graphical Visual Banjo (Gleam + Rust)

Visual Banjo is an **interactive graphical music-theory explorer**. The terminal
tuner was an early practical prototype, not the intended application interface.
Do not extend the Python UI: the Python files on `main` remain only as a
reference while features are migrated.

## Initial target: browser application

| Layer | Technology | Responsibility |
| --- | --- | --- |
| UI and state | Gleam (JavaScript target) | Model/update loop, tuning/chord/scale choices, interactions, visualization state |
| Fretboard rendering | SVG in the browser | Interactive strings, frets, note locations, chord tones, later playable shapes |
| Audio input | Browser Web Audio APIs | Microphone permissions, device input, buffering, sending audio frames for analysis |
| Pitch estimation | Rust compiled to WebAssembly | DSP and note-frequency/confidence estimation, without UI or music-theory state |
| Bridge | Typed Gleam events + narrow JS externals | Translate browser microphone/pitch events into application messages |

The browser handles audio capture, while Rust owns the signal-processing
algorithm. Rust/WASM does **not** directly own the microphone: Web Audio
provides it. A small JavaScript interop adapter will be necessary for Web
Audio and for invoking the WASM module. Mic access is optional: the explorer
must work without microphone permission. The application should work on
localhost and over HTTPS, where browser microphone permissions are supported.

Start with SVG and semantic UI controls rather than introducing a large
JavaScript frontend framework. Keep note mapping, chord-tone rules, and
application state in pure Gleam functions so they are testable separately from
DOM and Web Audio integrations.

### Conceptual state flow

```
User input (tuning, chord, note selection)
    -> Gleam Msg
    -> Gleam update(Model, Msg)
    -> SVG fretboard redraw

Browser microphone (with user permission)
    -> Web Audio frames
    -> Rust/WASM pitch estimator
    -> PitchObserved(frequency, confidence) / PitchLost
    -> Gleam update(Model, Msg)
    -> highlight sounding note positions
```

Audio work should not block the UI thread. A production integration should
use an AudioWorklet for capture and an appropriate worker/processing boundary
for DSP, then measure latency and CPU usage. Avoid shipping an implementation
that performs expensive DSP synchronously during rendering.

## Initial exploration experience

- Show the entire five-string fretboard with the short fifth string beginning
  at physical fret 5; support Open G and Double C tunings.
- Highlight all locations of a chosen note or chord's pitch classes, with a
  distinct root marker and optional note-name labels.
- Make fret positions selectable, with a small inspector showing string,
  fret, sounding note and interval relative to the selected chord.
- Keep chord-tone locations separate from *playable chord shapes*, which
  require explicit fingering/fret-span constraints.
- Make the microphone tuner a later mode or overlay rather than the top-level
  application architecture.

## Migration increments

1. **Interactive fretboard, no microphone:** Gleam model/update, browser SVG
   view, tuning and chord selection, automated tests for note mapping.
2. **Music-theory exploration:** note/interval inspection, major/minor chords,
   then shape search with practical fingering constraints.
3. **Rust audio core:** deterministic sine/noise tests and stable DSP API,
   building for WebAssembly; avoid tying the DSP crate to an audio device.
4. **Browser microphone integration:** secure-context permission flow,
   worklet/worker audio pipeline, pitch/silence event bridge to Gleam.
5. **Tuner overlay and live fretboard feedback:** calibration, confidence
   filtering and latency testing.
6. Remove Python files, dependencies and terminal entry point after the new
   graphical application provides replacement functionality.

## Future research: Faust-generated Rust DSP

Investigate [Faust](https://github.com/grame-cncm/faust), a functional DSP
language, and the [Faust Rust compiler project](https://github.com/grame-cncm/faust-rs)
as a possible way to express reusable audio-processing components and generate
Rust for the WebAssembly audio engine. This is a **research direction, not a
committed dependency or a replacement for the existing Rust estimator**.

Questions for a small proof of concept:

- Which parts of the pipeline (high-pass filters, noise shaping, harmonic
  analysis, reference-tone generation) are clearer in Faust than handwritten
  Rust?
- How complete and stable is the Faust-to-Rust compiler, and does the generated
  output build cleanly for the `wasm32` target?
- How does compiled Faust compare against direct Rust for latency, binary
  size, memory allocation and correctness on recorded banjo samples?
- Can generated DSP modules remain independent of browser microphone APIs and
  pass deterministic audio fixtures through Rust tests?
- Would Faust's direct WebAssembly backend be a more practical fallback while
  Rust code generation matures?

Keep microphone capture in the browser's Web Audio layer and keep application
state and music theory in Gleam. Do not introduce Faust into the build until a
measured prototype justifies its complexity.

## Portability

A desktop wrapper may be considered later if offline installation or native
audio access is valuable. It should use the same graphical frontend and
domain state, not a separate terminal-centered application. Do not build a
native-process JSON protocol until a concrete desktop requirement calls for it.

## Non-goals

- No Python dependencies in newly implemented features.
- No Rust ownership of UI state or chord, scale and navigation rules.
- No assumption that all highlighted chord tones form playable grips.
- No microphone requirement merely to explore notes and harmony.

## References

- Gleam JavaScript target and externals: https://gleam.run/documentation/
- Web Audio API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- AudioWorklet: https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet
- Rust and WebAssembly: https://rustwasm.github.io/docs/book/
