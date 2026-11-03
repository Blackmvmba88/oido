from __future__ import annotations

import re
from .models import Annotation

RULES: list[tuple[str, str, tuple[str, ...]]] = [
    ("idea", "💡 IDEA", ("estaría bueno", "se me ocurre", "podríamos", "idea", "imagina")),
    ("roadmap", "🧭 ROADMAP", ("primero", "después", "luego", "fase", "roadmap")),
    ("readme", "📘 README", ("readme", "documentación", "arquitectura", "funciona así")),
    ("task", "✅ TAREA", ("hay que", "falta", "pendiente", "tenemos que")),
    ("bug", "🐛 BUG", ("falla", "error", "se traba", "no funciona", "bug")),
    ("decision", "🔒 DECISIÓN", ("decidí", "queda así", "vamos a usar", "definitivamente")),
    ("question", "❓ PREGUNTA", ("?", "por qué", "cómo hacemos", "qué pasa")),
]

def _words(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúüñ0-9]+", text.lower())

def detect_rhyme(text: str) -> list[Annotation]:
    lines = [x.strip() for x in re.split(r"[\n.!?]+", text) if x.strip()]
    endings: dict[str, list[str]] = {}
    for line in lines:
        ws = _words(line)
        if not ws:
            continue
        tail = ws[-1][-3:] if len(ws[-1]) >= 3 else ws[-1]
        endings.setdefault(tail, []).append(ws[-1])
    out: list[Annotation] = []
    for tail, words in endings.items():
        if len(words) >= 2:
            out.append(Annotation("rhyme", "🔁 RIMA", 0.72, f"terminaciones cercanas: {', '.join(words)}"))
    return out

def classify(text: str) -> list[Annotation]:
    low = text.lower()
    out: list[Annotation] = []
    for kind, label, needles in RULES:
        hits = [n for n in needles if n in low]
        if hits:
            conf = min(0.95, 0.58 + 0.09 * len(hits))
            out.append(Annotation(kind, label, conf, " / ".join(hits)))

    poetic = len(_words(text)) >= 6 and any(
        x in low for x in ("noche", "voz", "silencio", "nombre", "piel", "calle", "luna", "ritmo")
    )
    if poetic:
        out.append(Annotation("lyric", "🎵 POSIBLE LETRA", 0.62, "lenguaje con carga poética"))

    repeated = re.findall(r"\b([\wáéíóúüñ]+)\b(?:\s+\1\b)+", low)
    if repeated:
        out.append(Annotation("hook", "🎯 HOOK POTENCIAL", 0.70, f"repetición: {', '.join(set(repeated))}"))

    out.extend(detect_rhyme(text))
    if not out:
        out.append(Annotation("note", "📝 NOTA", 0.50, "sin intención dominante"))
    return out
