from __future__ import annotations

from html import escape
from pathlib import Path

CSS = """
body{font-family:ui-rounded,system-ui,sans-serif;background:#fffdf7;color:#26231f;max-width:980px;margin:40px auto;padding:0 20px}
h1{font-size:38px}.card{background:#fff;border:1px solid #e8e0d3;border-radius:18px;padding:18px 20px;margin:16px 0;box-shadow:0 8px 24px #0000000d}
.time{font:12px ui-monospace,monospace;color:#7c7267}.raw{font-size:21px;line-height:1.55;margin:10px 0;border-bottom:3px double #d4c3a3;padding-bottom:10px}
.tags{display:flex;gap:8px;flex-wrap:wrap}.tag{background:#f4efe4;border-radius:999px;padding:5px 10px;font-size:13px}.detail{margin-top:8px;color:#665c50;font-size:13px}
.speech{border-left:6px solid #8a7}.singing{border-left:6px solid #a78}.unknown{border-left:6px solid #aa9}
"""

def render(rows: list[dict], output: str = "data/notebook.html") -> str:
    cards = []
    for row in rows:
        anns = row.get("annotations", [])
        tags = "".join(f'<span class="tag">{escape(a["label"])}</span>' for a in anns)
        details = "".join(
            f'<div class="detail">↳ {escape(a.get("detail",""))} · {a.get("confidence",0):.0%}</div>'
            for a in anns if a.get("detail")
        )
        mode = row.get("mode", "unknown")
        cards.append(f"""
        <article class="card {escape(mode)}">
          <div class="time">{row.get("start_ms",0)}–{row.get("end_ms",0)} ms · {escape(mode)}</div>
          <div class="raw">{escape(row.get("raw_text") or row.get("clean_text") or "…")}</div>
          <div class="tags">{tags}</div>{details}
          <div class="detail">🎧 {escape(row.get("audio_path",""))}</div>
        </article>""")
    html = f"""<!doctype html><meta charset="utf-8"><title>Oído — Cuaderno</title>
    <style>{CSS}</style><body><h1>📓 Oído</h1><p>Cuaderno inteligente de voz, canto e ideas.</p>{''.join(cards)}</body>"""
    p = Path(output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    return str(p)
