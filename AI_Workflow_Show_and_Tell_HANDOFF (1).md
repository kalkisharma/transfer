# AI Workflow Automation Show-and-Tell — Complete Project Handoff

**Status:** 12-slide PowerPoint deck has undergone a professional content and visual refinement. The revised deck and a companion speaker-notes PDF exist. Demonstrations on slides 9–11 are still placeholders awaiting program-approved content.

**Date of this handoff:** November 11, 2026.

## 1. What you are being asked to do

You are taking over an existing PowerPoint presentation project. Treat **`AI_Workflow_Show_and_Tell_Refined.pptx` as the current working master**. The presenter wants a polished, welcoming, technically sound presentation on practical AI workflow automation for a broad engineering audience. Continue refining the existing slides and eventually replace the three demonstration placeholders with real, authorized material. **Do not redesign from scratch or change the overall slide count without a specific reason or request.** Preserve the editable PowerPoint objects, visual identity, and speaker notes. Read all slides and speaker notes before making content changes.

## 2. Presenter, audience, and purpose

- Presenter: Kalki Sharma, senior aerospace engineer working in computational aerodynamics/CFD at Lockheed Martin. The slide byline currently reads **“Kalki Sharma · Computational Aerodynamics.”** The professional specialty is appropriate as a byline, but the presentation must **not frame itself as only for “Aerosciences” or “aerospace sciences.”**
- Audience: approximately 40 engineers in an internal, cross-disciplinary technical group (examples include aerodynamics, thermal, propulsion, dynamics, space, AI/ML, test, design, analysis, and software). Assume varied familiarity with AI; many are AI beginners but technically trained.
- Event: monthly, informal **“AI Workflow Automation Show-and-Tell”** series.
- Main goal: lower the barrier to using AI/agents in ordinary engineering workflows, show that small automations are worthwhile, encourage safe and verifiable use, and motivate attendees to present their own workflows at upcoming sessions.
- Desired tone: conversational, light and fun, encouraging but not promotional; credible and technically careful; **visual-first and minimal slide text, one main idea per slide.** Speaker notes can carry more detail.
- Keep the narrative practical: **why this matters → what an agent is and why context matters → two reusable automation patterns → habits and verification → demonstrations → invitation to participate.**

## 3. Files and source-of-truth hierarchy

**Highest priority/current:**
1. `AI_Workflow_Show_and_Tell_Refined.pptx` — editable 12-slide current deck, 16:9, with updated notes on every slide.
2. `AI_Workflow_Show_and_Tell_Refined_with_notes.pdf` — one rendered slide with readable notes per letter-size page; useful for reviewing the on-screen output and rehearsing on a phone.

**Reference/reproducibility:**
3. `AI_Workflow_Show_and_Tell.pptx` — original pre-refinement deck. Do not mistakenly overwrite the refined version with this source.
4. `refine_deck.py` — Python script that reads the ORIGINAL `.pptx` and emits the REFINED `.pptx`, replacing slide copy and speaker notes in place while preserving the original vector layouts and icons. It uses hard-coded `/mnt/data` paths, which must be changed if running in another environment. It was not used to rebuild the deck from scratch.
5. `build_deck.py` — original full-deck generator shared as source code in the conversation, **not necessarily included as a separate file in this package**. Uses `python-pptx` and `lxml` to create all layouts, icons, footer, and speaker notes. Running the unmodified original generator would recreate the **pre-refinement** version, so port copy and notes changes into it before treating it as a reproducible current master.
6. `icons.js` — original Node helper shared as source code in the conversation, **not necessarily included as a separate file in this package**. Renders Font Awesome 6 React icons to transparent PNG files, typically invoked by `build_deck.py` when an icon asset is missing.
7. `AI_Workflow_Show_and_Tell_with_notes(1).pdf` — original pre-refinement slide/notes reference.

Important distinction: The **current PowerPoint is the editable working master**; `refine_deck.py` is a reproducible set of edits to the original PowerPoint. `build_deck.py` has NOT been synchronized with these edits. If long-term generator-driven maintenance is desired, reconcile the generator with the revised deck first.

