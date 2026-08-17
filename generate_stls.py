"""Generate a set of simple parametric aircraft components as binary STL files.

Every component is built the same way: define a closed 2-D cross-section, place
copies of it along a span (or axis), loft quads between neighbouring sections
and cap the two ends.  The shapes are representative rather than
aerodynamically accurate -- they exist to give an STL viewer non-trivial,
recognisable test geometry.

Axes (right-handed, aircraft convention used loosely):
    +x  aft (chordwise)
    +y  starboard (spanwise)
    +z  up

Run with:  python generate_stls.py
"""

from __future__ import annotations

import math
import struct
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "stls"


# --------------------------------------------------------------- vector maths

def sub(a, b):
    """Return the vector a - b."""
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    """Return the vector a + b."""
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def scale(a, k):
    """Return the vector a scaled by the scalar k."""
    return (a[0] * k, a[1] * k, a[2] * k)


def dot(a, b):
    """Return the dot product of a and b."""
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    """Return the cross product a x b."""
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def normalise(a):
    """Return the unit vector along a, or (0, 0, 0) for a degenerate input."""
    length = math.sqrt(dot(a, a))
    return scale(a, 1.0 / length) if length > 1e-12 else (0.0, 0.0, 0.0)


def centroid(points):
    """Return the arithmetic mean of a sequence of points."""
    n = len(points)
    return (sum(p[0] for p in points) / n,
            sum(p[1] for p in points) / n,
            sum(p[2] for p in points) / n)


# ------------------------------------------------------------- mesh assembly

def _outward(tri, inside):
    """Return tri wound so its normal points away from the `inside` reference.

    Cheap alternative to tracking winding by hand.  It is valid because every
    section we loft is star-shaped about its own centroid, and `inside` is
    always a local centroid rather than a global one.
    """
    a, b, c = tri
    normal = cross(sub(b, a), sub(c, a))
    if dot(normal, sub(centroid(tri), inside)) < 0.0:
        return (a, c, b)
    return tri


def loft(sections):
    """Return triangles skinning a list of equal-length closed point loops."""
    triangles = []
    for lower, upper in zip(sections, sections[1:]):
        inside = centroid(list(lower) + list(upper))
        count = len(lower)
        for i in range(count):
            j = (i + 1) % count
            triangles.append(_outward((lower[i], upper[i], upper[j]), inside))
            triangles.append(_outward((lower[i], upper[j], lower[j]), inside))
    return triangles


def cap(loop, inside):
    """Return a triangle fan closing one end loop, facing away from `inside`."""
    hub = centroid(loop)
    count = len(loop)
    return [_outward((hub, loop[i], loop[(i + 1) % count]), inside)
            for i in range(count)]


def solid(sections):
    """Return a closed surface: the lofted skin plus both end caps."""
    triangles = loft(sections)
    triangles += cap(sections[0], centroid(sections[1]))
    triangles += cap(sections[-1], centroid(sections[-2]))
    return triangles


def mirror_y(triangles):
    """Return a copy of `triangles` reflected across the y = 0 plane.

    Reflection reverses handedness, so the winding is flipped to keep the
    normals pointing outward.
    """
    flip = lambda p: (p[0], -p[1], p[2])  # noqa: E731 - local, single use
    return [(flip(c), flip(b), flip(a)) for a, b, c in triangles]


# ------------------------------------------------------------------- profiles

