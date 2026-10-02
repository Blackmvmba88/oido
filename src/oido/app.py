from __future__ import annotations

import argparse
import sys
from .context import classify
from .models import Segment
from .storage import Store
from .notebook import render

def ingest_text(text: str, store: Store) -> Segment:
    seg = Segment(
        start_ms=0,
        end_ms=0,
        audio_path="",
        raw_text=text,
        clean_text=text.strip(),
        mode="unknown",
        confidence=1.0,
        stt_engine="manual",
        annotations=classify(text),
    )
    store.append(seg)
    return seg

def main() -> None:
    parser = argparse.ArgumentParser(prog="oido")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_note = sub.add_parser("note", help="Inject text into the intelligent notebook")
    p_note.add_argument("text", nargs="+")

    p_render = sub.add_parser("render", help="Render notebook HTML")
    p_render.add_argument("--output", default="data/notebook.html")

    args = parser.parse_args()
    store = Store()

    if args.cmd == "note":
        text = " ".join(args.text)
        seg = ingest_text(text, store)
        print(seg.to_json())
        render(store.all())
    elif args.cmd == "render":
        print(render(store.all(), args.output))
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
