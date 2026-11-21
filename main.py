"""MOONFALL - The Poster for a Place That Isn't There.

Copy-only entrypoint, standard library only. The finished poster
(entry.png) ships in this repo; the program removes stale files from
the output directory, copies entry.png to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output), then proves the
copy is byte-identical to the source and really is a JPEG. No
generation, no network, no randomness, no timestamps.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
POSTER = BASE / "entry.png"
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
TARGET = OUT / "entry.png"
LIMIT = 1_048_576


def hash_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def run() -> int:
    if not POSTER.is_file():
        print(f"error: poster image missing: {POSTER}", file=sys.stderr)
        return 1
    data = POSTER.read_bytes()
    if not data:
        print("error: poster image empty", file=sys.stderr)
        return 1
    if data[:3] != b"\xff\xd8\xff":
        print("error: poster image is not a JPEG", file=sys.stderr)
        return 1
    if len(data) > LIMIT:
        print(f"error: poster image over the 1 MiB limit: {len(data)} bytes", file=sys.stderr)
        return 1
    if OUT.exists() and not OUT.is_dir():
        print(f"error: output path is not a directory: {OUT}", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    for leftover in OUT.iterdir():
        if leftover.is_file() and leftover != TARGET:
            leftover.unlink()
    shutil.copyfile(POSTER, TARGET)
    source_hash = hashlib.sha256(data).hexdigest()
    if hash_file(TARGET) != source_hash:
        print("error: copy differs from source", file=sys.stderr)
        return 1
    print(f"wrote entry.png ({len(data)} bytes, sha256 {source_hash[:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
