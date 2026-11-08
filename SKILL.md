---
name: create-ccd-pptx
description: Turn an NEJM Case Record (Case Records of the Massachusetts General Hospital, "Case N-YYYY" PDF) into a Clinical Case Discussion (CCD) PowerPoint for medical students in the exact LMU CCD house format (intro slides, CC>HPI>…>PE history, admission labs, hyperlinked test menu, final diagnosis, differentials, teaching points), plus the moderator guide and problems list. Use when the user gives an NEJM case PDF/case number and asks for a CCD, case presentation, case discussion deck or Fallpräsentation.
---

# Create a CCD presentation from an NEJM Case Record

Skill folder: `~/.claude/skills/create-ccd-pptx` (written `$K` below).
Python with all dependencies: `$K/.venv/bin/python`. If it is missing, create it:
`python3 -m venv $K/.venv && $K/.venv/bin/python -m pip install -r $K/requirements.txt`.

**Read `$K/reference/conventions.md` first.** It is the house style learned from ~45 past decks (kept locally in `$K/Cases/`, not part of the repo), and following it is the whole point of this skill. The JSON input format is in `$K/reference/case_schema.md`.

## Inputs

- **NEJM case PDF** (required). NEJM is paywalled, so don't try to fetch it. Ask the user to download it via their institutional access and give the path. If they only give a case number, ask for the PDF.
- **Session date, presenter names, clinician** (optional). Use "TBD" if they aren't given, and mention it at the end.
- **Output folder**: `<N-YYYY>/` next to the PDF.
  - **Path trap:** folder names on macOS (e.g. localized or synced folders like `Dokumente – …`) can contain a **non-breaking space** (U+00A0). If you retype such a path by hand (Write/Edit tools, prompts to subagents), you silently create a look-alike folder.
  - Resolve paths in the shell from the PDF location, e.g. `O="$(dirname "$PDF")/N-YYYY"`, or with a glob.
  - Write `case.json` through the shell into `$O/_work`, e.g. with a heredoc, or Write it to a scratch location and `cp` it in.
  - Before reporting, check that no duplicate look-alike folder was created.

## Workflow

1. **Extract**
   `$K/.venv/bin/python $K/scripts/extract_nejm.py <case.pdf> <outdir>/_work`
   This gives `case.txt`, the embedded `figures/*.png` and `pages/page_N.png`.

2. **Read the whole case.**
   - Read `case.txt` fully: presentation, Table 1, discussion, pathological discussion, final diagnosis, management, follow-up.
   - Look at every figure image and identify which panel is which (imaging, smear, histology).
   - For figures, crop panels from the 250-dpi `pages/page_N.png` with
     `extract_nejm.py --crop page_N.png l,t,r,b out.png`. Embedded images lose NEJM's arrows and panel letters and are sometimes tiled. Exclude the NEJM legend text from the crop.

3. **Plan before writing.** Decide each of these and keep it in mind for step 4:
   - What is admission data and what is held back as an orderable test. Scrub any spoilers from the history.
   - **10–13 tests**: NEJM results, discussant-mentioned tests and 1–3 plausible normal distractors. Basic → specialised → imaging → decisive test last.
   - Up to 3 differentials plus "Diagnosis: X".
   - Up to 3 teaching points relevant to medical students: one score or algorithm, one mechanism, one clinical pearl or German context.

4. **Write `<outdir>/_work/case.json`** following the schema, in this order:
   - timeline(1)
   - CC, HPI…PE
   - labs
   - updates
   - timeline(2) → one_liner
   - timeline(3) → timeline(4)
   - tests
   - management
   - differentials
   - teaching_overview → teaching points

   Also fill `problems_list` and `moderator_guide`. Add speaker `notes` with moderator prompts on history, labs and tests. **Copy every lab value and reference range from the PDF and double-check it.** Never invent results or citations.

5. **Build**
   ```
   $K/.venv/bin/python $K/scripts/build_ccd.py <outdir>/_work/case.json "<outdir>/Case N-YYYY.pptx"
   $K/.venv/bin/python $K/scripts/build_docs.py <outdir>/_work/case.json <outdir>
   ```

6. **Visual QA** (needs Microsoft PowerPoint on macOS; skip and say so if it is unavailable):
   `$K/.venv/bin/python $K/scripts/render_check.py "<outdir>/Case N-YYYY.pptx" <outdir>/_work/render`
   - Look at **every** `sheet_*.png`. There are 16 slides per sheet, usually 4–5 sheets.
   - Fix overflowing text by splitting the slide or shortening bullets, then fix bad image sizes and empty slides. Blank buffer slides after tests and the empty Problems list / DD timeline slides are intentional.
   - Rebuild until the deck is clean.

7. **Report back** briefly:
   - The file paths.
   - Slide count.
   - The test list (A–M with a one-word result).
   - The final diagnosis, differentials and teaching points.
   - Anything assumed or not reported in NEJM.
   - Any "TBD" fields.

   Don't paste the deck content.

## Rules that matter most

- **No spoilers.** Keep the NEJM title, diagnosis words and decisive results out of the title slide, history, one-liner and test names.
- Write fragments with CCD abbreviations (y/o, p/w, pta, DoA, h/o, NKA…), keep numbers exact and use NEJM units.
- Max 3 differentials, max 3 teaching points, no placeholder tests.
- The deck is in English. The moderator guide may mix German and English, like the originals.
- Teaching points are for **medical students** (clinical semesters). Focus on reasoning, high-yield mechanisms and scores, not subspecialty minutiae.
