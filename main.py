#!/usr/bin/env python3
"""Entrypoint for news-image-20261123 (standard library only).

Copies the pre-rendered front page, entry.png (produced by render.py
in this same repository), to /output/entry.png. Runs with no network
and nothing installed, so it uses only the standard library. The copy
is byte-for-byte, so repeated runs write identical bytes.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("ENTRY_OUTPUT_DIR", "/output")
OUT = os.path.join(OUT_DIR, "entry.png")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SRC, OUT)


if __name__ == "__main__":
    main()
