"""Entry point for news-image-20261123.

Draws the front page with render.py and writes it to /output/entry.png
(the path the contest gate reads). When /output does not exist (local
runs), the image is written next to this file instead.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import render


def main():
    img = render()
    if os.path.isdir("/output"):
        out = "/output/entry.png"
    else:
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "entry.png")
    img.save(out, "PNG")
    print("wrote", out)


if __name__ == "__main__":
    main()