def naca_4digit(code, n_points=40):
    """Return a closed NACA 4-digit contour as (x, z) fractions of chord.

    The loop runs trailing edge -> leading edge along the upper surface, then
    back to the trailing edge along the lower surface.  The trailing edge is
    left blunt (the standard open-TE coefficients) so no degenerate triangles
    appear in the mesh.
    """
    camber = int(code[0]) / 100.0
    camber_pos = int(code[1]) / 10.0
    thickness = int(code[2:]) / 100.0

    # Cosine spacing clusters points where curvature is highest.
    stations = [0.5 * (1.0 - math.cos(math.pi * i / (n_points - 1)))
                for i in range(n_points)]

    upper, lower = [], []
    for x in stations:
        half_thickness = 5.0 * thickness * (
            0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2
            + 0.2843 * x ** 3 - 0.1015 * x ** 4)

        if camber > 0.0 and 0.0 < camber_pos < 1.0:
            if x < camber_pos:
                mean_line = camber / camber_pos ** 2 * (
                    2 * camber_pos * x - x ** 2)
                slope = 2 * camber / camber_pos ** 2 * (camber_pos - x)
            else:
                mean_line = camber / (1 - camber_pos) ** 2 * (
                    1 - 2 * camber_pos + 2 * camber_pos * x - x ** 2)
                slope = 2 * camber / (1 - camber_pos) ** 2 * (camber_pos - x)
        else:
            mean_line, slope = 0.0, 0.0

        angle = math.atan(slope)
        upper.append((x - half_thickness * math.sin(angle),
                      mean_line + half_thickness * math.cos(angle)))
        lower.append((x + half_thickness * math.sin(angle),
                      mean_line - half_thickness * math.cos(angle)))

    # Drop the duplicated leading-edge point where the two surfaces meet.
    return list(reversed(upper)) + lower[1:]


def contour_slice(contour, x_min, x_max):
    """Return the part of a contour between two chord fractions, still closed.

    The removed span is replaced implicitly by the straight edge joining the
    two cut points, which is what makes a flap or slat panel a closed body.
    """
    return [(x, z) for x, z in contour if x_min <= x <= x_max]


def circle(n_points=32):
    """Return a unit circle as a closed (y, z) loop, used for the fuselage."""
    return [(math.cos(2 * math.pi * i / n_points),
             math.sin(2 * math.pi * i / n_points)) for i in range(n_points)]


# ------------------------------------------------------------------ placement

