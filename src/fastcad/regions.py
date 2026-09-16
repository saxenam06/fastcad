"""Finding, on the canvas, the regions the deck names.

The deck is meshed on a different version of the housing, so its node groups cannot be copied
across by node number. What carries over is where they *are*: a bearing seat is the same bore at
the same place, whichever version of the casting it sits in. So each group's nodes are matched to
the CAD faces they lie on, and the group's name travels to those faces.

Nothing here is looked up. A seat is a seat because the deck's nodes sit on it, and the match is
reported with the distance it took, so a region that did not really match is visible.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.TopoDS import TopoDS_Shape

from .deck import Region
from .geometry import Surface, faces_of


@dataclass
class Match:
    """A deck region and the CAD faces it was found on."""

    name: str
    """The deck's name for the region."""
    faces: list[int]
    """The CAD face indices its nodes lie on."""
    distance_mm: float
    """How far the group's nodes sit from those faces: the match's own error bar."""
    area_mm2: float
    """Total area of the matched faces."""
    diameters: list[float]
    """The diameter of each matched cylindrical face, largest first. More than one means a step."""

    @property
    def matched(self) -> bool:
        return bool(self.faces)


@dataclass
class Cylinder:
    """A cylindrical CAD face, as the line it turns about and the radius it turns at."""

    face: int
    direction: np.ndarray
    point: np.ndarray
    """A point on the axis."""
    radius: float

    def offset_from(self, axis: np.ndarray, through: np.ndarray) -> float:
        """How far this cylinder's axis lies from another one, in mm, measured perpendicular."""
        gap = self.point - through
        return float(np.linalg.norm(gap - np.dot(gap, axis) * axis))


def cylinder_of(shape: TopoDS_Shape, index: int) -> tuple[np.ndarray, float] | None:
    """A face's axis and radius, if it is a cylinder."""
    found = cylinder_face(shape, index)
    return (found.direction, found.radius) if found else None


def cylinder_face(shape: TopoDS_Shape, index: int) -> Cylinder | None:
    """A face as a cylinder, if that is what it is."""
    face = faces_of(shape)[index]
    adaptor = BRepAdaptor_Surface(face)
    if adaptor.GetType() != GeomAbs_Cylinder:
        return None
    cylinder = adaptor.Cylinder()
    direction = cylinder.Axis().Direction()
    location = cylinder.Axis().Location()
    return Cylinder(
        face=index,
        direction=np.array([direction.X(), direction.Y(), direction.Z()]),
        point=np.array([location.X(), location.Y(), location.Z()]),
        radius=float(cylinder.Radius()),
    )


_CYLINDER_CACHE: dict[int, tuple[TopoDS_Shape, list[Cylinder]]] = {}


def cylinders(shape: TopoDS_Shape) -> list[Cylinder]:
    """Every cylindrical face of the shape."""
    cached = _CYLINDER_CACHE.get(id(shape))
    if cached is not None and cached[0] is shape:
        return cached[1]
    found = (cylinder_face(shape, i) for i in range(len(faces_of(shape))))
    result = [c for c in found if c is not None]
    _CYLINDER_CACHE[id(shape)] = (shape, result)
    return result


def match_bands(
    shape: TopoDS_Shape,
    surface: Surface,
    region: Region,
    radius_tol: float = 0.5,
    axis_tol: float = 2.0,
    parallel: float = 0.999,
) -> Match:
    """Which CAD faces carry the region's cylindrical bands.

    The deck is meshed on a different version of the casting, so the nodes themselves sit
    millimetres off this one's surface and cannot be matched by proximity. A bore survives that
    change as a line in space and a diameter, and those are what this matches on: same axis
    direction, same axis line, same radius. The axial extent is not required to agree, because a
    seat may well be longer or shorter on another casting.
    """
    if not region.bands:
        return Match(region.name, [], float("inf"), 0.0, [])

    axis = region.axis / np.linalg.norm(region.axis)
    through = region.axis_point if region.axis_point is not None else region.centre
    span = (region.bands[0].span[0], region.bands[-1].span[1])
    wanted = region.bands[0].radius

    # Candidates: cylinders turning about the same line, reaching the same part of it.
    candidates: list[tuple[float, Cylinder]] = []
    for candidate in cylinders(shape):
        direction = candidate.direction / np.linalg.norm(candidate.direction)
        if abs(float(np.dot(direction, axis))) < parallel:
            continue
        offset = candidate.offset_from(axis, through)
        if offset > axis_tol:
            continue
        on_face = surface.face_of_triangle == candidate.face
        if not on_face.any():
            continue
        reach = (surface.vertices[surface.triangles[on_face]].mean(axis=1) - region.centre) @ axis
        if reach.max() < span[0] - axis_tol or reach.min() > span[1] + axis_tol:
            continue
        candidates.append((offset, candidate))

    if not candidates:
        return Match(region.name, [], float("inf"), 0.0, [])

    # The deck's radius is coarse, so it is used only to pick which of these bores is meant —
    # and then the CAD's own radius is what gets reported, because that one is exact.
    best = min(candidates, key=lambda c: abs(c[1].radius - wanted))[1].radius
    chosen = [(o, c) for o, c in candidates if abs(c.radius - best) <= radius_tol]
    faces = sorted(c.face for _, c in chosen)
    return Match(
        name=region.name,
        faces=faces,
        distance_mm=float(max(o for o, _ in chosen)),
        area_mm2=float(surface.area_by_face[faces].sum()),
        diameters=sorted({round(2 * c.radius, 2) for _, c in chosen}, reverse=True),
    )


