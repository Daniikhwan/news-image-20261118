#!/usr/bin/env python3
"""news-image-20261118 -- Sum up 18 November 2026's world news in one image.

A deterministic, pure-stdlib program. It renders a 1600x1000 newspaper-style
infographic PNG summarising the six biggest world-news stories of Wednesday
18 November 2026, using a hand-authored 5x7 bitmap font and a hand-written
PNG encoder (zlib is stdlib). No network, no clock, no randomness, no
unordered iteration: the same run always produces the same bytes.

Run:   python3 main.py
Out:   $MAKEFUN_OUTPUT_DIR/image.png   (defaults to ./output)
"""

import os
import struct
import sys
import zlib

WIDTH = 1600
HEIGHT = 1000

# ---------------------------------------------------------------------------
# PNG encoder (pure stdlib: struct + zlib + binascii-free CRC via zlib)
# ---------------------------------------------------------------------------

def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path, width, height, rgb):
    """Write 8-bit RGB pixels (bytes, row-major, no padding) as a PNG."""
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter: None
        raw += rgb[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------------------
# Canvas: a flat RGB bytearray with rectangle / circle helpers
# ---------------------------------------------------------------------------

class Canvas:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.pixels = bytearray(color * (width * height))

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                off = base + (xx - x0) * 3
                self.pixels[off] = r
                self.pixels[off + 1] = g
                self.pixels[off + 2] = b

    def fill_circle(self, cx, cy, radius, color):
        r2 = radius * radius
        for yy in range(cy - radius, cy + radius + 1):
            for xx in range(cx - radius, cx + radius + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r2:
                    if 0 <= xx < self.width and 0 <= yy < self.height:
                        off = (yy * self.width + xx) * 3
                        self.pixels[off:off + 3] = bytes(color)


# ---------------------------------------------------------------------------
# Hand-authored 5x7 bitmap font. Every glyph is 7 rows of 5 cells, "#" = ink.
# Uppercase A-Z, digits 0-9 and common punctuation, drawn by hand in this file.
# ---------------------------------------------------------------------------

FONT = {
    "A": (
        ".###.",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ),
    "B": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#...#",
        "#...#",
        "####.",
    ),
    "C": (
        ".####",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        ".####",
    ),
    "D": (
        "####.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "####.",
    ),
    "E": (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#####",
    ),
    "F": (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    "G": (
        ".####",
        "#....",
        "#....",
        "#.###",
        "#...#",
        "#...#",
        ".###.",
    ),
    "H": (
        "#...#",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ),
    "I": (
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "#####",
    ),
    "J": (
        "..###",
        "...#.",
        "...#.",
        "...#.",
        "...#.",
        "#..#.",
        ".##..",
    ),
    "K": (
        "#...#",
        "#..#.",
        "#.#..",
        "##...",
        "#.#..",
        "#..#.",
        "#...#",
    ),
    "L": (
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#####",
    ),
    "M": (
        "#...#",
        "##.##",
        "#.#.#",
        "#.#.#",
        "#...#",
        "#...#",
        "#...#",
    ),
    "N": (
        "#...#",
        "##..#",
        "##..#",
        "#.#.#",
        "#..##",
        "#..##",
        "#...#",
    ),
    "O": (
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    "P": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    "Q": (
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#..#.",
        ".##.#",
    ),
    "R": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#.#..",
        "#..#.",
        "#...#",
    ),
    "S": (
        ".####",
        "#....",
        "#....",
        ".###.",
        "....#",
        "....#",
        "####.",
    ),
    "T": (
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    "U": (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    "V": (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
    ),
    "W": (
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#.#.#",
        "##.##",
        "#...#",
    ),
    "X": (
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        ".#.#.",
        "#...#",
        "#...#",
    ),
    "Y": (
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    "Z": (
        "#####",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        "#####",
    ),
    "0": (
        ".###.",
        "#...#",
        "#..##",
        "#.#.#",
        "##..#",
        "#...#",
        ".###.",
    ),
    "1": (
        "..#..",
        ".##..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".###.",
    ),
    "2": (
        ".###.",
        "#...#",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#####",
    ),
    "3": (
        "####.",
        "....#",
        "....#",
        ".###.",
        "....#",
        "....#",
        "####.",
    ),
    "4": (
        "...#.",
        "..##.",
        ".#.#.",
        "#..#.",
        "#####",
        "...#.",
        "...#.",
    ),
    "5": (
        "#####",
        "#....",
        "####.",
        "....#",
        "....#",
        "#...#",
        ".###.",
    ),
    "6": (
        ".###.",
        "#....",
        "#....",
        "####.",
        "#...#",
        "#...#",
        ".###.",
    ),
    "7": (
        "#####",
        "....#",
        "...#.",
        "...#.",
        "..#..",
        "..#..",
        "..#..",
    ),
    "8": (
        ".###.",
        "#...#",
        "#...#",
        ".###.",
        "#...#",
        "#...#",
        ".###.",
    ),
    "9": (
        ".###.",
        "#...#",
        "#...#",
        ".####",
        "....#",
        "....#",
        ".###.",
    ),
    " ": (
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
    ".": (
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".##..",
        ".##..",
    ),
    ",": (
        ".....",
        ".....",
        ".....",
        ".....",
        ".##..",
        ".##..",
        ".#...",
    ),
    ":": (
        ".....",
        ".##..",
        ".##..",
        ".....",
        ".##..",
        ".##..",
        ".....",
    ),
    ";": (
        ".....",
        ".##..",
        ".##..",
        ".....",
        ".##..",
        ".##..",
        ".#...",
    ),
    "!": (
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".....",
        "..#..",
    ),
    "?": (
        ".###.",
        "#...#",
        "....#",
        "...#.",
        "..#..",
        ".....",
        "..#..",
    ),
    "-": (
        ".....",
        ".....",
        ".....",
        ".###.",
        ".....",
        ".....",
        ".....",
    ),
    "(": (
        "...#.",
        "..#..",
        ".#...",
        ".#...",
        ".#...",
        "..#..",
        "...#.",
    ),
    ")": (
        ".#...",
        "..#..",
        "...#.",
        "...#.",
        "...#.",
        "..#..",
        ".#...",
    ),
    "/": (
        "....#",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        "#....",
    ),
    "%": (
        "#...#",
        "#..#.",
        "...#.",
        "..#..",
        ".#...",
        ".#..#",
        "#...#",
    ),
    "$": (
        "..#..",
        ".####",
        "#.#..",
        ".###.",
        "..#.#",
        "####.",
        "..#..",
    ),
    "&": (
        ".##..",
        "#..#.",
        "#..#.",
        ".#...",
        "#.#.#",
        "#..#.",
        ".##.#",
    ),
    "+": (
        ".....",
        "..#..",
        "..#..",
        "#####",
        "..#..",
        "..#..",
        ".....",
    ),
    "=": (
        ".....",
        ".....",
        ".####",
        ".....",
        ".####",
        ".....",
        ".....",
    ),
    '"': (
        ".#.#.",
        ".#.#.",
        ".#.#.",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
    "'": (
        "..#..",
        "..#..",
        ".#...",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
    "*": (
        ".....",
        ".#.#.",
        ".###.",
        "#####",
        ".###.",
        ".#.#.",
        ".....",
    ),
    "|": (
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
}


# ---------------------------------------------------------------------------
# Text drawing on the canvas (scale = pixel size of one font cell)
# ---------------------------------------------------------------------------

def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(canvas, x, y, text, scale, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is not None:
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        canvas.fill_rect(
                            cx + col * scale, y + row * scale, scale, scale, color
                        )
        cx += 6 * scale
    return cx


def draw_text_centered(canvas, cx, y, text, scale, color):
    draw_text(canvas, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_text(text, scale, max_width):
    lines = []
    current = ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

PAPER = (246, 241, 231)
INK = (20, 33, 61)
NAVY = (18, 35, 61)
NAVY_LIGHT = (38, 58, 90)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
CARD_BORDER = (216, 210, 196)
GOLD = (217, 164, 65)
RED = (192, 57, 43)
MUTED = (90, 100, 114)
FAINT = (227, 220, 203)
RULE = (200, 192, 176)


# ---------------------------------------------------------------------------
# The news of 18 November 2026, researched from live reporting on the day.
# Headlines and summaries are embedded as data: the program never touches
# the network, so the image is identical on every run.
# ---------------------------------------------------------------------------

STORIES = [
    {
        "num": "01",
        "tag": "ASIA",
        "color": (192, 57, 43),
        "headline": "TRUMP LANDS IN MANILA FOR QUAD TALKS",
        "summary": (
            "THE US PRESIDENT OPENS AN ASIA TOUR IN THE PHILIPPINES AHEAD "
            "OF THE QUAD SUMMIT AND A PLANNED CHINA VISIT."
        ),
        "source": "REUTERS",
    },
    {
        "num": "02",
        "tag": "UKRAINE",
        "color": (36, 113, 163),
        "headline": "UKRAINE HITS CRIMEAN BRIDGE AGAIN",
        "summary": (
            "KYIV STRIKES THE STRATEGIC BRIDGE FOR A SECOND STRAIGHT DAY "
            "AS RUSSIAN MISSILES HIT TWO BRIDGES IN KYIV."
        ),
        "source": "AP",
    },
    {
        "num": "03",
        "tag": "MIDDLE EAST",
        "color": (20, 143, 119),
        "headline": "IRAN DRONES HIT US RADAR IN BAHRAIN",
        "summary": (
            "IRAN ATTACKS A US MILITARY RADAR SYSTEM IN BAHRAIN AS GULF "
            "STATES REPORT DRONE INTERCEPTIONS AND AN ALL-CLEAR."
        ),
        "source": "THE GUARDIAN",
    },
    {
        "num": "04",
        "tag": "TRADE",
        "color": (125, 60, 152),
        "headline": "CANADA AND CHINA EXTEND TRADE DEALS",
        "summary": (
            "XI MEETS CARNEY AND THE TWO COUNTRIES EXTEND TRADE "
            "COOPERATION DAYS BEFORE THE APEC SUMMIT."
        ),
        "source": "REUTERS",
    },
    {
        "num": "05",
        "tag": "UNITED KINGDOM",
        "color": (202, 111, 30),
        "headline": "UK SANCTIONS ISRAELI SETTLEMENT FIRMS",
        "summary": (
            "BRITAIN BLACKLISTS EIGHT FIRMS OVER ILLEGAL WEST BANK "
            "SETTLEMENTS IN A PUSH TO PROTECT THE TWO-STATE SOLUTION."
        ),
        "source": "BBC",
    },
    {
        "num": "06",
        "tag": "MARKETS",
        "color": (30, 132, 73),
        "headline": "NVIDIA REVENUE DOUBLES TO $115.8BN",
        "summary": (
            "THE CHIPMAKER'S QUARTERLY REVENUE DOUBLES YEAR ON YEAR. ITS "
            "BOARD SAYS OUSTED CEO JENSEN HUANG WILL NOT RETURN."
        ),
        "source": "THE GUARDIAN",
    },
]


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def draw_card(canvas, x, y, w, h, story):
    canvas.fill_rect(x, y, w, h, CARD)
    # border
    canvas.fill_rect(x, y, w, 2, CARD_BORDER)
    canvas.fill_rect(x, y + h - 2, w, 2, CARD_BORDER)
    canvas.fill_rect(x, y, 2, h, CARD_BORDER)
    canvas.fill_rect(x + w - 2, y, 2, h, CARD_BORDER)
    # accent bar on the left
    canvas.fill_rect(x + 2, y + 2, 10, h - 4, story["color"])

    ix = x + 30          # inner left
    iw = w - 30 - 24     # inner width

    # story number, top right, faint
    num = story["num"]
    draw_text(canvas, x + w - 24 - text_width(num, 4), y + 16, num, 4, FAINT)

    # tag chip
    tag = story["tag"]
    chip_w = text_width(tag, 2) + 18
    canvas.fill_rect(ix, y + 18, chip_w, 26, story["color"])
    draw_text(canvas, ix + 9, y + 25, tag, 2, WHITE)

    # headline (scale 3, wraps to at most 2 lines)
    lines = wrap_text(story["headline"], 3, iw)
    hy = y + 62
    for line in lines:
        draw_text(canvas, ix, hy, line, 3, INK)
        hy += 26

    # summary (scale 2)
    sy = hy + 10
    for line in wrap_text(story["summary"], 2, iw):
        draw_text(canvas, ix, sy, line, 2, MUTED)
        sy += 19

    # rule + source line at the bottom of the card
    canvas.fill_rect(ix, y + h - 34, iw, 2, RULE)
    draw_text(canvas, ix, y + h - 26, "SOURCE: " + story["source"], 1, MUTED)
    draw_text(
        canvas,
        x + w - 24 - text_width("18 NOV 2026", 1),
        y + h - 26,
        "18 NOV 2026",
        1,
        MUTED,
    )


def render():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)

    # ---- header band ------------------------------------------------------
    canvas.fill_rect(0, 0, WIDTH, 168, NAVY)
    canvas.fill_rect(0, 168, WIDTH, 5, GOLD)

    draw_text(canvas, 40, 26, "WORLD NEWS  -  WEDNESDAY 18 NOVEMBER 2026", 2, GOLD)
    draw_text(canvas, 40, 56, "THE WORLD IN ONE IMAGE", 7, WHITE)
    draw_text(
        canvas, 40, 124, "SIX STORIES THAT DEFINED THE DAY", 3, (200, 210, 225)
    )

    # date badge, top right of the header
    bx, by, bw, bh = 1400, 24, 160, 120
    canvas.fill_rect(bx, by, bw, bh, RED)
    draw_text_centered(canvas, bx + bw // 2, by + 12, "18", 7, WHITE)
    draw_text_centered(canvas, bx + bw // 2, by + 76, "NOVEMBER", 2, WHITE)
    draw_text_centered(canvas, bx + bw // 2, by + 98, "2026", 2, WHITE)

    # ---- story grid: 2 columns x 3 rows ----------------------------------
    margin = 40
    gap_x = 24
    gap_y = 20
    top = 196
    bottom = 920
    card_w = (WIDTH - 2 * margin - gap_x) // 2
    card_h = (bottom - top - 2 * gap_y) // 3
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        x = margin + col * (card_w + gap_x)
        y = top + row * (card_h + gap_y)
        draw_card(canvas, x, y, card_w, card_h, story)

    # ---- footer -----------------------------------------------------------
    draw_text(
        canvas,
        40,
        946,
        "HEADLINES AS REPORTED ON 18 NOVEMBER 2026  |  SOURCES: REUTERS, AP, "
        "THE GUARDIAN, BBC",
        2,
        MUTED,
    )
    draw_text(
        canvas,
        40,
        972,
        "RENDERED BY A DETERMINISTIC PYTHON PROGRAM  -  NO LIVE DATA, "
        "NO CLOCK, NO RANDOMNESS",
        1,
        MUTED,
    )
    return canvas


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "image.png")
    canvas = render()
    write_png(out_path, WIDTH, HEIGHT, canvas.pixels)
    print("Wrote %s (%dx%d)" % (out_path, WIDTH, HEIGHT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
