#!/usr/bin/env python3
"""Extract text and figures from an NEJM Case Record PDF.

Usage: python extract_nejm.py case.pdf outdir

Writes:
  outdir/case.txt              full text, page-separated ("=== page N ===")
  outdir/figures/pN_iK.png     embedded images (small icons/logos skipped)
  outdir/pages/page_N.png      250-dpi page renders. Crop figure panels from
                               these: embedded images lack NEJM's vector arrows
                               and panel letters, and are sometimes split into tiles.

Crop: python extract_nejm.py --crop page_N.png left,top,right,bottom out.png
      (pixel coordinates in the page render)
"""
import os
import sys

import pymupdf


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    pdf, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(out, "figures"), exist_ok=True)
    os.makedirs(os.path.join(out, "pages"), exist_ok=True)
    doc = pymupdf.open(pdf)
    with open(os.path.join(out, "case.txt"), "w") as f:
        for i, page in enumerate(doc, 1):
            f.write(f"\n=== page {i} ===\n")
            f.write(page.get_text())
    n = 0
    for i, page in enumerate(doc, 1):
        page.get_pixmap(dpi=250).save(os.path.join(out, "pages", f"page_{i}.png"))
        for k, img in enumerate(page.get_images(full=True), 1):
            info = doc.extract_image(img[0])
            if not info or info["width"] < 200 or info["height"] < 150:
                continue
            from io import BytesIO
            from PIL import Image
            try:
                im = Image.open(BytesIO(info["image"]))
                if im.mode not in ("RGB", "L"):
                    im = im.convert("RGB")
                im.save(os.path.join(out, "figures", f"p{i}_i{k}.png"))
            except Exception:
                with open(os.path.join(out, "figures", f"p{i}_i{k}.{info['ext']}"), "wb") as f:
                    f.write(info["image"])
            n += 1
    print(f"{len(doc)} pages, {n} figures -> {out}")


def crop(page_png, box, out_png):
    """Crop a region (left, top, right, bottom in pixels) from a page render."""
    from PIL import Image
    with Image.open(page_png) as im:
        im.crop(tuple(box)).save(out_png)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--crop":
        sys.exit("usage: extract_nejm.py --crop page.png l,t,r,b out.png")
    if len(sys.argv) == 5 and sys.argv[1] == "--crop":
        crop(sys.argv[2], [int(v) for v in sys.argv[3].split(",")], sys.argv[4])
    else:
        main()
