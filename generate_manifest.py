"""Build ./data/geometry.json by listing and measuring the STL files in ./stls/.

The manifest is the single source of truth for the viewer: the front end never
guesses filenames and never computes units -- it only formats what it reads
here.  Re-run after adding, removing or regenerating an STL.

Each entry is:
    name    display name (filename minus the .stl extension)
    file    path relative to the site root, for fetch()
    parent  name of the parent component, or null for a scene-graph root
    specs   ordered [{label, value}] pairs, measured from the mesh itself

Specs are derived from the geometry rather than authored, so they cannot drift
from the STL and they work for any file dropped into ./stls/.  All lengths are
reported in decimal feet.

`parent` is null for every component today.  It exists so the viewer can build
a real scene graph (slats parented to the wing, rudder to the fuselage, ...)
without a format change later.

Run with:  python generate_manifest.py
"""

from __future__ import annotations

import json
import math
import struct
from pathlib import Path

# The vector helpers already exist in the mesh generator, whose main() is
# __name__-guarded, so importing them here is free of side effects.
from generate_stls import cross, dot, sub

ROOT = Path(__file__).resolve().parent
STL_DIR = ROOT / "stls"
MANIFEST_PATH = ROOT / "data" / "geometry.json"

M_TO_FT = 3.280839895

# A closed surface's area-weighted normals cancel out.  Anything above this
# fraction of total area means the mesh has holes, which makes its enclosed
# volume meaningless.
CLOSURE_TOLERANCE = 1e-6

# Component name -> parent name.  Anything absent here is treated as a root.
# Populate this when the hierarchy is defined; the viewer already honours it.
HIERARCHY: dict[str, str] = {}


def read_binary_stl(path):
    """Return the triangles of a binary STL as tuples of three vertices.

    Mirrors the writer in generate_stls.write_binary_stl: an 80-byte header, a
    uint32 facet count, then 50 bytes per facet (normal, three vertices, and a
    two-byte attribute word that we ignore in favour of recomputing normals).
    """
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError(f"{path.name}: too short to be an STL")

    (count,) = struct.unpack_from("<I", data, 80)
    expected = 84 + count * 50
    if len(data) != expected:
        # The usual cause is an ASCII STL, whose header happens to parse as a
        # nonsense facet count.
        hint = " (looks like an ASCII STL)" if data[:5] == b"solid" else ""
        raise ValueError(
            f"{path.name}: expected {expected} bytes for {count} facets, "
            f"found {len(data)}{hint}")

    triangles = []
    for index in range(count):
        values = struct.unpack_from("<12f", data, 84 + index * 50)
        triangles.append((values[3:6], values[6:9], values[9:12]))
    return triangles


def mesh_metrics(triangles):
    """Return bounding box, wetted area, enclosed volume and closure error.

    Volume uses the signed-tetrahedron sum, which is only meaningful for a
    watertight surface -- `closure` reports how far from watertight the mesh
    is, as a fraction of its own area.
    """
    low = [math.inf] * 3
    high = [-math.inf] * 3
    area = 0.0
    volume = 0.0
    normal_sum = [0.0, 0.0, 0.0]

    for a, b, c in triangles:
        for vertex in (a, b, c):
            for axis in range(3):
                low[axis] = min(low[axis], vertex[axis])
                high[axis] = max(high[axis], vertex[axis])

        normal = cross(sub(b, a), sub(c, a))
        magnitude = math.sqrt(dot(normal, normal))
        area += 0.5 * magnitude
        volume += dot(a, cross(b, c)) / 6.0
        # 0.5 * normal is the area-weighted unit normal, since |normal| is
        # twice the triangle's area.
        for axis in range(3):
            normal_sum[axis] += 0.5 * normal[axis]

    residual = math.sqrt(dot(normal_sum, normal_sum))
    return {
        "min": tuple(low),
        "max": tuple(high),
        "size": tuple(high[axis] - low[axis] for axis in range(3)),
        "area": area,
        "volume": abs(volume),
        "facets": len(triangles),
        "closure": residual / area if area > 0 else math.inf,
    }


def assembly_extents(all_metrics):
    """Return the overall size of every component combined, as a string.

    Computed here rather than in the viewer so that unit conversion stays in
    exactly one place.
    """
    low = [min(m["min"][axis] for m in all_metrics) for axis in range(3)]
    high = [max(m["max"][axis] for m in all_metrics) for axis in range(3)]
    spans = [(high[axis] - low[axis]) * M_TO_FT for axis in range(3)]
    return " × ".join(f"{span:.1f}" for span in spans) + " ft"


def build_specs(metrics):
    """Return display-ready {label, value} pairs in imperial units.

    Values are pre-formatted strings so the viewer holds no unit logic at all.
    The trade-off: switching to metric means regenerating this file.
    """
    length, width, height = metrics["size"]
    return [
        {"label": "Length (X)", "value": f"{length * M_TO_FT:.2f} ft"},
        {"label": "Width (Y)", "value": f"{width * M_TO_FT:.2f} ft"},
        {"label": "Height (Z)", "value": f"{height * M_TO_FT:.2f} ft"},
        {"label": "Wetted area",
         "value": f"{metrics['area'] * M_TO_FT ** 2:.1f} ft²"},
        {"label": "Volume",
         "value": f"{metrics['volume'] * M_TO_FT ** 3:.2f} ft³"},
        {"label": "Triangles", "value": f"{metrics['facets']:,}"},
    ]


def collect_components(stl_dir):
    """Return (manifest entries, metrics per component) for every STL found.

    Warns rather than fails on an unwatertight mesh: the part still renders and
    its dimensions are still valid, only the volume figure is suspect.
    """
    entries = []
    measurements = []
    for path in sorted(stl_dir.glob("*.stl")):
        metrics = mesh_metrics(read_binary_stl(path))
        if metrics["closure"] > CLOSURE_TOLERANCE:
            print(f"  warning: {path.name} is not watertight "
                  f"(closure error {metrics['closure']:.2e}); "
                  f"its volume is an estimate")

        entries.append({
            "name": path.stem,
            "file": f"stls/{path.name}",
            "parent": HIERARCHY.get(path.stem),
            "specs": build_specs(metrics),
        })
        measurements.append(metrics)
    return entries, measurements


def main():
    """Write the manifest and report what was found."""
    if not STL_DIR.is_dir():
        raise SystemExit(f"no STL directory at {STL_DIR}")

    components, measurements = collect_components(STL_DIR)
    if not components:
        raise SystemExit(f"no .stl files found in {STL_DIR}")

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "units": "foot",
        "extents": assembly_extents(measurements),
        "components": components,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")

    print(f"{MANIFEST_PATH.relative_to(ROOT)}: {len(components)} components")
    for entry in components:
        dimensions = " x ".join(
            spec["value"].removesuffix(" ft") for spec in entry["specs"][:3])
        print(f"  {entry['name']:<12} {dimensions} ft")


if __name__ == "__main__":
    main()
