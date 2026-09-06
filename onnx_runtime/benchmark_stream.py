from __future__ import annotations

import argparse
import base64
import json
import time
import urllib.request
import wave
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Nori TTS streaming latency")
    parser.add_argument("--url", default="http://127.0.0.1:8024/api/tts/stream")
    parser.add_argument("--text", default="早上好，今天也要一起努力哦。")
    parser.add_argument("--voice", default="nori")
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = json.dumps(
        {
            "text": args.text,
            "voice_name": args.voice,
            "temperature": args.temperature,
            "top_p": args.top_p,
            "top_k": args.top_k,
            "seed": args.seed,
            "max_new_tokens": args.max_new_tokens,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        args.url,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    started = time.perf_counter()
    first_audio_at: float | None = None
    sample_rate = 44100
    pcm_parts: list[bytes] = []
    frame_count = 0

    with urllib.request.urlopen(request) as response:
        for raw_line in response:
            if not raw_line.strip():
                continue
            event = json.loads(raw_line)
            event_type = event.get("event")
            if event_type == "start":
                sample_rate = int(event.get("sample_rate", sample_rate))
            elif event_type == "audio_chunk":
                if first_audio_at is None:
                    first_audio_at = time.perf_counter()
                pcm_parts.append(base64.b64decode(event["pcm_b64"]))
                frame_count = int(event.get("frame_count", frame_count))
            elif event_type == "complete":
                frame_count = int(event.get("frame_count", frame_count))
            elif event_type == "cancelled":
                raise RuntimeError("stream was cancelled")

    finished = time.perf_counter()
    total_seconds = finished - started
    ttfa_seconds = None if first_audio_at is None else first_audio_at - started
    pcm = b"".join(pcm_parts)
    audio_seconds = len(pcm) / 2 / sample_rate if sample_rate and pcm else 0.0
    rtf = total_seconds / audio_seconds if audio_seconds > 0 else None

    print(f"TTFA: {ttfa_seconds:.3f} s" if ttfa_seconds is not None else "TTFA: unavailable")
    print(f"Total: {total_seconds:.3f} s")
    print(f"Audio: {audio_seconds:.3f} s")
    print(f"RTF: {rtf:.3f}" if rtf is not None else "RTF: unavailable")
    print(f"Codec frames: {frame_count}")

    if args.output and pcm:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(args.output), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(pcm)
        print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
