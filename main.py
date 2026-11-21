"""ONDINA - The Poster for a Place That Isn't There.

Copy-only entrypoint, standard library only. The finished poster
(entry.png) ships in this repo; the program empties the output
directory of stale files, copies entry.png to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output), then checks the
copy is byte-identical to the source and is a real JPEG. Nothing is
generated, nothing is fetched, nothing is random, nothing is dated.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POSTER = ROOT / "entry.png"
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
TARGET = OUT_DIR / "entry.png"
JPEG_MAGIC = b"\xff\xd8\xff"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1 << 20)
            if not block:
                break
            hasher.update(block)
    return hasher.hexdigest()


def run() -> int:
    if not POSTER.is_file():
        print(f"error: poster image missing: {POSTER}", file=sys.stderr)
        return 1
    blob = POSTER.read_bytes()
    if not blob:
        print("error: poster image empty", file=sys.stderr)
        return 1
    if blob[:3] != JPEG_MAGIC:
        print("error: poster image is not a JPEG", file=sys.stderr)
        return 1
    if len(blob) > 1_048_576:
        print(f"error: poster image over the 1 MiB limit: {len(blob)} bytes", file=sys.stderr)
        return 1
    if OUT_DIR.exists() and not OUT_DIR.is_dir():
        print(f"error: output path is not a directory: {OUT_DIR}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for leftover in OUT_DIR.iterdir():
        if leftover.is_file() and leftover != TARGET:
            leftover.unlink()
    shutil.copyfile(POSTER, TARGET)
    if digest(TARGET) != hashlib.sha256(blob).hexdigest():
        print("error: copy differs from source", file=sys.stderr)
        return 1
    print(f"wrote entry.png ({len(blob)} bytes, sha256 {digest(TARGET)[:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
