"""Meshing the faces gmsh gives up on, using the nodes it already put on their edges.

gmsh meshes each CAD face in its own parameter space, and on this housing five faces defeat it:
full cylinders and a cone whose seam leaves their parameter-space boundary unclosed. It still
meshes their *edges*, though, and those edge nodes are shared with the neighbouring faces that did
mesh. Building the missing triangles on exactly those nodes therefore closes the surface without
adding a single vertex, which is what makes the result conformal rather than a patch laid on top.

The triangles are built in the face's own parameter space and so lie on the real surface, not on a
flat lid across the hole. That distinction is the whole point: a flat fan over a 134 mm opening
passes every mesh-quality check and still moves the answer.
"""

from __future__ import annotations

import numpy as np
from OCP.BRep import BRep_Tool
from OCP.gp import gp_Pnt
from OCP.ShapeAnalysis import ShapeAnalysis_Surface
from OCP.TopoDS import TopoDS_Shape

from .geometry import faces_of


def chain(segments: list[list[int]]) -> list[list[int]]:
    """Join edge meshes end to end into the closed rings they form.

    Each segment is one CAD edge's nodes in order. A face's boundary is one ring for a patch with
    corners, or two for a tube — the outer and inner rims — so the segments are chained until each
    returns to where it began.
    """
    remaining = [list(s) for s in segments if len(s) >= 2]
    rings: list[list[int]] = []
    while remaining:
        ring = remaining.pop(0)
        progressed = True
        while ring[0] != ring[-1] and progressed:
            progressed = False
            for i, candidate in enumerate(remaining):
                if candidate[0] == ring[-1]:
                    ring += candidate[1:]
                elif candidate[-1] == ring[-1]:
                    ring += candidate[::-1][1:]
                elif candidate[-1] == ring[0]:
                    ring = candidate[:-1] + ring
                elif candidate[0] == ring[0]:
                    ring = candidate[::-1][:-1] + ring
                else:
                    continue
                remaining.pop(i)
                progressed = True
                break
        if ring[0] == ring[-1]:
            ring = ring[:-1]
        if len(ring) >= 3:
            rings.append(ring)
    return rings


def uv_of(shape: TopoDS_Shape, face_index: int, points: np.ndarray) -> np.ndarray:
    """Where the points sit in the face's parameter space."""
    surface = BRep_Tool.Surface_s(faces_of(shape)[face_index])
    analyser = ShapeAnalysis_Surface(surface)
    out = np.empty((len(points), 2))
    for i, p in enumerate(points):
        found = analyser.ValueOfUV(gp_Pnt(float(p[0]), float(p[1]), float(p[2])), 1e-4)
        out[i] = (found.X(), found.Y())
    return out


def unwrap(u: np.ndarray, period: float = 2 * np.pi) -> np.ndarray:
    """Undo the wrap in a periodic coordinate, so a ring reads as a run of increasing values.

    A cylinder's angular parameter jumps from 2pi back to 0 at the seam. Left wrapped, the ring
    looks like it doubles back on itself and anything built from it comes out inside out.
    """
    out = u.astype(float).copy()
    steps = np.diff(out)
    out[1:] -= period * np.cumsum(np.round(steps / period))
    return out


def strip(a: list[int], b: list[int], ua: np.ndarray, ub: np.ndarray) -> np.ndarray:
    """Triangles spanning between two rings, as the wall of a tube.

    The rings are walked together in the angular parameter, always advancing whichever is further
    behind, so every node of both is used and the band closes.
    """
    order_a = np.argsort(ua)
    order_b = np.argsort(ub)
    ring_a = [a[i] for i in order_a]
    ring_b = [b[i] for i in order_b]
    pa = ua[order_a]
    pb = ub[order_b]
    # Both rings start from the same angular place, so the band does not spiral.
    span_a = (pa - pa[0]) / max(np.ptp(pa), 1e-12)
    span_b = (pb - pb[0]) / max(np.ptp(pb), 1e-12)

    out: list[tuple[int, int, int]] = []
    i = j = 0
    while i < len(ring_a) or j < len(ring_b):
        take_a = j >= len(ring_b) - 1 or (
            i < len(ring_a) - 1 and span_a[min(i + 1, len(span_a) - 1)] <= span_b[min(j + 1, len(span_b) - 1)]
        )
        if take_a and i < len(ring_a) - 1:
            out.append((ring_a[i], ring_a[i + 1], ring_b[j % len(ring_b)]))
            i += 1
        elif j < len(ring_b) - 1:
            out.append((ring_b[j + 1], ring_b[j], ring_a[i % len(ring_a)]))
            j += 1
        else:
            break
    # Close the band round the seam.
    out.append((ring_a[-1], ring_a[0], ring_b[0]))
    out.append((ring_b[0], ring_b[-1], ring_a[-1]))
    return np.array(out, dtype=np.int64).reshape(-1, 3)


def ear_clip(ring: list[int], uv: np.ndarray) -> np.ndarray:
    """Triangles filling one ring, in its own parameter space, adding no vertices."""
    from .geometry import _is_ear, _signed_area

    flat = uv.copy()
    order = list(range(len(ring)))
    if _signed_area(flat) < 0:
        order = order[::-1]
    out: list[tuple[int, int, int]] = []
    guard = 0
    while len(order) > 2 and guard < 10 * len(ring):
        guard += 1
        for k in range(len(order)):
            prev, here, nxt = order[k - 1], order[k], order[(k + 1) % len(order)]
            if _is_ear(flat, order, prev, here, nxt):
                out.append((ring[prev], ring[here], ring[nxt]))
                order.remove(here)
                break
        else:
            for k in range(1, len(order) - 1):
                out.append((ring[order[0]], ring[order[k]], ring[order[k + 1]]))
            break
    return np.array(out, dtype=np.int64).reshape(-1, 3)


def patch_face(
    shape: TopoDS_Shape, face_index: int, rings: list[list[int]], vertices: np.ndarray
) -> np.ndarray:
    """Triangles covering one CAD face, built on the ring nodes gmsh already placed."""
    if not rings:
        return np.empty((0, 3), dtype=np.int64)

    parameters = [uv_of(shape, face_index, vertices[ring]) for ring in rings]
    if len(rings) == 1:
        uv = parameters[0]
        uv[:, 0] = unwrap(uv[:, 0])
        return ear_clip(rings[0], uv)
    if len(rings) == 2:
        # A tube: two rims round the same axis, joined by a band.
        ua, ub = unwrap(parameters[0][:, 0]), unwrap(parameters[1][:, 0])
        return strip(rings[0], rings[1], ua, ub)

    # More rims than that means the face has holes in it; fill the outer one and leave the rest,
    # rather than guessing which is which.
    uv = parameters[int(np.argmax([len(r) for r in rings]))]
    uv[:, 0] = unwrap(uv[:, 0])
    return ear_clip(rings[int(np.argmax([len(r) for r in rings]))], uv)
