# Step 1 — Fig. 1(a) geometry: digitization and cross-check

**Source:** NACA TN 2318 (Harrington, 1951), Fig. 1(a), report page 9 (PDF page 11).
SHA-256 of the scan used: `7d1c39191dcb1dafed0b1eac8aa4e878dc176c9f060c13b286c99de0e9df89bf`.
**Output:** `data/geometry_fig1a.csv`. **Overlay check:** `docs/fig1a_trace_overlay.png` (red = chord, blue = t/c, green = linear chord fit).

## What the figure shows

- Axes: blade radius r in **inches** (0–160; R = 150 in), chord in **inches** (0–16), t/c in **percent** (0–32).
- Solid curves begin at r ≈ 21 in (r/R ≈ 0.14). Inboard of that the chord line is dashed (hub/shank region). The blade root cutout is therefore about 21 in, read from where the solid line starts. **Flag:** the text gives no root cutout value.
- Chord is linear from r = 21 to about 147.6 in, then closes vertically to zero at r ≈ 149.5 in (tip cap).
- t/c is about 30.6 % at r = 21 in, falls slowly to 29.5 % at r = 42 in, then steps down to 24.5 % between r ≈ 44 and 48 in (r/R 0.29–0.32). It then decreases nearly linearly to about 20 % at r/R 0.78 and drops off faster toward the tip.

## Method

Grid lines were auto-detected on the 300 dpi scan for axis calibration (17 vertical lines at 93.47 px per 10 in; 0–32 over 1486.6 px). Each curve was traced per pixel column, and row by row in the near-vertical tip region. Values were median-smoothed over ±1.2 in and resampled at 2.5 in stations, with denser stations through the root step and tip. Three stations where the t/c curve lies on a grid line are interpolated and labelled as such. Scripts are in `scripts/`.

Pixel resolution: 0.107 in radius, 0.011 in chord, 0.022 % t/c. The linear chord fit over r = 22–145 in has an rms residual of 0.005 in (max 0.029 in), so the chord line is straight to the resolution of the scan.

## Cross-check against the stated values

| Quantity | Digitized | Stated | Status |
|---|---|---|---|
| Linear chord law | c = 12.378 − 0.05337·r (in) | — | — |
| Chord at r = 0 (extrapolated) | 12.38 in (1.032 ft) | — | — |
| Chord at r = R = 150 in | 4.37 in (0.364 ft) | 0.375 ft (4.50 in) | **−2.8 %, flag** |
| r where linear chord = 4.50 in | 147.6 in (r/R 0.984) | — | end of linear taper |
| Taper ratio c(R)/c(0) | 0.353 | 0.35 | OK |
| Root chord if both stated values imposed at R and r = 0 | — | 12.86 in | **+3.9 % vs digitized, flag** |
| Solidity, single (thrust-weighted c_e, 0..R) | 0.0271 | 0.027 | OK |
| Solidity, coaxial | 0.0541 | 0.054 | OK |
| σ_coax / σ_tip,single | 2.92 | 2.92 (Figs. 4, 6, 7 captions) | OK (see flag 3) |
| t/c at the tip | 12 % reached only at r ≈ 148.4 in (r/R 0.99) | "tip NACA 0012" | **flag** |

## Flags

1. **Tip chord and taper ratio are mutually inconsistent at the ~3 % level.** The figure supports the 0.35 taper ratio when it is defined as c(R)/c(r = 0) on the extrapolated line. 0.375 ft is the chord where the linear taper ends (r ≈ 147.6 in), not the chord at R. Using both stated values as "tip at R" and "taper about r = 0" overstates the root chord by 3.9 %. Recommendation: use the digitized law c = 1.0315 − 0.05337·r (both in ft), valid from r = 1.75 ft to 12.30 ft (r/R 0.14–0.984), rather than the two rounded values. It reproduces the published solidity exactly.
2. **"Tip NACA 0012" is only true at the extreme tip.** t/c is 20.3 % at r/R 0.75, 17.1 % at 0.90, 15.4 % at 0.95 and 14.6 % at 0.967. It reaches 12 % only inside r/R ≈ 0.99, in the tip-cap region. The outer 10 % of span, where most thrust is produced, is roughly 0017 → 0014. The section assignment in step 3 needs to reflect this rather than treating the tip as 0012.
3. **The σ/σt = 2.92 caption is explained by the digitized geometry:** coaxial thrust-weighted solidity over single-rotor tip solidity (tip chord at R) gives 2.92. This is not consistent with rotor 2's caption (σ/σt = 1 for an untapered blade, where the same definition would give 2). The rotor 1 figures are unaffected, but the caption convention is not fully confirmed.
4. **Root step location ±1 in.** The thickness transition at r ≈ 44–48 in is steep, so stations there carry about ±1 in radial uncertainty. It is presumably the spar/cuff transition; the text does not say.
5. **Root cutout ≈ 21 in**, inferred from where the solid curves begin, not stated in the text.
6. The text states 540 ft/s as the design tip speed. Testing was limited to 500 ft/s by vibration, consistent with your operating point.
