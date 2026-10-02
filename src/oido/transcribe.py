from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf


@dataclass
class Transcript:
    text: str
    confidence: float
    engine: str
    error: str = ""


class NullTranscriber:
    def transcribe(self, audio_path: str | Path) -> Transcript:
        return Transcript("", 0.0, "none")


class WhisperTranscriber:
    """Whisper adapter that bypasses faster-whisper's PyAV decoder.

    Oído records WAV itself, so decoding through PyAV is unnecessary. Reading with
    soundfile also isolates us from PyAV API changes (notably PyAV 19).
    """

    def __init__(
        self,
        model: str = "small",
        device: str = "auto",
        compute_type: str = "int8",
    ) -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper no está instalado. Usa: pip install -e '.[stt]'"
            ) from exc

        self.model = WhisperModel(model, device=device, compute_type=compute_type)
        self.name = f"faster-whisper:{model}"
        self.target_sr = int(self.model.feature_extractor.sampling_rate)

    @staticmethod
    def _mono_float32(audio: np.ndarray) -> np.ndarray:
        x = np.asarray(audio, dtype=np.float32)
        if x.ndim > 1:
            x = x.mean(axis=1)
        return np.ascontiguousarray(x, dtype=np.float32)

    @staticmethod
    def _resample_linear(audio: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
        if src_sr == dst_sr or audio.size == 0:
            return audio
        duration = audio.size / float(src_sr)
        dst_n = max(1, int(round(duration * dst_sr)))
        old_x = np.linspace(0.0, duration, num=audio.size, endpoint=False)
        new_x = np.linspace(0.0, duration, num=dst_n, endpoint=False)
        return np.interp(new_x, old_x, audio).astype(np.float32)

    def _load_audio(self, audio_path: str | Path) -> np.ndarray:
        audio, sr = sf.read(str(audio_path), always_2d=False, dtype="float32")
        x = self._mono_float32(audio)
        return self._resample_linear(x, int(sr), self.target_sr)

    def transcribe(self, audio_path: str | Path) -> Transcript:
        try:
            audio = self._load_audio(audio_path)
            if audio.size == 0:
                return Transcript("", 0.0, self.name)

            segments, info = self.model.transcribe(
                audio,
                vad_filter=True,
                beam_size=5,
                word_timestamps=True,
            )
            parts = [seg.text.strip() for seg in segments if seg.text.strip()]
            text = " ".join(parts).strip()
            confidence = float(getattr(info, "language_probability", 0.0) or 0.0)
            return Transcript(text, confidence, self.name)
        except Exception as exc:
            # Critical redundancy rule: transcription failure must never destroy
            # the audio capture loop or the original WAV.
            return Transcript("", 0.0, self.name, f"{type(exc).__name__}: {exc}")
