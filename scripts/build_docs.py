#!/usr/bin/env python3
"""Build the companion Word documents for a CCD case from the same case JSON.

Usage: python build_docs.py case.json outdir

Writes (if the JSON has the matching keys):
  outdir/Problems List <case>.docx          blank table for participants
  outdir/Problems List <case> filled.docx   filled table for the moderator
  outdir/Mod Leitfaden <case>.docx          moderator guide
"""
import json
import os
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt


def problems_doc(spec, filled):
    doc = Document()
    h = doc.add_heading(f"Case {spec['case_number']} – Problems List", level=1)
    rows = spec["problems_list"]
    cols = ["Problems", "Differentials", "Tests"]
    t = doc.add_table(rows=1, cols=3)
    t.style = "Table Grid"
    for i, c in enumerate(cols):
        cell = t.rows[0].cells[i]
        cell.text = c.upper()
        cell.paragraphs[0].runs[0].bold = True
    for r in rows:
        cells = t.add_row().cells
        if filled:
            cells[0].text = "\n".join(r.get("problems", []))
            cells[1].text = "\n".join(r.get("differentials", []))
            cells[2].text = "\n".join(r.get("tests", []))
        else:
            for c in cells:
                c.text = "\n\n\n"
    if filled and spec.get("rule_out_first"):
        doc.add_paragraph()
        p = doc.add_paragraph()
        p.add_run("Rule out first: ").bold = True
        p.add_run(", ".join(spec["rule_out_first"]))
    return doc


def guide_doc(spec):
    g = spec["moderator_guide"]
    doc = Document()
    doc.add_heading(f"Moderatorenleitfaden – Case {spec['case_number']}", level=1)
    p = doc.add_paragraph()
    p.add_run("Final diagnosis: ").bold = True
    fd = spec["final_diagnosis"]
    p.add_run(fd if isinstance(fd, str) else fd["diagnosis"].replace("\n", " "))
    doc.add_heading("Tests", level=2)
    for t in spec.get("tests", []):
        doc.add_paragraph(f"{t['letter']}: {t['name']} – {t.get('summary', '')}".rstrip(" –"), style="List Bullet")
    for sec in g["sections"]:
        doc.add_heading(sec["heading"], level=2)
        for fact in sec.get("facts", []):
            doc.add_paragraph(fact, style="List Bullet")
        for q in sec.get("questions", []):
            para = doc.add_paragraph(style="List Bullet 2")
            para.add_run("Q: ").bold = True
            para.add_run(q.get("q", q) if isinstance(q, dict) else q)
            if isinstance(q, dict) and q.get("a"):
                para.add_run("  → " + q["a"]).italic = True
    if g.get("one_liner"):
        doc.add_heading("Model assessment (one-liner)", level=2)
        doc.add_paragraph(g["one_liner"])
    if g.get("background"):
        doc.add_heading("Background / scores", level=2)
        for b in g["background"]:
            doc.add_paragraph(b, style="List Bullet")
    return doc


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    n = spec["case_number"]
    if spec.get("problems_list"):
        problems_doc(spec, False).save(os.path.join(out, f"Problems List {n}.docx"))
        problems_doc(spec, True).save(os.path.join(out, f"Problems List {n} filled.docx"))
    if spec.get("moderator_guide"):
        guide_doc(spec).save(os.path.join(out, f"Mod Leitfaden {n}.docx"))
    print("Docs written to", out)


if __name__ == "__main__":
    main()
