# CCD house style (derived from ~45 past decks in ../Cases)

These are curricular Clinical Case Discussions (LMU, Munich): German medical
students practise clinical reasoning **in English** on NEJM Case Records
(Massachusetts General Hospital CPCs). The deck is a *game*: students get the
history piece by piece, build a one-liner, problems list and differential,
then **order tests** from a hyperlinked menu until they reach the diagnosis.
Everything that would give the answer away is held back.

Gold-standard decks to imitate (open them if in doubt; only available if the local `Cases/` folder exists):
`Cases/34-2023_Acquired TTP/Case 34-2023.pptx` (structure and look),
`Cases/06-2024_Pancytopenia/Case 6-2024.pptx` (test selection, one-liner),
`Cases/18-2025_Erdheim_Chester/18-2025 last version .pptx` (moderator prompts in speaker notes).

## Slide sequence

1. 5 intro slides (What is CCD / session structure / roles / rules / "So…"): come from the template automatically.
2. **Title**: `Case N-YYYY / date / presenters / Clinician: …`. **Never the NEJM title** (it gives the diagnosis away).
3. **Timeline** slide with "1. Admission note" highlighted.
4. **History**, with breadcrumb `CC > HPI > PMH > ME > ALL > SH > FH > ROS > VS > PE` (the current tab is red; only tabs that are present are shown).
   - **CC**: 1 slide, one centred sentence ("A 49 y/o woman was found unconscious at work around 4:30 pm on the DoA.").
   - **HPI**: 2–8 slides in chronological order. Each starts with a **bold time anchor** (`**4w pta:**`, `**DoA, 2 p.m.:**`, `**O/A:**`), followed by short fragment bullets. Vitals, labs or imaging from an *outside hospital* go into the HPI as their own slides or tables.
   - **PMH, ME, ALL, SH, FH, ROS, VS, PE**: usually 1 slide each. Use "None" / "NKA" / "Could not be obtained" when that is the case.
     - ROS: "(-) fever, night sweats, …" or "No …".
     - VS: `T: 37.0 °C / BP: 121/61 mmHg / HR: 89 bpm / RR: 19/min / SpO2: 97% (AA) / BMI: 18.7`.
     - PE: system prefixes `**General:** / **HEENT:** / **Resp:** / **CV:** / **Abd:** / **Ext:** / **Skin:** / **Neuro:**`.
