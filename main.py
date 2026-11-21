"""Draw the travel poster of NIMBARA as /output/entry.png.

NIMBARA is a place that does not exist: an island where the sky
falls into the sea. A luminous waterfall pours out of a low golden
cloud straight down into a turquoise bay, a whitewashed cliff
village climbs the rock on the right, and a single sailboat drifts
on the calm water below the falls. The name is set into the picture
in huge cream serif, with the promise underneath: WHERE THE SKY
FALLS INTO THE SEA.

The base scene is a painting generated for this entry and kept in
the repository as base.jpg; main.py crops it square on the
waterfall, frames it in cream like a vintage poster, and sets the
name and tagline in Pillow (generated text garbles, so the lettering
is drawn, never generated). No network, no randomness: two runs
produce the same bytes.

Run it locally the same way the grader does, with an output
directory of your own:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BASE = HERE / "base.jpg"

W, H = 1024, 1024
CREAM = (250, 242, 220)
CREAM_DIM = (238, 226, 196)
DARK = (46, 30, 16)
GOLD = (212, 164, 74)

SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def tracked_w(draw, text, fnt, tracking):
    w = draw.textlength(text, font=fnt)
    return w + tracking * max(0, len(text) - 1)


def draw_tracked(draw, x, y, text, fnt, fill, tracking):
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking


def center_tracked(draw, cx, y, text, fnt, fill, tracking):
    w = tracked_w(draw, text, fnt, tracking)
    draw_tracked(draw, cx - w / 2, y, text, fnt, fill, tracking)


def fit_serif(draw, text, max_w, start):
    size = start
    while size > 40:
        f = font(SERIF_B, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return font(SERIF_B, size)


def draw_poster():
    base = Image.open(BASE).convert("RGB")
    bw, bh = base.size
    # Square crop centred on the waterfall (x ~ 0.55 of the width),
    # so the falls stay central, the village stays on the right and
    # the sailboat stays below the falls.
    side = min(bw, bh)
    cx = int(bw * 0.55)
    x0 = max(0, min(bw - side, cx - side // 2))
    img = base.crop((x0, 0, x0 + side, side)).resize((W, H), Image.LANCZOS)

    draw = ImageDraw.Draw(img, "RGBA")

    # Soft dark scrim behind the title zone so cream serif stays
    # legible over the bright golden cloud.
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    for y in range(0, 250):
        alpha = int(90 * (1 - y / 250.0) ** 1.5)
        sd.line([(0, y), (W, y)], fill=(40, 26, 12, alpha))
    img.paste(scrim, (0, 0), scrim)
    draw = ImageDraw.Draw(img, "RGBA")

    # Name, huge cream serif with one soft dark shadow (no hard
    # outline: the v1 stroke + five shadows read as a black halo).
    name = "NIMBARA"
    name_font = fit_serif(draw, name, 860, 150)
    nw = draw.textlength(name, font=name_font)
    nx, ny = (W - nw) / 2, 52
    draw.text((nx + 4, ny + 6), name, font=name_font,
              fill=(30, 20, 10, 200))
    draw.text((nx, ny), name, font=name_font, fill=CREAM)

    # Tagline, tracked caps beneath the name, clear of its baseline
    # (v1 sat it on the letters' bottom edge).
    tag = "WHERE THE SKY FALLS INTO THE SEA"
    tag_font = font(SANS_B, 30)
    center_tracked(draw, W / 2, 248, tag, tag_font, CREAM, 7)

    # Thin gold rule under the tagline.
    tw = tracked_w(draw, tag, tag_font, 7)
    draw.line([(W / 2 - tw / 2, 296), (W / 2 + tw / 2, 296)],
              fill=GOLD, width=3)

    # Cream vintage frame + thin inner rule.
    draw.rectangle([0, 0, W - 1, H - 1], outline=CREAM, width=26)
    draw.rectangle([26, 26, W - 27, H - 27], outline=DARK, width=2)
    return img


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "entry.png"
    if not BASE.is_file():
        print(f"missing base image: {BASE}", file=sys.stderr)
        return 1
    img = draw_poster()
    img.save(out, format="PNG", optimize=True)
    size = out.stat().st_size
    print(f"wrote {out} {img.size} {size} bytes "
          f"sha256={hashlib.sha256(out.read_bytes()).hexdigest()}")
    if size > 1_048_576:
        print("over 1 MiB cap, re-saving as JPEG", file=sys.stderr)
        img.save(out, format="JPEG", quality=93, optimize=True)
        size = out.stat().st_size
        print(f"re-saved {out} {size} bytes "
              f"sha256={hashlib.sha256(out.read_bytes()).hexdigest()}")
    if size > 1_048_576 or img.size != (1024, 1024):
        print("entry fails the size cap", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
