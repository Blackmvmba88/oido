from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
from .models import Segment

class Store:
    def __init__(self, root: str = "data") -> None:
        self.root = Path(root)
        self.audio = self.root / "audio"
        self.events = self.root / "segments.jsonl"
        self.audio.mkdir(parents=True, exist_ok=True)
        self.events.parent.mkdir(parents=True, exist_ok=True)

    def audio_path(self, suffix: str = ".wav") -> Path:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        return self.audio / f"{stamp}{suffix}"

    def append(self, segment: Segment) -> None:
        with self.events.open("a", encoding="utf-8") as f:
            f.write(segment.to_json() + "\n")

    def all(self) -> list[dict]:
        if not self.events.exists():
            return []
        rows = []
        for line in self.events.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows
