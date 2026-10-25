#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Groq Whisper Word-Level & Segment-Level Transcription Script
For `suno-battle-mv-architect` skill.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: `requests` library is required. Install via `pip install requests`.", file=sys.stderr)
    sys.exit(1)


class RateLimitError(Exception):
    """Raised when Groq API returns HTTP 429."""
    pass


def load_groq_api_key() -> str:
    env_key = os.environ.get("GROQ_API_KEY", "").strip()
    if env_key:
        return env_key
    key_file = Path.home() / ".groq_api_key"
    if key_file.exists():
        return key_file.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        "Groq API key not found. Please set GROQ_API_KEY environment variable or save it in ~/.groq_api_key."
    )


def compress_audio_for_groq(input_audio: str, temp_mp3: str) -> None:
    cmd = [
        "ffmpeg", "-y",
        "-i", input_audio,
        "-ac", "1",
        "-ar", "16000",
        "-b:a", "48k",
        temp_mp3
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def transcribe_with_groq(audio_path: str, prompt: str, language: str = "zh") -> dict:
    api_key = load_groq_api_key()
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_mp3 = os.path.join(tmpdir, "compressed_16k.mp3")
        compress_audio_for_groq(audio_path, temp_mp3)

        max_retries = 3
        delay = 2.0
        for attempt in range(1, max_retries + 1):
            with open(temp_mp3, "rb") as f:
                files = {"file": ("audio.mp3", f, "audio/mpeg")}
                data = [
                    ("model", "whisper-large-v3-turbo"),
                    ("language", language),
                    ("response_format", "verbose_json"),
                    ("timestamp_granularities[]", "word"),
                    ("timestamp_granularities[]", "segment"),
                    ("prompt", prompt),
                ]
                resp = requests.post(url, headers=headers, files=files, data=data, timeout=180)

            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                if attempt == max_retries:
                    raise RateLimitError(f"Rate limit exceeded (HTTP 429) at {url}: {resp.text}")
                print(f"[Groq Whisper] HTTP 429 rate limit hit, retrying in {delay:.1f}s (attempt {attempt}/{max_retries})...", file=sys.stderr)
                time.sleep(delay)
                delay *= 2.0
            elif resp.status_code >= 500:
                if attempt == max_retries:
                    raise RuntimeError(f"Groq server error HTTP {resp.status_code} at {url}: {resp.text}")
                print(f"[Groq Whisper] Server error {resp.status_code}, retrying in {delay:.1f}s...", file=sys.stderr)
                time.sleep(delay)
                delay *= 2.0
            else:
                raise RuntimeError(f"Groq API error HTTP {resp.status_code} at {url}: {resp.text}")

    raise RuntimeError("Unexpected transcription failure.")


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio with Groq Whisper word-level timestamps.")
    parser.add_argument("--audio", required=True, help="Path to input audio file (.mp3, .wav, .m4a)")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    parser.add_argument("--prompt", default="繁體中文歌詞與說唱對決字幕", help="Whisper context prompt")
    parser.add_argument("--language", default="zh", help="Language code (default: zh)")
    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}", file=sys.stderr)
        sys.exit(1)

    try:
        result = transcribe_with_groq(args.audio, prompt=args.prompt, language=args.language)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        seg_count = len(result.get("segments", []))
        word_count = len(result.get("words", []))
        print(f"Success! Transcription written to: {out_path} ({seg_count} segments, {word_count} words)")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
