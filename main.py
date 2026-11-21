"""MOONFALL - The Poster for a Place That Isn't There.

Copy-only entrypoint, standard library only. The finished poster
(entry.png) ships in this repo; the program sweeps stale files out
of the output directory, copies entry.png to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output), then proves the
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
OUTPUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
DEST = OUTPUT / "entry.png"
LIMIT = 1_048_576


def sha_of(path: Path) -> str:
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
    if OUTPUT.exists() and not OUTPUT.is_dir():
        print(f"error: output path is not a directory: {OUTPUT}", file=sys.stderr)
        return 1
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for old in OUTPUT.iterdir():
        if old.is_file() and old != DEST:
            old.unlink()
    shutil.copyfile(POSTER, DEST)
    want = hashlib.sha256(image).hexdigest()
    got = sha_of(DEST)
    if got != want:
        print("error: copy differs from source", file=sys.stderr)
        return 1
    print(f"wrote entry.png ({len(image)} bytes, sha256 {want[:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