def match(
    shape: TopoDS_Shape,
    surface: Surface,
    region: Region,
    tolerance_mm: float = 2.0,
    coverage: float = 0.5,
) -> Match:
    """Which CAD faces the region's nodes lie on.

    A face counts when at least `coverage` of its triangles sit within `tolerance_mm` of the
    region's nodes. Requiring most of the face, rather than any part of it, keeps a seat from
    swallowing the chamfer or the wall it happens to touch.
    """
    from scipy.spatial import cKDTree

    tree = cKDTree(region.points)
    centres = surface.vertices[surface.triangles].mean(axis=1)
    distance, _ = tree.query(centres)
    near = distance < tolerance_mm

    faces: list[int] = []
    for index in np.unique(surface.face_of_triangle[near]):
        on_face = surface.face_of_triangle == index
        if near[on_face].mean() >= coverage:
            faces.append(int(index))

    if not faces:
        return Match(region.name, [], float("inf"), 0.0, [])

    chosen = np.isin(surface.face_of_triangle, faces)
    area = surface.area_by_face[faces].sum()
    diameters = sorted(
        (2 * c[1] for c in (cylinder_of(shape, i) for i in faces) if c is not None), reverse=True
    )
    return Match(
        name=region.name,
        faces=faces,
        distance_mm=float(np.percentile(distance[chosen], 95)),
        area_mm2=float(area),
        diameters=[round(d, 2) for d in diameters],
    )


def match_all(
    shape: TopoDS_Shape, surface: Surface, regions: dict[str, Region], **kwargs
) -> dict[str, Match]:
    """Every deck region, found on the canvas. Reference points are skipped: they are not surfaces."""
    return {
        name: match(shape, surface, region, **kwargs)
        for name, region in regions.items()
        if region.kind != "point"
    }


def match_through(
    shape: TopoDS_Shape,
    surface: Surface,
    name: str,
    point: np.ndarray,
    tolerance_mm: float = 3.0,
) -> Match:
    """The bore whose axis runs through a reference point.

    For a bolt this is exact and nothing else is: the group's nodes cover the hole *and* the
    flange around it, so no single cylinder fits them, while the reference node the deck ties
    them to sits dead on the hole's axis — on all twenty-five of them, to 0.00 mm.
    """
    best: Cylinder | None = None
    offset = float("inf")
    for candidate in cylinders(shape):
        direction = candidate.direction / np.linalg.norm(candidate.direction)
        gap = point - candidate.point
        distance = float(np.linalg.norm(gap - np.dot(gap, direction) * direction))
        # The nearest axis wins; ties go to the tighter bore, which is the hole itself rather
        # than the counterbore or the boss around it.
        if distance < offset - 1e-9 or (abs(distance - offset) < 1e-9 and best and candidate.radius < best.radius):
            best, offset = candidate, distance
    if best is None or offset > tolerance_mm:
        return Match(name, [], float("inf"), 0.0, [])

    faces = sorted(
        c.face for c in cylinders(shape)
        if abs(c.radius - best.radius) < 0.01
        and np.linalg.norm(np.cross(c.direction, best.direction)) < 1e-3
        and c.offset_from(best.direction / np.linalg.norm(best.direction), best.point) < tolerance_mm
    )
    return Match(
        name=name,
        faces=faces,
        distance_mm=offset,
        area_mm2=float(surface.area_by_face[faces].sum()),
        diameters=[round(2 * best.radius, 2)],
    )


def find_regions(
    shape: TopoDS_Shape, surface: Surface, regions: dict[str, Region], pairs: dict[str, str]
) -> dict[str, Match]:
    """Every region the deck drives, found on the canvas.

    A seat is found from the cylinder its nodes lie on; a bolt hole from the reference node the
    deck ties it to. Only regions the command file actually uses are looked for — the mesh
    carries more groups than the analysis drives, and inventing a home for the spares would be
    claiming to know something the deck does not say.
    """
    found: dict[str, Match] = {}
    for name, reference in pairs.items():
        region = regions.get(name)
        if region is None:
            continue
        point = regions[reference].centre if reference in regions else None
        by_bands = match_bands(shape, surface, region) if region.bands else None
        if by_bands is not None and by_bands.matched:
            found[name] = by_bands
        elif point is not None:
            found[name] = match_through(shape, surface, name, point)
        else:
            found[name] = Match(name, [], float("inf"), 0.0, [])
    return found
