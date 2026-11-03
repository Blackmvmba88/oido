from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time

import numpy as np
import sounddevice as sd
import soundfile as sf

@dataclass
class CaptureConfig:
    sample_rate: int = 16000
    channels: int = 1
    chunk_seconds: float = 8.0
    device: int | str | None = None

class MicrophoneCapture:
    """Record independent WAV chunks so capture survives downstream failures."""

    def __init__(self, config: CaptureConfig | None = None) -> None:
        self.config = config or CaptureConfig()

    def record_chunk(self, path: str | Path) -> tuple[int, int]:
        cfg = self.config
        frames = int(cfg.sample_rate * cfg.chunk_seconds)
        start = time.time_ns() // 1_000_000
        audio = sd.rec(
            frames,
            samplerate=cfg.sample_rate,
            channels=cfg.channels,
            dtype="float32",
            device=cfg.device,
        )
        sd.wait()
        end = time.time_ns() // 1_000_000
        sf.write(str(path), np.asarray(audio), cfg.sample_rate, subtype="PCM_16")
        return start, end
