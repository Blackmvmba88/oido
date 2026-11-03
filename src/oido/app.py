from __future__ import annotations

import argparse
import sys

from .capture import CaptureConfig, MicrophoneCapture
from .context import classify
from .mode import detect_mode
from .models import Segment
from .notebook import render
from .storage import Store
from .transcribe import NullTranscriber, WhisperTranscriber


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


def listen_forever(
    store: Store,
    chunk_seconds: float,
    sample_rate: int,
    whisper_model: str | None,
) -> None:
    capture = MicrophoneCapture(
        CaptureConfig(sample_rate=sample_rate, chunk_seconds=chunk_seconds)
    )
    transcriber = WhisperTranscriber(whisper_model) if whisper_model else NullTranscriber()

    print("🎙️ Oído escuchando. Ctrl+C detiene la sesión.")
    try:
        while True:
            audio_path = store.audio_path(".wav")
            start_ms, end_ms = capture.record_chunk(audio_path)
            transcript = transcriber.transcribe(audio_path)
            mode, mode_conf = detect_mode(audio_path)

            text = transcript.text.strip()
            seg = Segment(
                start_ms=start_ms,
                end_ms=end_ms,
                audio_path=str(audio_path),
                raw_text=text,
                clean_text=text,
                mode=mode,
                confidence=max(transcript.confidence, mode_conf),
                stt_engine=transcript.engine,
                annotations=classify(text) if text else [],
            )
            store.append(seg)
            render(store.all())

            label = "🎤" if mode == "singing" else "🗣️" if mode == "speech" else "◌"
            print(f"{label} {text or '[audio guardado, sin texto]'}")
            if transcript.error:
                print(f"   ⚠️ STT falló, WAV preservado: {transcript.error}")
            for ann in seg.annotations:
                print(f"   {ann.label} {ann.detail}")
    except KeyboardInterrupt:
        render(store.all())
        print("\n📓 Sesión cerrada. Cuaderno: data/notebook.html")


def main() -> None:
    parser = argparse.ArgumentParser(prog="oido")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_note = sub.add_parser("note", help="Inyecta texto al cuaderno inteligente")
    p_note.add_argument("text", nargs="+")

    p_render = sub.add_parser("render", help="Genera el cuaderno HTML")
    p_render.add_argument("--output", default="data/notebook.html")

    p_listen = sub.add_parser("listen", help="Escucha continuamente y conserva el audio")
    p_listen.add_argument("--chunk-seconds", type=float, default=8.0)
    p_listen.add_argument("--sample-rate", type=int, default=16000)
    p_listen.add_argument(
        "--whisper-model",
        default=None,
        help="Ej. tiny, base, small. Requiere instalar el extra stt.",
    )

    args = parser.parse_args()
    store = Store()

    if args.cmd == "note":
        text = " ".join(args.text)
        seg = ingest_text(text, store)
        print(seg.to_json())
        render(store.all())
    elif args.cmd == "render":
        print(render(store.all(), args.output))
    elif args.cmd == "listen":
        listen_forever(store, args.chunk_seconds, args.sample_rate, args.whisper_model)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