def place_airfoil(contour, leading_edge, chord, twist_deg=0.0,
                  chord_axis=(1.0, 0.0, 0.0), up_axis=(0.0, 0.0, 1.0)):
    """Return a 3-D section: a contour scaled to `chord` and pinned at its LE.

    `twist_deg` rotates the section nose-down/nose-up in the plane spanned by
    the chord and up axes (positive = leading edge up, i.e. washin).
    """
    angle = math.radians(twist_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    points = []
    for x, z in contour:
        x_rot = x * cos_a + z * sin_a
        z_rot = -x * sin_a + z * cos_a
        offset = add(scale(chord_axis, x_rot * chord),
                     scale(up_axis, z_rot * chord))
        points.append(add(leading_edge, offset))
    return points


def place_circle(loop, x, radius_y, radius_z, z_offset=0.0):
    """Return a 3-D fuselage station from a unit (y, z) loop."""
    return [(x, y * radius_y, z * radius_z + z_offset) for y, z in loop]


# ------------------------------------------------------------------- STL file

def write_binary_stl(path, triangles, header="generated by generate_stls.py"):
    """Write `triangles` to `path` as a binary STL with computed facet normals."""
    with path.open("wb") as handle:
        handle.write(header.encode("ascii", "replace").ljust(80, b" ")[:80])
        handle.write(struct.pack("<I", len(triangles)))
        for a, b, c in triangles:
            normal = normalise(cross(sub(b, a), sub(c, a)))
            handle.write(struct.pack("<12fH", *normal, *a, *b, *c, 0))


# ------------------------------------------------------------------ components

def build_wing():
    """Return a full tapered, swept, twisted wing with dihedral (NACA 2412)."""
    contour = naca_4digit("2412")
    half_span, root_chord, tip_chord = 5.0, 1.6, 0.7
    sweep, dihedral, tip_twist = math.radians(15.0), math.radians(5.0), -3.0

    sections = []
    for i in range(9):
        f = i / 8.0
        y = f * half_span
        sections.append(place_airfoil(
            contour,
            leading_edge=(y * math.tan(sweep), y, y * math.tan(dihedral)),
            chord=root_chord + f * (tip_chord - root_chord),
            twist_deg=f * tip_twist))

    right = solid(sections)
    return right + mirror_y(right)


def build_fuselage():
    """Return a body of revolution: elliptical nose, constant barrel, tail cone."""
    loop = circle()
    length, radius, nose, tail = 12.0, 0.75, 3.0, 4.5

    sections = []
    for i in range(41):
        x = length * i / 40.0
        if x < nose:                      # quarter-ellipse nose
            r = radius * math.sqrt(max(0.0, 1.0 - ((nose - x) / nose) ** 2))
            r = max(r, 0.05)              # keep the tip cap non-degenerate
        elif x > length - tail:           # tapered tail cone, slightly upswept
            f = (x - (length - tail)) / tail
            r = radius * (1.0 - 0.75 * f ** 1.5)
        else:
            r = radius
        upsweep = 0.35 * max(0.0, (x - (length - tail)) / tail) ** 2
        sections.append(place_circle(loop, x, r, r * 1.1, upsweep))

    return solid(sections)


def build_rudder():
    """Return a swept, tapered vertical fin with a symmetric NACA 0012 section."""
    contour = naca_4digit("0012")
    height, root_chord, tip_chord = 2.4, 1.8, 0.9
    sweep = math.radians(38.0)

    sections = []
    for i in range(7):
        f = i / 6.0
        z = f * height
        # Chord runs aft, "thickness" runs to starboard: the fin stands upright.
        sections.append(place_airfoil(
            contour,
            leading_edge=(z * math.tan(sweep), 0.0, z),
            chord=root_chord + f * (tip_chord - root_chord),
            up_axis=(0.0, 1.0, 0.0)))

    return solid(sections)


def build_htail():
    """Return a full horizontal stabiliser (NACA 0010) with anhedral-free span."""
    contour = naca_4digit("0010")
    half_span, root_chord, tip_chord = 1.9, 1.0, 0.5
    sweep = math.radians(22.0)

    sections = []
    for i in range(7):
        f = i / 6.0
        y = f * half_span
        sections.append(place_airfoil(
            contour,
            leading_edge=(y * math.tan(sweep), y, 0.0),
            chord=root_chord + f * (tip_chord - root_chord)))

    right = solid(sections)
    return right + mirror_y(right)


def build_flaps():
    """Return a pair of trailing-edge flap panels cut from the wing profile.

    The panel is the aft 30% of the wing section, deflected about its hinge
    line, and spans the inboard part of the wing only.
    """
    panel = contour_slice(naca_4digit("2412"), 0.70, 1.01)
    root_chord, tip_chord = 1.6, 1.15
    sweep, dihedral = math.radians(15.0), math.radians(5.0)
    deflection = -20.0                    # nose-down rotation = flap deployed

    sections = []
    for i in range(5):
        f = i / 4.0
        y = 0.9 + f * 2.4                 # inboard span station, metres
        sections.append(place_airfoil(
            panel,
            leading_edge=(y * math.tan(sweep), y, y * math.tan(dihedral)),
            chord=root_chord + (y / 5.0) * (tip_chord - root_chord),
            twist_deg=deflection))

    right = solid(sections)
    return right + mirror_y(right)


def build_slats():
    """Return a pair of leading-edge slats: the front 15% of the wing profile.

    Each slat is translated forward and down from its stowed position, the way
    a deployed slat opens a slot ahead of the wing.
    """
    panel = contour_slice(naca_4digit("2412"), 0.0, 0.15)
    root_chord, tip_chord = 1.55, 0.75
    sweep, dihedral = math.radians(15.0), math.radians(5.0)
    extend_x, extend_z = -0.12, -0.06     # slot gap: forward and down

    sections = []
    for i in range(7):
        f = i / 6.0
        y = 1.2 + f * 3.6                 # outboard of the flap span
        chord = root_chord + (y / 5.0) * (tip_chord - root_chord)
        sections.append(place_airfoil(
            panel,
            leading_edge=(y * math.tan(sweep) + extend_x, y,
                          y * math.tan(dihedral) + extend_z),
            chord=chord,
            twist_deg=-6.0))

    right = solid(sections)
    return right + mirror_y(right)


COMPONENTS = {
    "wing": build_wing,
    "fuselage": build_fuselage,
    "rudder": build_rudder,
    "flaps": build_flaps,
    "htail": build_htail,
    "slats": build_slats,
}


def main():
    """Write every component to OUTPUT_DIR and report the mesh sizes."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, builder in COMPONENTS.items():
        triangles = builder()
        path = OUTPUT_DIR / f"{name}.stl"
        write_binary_stl(path, triangles, header=f"{name} - parametric mesh")
        print(f"{path.name:<14} {len(triangles):>6} triangles"
              f"  {path.stat().st_size / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
