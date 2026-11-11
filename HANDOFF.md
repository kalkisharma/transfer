# Handoff: Harrington Coaxial Rotor Report + Cat Mode

**Paste this file into the new session together with the attachments listed below.**

## Opening message for the new session

> I'm continuing work on a self-contained HTML rotor report (Harrington coaxial rotor, RCAS) that has an optional "Cat mode". Read HANDOFF.md first. Then open `harrington_rotor_report.html`, which is the current source of truth, and keep working from it. Keep every rule under "Non-negotiables". Run `verify_cat_mode.py` after any change. Next task: [your request].

## Attachments to include

| File | What it is |
|---|---|
| `harrington_rotor_report.html` | The current, working report. It is the source of truth and is fully self-contained: data JSON and all 14 stickers are embedded. |
| `HANDOFF.md` | This file. |
| `prep_data.py` | Regenerates the placeholder data JSON and the embedded stickers. Only needed if the geometry or model changes, or stickers need re-encoding. |
| `verify_cat_mode.py` | Headless Chrome regression check (Playwright). |
| The 14 original cat PNGs | Optional. Needed only to re-encode stickers. Name them `cat01.png`…`cat14.png` in the order below. |

## What the report is

A single HTML file with no external requests, for a demo of the Harrington Coaxial Rotor 1. It has five sections:

1. **Blade geometry:** planform drawn to scale with chord ×2, pitch axis at 0.25c, and chord dimensions.
2. **Spanwise & chordwise properties:** three SVG line charts: chord vs r/R, t/c vs r/R, and NACA 00xx sections at 0.25/0.50/0.75/1.00R (equal aspect).
3. **Specifications:** a table with source tags (TN 2318 / derived / assumed / model) and a coaxial side-view diagram drawn to scale.
4. **Disk loading:** two disks, upper and lower, colored by dCT/d(r/R). Blades rotate: the upper rotor CCW and the lower CW as seen from above. The lower disk shows a dashed upper-wake boundary at r/R 0.82. There is a Pause/Spin button.
5. **Blade loading:** dCT/d(r/R) and inflow λ for each rotor.

Also included: hover tooltips on all plots, light and dark themes, and responsive layout from 390 px phones to 1080p. Rotation is off under reduced-motion.

### Data: the `<script id="report-data" type="application/json">` block
- `geometry`: published Rotor 1 values. R = 12.5 ft, 2+2 blades, σ = 0.027 per rotor, taper 0.35, tip chord 0.375 ft (root 1.071 ft derived), t/c 31%→12% nonlinear, h = 0.093D (2.33 ft), untwisted, Vtip = 469 ft/s (358 rpm, M 0.42).
- **Assumed (marked †):**
  - root cutout of 0.10R
  - the exact shape of the thickness taper
  - upper rotor turning CCW
- `span`: r, chord_ft, tc. `sections`: airfoil x/y in ft.
- `loads`: the r array, plus for `upper` and `lower` the values `dCT`, `lam`, `CT`, `CP` and `theta_deg`. Also `total {CT, CP, FM}` and `wake_radius`.
- **Loads are a placeholder.** They come from a simple coaxial BEMT I wrote:
  - upper rotor at θ = 10°, lower collective trimmed for torque balance
  - lower rotor inboard of 0.82R sees the upper slipstream, with a tanh-smoothed edge
  - Result: CT 0.00514, FM 0.749, thrust share 1.42:1.
- While `meta.loads_is_placeholder` is true, the report shows "Placeholder loads · simple BEMT" badges. **To use real RCAS output**, replace the `loads` arrays and scalars and set `loads_is_placeholder: false`. The badges then read "Source: RCAS".

### Report JS API: `window.RotorReport`
- `charts[id].getState()` returns `{svg, m, pw, ph, sx, sy, paths:[{el, pts}]}` for each line chart. The chart ids are `plot-chord`, `plot-tc`, `plot-sec`, `plot-load` and `plot-lam`.
- `planform` gives `{svg, rootX, tipX, centerY(r)}`. `elev` gives `{svg, yU, W, pad}`. `disks.upper` and `disks.lower` give `{svg, blades}`.
- `getAzimuth()` and `isSpinning()` report blade rotation. The upper blades are drawn at `rotate(-az)` and the lower at `rotate(+az)`.
- Every re-render dispatches `window` event `rotor:render`.

## Cat Mode

The toggle is in the header, labeled "Cat mode", and also responds to the **C** key. It is off on load and its state is not saved. All cat code lives in one IIFE (`window.catMode`) plus one CSS block marked `Cat Mode`, so it is easy to delete. Console helpers:
- `catMode.on()` / `catMode.off()`
- `catMode.fire('cat11')` forces one cat's animation, which is useful in a live demo.
- `catMode._debug()` returns leftover timers, rAFs, animations and cleanups.

