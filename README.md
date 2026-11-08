# create-ccd-pptx

A [Claude Code](https://claude.com/claude-code) skill that turns an NEJM *Case Record of the Massachusetts General Hospital* (PDF) into a **Clinical Case Discussion (CCD)** deck for medical students. It follows the house format of the LMU curricular CCDs:

- intro slides, title slide (no spoiler title), timeline
- history with `CC > HPI > PMH > ME > ALL > SH > FH > ROS > VS > PE` navigation
- admission labs (`CMP > CBC > PT, PTT > UA > ECG > CXR`), updates, one-liner assessment
- hyperlinked **test menu** (A–M) with back arrows and blank buffer slides
- final diagnosis, patient management, Pros/Cons differentials, teaching points
- moderator prompts in the speaker notes

It also generates the companion Word files: the moderator guide (*Mod Leitfaden*) and the problems list (blank and filled).

## Install

```bash
git clone <this repo> ~/.claude/skills/create-ccd-pptx
cd ~/.claude/skills/create-ccd-pptx
python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt
```

Restart Claude Code. The skill is then available as `/create-ccd-pptx`.

## Use

Download the case PDF from NEJM yourself (it is paywalled), then in Claude Code:

```
/create-ccd-pptx ~/Downloads/NEJMcpc....pdf, date 12.11.2026, presenters A & B, clinician Prof. X
```

Output goes to a `<N-YYYY>/` folder next to the PDF:
- `Case N-YYYY.pptx`
- `Mod Leitfaden N-YYYY.docx`
- `Problems List N-YYYY.docx` and `Problems List N-YYYY filled.docx`

The intermediate `case.json`, extracted figures and render previews go in `_work/` inside that folder.

## Layout

| Path | Purpose |
|---|---|
| `SKILL.md` | Workflow Claude follows |
| `reference/conventions.md` | CCD house style (derived from ~45 past decks) |
| `reference/case_schema.md` | `case.json` format consumed by the scripts |
| `scripts/extract_nejm.py` | PDF → text, figures, 250-dpi page renders, `--crop` helper |
| `scripts/build_ccd.py` | `case.json` → `.pptx` (template, hyperlinks, tables, images) |
| `scripts/build_docs.py` | `case.json` → moderator guide + problems lists (`.docx`) |
| `scripts/render_check.py` | Renders the deck via PowerPoint (macOS) into contact sheets for visual QA |
| `assets/template.pptx`, `assets/ccd_logo.jpg` | CCD slide master, intro slides and logo |

## Notes

- **Not included:** the past-case corpus (`Cases/`), because NEJM PDFs are copyrighted and the decks contain participants' names. Put it locally into `Cases/` if you want Claude to consult the original decks. It is git-ignored.
- **Visual QA** needs Microsoft PowerPoint on macOS. Without it, the deck still builds.
- **Teaching points** can be combined with a research skill, e.g. "…and research the teaching points with deep-research".
