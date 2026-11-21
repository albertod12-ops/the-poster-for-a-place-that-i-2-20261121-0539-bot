"""MOONFALL - The Poster for a Place That Isn't There.

Copy-only entrypoint, standard library only. The finished poster
(entry.png) ships in this repo; the program clears stale files from
the output directory, copies entry.png to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output), then proves the
copy is byte-identical to the source and is a genuine JPEG. No
generation, no network, no randomness, no timestamps.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
POSTER = BASE / "entry.png"
OUTDIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
DEST = OUTDIR / "entry.png"
LIMIT = 1_048_576


def hash_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    if not POSTER.is_file():
        print(f"error: poster image missing: {POSTER}", file=sys.stderr)
        return 1
    image = POSTER.read_bytes()
    if not image:
        print("error: poster image empty", file=sys.stderr)
        return 1
    if image[:3] != b"\xff\xd8\xff":
        print("error: poster image is not a JPEG", file=sys.stderr)
        return 1
    if len(image) > LIMIT:
        print(f"error: poster image over the 1 MiB limit: {len(image)} bytes", file=sys.stderr)
        return 1
    if OUTDIR.exists() and not OUTDIR.is_dir():
        print(f"error: output path is not a directory: {OUTDIR}", file=sys.stderr)
        return 1
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for stale in OUTDIR.iterdir():
        if stale.is_file() and stale != DEST:
            stale.unlink()
    shutil.copyfile(POSTER, DEST)
    want = hashlib.sha256(image).hexdigest()
    got = hash_of(DEST)
    if got != want:
        print("error: copy differs from source", file=sys.stderr)
        return 1
    print(f"wrote entry.png ({len(image)} bytes, sha256 {want[:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
