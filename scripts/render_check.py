#!/usr/bin/env python3
"""Render a .pptx to PDF via Microsoft PowerPoint (macOS) and make contact sheets.

Usage: python render_check.py deck.pptx outdir

Produces outdir/deck.pdf and outdir/sheet_NN.png (16 slides per sheet) so the
slides can be visually checked for overflowing text and image placement.
PowerPoint is sandboxed, so the file is round-tripped through its container.
"""
import os
import shutil
import subprocess
import sys
import time

import pymupdf
from PIL import Image

CONTAINER = os.path.expanduser("~/Library/Containers/com.microsoft.Powerpoint/Data")


def export_pdf(pptx, pdf_out):
    tmp_in = os.path.join(CONTAINER, "ccd_render_in.pptx")
    tmp_out = os.path.join(CONTAINER, "ccd_render_out.pdf")
    shutil.copy(pptx, tmp_in)
    if os.path.exists(tmp_out):
        os.remove(tmp_out)
    script = f'''
    tell application "Microsoft PowerPoint"
        open POSIX file "{tmp_in}"
        delay 3
        save active presentation in POSIX file "{tmp_out}" as save as PDF
        delay 2
        close active presentation saving no
    end tell'''
    subprocess.run(["osascript", "-e", script], check=True)
    for _ in range(30):
        if os.path.exists(tmp_out):
            break
        time.sleep(1)
    shutil.move(tmp_out, pdf_out)
    os.remove(tmp_in)


def sheets(pdf, outdir, per=16, cols=4):
    d = pymupdf.open(pdf)
    paths = []
    for start in range(0, len(d), per):
        ims = []
        for i in range(start, min(start + per, len(d))):
            pix = d[i].get_pixmap(dpi=40)
            ims.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        w, h = ims[0].size
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (w * cols, h * rows), "white")
        for k, im in enumerate(ims):
            sheet.paste(im, ((k % cols) * w, (k // cols) * h))
            # thin frame so slide borders are visible
            for x in range(w):
                sheet.putpixel(((k % cols) * w + x, (k // cols) * h), (180, 180, 180))
        p = os.path.join(outdir, f"sheet_{start // per + 1:02d}.png")
        sheet.save(p)
        paths.append(p)
    return paths


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    pptx, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    pdf = os.path.join(outdir, "deck.pdf")
    export_pdf(pptx, pdf)
    for p in sheets(pdf, outdir):
        print(p)


if __name__ == "__main__":
    main()
