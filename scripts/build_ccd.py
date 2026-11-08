#!/usr/bin/env python3
"""Build a CCD (Clinical Case Discussion) deck from a case JSON spec.

Usage: python build_ccd.py case.json output.pptx

The JSON format is documented in ../reference/case_schema.md.
Paths to images inside the JSON are resolved relative to the JSON file.
"""
import copy
import json
import os
import re
import sys

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
TEMPLATE = os.path.join(ASSETS, "template.pptx")
LOGO = os.path.join(ASSETS, "ccd_logo.jpg")

FONT = "Calibri"
RED = RGBColor(0xFF, 0x00, 0x00)
BLACK = RGBColor(0, 0, 0)
LINK_BLUE = RGBColor(0x00, 0x70, 0xC0)
ARROW_BLUE = RGBColor(0x4A, 0x7D, 0xBA)
TABLE_STYLE = "{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"  # Medium Style 2 - Accent 1 (blue header, banded rows)

# Geometry taken from the existing CCD decks (4:3, 14in x 10.5in)
SW, SH = 12801600, 9601200
LOGO_BOX = (5288734, 149411, 2212176, 1579488)
CRUMB_BOX = (0, 1924423, 12801600, 624786)
BODY_TOP = 2700000
MARGIN = 640080
BODY_W = SW - 2 * MARGIN
BACK_ARROW = (11626001, 8803332, 1071039, 647934)

DEFAULT_HISTORY_TABS = ["CC", "HPI", "PMH", "ME", "ALL", "SH", "FH", "ROS", "VS", "PE"]
DEFAULT_LAB_TABS = ["CMP", "CBC", "PT, PTT", "UA", "ECG", "CXR"]
TIMELINE = ["Admission note", "Assessment", "Problems list", "DD"]


# ---------------------------------------------------------------- helpers

def layout(prs, name):
    for l in prs.slide_layouts:
        if l.name == name:
            return l
    raise KeyError(name)


def new_slide(prs, layout_name="BLANK"):
    s = prs.slides.add_slide(layout(prs, layout_name))
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    return s


def add_logo(slide):
    slide.shapes.add_picture(LOGO, *[Emu(v) for v in LOGO_BOX])


def set_notes(slide, text):
    if text:
        slide.notes_slide.notes_text_frame.text = text


def style_run(run, size, bold=False, italic=False, color=BLACK, underline=False):
    f = run.font
    f.name = FONT
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.underline = underline
    f.color.rgb = color


