"""MOONFALL - The Poster for a Place That Isn't There.

Copy-only entrypoint, standard library only. The finished poster
(entry.png) ships in this repo; the program clears stale files from
the output directory, copies entry.png to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output), then verifies the
copy is byte-identical to the source and is a genuine JPEG. No
generation, no network, no randomness, no timestamps.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
POSTER = HERE / "entry.png"
OUTDIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
DEST = OUTDIR / "entry.png"
MAX_BYTES = 1_048_576


def file_hash(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    if not POSTER.is_file():
        print(f"error: poster image missing: {POSTER}", file=sys.stderr)
        return 1
    payload = POSTER.read_bytes()
    if not payload:
        print("error: poster image empty", file=sys.stderr)
        return 1
    if payload[:3] != b"\xff\xd8\xff":
        print("error: poster image is not a JPEG", file=sys.stderr)
        return 1
    if len(payload) > MAX_BYTES:
        print(f"error: poster image over the 1 MiB limit: {len(payload)} bytes", file=sys.stderr)
        return 1
    if OUTDIR.exists() and not OUTDIR.is_dir():
        print(f"error: output path is not a directory: {OUTDIR}", file=sys.stderr)
        return 1
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for stale in OUTDIR.iterdir():
        if stale.is_file() and stale != DEST:
            stale.unlink()
    shutil.copyfile(POSTER, DEST)
    expected = hashlib.sha256(payload).hexdigest()
    actual = file_hash(DEST)
    if actual != expected:
        print("error: copy differs from source", file=sys.stderr)
        return 1
    print(f"wrote entry.png ({len(payload)} bytes, sha256 {expected[:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
