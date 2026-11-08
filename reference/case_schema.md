# case.json schema (input for scripts/build_ccd.py and scripts/build_docs.py)

Image paths are relative to the JSON file.

## Body text mini-markup (all `body` fields)

A string with `\n` line breaks, or a list of lines:

| line | result |
|---|---|
| `- text` | bullet, level 0 |
| `  - text` | bullet, level 1 (2 spaces per level) |
| `text` | paragraph without bullet |
| `""` | spacer line |
| `**bold**`, `*italic*` | inline formatting |

Font size is auto-fitted, but keep each slide short. About 8 bullets is the comfortable maximum.

## Top level

```json
{
  "case_number": "9-2026",
  "date": "13.05.2026",
  "presenters": "Ata & Elisa",
  "clinician": "Prof. X",
  "include_intro": true,
  "history_tabs": null,
  "lab_tabs": null,
  "slides": [ ... ],
  "tests": [ ... ],
  "final_diagnosis": {"diagnosis": "Line 1\nLine 2", "notes": "..."},
  "problems_list": [ ... ],
  "rule_out_first": ["..."],
  "moderator_guide": { ... }
}
```

- `history_tabs` / `lab_tabs`: leave them null. They are derived from the `tab` values used, in canonical order.
- Use the placeholders "TBD" for `date`, `presenters` or `clinician` if the user didn't give them.

## Slide types (`slides` array, in order)

```json
{"type": "timeline", "active": 1}
{"type": "history", "tab": "CC", "body": "A 12 y/o girl was brought to the ED b/c of ...", "notes": "..."}
{"type": "history", "tab": "HPI", "body": "**1y pta:**\n  - 4 kg weight loss during intense running\n**Recently:**\n  - early satiety", "notes": "Ask: ..."}
{"type": "history", "tab": "VS", "body": "- T: 37.0 °C\n- BP: 121/61 mmHg"}
{"type": "history", "tab": "PE", "body": "- short caption line", "images": [{"path": "img/rash.png", "caption": "..."}]}
{"type": "labs", "tab": "CMP", "table": {"columns": ["Parameter", "On admission", "Reference Range"],
   "rows": [["Sodium (mmol/l)", "140", "135–145"], ["Glucose (mg/dl)", "!30", "70–110"]]}}
{"type": "labs", "tab": "CXR", "body": "- Not performed"}
{"type": "labs", "tab": "ECG", "images": [{"path": "fig/ecg.png", "caption": "Sinus rhythm"}]}
{"type": "update", "title": "Update (1/2)", "body": "...", "table": {...}}
{"type": "one_liner", "text": "A previously healthy ..."}
{"type": "tests"}
{"type": "management", "body": "- ...", "notes": "..."}
{"type": "differential", "name": "Insulinoma", "pros": ["..."], "cons": ["..."], "notes": "..."}
{"type": "differential", "name": "Diagnosis: ...", "pros": ["..."], "cons": []}
{"type": "teaching_overview", "points": ["Critical sample in hypoglycemia", "IGF-2-mediated (non-islet cell tumor) hypoglycemia"]}
{"type": "teaching_point", "title": "1) Critical sample", "body": "- ...", "table": {...},
   "images": [{"path": "...", "caption": "..."}], "layout": "stack|side", "source": "Citation", "notes": "long explanation"}
{"type": "text", "title": "Anything else", "body": "...", "images": [...], "table": {...}, "source": "..."}
{"type": "blank"}
```

- `{"type": "tests"}` produces the hyperlinked menu, every test slide with its back arrow and blank buffer slide, **and the Final Diagnosis slide**. Do not add a separate `final_diagnosis` slide.
- In tables, a value starting with `!` is rendered bold (use it for abnormal values).
- `notes` is accepted on every slide type and becomes the speaker notes.

## tests

```json
{"letter": "A", "name": "Hemolysis parameters", "summary": "LDH, haptoglobin – normal",
 "table": {"columns": ["Parameter", "In this hospital", "Reference Range"], "rows": [["LDH (U/l)", "!1495", "110–210"]]},
 "body": "- optional text result", "images": [{"path": "fig/p6_i1.png", "caption": "Panel A: ..."}],
 "extra_slides": [{"body": "...", "images": [...]}],
 "notes": "What it shows + question for the group"}
```

`summary` appears only in the moderator guide.

## problems_list (for the docx)

```json
[{"problems": ["Hypoglycemia despite IV dextrose", "suppressed ketones"],
  "differentials": ["Insulin-mediated: insulinoma, factitious, congenital HI", "Non-insulin: IGF-2 (NICTH), ..."],
  "tests": ["Critical sample: insulin, C-peptide, BHB, proinsulin", "Sulfonylurea screen", "IGF-1/IGF-2"]}]
```

## moderator_guide (for the docx; German/English mix is fine)

```json
{"sections": [
   {"heading": "CC", "facts": ["..."], "questions": [{"q": "What can cause altered mental status in a 12 y/o?", "a": "AEIOU TIPS ..."}]},
   {"heading": "HPI", "facts": [], "questions": []}],
 "one_liner": "...",
 "background": ["Whipple's triad: ...", "..."]}
```
