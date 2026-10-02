from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Literal
import json
import uuid

Mode = Literal["speech", "singing", "unknown"]
Kind = Literal[
    "idea", "readme", "roadmap", "task", "bug", "feature", "question",
    "decision", "lyric", "rhyme", "hook", "note"
]

@dataclass
class Annotation:
    kind: Kind
    label: str
    confidence: float = 0.5
    detail: str = ""

@dataclass
class Segment:
    start_ms: int
    end_ms: int
    audio_path: str
    raw_text: str = ""
    clean_text: str = ""
    mode: Mode = "unknown"
    confidence: float = 0.0
    stt_engine: str = "none"
    annotations: list[Annotation] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)