def textbox(slide, box, size=28, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(*[Emu(v) for v in box])
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    return tb, tf


INLINE = re.compile(r"(\*\*.+?\*\*|\*.+?\*)")


def add_inline_runs(par, text, size, color=BLACK, bold=False, italic=False):
    """Supports **bold** and *italic* inline markup."""
    for chunk in INLINE.split(text):
        if not chunk:
            continue
        b, i, t = bold, italic, chunk
        if chunk.startswith("**") and chunk.endswith("**"):
            b, t = True, chunk[2:-2]
        elif chunk.startswith("*") and chunk.endswith("*") and len(chunk) > 1:
            i, t = True, chunk[1:-1]
        style_run(_run(par, t), size, bold=b, italic=i, color=color)


def _run(par, text):
    r = par.add_run()
    r.text = text
    return r


def set_bullet(par, level, char="•"):
    pPr = par._p.get_or_add_pPr()
    indent = 457200
    pPr.set("marL", str(indent * (level + 1)))
    pPr.set("indent", str(-indent))
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum", "a:buFont"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    buFont = etree.SubElement(pPr, qn("a:buFont"))
    buFont.set("typeface", "Arial")
    bu = etree.SubElement(pPr, qn("a:buChar"))
    bu.set("char", char)


def set_no_bullet(par):
    pPr = par._p.get_or_add_pPr()
    pPr.set("marL", "0")
    pPr.set("indent", "0")
    etree.SubElement(pPr, qn("a:buNone"))


def parse_body(body):
    """Body is a string (markdown-ish) or a list of lines.

    "- text"      bullet level 0, "  - text" level 1 (2 spaces per level)
    "=> text"     arrow line without bullet (common in the decks)
    "text"        plain paragraph, no bullet
    ""            empty spacer line
    """
    if body is None:
        return []
    lines = body.split("\n") if isinstance(body, str) else list(body)
    out = []
    for ln in lines:
        m = re.match(r"^(\s*)[-•]\s+(.*)$", ln)
        if m:
            out.append(("bullet", len(m.group(1).replace("\t", "  ")) // 2, m.group(2)))
        elif ln.strip() == "":
            out.append(("blank", 0, ""))
        else:
            out.append(("plain", 0, ln.strip()))
    return out


def estimate_lines(items, size, width_emu):
    width_pt = width_emu / 12700
    total = 0
    for kind, level, text in items:
        chars = max(1, int((width_pt - 36 * (level + 1)) / (size * 0.48)))
        plain = re.sub(r"\*", "", text)
        total += max(1, -(-len(plain) // chars)) if kind != "blank" else 0.6
    return total


def fit_size(items, box_w, box_h, sizes=(36, 32, 28, 26, 24, 22, 20, 18, 16, 14)):
    for s in sizes:
        if estimate_lines(items, s, box_w) * s * 1.25 <= box_h / 12700:
            return s
    return sizes[-1]


def fill_body(tf, body, box_w, box_h, size=None, align=PP_ALIGN.LEFT, max_size=32):
    items = parse_body(body)
    if size is None:
        size = fit_size(items, box_w, box_h, tuple(s for s in (36, 32, 28, 26, 24, 22, 20, 18, 16, 14) if s <= max_size))
    first = True
    for kind, level, text in items:
        par = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        par.alignment = align
        sz = size if level == 0 else max(12, size - 2 * level)
        if kind == "bullet":
            set_bullet(par, level, "•" if level == 0 else "–" if level == 2 else "•")
            add_inline_runs(par, text, sz)
        elif kind == "plain":
            set_no_bullet(par)
            add_inline_runs(par, text, sz)
        else:
            set_no_bullet(par)
            style_run(_run(par, ""), sz)
        par.space_before = Pt(4)
    return size


def body_box(slide, body, top=BODY_TOP, left=MARGIN, width=BODY_W, height=None, align=PP_ALIGN.LEFT, size=None, max_size=32):
    height = height or (SH - top - 500000)
    tb, tf = textbox(slide, (left, top, width, height))
    fill_body(tf, body, width, height, size=size, align=align, max_size=max_size)
    return tb


def title_box(slide, text, top=1800000, size=40, color=BLACK, bold=False, italic=False, align=PP_ALIGN.LEFT, height=800000):
    tb, tf = textbox(slide, (MARGIN, top, BODY_W, height), anchor=MSO_ANCHOR.MIDDLE)
    p = tf.paragraphs[0]
    p.alignment = align
    add_inline_runs(p, text, size, color=color, bold=bold, italic=italic)
    return tb


def breadcrumb(slide, tabs, active):
    tb, tf = textbox(slide, CRUMB_BOX)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    for i, t in enumerate(tabs):
        on = t == active
        style_run(_run(p, t), 32 if len(tabs) <= 10 else 28, bold=on, color=RED if on else BLACK)
        if i < len(tabs) - 1:
            style_run(_run(p, "   >   " if len(tabs) <= 8 else "  >  "), 32 if len(tabs) <= 10 else 28)


def add_table(slide, columns, rows, box, max_size=24):
    n_rows = len(rows) + 1
    left, top, width, height = box
    size = max_size
    for s in (max_size, 22, 20, 18, 16, 14, 12, 11, 10):
        size = s
        if n_rows * s * 2.0 * 12700 <= height:
            break
    row_h = int(size * 1.9 * 12700)
    gf = slide.shapes.add_table(n_rows, len(columns), Emu(left), Emu(top), Emu(width), Emu(row_h * n_rows))
    tbl = gf.table
    tbl._tbl.tblPr.find(qn("a:tableStyleId")).text = TABLE_STYLE
    # first column wider (parameter names)
    if len(columns) >= 2:
        first = int(width * (0.36 if len(columns) > 3 else 0.4))
        rest = (width - first) // (len(columns) - 1)
        tbl.columns[0].width = Emu(first)
        for c in range(1, len(columns)):
            tbl.columns[c].width = Emu(rest)
    for r in range(n_rows):
        tbl.rows[r].height = Emu(row_h)
        vals = columns if r == 0 else rows[r - 1]
        for c in range(len(columns)):
            cell = tbl.cell(r, c)
            cell.margin_top = cell.margin_bottom = Emu(20000)
            v = vals[c] if c < len(vals) else ""
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            text = str(v)
            bold = r == 0
            if text.startswith("!"):  # "!value" marks abnormal values -> bold
                text, bold = text[1:], True
            style_run(_run(p, text), size, bold=bold, color=RGBColor(0xFF, 0xFF, 0xFF) if r == 0 else BLACK)
    return gf


def resolve(path, base):
    return path if os.path.isabs(path) else os.path.join(base, path)


def place_images(slide, images, box, base, caption_size=14):
    """images: list of {"path", "caption"?}; laid out in a row inside box."""
    from PIL import Image
    if not images:
        return
    left, top, width, height = box
    gap = 150000
    caption_size = max(caption_size, 16)
    # caption height from its text: ~ chars per line at caption_size over the per-image width
    per_w = (width - gap * (len(images) - 1)) / len(images)
    cap_lines = max([estimate_lines(parse_body(im.get("caption")), caption_size, per_w)
                     for im in images if im.get("caption")] or [0])
    cap_h = int(min(height * 0.3, cap_lines * caption_size * 1.3 * 12700 + 100000)) if cap_lines else 0
    img_h_max = height - cap_h
    dims = []
    for im in images:
        with Image.open(resolve(im["path"], base)) as I:
            dims.append(I.size)
    # scale so all images share a height and fit the width
    total_ratio = sum(w / h for w, h in dims)
    h = min(img_h_max, int((width - gap * (len(images) - 1)) / total_ratio))
    x = left + (width - (int(total_ratio * h) + gap * (len(images) - 1))) // 2
    for im, (w0, h0) in zip(images, dims):
        w = int(h * w0 / h0)
        slide.shapes.add_picture(resolve(im["path"], base), Emu(x), Emu(top), Emu(w), Emu(h))
        if im.get("caption"):
            tb, tf = textbox(slide, (x, top + h + 50000, max(w, 2400000), cap_h))
            fill_body(tf, im["caption"], max(w, 2400000), cap_h, size=caption_size)
        x += w + gap


def add_slide_jump(run, source_slide, target_slide):
    rId = source_slide.part.relate_to(target_slide.part, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide")
    rPr = run._r.get_or_add_rPr()
    h = etree.SubElement(rPr, qn("a:hlinkClick"))
    h.set(qn("r:id"), rId)
    h.set("action", "ppaction://hlinksldjump")


def back_arrow(slide, target):
    shp = slide.shapes.add_shape(MSO_SHAPE.LEFT_ARROW, *[Emu(v) for v in BACK_ARROW])
    shp.fill.solid()
    shp.fill.fore_color.rgb = ARROW_BLUE
    shp.line.fill.background()
    shp.click_action.target_slide = target


def hint_box(slide, text):
    """Grey off-slide hint (as in the template): visible only in edit mode."""
    tb, tf = textbox(slide, (13036641, 3737265, 3602173, 3251363))
    tb.fill.solid()
    tb.fill.fore_color.rgb = RGBColor(0xFF, 0xF2, 0xCC)
    p = tf.paragraphs[0]
    style_run(_run(p, text), 16)


# ---------------------------------------------------------------- slide builders

class Builder:
    def __init__(self, spec, base):
        self.spec = spec
        self.base = base
        self.prs = Presentation(TEMPLATE)
        self.history_tabs = spec.get("history_tabs") or self._tabs("history", DEFAULT_HISTORY_TABS)
        self.lab_tabs = spec.get("lab_tabs") or self._tabs("labs", DEFAULT_LAB_TABS)

    def _tabs(self, kind, default):
        used = [s.get("tab") for s in self.spec["slides"] if s.get("type") == kind]
        ordered = [t for t in default if t in used]
        ordered += [t for t in dict.fromkeys(used) if t and t not in ordered]
        return ordered

    def intro_and_title(self):
        s = self.spec
        if not s.get("include_intro", True):
            ids = self.prs.slides._sldIdLst
            for sid in list(ids)[:5]:
                self.prs.part.drop_rel(sid.rId)
                ids.remove(sid)
        title = self.prs.slides[-1]
        sub = [sh for sh in title.placeholders if sh.placeholder_format.idx == 1][0]
        lines = [f"Case {s['case_number']}", s.get("date", ""), s.get("presenters", ""),
                 f"Clinician: {s['clinician']}" if s.get("clinician") else ""]
        tf = sub.text_frame
        paras = tf.paragraphs
        for extra in paras[len(lines):]:
            extra._p.getparent().remove(extra._p)
        for i, text in enumerate(lines):
            if i < len(paras):
                p = paras[i]
                runs = p.runs
                if runs:
                    runs[0].text = text
                    for r in runs[1:]:
                        r._r.getparent().remove(r._r)
                else:
                    _run(p, text)
        set_notes(title, "Please don't use the actual title of the case! It gives away too much info.")

    def timeline(self, d):
        sl = new_slide(self.prs)
        add_logo(sl)
        tb, tf = textbox(sl, (MARGIN, 2600000, BODY_W, 5500000))
        p = tf.paragraphs[0]
        style_run(_run(p, "Timeline:"), 40)
        for i, step in enumerate(TIMELINE, 1):
            p = tf.add_paragraph()
            p.space_before = Pt(24)
            on = i == d.get("active", 1)
            style_run(_run(p, f"{i}. {step}"), 44 if on else 40, bold=on, color=RED if on else BLACK)
        set_notes(sl, d.get("notes"))
        return sl

    def history(self, d):
        sl = new_slide(self.prs)
        add_logo(sl)
        breadcrumb(sl, self.history_tabs, d["tab"])
        centered = d.get("centered", d["tab"] == "CC")
        top = BODY_TOP + 200000
        if d.get("images"):  # e.g. clinical photographs on a PE slide
            if d.get("body"):
                body_box(sl, d["body"], top=top, height=1500000, max_size=28)
                top += 1600000
            place_images(sl, d["images"], (MARGIN, top, BODY_W, SH - top - 300000), self.base)
        else:
            body_box(sl, d.get("body"), top=top, align=PP_ALIGN.CENTER if centered else PP_ALIGN.LEFT,
                     max_size=36)
        set_notes(sl, d.get("notes"))
        return sl

    def labs(self, d):
        rows = (d.get("table") or {}).get("rows", [])
        if len(rows) > 12:  # long panels (e.g. full CMP) are split so the font stays readable
            half = (len(rows) + 1) // 2
            t = d["table"]
            self.labs({**d, "table": {**t, "rows": rows[:half]}, "body": None, "images": None})
            return self.labs({**d, "table": {**t, "rows": rows[half:]}})
        sl = new_slide(self.prs)
        add_logo(sl)
        breadcrumb(sl, self.lab_tabs, d["tab"])
        top = BODY_TOP + 100000
        if d.get("table"):
            t = d["table"]
            h = SH - top - (1800000 if d.get("body") else 500000)
            gf = add_table(sl, t["columns"], t["rows"], (1462575, top, 9876450, h))
            top = top + gf.height + 200000
        if d.get("images"):
            place_images(sl, d["images"], (MARGIN, top, BODY_W, SH - top - 400000), self.base)
        elif d.get("body"):
            body_box(sl, d["body"], top=top, height=SH - top - 300000)
        set_notes(sl, d.get("notes"))
        return sl

    def text(self, d):
        """Generic slide: optional title, body, table, images."""
        sl = new_slide(self.prs)
        if d.get("logo", True):
            add_logo(sl)
        top = 1800000
        if d.get("title"):
            title_box(sl, d["title"], top=top, size=d.get("title_size", 40),
                      color=RED if d.get("title_red") else BLACK, bold=d.get("title_bold", False),
                      align=PP_ALIGN.CENTER if d.get("title_center", True) else PP_ALIGN.LEFT)
            top += 950000
        if d.get("body"):
            avail = SH - top - 400000
            if d.get("table") or d.get("images"):
                # body takes only the height it needs (max 45%), the rest goes to table/images
                items = parse_body(d["body"])
                max_size = min(d.get("max_size", 32), 24)
                cap = int(avail * 0.45)
                size = fit_size(items, BODY_W, cap, tuple(s for s in (24, 22, 20, 18, 16, 14) if s <= max_size))
                need = int(estimate_lines(items, size, BODY_W) * size * 1.3 * 12700) + 150000
                h = min(cap, need)
                body_box(sl, d["body"], top=top, height=h, size=size)
            else:
                h = avail
                body_box(sl, d["body"], top=top, height=h, max_size=d.get("max_size", 32))
            top += h + 100000
        if d.get("table"):
            t = d["table"]
            gf = add_table(sl, t["columns"], t["rows"], (MARGIN + 300000, top, BODY_W - 600000, SH - top - 900000))
            top += gf.height + 150000
        if d.get("images"):
            place_images(sl, d["images"], (MARGIN, top, BODY_W, SH - top - 500000), self.base)
        if d.get("source"):
            tb, tf = textbox(sl, (MARGIN, SH - 500000, BODY_W, 400000))
            style_run(_run(tf.paragraphs[0], d["source"]), 12, italic=True)
        if d.get("hint"):
            hint_box(sl, d["hint"])
        set_notes(sl, d.get("notes"))
        return sl

    def update(self, d):
        return self.text({**d, "logo": d.get("logo", False)})

    def one_liner(self, d):
        sl = new_slide(self.prs)
        add_logo(sl)
        body_box(sl, d["text"], top=2600000, height=5500000, max_size=28)
        set_notes(sl, d.get("notes"))
        return sl

    def blank(self, d=None):
        return new_slide(self.prs)

    def tests(self, d):
        tests = self.spec["tests"]
        overview = new_slide(self.prs)
        tb, tf = textbox(overview, (MARGIN, 2240281, BODY_W, 6600000))
        half = (len(tests) + 1) // 2
        # two columns via two text boxes, mirroring the original decks
        col_boxes = [(MARGIN, 2240281, 5654040, 6600000), (6507480, 2240281, 5654040, 6600000)]
        tb._element.getparent().remove(tb._element)
        cols = []
        for i, box in enumerate(col_boxes):
            _, ctf = textbox(overview, box)
            cols.append(ctf)
        style_run(_run(cols[0].paragraphs[0], "Tests:"), 32)
        style_run(_run(cols[1].paragraphs[0], " "), 32)
        link_runs = []
        for i, t in enumerate(tests):
            ctf = cols[0] if i < half else cols[1]
            p = ctf.add_paragraph()
            p.space_before = Pt(8)
            r = _run(p, t["letter"])
            style_run(r, 32, color=LINK_BLUE, underline=True)
            link_runs.append(r)
        p = cols[1].add_paragraph()
        p.space_before = Pt(20)
        fd_run = _run(p, "Final Diagnosis")
        style_run(fd_run, 32, color=LINK_BLUE, underline=True)
        set_notes(overview, "Click a letter to jump to the test; the blue arrow on each test slide brings you back here.")

        test_slides = []
        for t in tests:
            sl = self.text({"title": f"Test {t['letter']}: {t['name']}", "title_center": False,
                            "title_size": 36, "logo": False, "body": t.get("body"), "table": t.get("table"),
                            "images": t.get("images"), "notes": t.get("notes"), "max_size": 28})
            back_arrow(sl, overview)
            test_slides.append(sl)
            for extra in t.get("extra_slides", []):
                ex = self.text({"title": f"Test {t['letter']}: {t['name']}", "title_center": False,
                                "title_size": 36, "logo": False, **extra})
                back_arrow(ex, overview)
            self.blank()  # buffer so "next" never reveals the following test
        fd = self.final_diagnosis(self.spec["final_diagnosis"])
        for r, sl in zip(link_runs, test_slides):
            add_slide_jump(r, overview, sl)
        add_slide_jump(fd_run, overview, fd)
        self._final_done = True
        return overview

    def final_diagnosis(self, d):
        if getattr(self, "_final_done", False):
            return None
        if isinstance(d, str):
            d = {"diagnosis": d}
        sl = new_slide(self.prs)
        add_logo(sl)
        title_box(sl, "Final Diagnosis", top=2500000, size=56, color=RED, bold=True, align=PP_ALIGN.CENTER)
        tb, tf = textbox(sl, (MARGIN, 4200000, BODY_W, 2600000), anchor=MSO_ANCHOR.TOP)
        for i, line in enumerate(d["diagnosis"].split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.CENTER
            style_run(_run(p, line), 40, bold=True)
        set_notes(sl, d.get("notes"))
        return sl

    def management(self, d):
        sl = new_slide(self.prs)
        add_logo(sl)
        tb, tf = textbox(sl, (MARGIN, 1800000, BODY_W, 700000))
        style_run(_run(tf.paragraphs[0], "Patient Management"), 36, bold=True, underline=True)
        body_box(sl, d["body"], top=2550000, max_size=24)
        set_notes(sl, d.get("notes"))
        return sl

    def differential(self, d):
        sl = new_slide(self.prs)
        add_logo(sl)
        name_size = 48 if len(d["name"]) <= 28 else 40 if len(d["name"]) <= 36 else 32
        title_box(sl, d["name"], top=1750000, size=name_size, bold=True, italic=True, align=PP_ALIGN.CENTER)
        colw = (BODY_W - 800000) // 2
        top = 3000000
        h = SH - top - 400000
        items = [("bullet", 0, x) for x in d.get("pros", []) + d.get("cons", [])]
        size = min(26, fit_size(items, colw, h * 2 // max(1, (len(d.get("pros", [])) > 0) + (len(d.get("cons", [])) > 0))))
        for k, (head, vals) in enumerate((("Pros", d.get("pros", [])), ("Cons", d.get("cons", []) or ["/"]))):
            _, tf = textbox(sl, (MARGIN + 400000 + k * (colw + 200000), top, colw, h))
            style_run(_run(tf.paragraphs[0], head), size, bold=True, italic=True)
            for v in vals:
                p = tf.add_paragraph()
                add_inline_runs(p, v, size, italic=True)
        hint_box(sl, "Include up to three differentials that were discussed in the case or are otherwise important. At the end of a case people don't have the energy for more.")
        set_notes(sl, d.get("notes"))
        return sl

    def teaching_overview(self, d):
        sl = new_slide(self.prs)
        add_logo(sl)
        title_box(sl, "Teaching points", top=2000000, size=56, color=RED, bold=True, align=PP_ALIGN.CENTER)
        tb, tf = textbox(sl, (MARGIN, 3400000, BODY_W, 5000000))
        for i, pt in enumerate(d["points"], 1):
            p = tf.paragraphs[0] if i == 1 else tf.add_paragraph()
            p.space_before = Pt(30)
            style_run(_run(p, f"{i}) {pt}"), 40, bold=True)
        hint_box(sl, "Include up to three teaching points that either came up during the discussion or that you explicitly want to mention at the end. Keep it concise and the more unique, the better.")
        set_notes(sl, d.get("notes"))
        return sl

    def teaching_point(self, d):
        sl = new_slide(self.prs)
        add_logo(sl)
        title_box(sl, "Teaching points", top=1700000, size=48, color=RED, bold=True, align=PP_ALIGN.CENTER, height=700000)
        tb, tf = textbox(sl, (MARGIN, 2450000, BODY_W, 650000))
        style_run(_run(tf.paragraphs[0], d["title"]), 36, bold=True)
        top = 3150000
        has_side = bool(d.get("table") or d.get("images"))
        if d.get("body"):
            if has_side and d.get("layout", "stack") == "side":
                body_box(sl, d["body"], top=top, width=BODY_W // 2 - 100000, height=SH - top - 700000, max_size=24)
                box = (MARGIN + BODY_W // 2 + 100000, top, BODY_W // 2 - 100000, SH - top - 900000)
            else:
                h = (SH - top - 700000) * (0.45 if has_side else 1.0)
                body_box(sl, d["body"], top=top, height=int(h), max_size=26)
                top += int(h) + 100000
                box = (MARGIN, top, BODY_W, SH - top - 700000)
        else:
            box = (MARGIN, top, BODY_W, SH - top - 700000)
        if d.get("table"):
            t = d["table"]
            gf = add_table(sl, t["columns"], t["rows"], box, max_size=18)
            box = (box[0], box[1] + gf.height + 100000, box[2], box[3] - gf.height - 100000)
        if d.get("images") and box[3] > 800000:
            place_images(sl, d["images"], box, self.base)
        if d.get("source"):
            tb, tf = textbox(sl, (MARGIN, SH - 600000, BODY_W, 450000))
            style_run(_run(tf.paragraphs[0], d["source"]), 12, italic=True)
        set_notes(sl, d.get("notes"))
        return sl

    def build(self, out):
        self.intro_and_title()
        handlers = {
            "timeline": self.timeline, "history": self.history, "labs": self.labs, "update": self.update,
            "one_liner": self.one_liner, "text": self.text, "tests": self.tests, "blank": self.blank,
            "final_diagnosis": self.final_diagnosis, "management": self.management,
            "differential": self.differential, "teaching_overview": self.teaching_overview,
            "teaching_point": self.teaching_point,
        }
        for d in self.spec["slides"]:
            handlers[d["type"]](d)
        self.prs.save(out)
        print(f"Saved {out} ({len(self.prs.slides)} slides)")


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    spec_path, out = sys.argv[1], sys.argv[2]
    with open(spec_path) as f:
        spec = json.load(f)
    Builder(spec, os.path.dirname(os.path.abspath(spec_path))).build(out)


if __name__ == "__main__":
    main()