### Non-negotiables (user's rules)
1. Cats never change, re-plot or re-scale data. Motion is CSS/WAAPI transforms on cat nodes only. The single exception is the "curve swat": it hides the original chord path with a `visibility` attribute, animates a **clone**, then restores the original exactly.
2. **Off means a clean report.** `off()` removes the layer and every timer, rAF, animation, listener and clone. `verify_cat_mode.py` checks that `body.innerHTML` is byte-identical after on/off cycles, with spin paused.
3. **Self-contained.** Stickers are embedded as base64 WebP: max 320 px, alpha kept, about 230 KB total.
4. **Simple motion only:** slide, bob, tilt, pop, spin and fade. No generated leg frames or sprite sheets.
5. **Never cover content.** Cats stay off numbers, labels, legends, ticks and text. They use `pointer-events: none`, so tooltips work through them. The layer is hidden in print.
6. **Short and random.** Animations last 0.6–2.5 s, cats fire every 5–11 s, and at most 2 animate at once. Two exceptions: the bat cat is "vip" (every 2.5–5 s, exempt from the limit), and the hub cats spin continuously.
7. **Cropped edges are always hidden.** Each cat sits in a clip box whose edge lines up with a card edge, plot axis or rotor line. Clip boxes are clamped to the page width, so there is no sideways scroll.
8. **Reduced motion:** cats appear in static poses, nothing animates and the rotors don't spin.

### Sticker map
Numbers follow the order the user first attached the photos. That numbering is how the user refers to them, e.g. "image 9".

| # | id | Sticker | Spot and behavior |
|---|---|---|---|
| 1 | cat01 | sleepy orange kitten | Naps on the footer line, left of #8, with a slow breathing scale. |
| 2 | cat02 | two orange kitten heads | Peeks up from behind the **chord plot's x-axis**, lower-left (empty under the curve), and blinks. |
| 3 | cat03 | upside-down orange face | **Upper hub.** Rotates with the upper blades (CCW). |
| 4 | cat04 | orange + black cuddle pile | **Naps on the upper rotor** in the coaxial side view, as a "coaxial pair". Breathing. |
| 5 | cat05 | black cat, pink collar | Peeks over the first row line of the specs table (top-right). Tilts or pops. |
| 6 | cat06 | orange cat, blue light | Sits above the disk card (top-right). Bobs or tilts. **Wide screens (≥820 px) only**, because a phone has no free spot. |
| 7 | cat07 | golden shorthair, side-eye | Slides in from the loading card's right edge into the gutter beside the top of the plot and stares. |
| 8 | cat08 | gray tabby looking up | Below the loading charts, bottom-right, clipped at the grid edge. Bobs. |
| 9 | cat09 | stretched orange kitten | **Lower hub.** Rotates with the lower blades (CW), counter-rotating against #3. |
| 10 | cat10 | black cat in bat wings | **Walks the blade planform** root→tip with a bob, peers over the tip, pops out. Frequent. |
| 11 | cat11 | orange cat leaning, paw down | Perches top-right inside the chord plot. Swats, and the curve wobbles on a clone and snaps back. |
| 12 | cat12 | brown tabby loaf | Toggle icon: greyscale when off, color when on. |
| 13 | cat13 | head-tilt orange kitten | Peeks up from behind the **t/c plot's x-axis**, lower-left, and tilts its head. |
| 14 | cat14 | reaching orange kitten | Lies along the bottom of the **airfoil plot**, bottom-right, and reaches toward the trailing edges. |

## Rebuild / verify
- **Edit directly:** change `harrington_rotor_report.html` (report JS is in the first script, Cat Mode in the second).
- **Regenerate data/stickers:** run `python3 prep_data.py OUT_DIR STICKER_DIR`. It writes `report_data.json` and `cats.json`; paste those into the two JSON `<script>` blocks.
- **Verify:** run `python3 verify_cat_mode.py harrington_rotor_report.html OUT_DIR`. A pass means:
  - every cat prints `:ok` (cat06 `:hidden` on mobile)
  - `overflow_px=0`
  - `dom_identical_after_off=True`
  - all leftovers are 0
  - no errors
  - It also saves full-page screenshots to `OUT_DIR`.

## Open items / next steps
- Swap the placeholder loads for real RCAS output (see the Data section). The disk color scale, plot ranges and specs table rescale automatically.
- Confirm the assumed values (root cutout, rotation sense, thickness-taper shape) against the RCAS deck.
- Optional: a phone-width spot for cat06.

## Sources
- Harrington, NACA TN 2318 (1951)
- Lim et al., JAHS 2009: https://rotorcraft.arc.nasa.gov/Publications/files/Lim_JAHS2009.pdf
- Barbely et al., SAE 2016: https://rotorcraft.arc.nasa.gov/Publications/files/Barbely_FINAL_SAE_1142_093016.pdf