5. **Admission labs**, with breadcrumb `CMP > CBC > PT, PTT > UA > ECG > CXR` (only what exists; use "Not performed" when NEJM says it wasn't done).
6. Optional **Update (1/n)** slides: events or labs during the first hours. Repeat labs get an added column.
7. **Timeline** "2. Assessment", then the **one-liner** slide.
8. **Timeline** "3. Problems list", then **Timeline** "4. DD". These are worked out live on the whiteboard; the slides stay empty.
9. **Tests** menu (letters A…M in two columns plus "Final Diagnosis", all hyperlinked). Each test slide has a blue back arrow, and a **blank buffer slide follows every test**. The builder does all of this.
10. **Final Diagnosis** (red title, diagnosis in bold).
11. **Patient Management**: treatment and follow-up from NEJM, condensed to bullets.
12. **Differentials**: up to **3** slides, each with Pros/Cons, plus a last one "Diagnosis: X" with pros only (cons "/").
13. **Teaching points**: an index slide "1) … 2) …", then 1–2 slides per point. **Maximum 3 points.**

## Writing style

- **Fragments, not prose.** 3–10 words per bullet. Keep numbers, timings and the patient's own words ("felt warm").
- **Abbreviations to use:** y/o, p/w, pta, DoA (day of admission), O/A, h/o, w/h/o, w/, w/o, b/c, s/p, NKA, AA (ambient air), pt./pat., sx, tx, dx, ED, PCP, SOB, DOE, N/V.
- **Time units:** `4w pta`, `2m pta`, `1y pta`, `3d pta`.
- **English for medical students** with plain clinical wording. Put a short glossary of unusual terms in the speaker notes.
- **Decimal point** (12.5), not a comma. **Units** as in NEJM (US conventional). Put SI in brackets only if NEJM gives it. Never convert units yourself. Copy reference ranges exactly from NEJM Table 1.

## Admission labs vs orderable tests (the most important judgement call)

**Admission panel** (shown before the DD; only what NEJM reports at presentation):
- **CMP:** Sodium, Potassium, Chloride, Carbon dioxide, Glucose, Urea nitrogen, Creatinine, (GFR), Calcium, Total protein, Albumin, AP, AST, ALT, Bilirubin (total/direct).
- **CBC:** Hemoglobin, Hematocrit, MCV, Platelets, WBC with differential.
- **Coagulation:** PT, INR, PTT.
- **UA:** dipstick and sediment.
- **ECG** and **CXR** as report text (or the NEJM image).

Other routine chemistry NEJM lists with the panel (globulin, uric acid, magnesium, phosphate) may stay in the CMP. Panels longer than 12 rows are split over two slides automatically.

**Everything else is held back as a test** the students must order: LDH, haptoglobin, reticulocytes, CRP/ESR, troponin, BNP, D-dimer, fibrinogen, lactate, ferritin/iron, lipase, TSH, B12/folate, hormones (cortisol, insulin, C-peptide…), serologies, cultures, blood smear, all imaging beyond CXR, biopsies and genetics.

Also remove from the history any sentence that *reveals* a held-back result. NEJM often reports CT, DAT or smear results in the presentation. Move them into tests.

Glucose stays in the CMP even if it is the key abnormality. Imaging done in the ED that NEJM reports in the presentation (e.g. head CT) also becomes a test.

Bold (`!`) only abnormal values, plus a normal value that is a key clue (e.g. negative urine ketones in hypoglycemia). Hormone levels drawn during a critical sample become tests.

## Tests

- **10–13 tests** (A–M). Fewer if the case is thin, never more than 14. **No placeholder tests.**
- **Sources:**
  1. Every investigation reported in the NEJM case (text, Table 1, figures).
  2. Tests the discussant mentions as having been done.
  3. Tests that rule out the main differentials, including **1–3 normal or negative "distractor" tests** a student would plausibly order (TSH, tox screen, hCG, ethanol, HIV, cultures). Only use results that NEJM states. If you must assume a result, write "(not reported in NEJM – assumed normal)" in the speaker notes and tell the user.
- **Order:** basic labs → specialised labs and serology → imaging → biopsy, pathology or genetics. The **decisive test comes late** (last or second to last), and the menu letter must not hint at it.
- **Naming:** `Test A: Hemolysis parameters`. Use neutral names: "Abdominal CT", not "CT showing ovarian mass".
- **Lab tests:** table `Parameter | In this hospital | Reference Range`. Prefix abnormal values with "!" to make them bold.
- **Imaging and pathology:** crop the panels from the 250-dpi page renders (they keep NEJM's arrows and panel letters) rather than using the embedded images. Show the NEJM figure panels with a condensed legend (Panel A: …, arrows). Long figures go over several slides (`extra_slides`).
- **Speaker notes** on every test: what it shows and why it matters (from the NEJM discussion), plus a question to ask the group.

## One-liner (assessment)

2–5 sentences, as if presenting to an attending: "A previously healthy 12 y/o girl p/w acute altered mental status and hypothermia, found to have persistent hypoglycemia despite IV dextrose. Exam notable for abdominal distention with a pelvic mass-like fullness. Additional h/o 4 kg weight loss and early satiety. Labs: …". Use only facts the students have seen at this point, never test results.

## Differentials

- Keep each differential name short (≤ 30 characters, e.g. "Diagnosis: NICTH") so it fits on one line.
- Up to 3, chosen from what the NEJM discussant considered, prioritising the ones students will raise.
- 3–6 **case-specific** pros and cons each, citing patient facts and test results ("Undetectable C-peptide → argues against insulinoma").
- The last differential slide is **"Diagnosis: <final dx>"** with pros, cons "/".

## Teaching points (max 3; concise and as unique as possible)

Mix these types:
1. **A score, criteria set or diagnostic algorithm** applied to the patient (PLASMIC score with X/? per criterion; Whipple's triad; Duke criteria; H-score; "critical sample" interpretation table).
2. **Pathophysiology or mechanism** that explains the case (ADAMTS13 and vWF; IGF-2-mediated hypoglycemia; heme synthesis in lead poisoning).
3. **A disease-specific clinical pearl or epidemiology point**, including a German or European angle when relevant (vaccination recommendation, notifiable disease, AWMF/S3 guideline, availability of a test in Germany).

Each teaching-point slide has a short title, 3–6 bullets, ideally a table or a figure, a **source line** (journal or guideline; NEJM figure "Adapted from N Engl J Med …"), and the longer explanation in the **speaker notes**. Never invent citations. Cite the NEJM case itself or sources you have verified.

## Speaker notes = moderator prompts

On history and lab slides, put 1–3 Socratic prompts with expected answers: "Ask: What can cause hypoglycemia + altered mental status? → think insulin-mediated vs not", "Why does dextrose need to be continuous? → increased glucose use". The moderator reads these live.

## Quality pitfalls seen in older decks (avoid)

- Transcription errors in labs (e.g. "bilirubin" written where NEJM says urobilinogen). **Re-check every value against the PDF.**
- Lost findings in imaging legends (e.g. splenomegaly omitted).
- Mixed thousands separators. Use "150,000–400,000" consistently.
- More than 3 differentials or teaching points.
- Leftover placeholder tests ("Test J: dsf").
- The NEJM title or the diagnosis leaking into slide titles, file names shown to students, or test names.
