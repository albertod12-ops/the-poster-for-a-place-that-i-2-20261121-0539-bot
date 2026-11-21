"""NIMBARA - The Poster for a Place That Isn't There.

Copy-only entrypoint (stdlib only): copies the finished poster image
(entry.png, shipped in this repo) to $MAKEFUN_OUTPUT_DIR/entry.png.
No generation, no network, no randomness, no timestamps.
"""

import os
import shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"poster image missing: {SOURCE}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, OUTPUT_DIR / "entry.png")
    print("wrote entry.png")


if __name__ == "__main__":
    main()
