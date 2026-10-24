# Architecture: Gleam + Rust

This is the intended replacement for the original Python prototype. The existing
Python tuner remains on `main` temporarily for reference; new features should not
extend it. The Python-only fretboard PR was closed.

## Ownership

| Layer | Language | Responsibility |
| --- | --- | --- |
| Application domain | Gleam | Tuning selection, fretboard positions, scale/chord selection, navigation and immutable application state |
| Audio engine | Rust | Microphone capture, buffering, DSP, pitch detection, confidence estimation |
| Boundary | Versioned messages | Rust emits discrete pitch observations; Gleam responds to events, never raw sample buffers |
| Presentation | To be selected | Rendering follows Gleam state; do not embed theory rules into the view |

Gleam compiles to Erlang or JavaScript rather than Rust. A separate Rust process
with line-delimited JSON messages is the initial recommended integration:
it keeps crashing or blocking audio code away from the UI runtime and allows
replaying recorded pitch events during testing. A Rust NIF or native bridge can
be reconsidered after measuring real latency; neither is necessary for the
first iteration.

### Example message

Rust -> Gleam:

```json
{"version":1,"type":"pitch","frequency_hz":392.0,"confidence":0.98}
```

The event rate should be throttled for presentation; it is not the audio
sampling rate. Invalid, silent or low-confidence frames should have an
explicit no-pitch event instead of retaining the last detected note forever.

## Migration slices

1. Implement a pure Gleam model for tunings, fret positions and chord tones,
   with tests independent of any UI or microphone.
2. Port pitch estimation into an isolated Rust library, with deterministic
   signal tests; add audio device capture only around that library.
3. Define and test the line-delimited message protocol and supervise the
   native process at the application's boundary.
4. Choose the presentation runtime (terminal versus browser/desktop) and
   connect it to the Gleam state.
5. Remove the Python entry point, dependency and lock files once both
   tunings and microphone detection work end to end.

## Non-goals

- No Python-to-Gleam bindings.
- No Rust ownership of user-facing chord, scale or navigation state.
- No premature Rust NIF dependency.
- No assumptions that highlighting chord tones automatically finds
  playable multi-string chord shapes.

## References

- Gleam compilation targets: https://gleam.run/documentation/command-line-reference/
- Gleam externals and interoperability: https://gleam.run/documentation/externals/
- Gleam OTP actors: https://github.com/gleam-lang/otp