## 4. Visual identity and implementation constraints

- Aspect ratio: **16:9**, slide size **13.333 × 7.5 inches**.
- Flat, modern engineering look: dark navy title and closing slides; dark indigo conceptual emphasis slide; white backgrounds on ordinary content slides.
- Palette (hex):
  - Navy background `#0E1A3A`
  - Indigo primary `#1C2E6B`
  - Indigo card on dark `#2A3F80`
  - Orange accent `#FF7A30`
  - Teal verification/checks `#1FB5A8`
  - Light card fill `#EEF2FB`
  - Placeholder fill `#F7F9FD`
  - Dark text `#16213E`
  - Muted text `#5A6684`
  - Muted text on dark `#AEB8D6`
  - White `#FFFFFF`
- Typography: **Calibri** throughout; **Courier New** for short code/prompt snippets. Typical content slide title **36 pt bold**; subtitle **18 pt**; smaller supporting copy inside cards.
- Design motif: white/light cards with rounded corners; icons in solid circles; simple chevrons and connecting lines; no shadows, decorative rules, or clutter.
- Most content slides: top-left heading, optionally one-line subtitle, discrete flat diagram or 3–4 cards, footer “AI Workflow Automation Show-and-Tell” and slide number `n / 12`.
- Slide 1 and 12 dark navy; slide 3 indigo; remaining content slides predominantly white.
- Slide 1 includes an orange central AI robot hub linked to six discipline icons. This may remain as a nod to the varied audience, but do not use the label “Aerosciences” again; the refined title chip reads **“MONTHLY SHOW-AND-TELL · ENGINEERING.”**
- For live presentations, prioritize readability from the back of a room and fit without truncation. Preserve notes and editable shapes rather than flattening slides into images.

## 5. Current refined slides (as of this handoff)

### Slide 1 — Opening
- Title: **Automating Your Engineering Workflow with AI**.
- Chip now says **MONTHLY SHOW-AND-TELL · ENGINEERING**.
- Tagline: **One workflow at a time. No experts required.**
- Byline: **Kalki Sharma · Computational Aerodynamics**.
- Visual: central orange robot connected to six engineering/AI discipline icons.
- Role: warmly introduce an informal monthly series for engineering workflow automation, not a specialized aerospace sciences lecture.

### Slide 2 — Why this series?
- Three-card story: **The tools are here → Where do you start? → You could present next**.
- Added beginner-friendly definition above cards: **“An agent is an AI assistant that can work through steps using the files and tools it can access.”**
- End line: **Any workflow. Any size. Any discipline.**
- Role: make the series feel accessible and invite future participation.

### Slide 3 — Context is key
- Main assertion refined to **Good context reduces guesswork** (not an absolute guarantee).
- Thin-context prompt: **“Make me a plot.”** This leaves input data, units, and format ambiguous.
- Rich-context prompt: **“Plot force vs. time from test_042.csv (s, N). Match example.png.”**
- Takeaway: specific data and output instructions improve the result, **but still verify**.
- Visual: two side-by-side indigo panels with contrasting outcomes.

### Slide 4 — Four sources of context
- Refined title/subtitle: **Four sources of context / Give the agent the context it needs for this task**.
- Sources: **Task request**, **Context files**, **Reference docs**, **Working files**.
- Examples: constraints and success criteria; `AGENTS.md` or reusable instructions; specs and approved examples; measurements, inputs, results, and models.
- Bottom agent bar says it **uses the context and tools it can access**.
- Important nuance: not all four sources are mandatory for every task; file access and tool permissions determine what can actually be read.

### Slide 5 — Pattern 1: Prompt chaining
- Subtitle: **Build a repeatable chain, with checks at each handoff**.
- Example chain: **Test report → Extract data → Prepare inputs → Run analysis → Summary**.
- Teal check at each handoff; checks might be code, tests, or a person. On failure, correct it before proceeding.
- Role: explain **sequential dependent steps** with verification gates. Do not imply every run or check is automatically guaranteed to succeed.

