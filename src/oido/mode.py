from __future__ import annotations

from pathlib import Path
import numpy as np
import soundfile as sf

def detect_mode(audio_path: str | Path) -> tuple[str, float]:
    """Conservative acoustic hint; unknown wins unless evidence is useful.

    This is intentionally replaceable by a trained speech-vs-singing model later.
    """
    data, sr = sf.read(str(audio_path), always_2d=False)
    x = np.asarray(data, dtype=np.float32)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if x.size < sr // 2:
        return "unknown", 0.2

    rms = float(np.sqrt(np.mean(x * x) + 1e-12))
    if rms < 0.003:
        return "unknown", 0.35

    frame = max(256, int(sr * 0.04))
    hop = frame // 2
    peaks = []
    window = np.hanning(frame)
    for i in range(0, max(1, len(x) - frame), hop):
        y = x[i:i+frame]
        if len(y) != frame:
            break
        spec = np.abs(np.fft.rfft(y * window))
        freqs = np.fft.rfftfreq(frame, 1 / sr)
        mask = (freqs >= 80) & (freqs <= 1000)
        if np.any(mask):
            idx = np.argmax(spec[mask])
            peaks.append(float(freqs[mask][idx]))

    if len(peaks) < 5:
        return "speech", 0.52

    p = np.asarray(peaks)
    stability = float(np.std(p) / (np.mean(p) + 1e-9))
    if stability < 0.12:
        return "singing", 0.62
    return "speech", 0.58
