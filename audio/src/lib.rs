//! Pure pitch estimation core. Device capture and the Gleam transport live
//! outside this module so tests can supply deterministic sample buffers.

/// Estimate a monophonic fundamental using normalized time-domain
/// autocorrelation over a bounded frequency range.
///
/// Removes the sample mean, searches candidate periods, and reports the
/// strongest lag with a normalized correlation score. This is a baseline
/// estimator: instrument-specific octave errors will need testing.
///
/// Reference: Rabiner (1977), "On the use of autocorrelation analysis for
/// pitch detection", IEEE TASSP 25(1), DOI 10.1109/TASSP.1977.1162905.
/// Accessible: https://en.wikipedia.org/wiki/Autocorrelation
pub fn estimate_pitch(
    samples: &[f32],
    sample_rate: f32,
    min_hz: f32,
    max_hz: f32,
) -> Option<(f32, f32)> {
    if samples.len() < 4
        || !sample_rate.is_finite() || sample_rate <= 0.0
        || !min_hz.is_finite() || !max_hz.is_finite()
        || min_hz <= 0.0 || max_hz <= min_hz
        || samples.iter().any(|sample| !sample.is_finite())
    {
        return None;
    }
    let mean = samples.iter().copied().sum::<f32>() / samples.len() as f32;
    let centered: Vec<f32> = samples.iter().map(|s| s - mean).collect();
    let energy = centered.iter().map(|s| s * s).sum::<f32>();
    if energy < 1.0e-8 { return None; }

    let first = (sample_rate / max_hz).ceil().max(2.0) as usize;
    let last = (sample_rate / min_hz).floor() as usize;
    if first > last || last >= centered.len() / 2 { return None; }

    let mut best = (0usize, 0.0f32);
    for lag in first..=last {
        let left = &centered[..centered.len() - lag];
        let right = &centered[lag..];
        let numerator: f32 = left.iter().zip(right).map(|(a, b)| a * b).sum();
        let energy_left: f32 = left.iter().map(|v| v * v).sum();
        let energy_right: f32 = right.iter().map(|v| v * v).sum();
        let denominator = (energy_left * energy_right).sqrt();
        if denominator <= 1.0e-8 { continue; }
        let score = numerator / denominator;
        if score > best.1 { best = (lag, score); }
    }

    if best.0 == 0 || best.1 < 0.6 { return None; }
    Some((sample_rate / best.0 as f32, best.1.clamp(0.0, 1.0)))
}

#[cfg(test)]
mod tests {
    use super::estimate_pitch;
    use std::f32::consts::TAU;

    #[test]
    fn detects_a440() {
        let rate = 44_100.0;
        let samples: Vec<f32> = (0..8192)
            .map(|i| (TAU * 440.0 * i as f32 / rate).sin())
            .collect();
        let (hz, confidence) = estimate_pitch(&samples, rate, 200.0, 500.0).unwrap();
        assert!((hz - 440.0).abs() < 6.0, "{hz}");
        assert!(confidence > 0.9);
    }

    #[test]
    fn silence_yields_none() {
        assert_eq!(estimate_pitch(&[0.0; 2048], 44_100.0, 80.0, 1000.0), None);
    }

    #[test]
    fn rejects_invalid_input() {
        assert_eq!(estimate_pitch(&[f32::NAN; 2048], 44_100.0, 80.0, 1000.0), None);
    }
}