### Slide 6 — Pattern 2: Orchestrator–workers
- Subtitle: **A coordinator assigns focused jobs, then combines the results**.
- Worker jobs: run status (analyses passed/failed), test data (new measurements vs model), action items (meeting notes), and schedule (review dates/deadlines).
- All feed an orchestrator, which produces a weekly report (“One page, every Friday”).
- Role: contrast **parallel or separable focused jobs** with the dependency chain on slide 5. A worker could be a separate agent, script, or tool call; multi-agent arrangements are not automatically best.

### Slide 7 — Three practical habits
- Reframed from rigid “rules” into habits:
  1. **Show a good example** — use an approved output as a target.
  2. **Reference the right files** — give permitted access to actual relevant files, e.g., `docs/test_plan.md`.
  3. **Start with one small chain** — get `Report → table → check` working before expanding.
- Role: give attendees immediately usable advice without overcomplicating prompt engineering.

### Slide 8 — How do we know it’s right?
- Subtitle: **Speed is useful; verification is still an engineering responsibility**.
- Left panel: **Fast and capable doesn't mean verified. You still own the engineering judgment.**
- Three specific checks: **Review** assumptions, units, and sources; **Spot-check** at least one critical result independently; **Compare to trusted data** such as a test, baseline, or known case.
- Role: reinforce discipline-appropriate quality and verification, not blind trust in AI output.

### Slide 9 — Demo 1: Getting started
- Subtitle: **Setup hub + embedded chatbot**.
- Still contains an orange **PLACEHOLDER** tag and dashed insertion area.
- Planned demonstration: where to find the hub and what it configures, asking its embedded chatbot a real setup question, inspecting the answer, and showing one step attendees could try afterward.
- Do not invent hub UI or links. Use an actual approved screenshot or a live view when supplied.

### Slide 10 — Demo 2: An engineering workflow
- Subtitle: **Before → automated steps → reviewed result**.
- Still a **PLACEHOLDER**.
- Show an approved internal program workflow: the tedious or error-prone “before,” automated steps, a clear verification checkpoint, and an improved outcome.
- Tie back to either chaining or orchestrator–workers without unnecessary jargon.
- Quantify time savings only if actually measured. Never invent program metrics or show sensitive data not cleared for the attendees.

### Slide 11 — Demo 3: RCAS end to end
- Subtitle: **Input → checks → reviewed output**.
- Still a **PLACEHOLDER**.
- Intention: demo a real RCAS-related workflow, show inputs and outputs, identify a verification gate, and demonstrate how a failed check is handled.
- The original deck called this an “RCAS live run” and anticipated input-deck → run → report. **Confirm what the actual RCAS/Hangar demo can safely and accurately perform before changing the slide**, since live parsing/deck inspection and executing an analysis are not necessarily the same thing.
- Prepare a recording as a backup to the live demo; use only approved material.

### Slide 12 — Close
- Headline: **You're the expert on your own work**.
- Three invitations: **Start small. Have fun.** / **Share your workflow next** / **Want a hand?**
- Small improvements count; attendees can present one example in about ten minutes, any team.
- Byline invitation still mentions **bringing a charge number for hands-on help**, an informal line appropriate to the current group if the presenter keeps it.
- Upcoming topics card: **Token efficiency**, **Choosing the right model**, **Git basics**.

## 6. Speaker notes and delivery approach

Every slide has presenter notes. The refined notes are in the PowerPoint itself and rendered verbatim in the companion phone-friendly PDF. For the next pass, read those notes before rewriting; they clarify distinctions and caveats not intentionally placed on-slide. Preferred speaking approach:

- Keep on-screen copy spare; explain concepts verbally using a friendly, concise engineering example.
- Define “agent” in plain language on slide 2 instead of assuming familiarity.
- Context is helpful, but not a correctness guarantee.
- “Agent can read files” is limited to actual **permitted and configured** access, and must follow organizational data-handling requirements.
- Prompt chaining = sequence with dependencies and checks. Orchestrator–workers = coordinator and focused jobs that can be combined, not necessarily dependent or concurrent.
- Every AI-assisted engineering conclusion still needs appropriate review, traceability, units, and comparison with trusted evidence.
- Keep demos focused on the audience question: **What problem was solved? How does it work at a high level? Where was it checked? What can I try?**
- Closing must encourage others to bring small examples to future sessions.

