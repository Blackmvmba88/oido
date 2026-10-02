from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

@dataclass
class Transcript:
    text: str
    confidence: float
    engine: str

class NullTranscriber:
    def transcribe(self, audio_path: str | Path) -> Transcript:
        return Transcript("", 0.0, "none")

class WhisperTranscriber:
    def __init__(self, model: str = "small", device: str = "auto", compute_type: str = "int8") -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper no está instalado. Usa: pip install -e '.[stt]'"
            ) from exc
        self.model = WhisperModel(model, device=device, compute_type=compute_type)
        self.name = f"faster-whisper:{model}"

    def transcribe(self, audio_path: str | Path) -> Transcript:
        segments, info = self.model.transcribe(
            str(audio_path),
            vad_filter=True,
            beam_size=5,
            word_timestamps=True,
        )
        parts = [seg.text.strip() for seg in segments if seg.text.strip()]
        text = " ".join(parts).strip()
        # faster-whisper exposes language probability, not a universal utterance confidence.
        confidence = float(getattr(info, "language_probability", 0.0) or 0.0)
        return Transcript(text, confidence, self.name)
