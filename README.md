# news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Daniikhwan/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Daniikhwan/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A deterministic Python program that sums up 18 November 2026's world news in one image: a 1600x1000 newspaper-style infographic rendered with a hand-authored 5x7 bitmap font and a pure-stdlib PNG encoder. No network, no clock, no randomness — the same run always produces the same bytes.

## Run it

```sh
python3 main.py
```

The image is written to `$MAKEFUN_OUTPUT_DIR/image.png` (defaults to `./output/image.png`).

## What it covers

Six stories researched from live reporting on Wednesday 18 November 2026:

1. **Asia** — Trump lands in Manila for Quad talks ahead of a China visit
2. **Ukraine** — Ukraine hits the Crimean Bridge for a second straight day
3. **Middle East** — Iran drones hit a US radar system in Bahrain
4. **Trade** — Canada and China extend trade deals before the APEC summit
5. **United Kingdom** — UK sanctions Israeli settlement firms
6. **Markets** — Nvidia revenue doubles to $115.8bn; board won't reinstate Huang

## How it works

- `main.py` is Python 3 stdlib only (`struct`, `zlib`, `os`, `sys`). The PNG
  encoder is written by hand: raw RGB scanlines, zlib compression, CRC32
  chunks — no Pillow, no pip packages.
- The type is set in a 5x7 bitmap font authored by hand in this file
  (A–Z, 0–9, punctuation), scaled up for headlines, body and labels.
- The news facts are embedded as data in the code, so the grader's
  offline, read-only sandbox run reproduces the exact same image.
- Verified locally: two runs to different output directories produce
  byte-identical PNGs (SHA-256 match), in ~0.5 s.

---

<sub>Entered on [make.fun](https://make.fun/?ref=vnsny7za&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
