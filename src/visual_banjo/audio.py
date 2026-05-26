import queue
import numpy as np
import sounddevice as sd

SAMPLE_RATE = 44100
BLOCK_SIZE = 4096  # ~93ms window — long enough for low banjo frequencies (~80 Hz)
CONFIDENCE_THRESHOLD = 0.8
FREQ_MIN = 60.0   # below banjo range, catches errant noise
FREQ_MAX = 2100.0


def _detect_pitch(samples: np.ndarray) -> tuple[float, float]:
    """Return (frequency_hz, confidence) from a mono audio block.

    Algorithm: normalized autocorrelation with FFT acceleration and parabolic
    interpolation for sub-sample peak refinement.

    Autocorrelation pitch detection
    --------------------------------
    The autocorrelation function (ACF) of a periodic signal peaks at lags that
    are integer multiples of the fundamental period T0. The first peak above
    lag 0 corresponds to T0, so f0 = sample_rate / T0.

    Reference: Rabiner, L.R. (1977). On the use of autocorrelation analysis
    for pitch detection. IEEE Transactions on Acoustics, Speech, and Signal
    Processing, 25(1), 24–33.
    https://doi.org/10.1109/TASSP.1977.1162905

    FFT acceleration (Wiener–Khinchin theorem)
    -------------------------------------------
    The ACF can be computed as the inverse FFT of the power spectral density:
        ACF(τ) = IFFT(|FFT(x)|²)
    Zero-padding to 2n before the FFT prevents circular wrap-around aliasing.
    This reduces complexity from O(n²) to O(n log n).

    Reference: Wiener, N. (1930). Generalized harmonic analysis. Acta
    Mathematica, 55, 117–258. https://doi.org/10.1007/BF02546511
    Practical explanation: https://numpy.org/doc/stable/reference/routines.fft.html

    Parabolic interpolation
    -----------------------
    Fitting a parabola through the three samples around the ACF peak gives a
    sub-sample estimate of the true peak location, improving frequency accuracy
    beyond what the discrete sample grid alone allows.

    Reference: Smith, J.O. (2011). Spectral Audio Signal Processing.
    W3K Publishing. Chapter on "Quadratic Interpolation of Spectral Peaks".
    https://ccrma.stanford.edu/~jos/sasp/Quadratic_Interpolation_Spectral_Peaks.html

    Confidence metric
    -----------------
    The normalized ACF value at the detected peak (relative to lag 0) indicates
    how periodic the signal is. A purely periodic signal scores 1.0; noise
    scores near 0. Threshold of 0.8 is empirically good for clean instrument
    recordings and rejects most ambient noise.
    """
    samples = samples - samples.mean()
    amplitude = np.sqrt(np.mean(samples ** 2))
    if amplitude < 1e-4:
        return 0.0, 0.0

    # Autocorrelation via FFT (Wiener–Khinchin theorem)
    n = len(samples)
    fft = np.fft.rfft(samples, n=2 * n)
    acf = np.fft.irfft(fft * np.conj(fft))[:n]
    acf = acf / (acf[0] + 1e-10)  # normalise so acf[0] == 1

    # Search only within the period range that matches FREQ_MIN..FREQ_MAX
    lag_min = int(SAMPLE_RATE / FREQ_MAX)
    lag_max = int(SAMPLE_RATE / FREQ_MIN)
    lag_max = min(lag_max, n - 1)

    search = acf[lag_min:lag_max]
    if len(search) == 0:
        return 0.0, 0.0

    peak_idx = int(np.argmax(search))
    peak_val = search[peak_idx]

    # Confidence: strength of ACF peak relative to zero-lag (see docstring)
    confidence = float(peak_val)
    if confidence < CONFIDENCE_THRESHOLD:
        return 0.0, confidence

    # Parabolic interpolation for sub-sample accuracy (see docstring)
    lag = peak_idx + lag_min
    if 0 < lag < n - 1:
        alpha, beta, gamma = acf[lag - 1], acf[lag], acf[lag + 1]
        adjustment = 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma + 1e-10)
        lag = lag + adjustment

    freq = SAMPLE_RATE / lag
    return float(freq), confidence


def start_audio_stream(result_queue: queue.Queue, device=None) -> sd.InputStream:
    """Open a sounddevice input stream and push (freq, confidence) into result_queue."""

    def callback(indata, frames, time, status):
        mono = indata[:, 0] if indata.ndim > 1 else indata.flatten()
        freq, conf = _detect_pitch(mono.astype(np.float64))
        if not result_queue.full():
            result_queue.put_nowait((freq, conf))

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        channels=1,
        dtype="float32",
        device=device,
        callback=callback,
    )
    return stream