## 7. Technical implementation notes

Original full generator (`build_deck.py`) in the preceding session used:
- `python-pptx` for slides, shapes, custom connectors, text styles, bullets and slide notes.
- `lxml` for certain drawing/XML properties.
- Node `icons.js` to render icons if missing; packages `react`, `react-dom`, `react-icons/fa6`, and `sharp`.
- A disk `icons/` folder containing transparent PNG icons named `{IconName}_{HEX}.png`.
- Helpers named `bg`, `shape`, `rrect`, `text`, `bullets`, `icon`, `icon_circle`, `line`, `chip`, `title`, `footer`, `notes`, `new_slide`, and `demo_placeholder`.
- Slide masters not essential: source generated blank-layout slides with manually composed shapes and notes.

`icons.js` core approach: parse JSON list of `[FaIconName, hexColor]`, render each icon with `ReactDOMServer.renderToStaticMarkup`, convert/resize with `sharp` to 512×512 transparent PNG, and save to `icons/`.

The refined **`refine_deck.py`** script works on the PPTX itself, not by importing `build_deck.py`. It asserts every replacement matches exactly one textbox; inserts a new definition textbox on slide 2; updates the notes on all 12 slides; checks slide count, size, absence of “AEROSCIENCES” in visible text, and presence of speaker notes; then saves `AI_Workflow_Show_and_Tell_Refined.pptx`.

The notes PDF was generated separately with one slide per letter page and large notes below. If the PowerPoint changes again, **re-export/rebuild the notes PDF** so the two match. A render-and-inspect QA pass is required after edits (overflow, font sizing, spacing, icons, footer, connectors, notes).

## 8. Decisions already made and guardrails

- **Keep** the basic 12-slide story, established flat/rounded-card theme, and minimal prose.
- **Remove** audience labeling as “Aerosciences”/“aerospace sciences,” while the presenter’s Computational Aerodynamics byline may remain.
- **Generalize** prominent use cases from CFD-only to broader engineering tasks such as measurements, test reports, analyses, specifications, model inputs, results, reports, and validation.
- **Avoid** overstated claims like “the output will be right if context is rich,” “the agent sees everything,” or “the AI removes the need for engineering checking.”
- **Do not fabricate** program-specific screenshots, demo results, links, time savings, or security clearance.
- **Keep** organizational information-handling restrictions in mind. Confirm that all live/recorded examples and screen shares are permitted for the intended audience.
- **Do not replace** the improved PPTX with the old `build_deck.py` output accidentally. Updating the generator to reproduce the refined version is a separate maintenance task.

## 9. Remaining work / next likely requests

1. Review and finalize exact content and visuals for demonstration slides 9, 10, and 11 once approved screenshots, clips, or data are provided.
2. Verify that the slide 11 RCAS description matches the actual demonstration's functionality; do not assume that deck inspection equals solver execution.
3. Perform an audience-level rehearsal/readability pass, especially on crowded multi-card slides and the transitions into and out of the demos.
4. Optional: reconcile the original `build_deck.py` source with the refined `.pptx` so the full generator becomes a reliable single source of truth.
5. After any changes, export the editable final `.pptx` and matching slide-plus-notes `.pdf`, and render/inspect all 12 slides.

## 10. Suggested instruction for the next assistant

> Please take over this existing engineering presentation. Start by reading this handoff, inspecting `AI_Workflow_Show_and_Tell_Refined.pptx` and its speaker notes, and viewing `AI_Workflow_Show_and_Tell_Refined_with_notes.pdf`. Use the refined deck—not the original—as the working master. Preserve the visual system, slide structure, and editing capability. Keep the audience broadly engineering-focused; do not call it an Aerosciences presentation. Be technically precise about agent access, context, orchestration, and verification, while keeping slides visual, light, and fun. The main unfinished work is the three program-approved demonstrations on slides 9–11. Do not invent internal details or measured benefits. When editing, update the notes, regenerate the notes PDF, and render-check the result. If you work from the original generator, first synchronize its content with the refined deck to avoid regressions.

