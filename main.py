"""SELENARA - The Poster for a Place That Isn't There.

Copy-only entrypoint, stdlib only. The finished poster (entry.png) is
shipped in this repo; this program clears any stale files from the
output directory, copies entry.png to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output), and verifies the copy is byte-identical to the
source before exiting. No generation, no network, no randomness,
no timestamps, no third-party imports.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
DEST_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
DEST = DEST_DIR / "entry.png"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    if not SOURCE.is_file():
        print(f"error: poster image missing: {SOURCE}", file=sys.stderr)
        return 1
    if SOURCE.stat().st_size == 0:
        print(f"error: poster image empty: {SOURCE}", file=sys.stderr)
        return 1
    if SOURCE.read_bytes()[:3] != b"\xff\xd8\xff":
        print("error: poster image is not a JPEG", file=sys.stderr)
        return 1
    if DEST_DIR.exists() and not DEST_DIR.is_dir():
        print(f"error: output path is not a directory: {DEST_DIR}", file=sys.stderr)
        return 1
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    for stale in DEST_DIR.iterdir():
        if stale.is_file() and stale != DEST:
            stale.unlink()
    shutil.copyfile(SOURCE, DEST)
    source_hash = sha256_of(SOURCE)
    if sha256_of(DEST) != source_hash:
        print("error: copy is not byte-identical", file=sys.stderr)
        return 1
    print(f"wrote entry.png ({DEST.stat().st_size} bytes, sha256 {source_hash[:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
