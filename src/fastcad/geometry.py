"""Reading the CAD, and turning it into a surface that still knows which CAD face it came from.

Every triangle carries the index of the CAD face it was tessellated from. That index is what
later lets a bearing seat keep its identity through meshing, naming and solving: the mesh's
boundary triangles inherit it, so a seat's patch is exactly its CAD face, not a guess.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.GeomAbs import (
    GeomAbs_BSplineSurface,
    GeomAbs_Cone,
    GeomAbs_Cylinder,
    GeomAbs_Plane,
    GeomAbs_Sphere,
    GeomAbs_Torus,
)
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS, TopoDS_Face, TopoDS_Shape
from OCP.TopTools import TopTools_IndexedMapOfShape

SURFACE_NAMES = {
    GeomAbs_Plane: "plane",
    GeomAbs_Cylinder: "cylinder",
    GeomAbs_Cone: "cone",
    GeomAbs_Sphere: "sphere",
    GeomAbs_Torus: "torus",
    GeomAbs_BSplineSurface: "bspline",
}


@dataclass
class Surface:
    """A welded triangle surface that remembers its CAD faces.

    `vertices` is (n, 3) in mm, `triangles` is (m, 3) of vertex indices wound outward, and
    `face_of_triangle` is (m,) holding the CAD face index each triangle came from.
    """

    vertices: np.ndarray
    triangles: np.ndarray
    face_of_triangle: np.ndarray
    face_count: int

    @property
    def area_by_face(self) -> np.ndarray:
        """Total triangle area per CAD face, in mm²."""
        v = self.vertices[self.triangles]
        cross = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
        area = 0.5 * np.linalg.norm(cross, axis=1)
        out = np.zeros(self.face_count)
        np.add.at(out, self.face_of_triangle, area)
        return out

    def volume(self) -> float:
        """Enclosed volume in mm³, from the divergence theorem. Negative means inward winding."""
        v = self.vertices[self.triangles]
        return float(np.einsum("ij,ij->i", v[:, 0], np.cross(v[:, 1], v[:, 2])).sum() / 6.0)


def read_step(path: Path | str) -> TopoDS_Shape:
    """Read a STEP file. Raises if the reader will not give us a shape."""
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise ValueError(f"could not read STEP: {path}")
    reader.TransferRoots()
    return reader.OneShape()


#: Face lists, kept per shape. Building one walks the whole B-rep, and face indices are looked up
#: often enough — once per cylinder, per region, per bolt — that rebuilding it each time turns
#: matching into an hours-long job. The shape is held alongside so the key stays its own.
_FACE_CACHE: dict[int, tuple[TopoDS_Shape, list[TopoDS_Face]]] = {}


def faces_of(shape: TopoDS_Shape) -> list[TopoDS_Face]:
    """The shape's faces, in the order that fixes every face index we use."""
    cached = _FACE_CACHE.get(id(shape))
    if cached is not None and cached[0] is shape:
        return cached[1]
    indexed = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_FACE, indexed)
    faces = [TopoDS.Face_s(indexed.FindKey(i)) for i in range(1, indexed.Extent() + 1)]
    _FACE_CACHE[id(shape)] = (shape, faces)
    return faces


def surface_kind(face: TopoDS_Face) -> str:
    return SURFACE_NAMES.get(BRepAdaptor_Surface(face).GetType(), "other")


def solid_volume(shape: TopoDS_Shape) -> float:
    """Volume in mm³, from the CAD itself."""
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return float(props.Mass())


def tessellate(shape: TopoDS_Shape, deflection: float = 0.2, angle_deg: float = 12.0) -> Surface:
    """Triangulate every face, then weld the result into one watertight surface.

    `deflection` is how far a triangle may sit from the true surface, in mm. Faces are meshed
    with OpenCascade, so each triangle belongs to exactly one CAD face; welding merges the
    duplicated vertices along shared edges so the surface closes.
    """
    BRepMesh_IncrementalMesh(shape, deflection, False, np.deg2rad(angle_deg), True)

    chunks: list[np.ndarray] = []
    tris: list[np.ndarray] = []
    owners: list[np.ndarray] = []
    offset = 0
    faces = faces_of(shape)
    for index, face in enumerate(faces):
        location = TopLoc_Location()
        triangulation = BRep_Tool.Triangulation_s(face, location)
        if triangulation is None:
            continue
        transform = location.Transformation()
        n = triangulation.NbNodes()
        points = np.empty((n, 3))
        for i in range(1, n + 1):
            p = triangulation.Node(i).Transformed(transform)
            points[i - 1] = (p.X(), p.Y(), p.Z())

        m = triangulation.NbTriangles()
        cells = np.empty((m, 3), dtype=np.int64)
        for i in range(1, m + 1):
            a, b, c = triangulation.Triangle(i).Get()
            cells[i - 1] = (a - 1, b - 1, c - 1)
        if face.Orientation() == TopAbs_REVERSED:
            cells = cells[:, [0, 2, 1]]

        chunks.append(points)
        tris.append(cells + offset)
        owners.append(np.full(m, index, dtype=np.int64))
        offset += n

    vertices = np.vstack(chunks)
    triangles = np.vstack(tris)
    face_of_triangle = np.concatenate(owners)

    vertices, triangles, keep, _ = weld(vertices, triangles, return_keep=True)
    return Surface(vertices, triangles, face_of_triangle[keep], face_count=len(faces))


def surface_mesh(
    path: Path | str,
    shape: TopoDS_Shape,
    size: float = 20.0,
    min_size: float | None = None,
    curvature: int = 0,
    patch: bool = True,
    patch_deflection: float = 0.5,
) -> tuple[Surface, dict]:
    """Mesh the B-rep's faces with triangles at the element size we actually want.

    This is the route agenticCAE's campaign uses (`mesh/surface.py:cad_surface`), and it is not
    the same thing as tessellating finely and decimating. gmsh meshes each CAD face in its own
    parameter space, so a triangle belongs to exactly one face by construction rather than by a
    nearest-neighbour guess, and the triangles come out at element size, which is what a volume
    mesher should be given.

    `AbortOnError` is off because gmsh stops at the first face it cannot parametrise instead of
    meshing the rest; the faces it skipped are counted and returned, because each one is a hole
    somebody would otherwise have to invent a lid for.
    """
    import gmsh

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.AbortOnError", 0)
        gmsh.option.setNumber("Geometry.Tolerance", 1e-3)
        gmsh.model.occ.importShapes(str(path))
        gmsh.model.occ.synchronize()
        gmsh.option.setNumber("Mesh.MeshSizeMax", size)
        gmsh.option.setNumber("Mesh.MeshSizeMin", min_size if min_size is not None else size / 5)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", curvature)
        try:
            gmsh.model.mesh.generate(2)
        except Exception:  # noqa: BLE001, S110 - deliberate; see below
            # gmsh raises on the faces it cannot parametrise but has already meshed the rest, and
            # the rest is what we want. Which faces it gave up on is counted below and returned,
            # so the failure is reported as data rather than swallowed.
            pass

        tags, coords, _ = gmsh.model.mesh.getNodes()
        vertices = np.asarray(coords, dtype=float).reshape(-1, 3)
        row = np.zeros(int(tags.max()) + 1, dtype=np.int64)
        row[np.asarray(tags, dtype=np.int64)] = np.arange(len(tags))

        chunks: list[np.ndarray] = []
        owners: list[np.ndarray] = []
        centres: list[tuple[float, float, float]] = []
        rims: dict[int, list[list[int]]] = {}
        skipped = 0
        for index, (_, tag) in enumerate(gmsh.model.getEntities(2)):
            centres.append(gmsh.model.occ.getCenterOfMass(2, tag))
            kinds, _, nodes = gmsh.model.mesh.getElements(2, tag)
            found = False
            for kind, block in zip(kinds, nodes):
                if kind == 2:  # 3-node triangle
                    cells = row[np.asarray(block, dtype=np.int64)].reshape(-1, 3)
                    chunks.append(cells)
                    owners.append(np.full(len(cells), index, dtype=np.int64))
                    found = True
            skipped += not found
            if not found:
                # gmsh could not parametrise this face, but it did mesh the edges around it, and
                # those nodes are shared with the faces that did mesh. Keeping them is what lets
                # the hole be filled conformally later.
                rims[index] = _rim_of(gmsh, tag, row)
    finally:
        gmsh.finalize()

    triangles = np.vstack(chunks)
    gmsh_face = np.concatenate(owners)
    vertices, triangles, keep, moved = weld(vertices, triangles, return_keep=True)
    gmsh_face = gmsh_face[keep]
    rims = {
        face: [[int(moved[i]) for i in ring] for ring in rings] for face, rings in rims.items()
    }

    cad_face, matched = match_faces(shape, np.asarray(centres, dtype=float))
    face_of_triangle = cad_face[gmsh_face]
    face_count = len(faces_of(shape))

    report = {
        "triangles": len(triangles),
        "gmsh_faces": len(centres),
        "unparametrised_faces": int(skipped),
        "cad_faces_matched": int(matched),
    }

    missing = sorted(set(range(face_count)) - set(np.unique(face_of_triangle).tolist()))
    if rims and patch == "surface":
        # Mesh each failed face on its own surface, over the nodes already on its edges. Nothing
        # is added and nothing is invented: the triangles belong to the CAD face they cover, and
        # they carry its identity like every other triangle here.
        from .patching import patch_face

        built = 0
        for gmsh_index, rings in rims.items():
            cells = patch_face(shape, int(cad_face[gmsh_index]), rings, vertices)
            if len(cells):
                triangles = np.vstack([triangles, cells])
                face_of_triangle = np.concatenate(
                    [face_of_triangle, np.full(len(cells), cad_face[gmsh_index], dtype=np.int64)]
                )
                built += len(cells)
        report["patched_faces"] = len(rims)
        report["patch_triangles"] = built
        report["triangles"] = len(triangles)
    elif missing and patch == "close":
        # Close each hole with its own rim vertices, so the surface becomes watertight without
        # gaining a single node. That is what an exact-preserving volume mesher needs: a closed
        # complex whose every facet already carries the CAD face it belongs to. The fill itself
        # belongs to no CAD face, so it is marked -1 rather than being attributed to one.
        rings = open_loops(triangles)
        added = [fill_ring(vertices, ring) for ring in rings]
        added = [a for a in added if len(a)]
        if added:
            fill = np.vstack(added)
            triangles = np.vstack([triangles, fill])
            face_of_triangle = np.concatenate(
                [face_of_triangle, np.full(len(fill), -1, dtype=np.int64)]
            )
        report["closed_holes"] = len(rings)
        report["fill_triangles"] = int(sum(len(a) for a in added))
        report["unclassified_faces"] = len(missing)
        report["triangles"] = len(triangles)
    elif missing and patch:
        # Every face gmsh gave up on is a hole in the surface. Rather than let something invent a
        # lid over it — agenticCAE's MeshFix flattened holes up to 242 mm that way, and biased two
        # bearing-seat tilts by 20-53% — the face is tessellated by OpenCascade and dropped in.
        # The patch does not share nodes with its neighbours, which fTetWild tolerates: it wraps
        # the triangles it is given inside an envelope rather than requiring a closed surface.
        patched = tessellate(shape, deflection=patch_deflection)
        wanted = np.isin(patched.face_of_triangle, missing)
        used, cells = np.unique(patched.triangles[wanted], return_inverse=True)
        offset = len(vertices)
        vertices = np.vstack([vertices, patched.vertices[used]])
        triangles = np.vstack([triangles, cells.reshape(-1, 3) + offset])
        face_of_triangle = np.concatenate([face_of_triangle, patched.face_of_triangle[wanted]])
        report["patched_faces"] = len(missing)
        report["patch_triangles"] = int(wanted.sum())
        report["triangles"] = len(triangles)

    return Surface(vertices, triangles, face_of_triangle, face_count=face_count), report


def _rim_of(gmsh, tag: int, row: np.ndarray) -> list[list[int]]:
    """The rings of nodes gmsh placed along one face's edges, in order round each ring."""
    from .patching import chain

    segments: list[list[int]] = []
    for _, curve in gmsh.model.getBoundary([(2, tag)], oriented=True, recursive=False):
        tags, _, parameter = gmsh.model.mesh.getNodes(
            1, abs(curve), includeBoundary=True, returnParametricCoord=True
        )
        if len(tags) < 2:
            continue
        along = np.argsort(np.asarray(parameter, dtype=float))
        ordered = row[np.asarray(tags, dtype=np.int64)[along]].tolist()
        segments.append(ordered[::-1] if curve < 0 else ordered)
    return chain(segments)


def orient_consistently(vertices: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    """Wind every triangle the same way round as its neighbours, facing outward.

    Two triangles sharing an edge agree only if they traverse it in opposite directions; where
    they do not, the surface has no consistent inside. Patch triangles built in a face's own
    parameter space come out either way round, so they are reconciled here against the mesh they
    were dropped into rather than guessed at when they are made.

    Meshers care about more than the count of non-manifold edges: a surface can have none and
    still be rejected, because an outward normal cannot be defined across a winding flip.
    """
    order = np.sort(np.vstack([triangles[:, [0, 1]], triangles[:, [1, 2]], triangles[:, [2, 0]]]), axis=1)
    _, inverse = np.unique(order, axis=0, return_inverse=True)
    owner = np.tile(np.arange(len(triangles)), 3)

    by_edge = np.argsort(inverse, kind="stable")
    edges_sorted = inverse[by_edge]
    starts = np.flatnonzero(np.r_[True, edges_sorted[1:] != edges_sorted[:-1]])
    counts = np.diff(np.r_[starts, len(edges_sorted)])
    pairs = np.array(
        [owner[by_edge[s : s + 2]] for s, c in zip(starts, counts) if c == 2], dtype=np.int64
    ).reshape(-1, 2)

    neighbours: dict[int, list[int]] = {}
    for a, b in pairs:
        neighbours.setdefault(int(a), []).append(int(b))
        neighbours.setdefault(int(b), []).append(int(a))

    flipped = triangles.copy()
    visited = np.zeros(len(triangles), dtype=bool)
    for seed in range(len(triangles)):
        if visited[seed]:
            continue
        visited[seed] = True
        stack = [seed]
        while stack:
            here = stack.pop()
            mine = {(flipped[here][i], flipped[here][(i + 1) % 3]) for i in range(3)}
            for other in neighbours.get(here, ()):
                if visited[other]:
                    continue
                visited[other] = True
                theirs = {(flipped[other][i], flipped[other][(i + 1) % 3]) for i in range(3)}
                if mine & theirs:  # same direction along the shared edge: one of them is wrong
                    flipped[other] = flipped[other][[0, 2, 1]]
                stack.append(other)

    # Outward, not inward: a closed surface wound inside out encloses a negative volume.
    v = vertices[flipped]
    if np.einsum("ij,ij->i", v[:, 0], np.cross(v[:, 1], v[:, 2])).sum() < 0:
        flipped = flipped[:, [0, 2, 1]]
    return flipped


def open_loops(triangles: np.ndarray) -> list[list[int]]:
    """The holes in a surface, each as its ring of vertex indices in order.

    An edge with one triangle instead of two is on a hole's rim. Walking those edges from vertex
    to vertex gives the rim as a ring, which is what a hole has to be filled around.
    """
    # Directed, taken from each triangle's winding: an edge is on the rim when the same edge does
    # not come back the other way from a neighbour. Direction is what makes this reliable where
    # the rim branches — and it does branch here, at one vertex of degree 4 and one of degree 6.
    # Every rim vertex then has as many ways out as in, so every rim edge lands in exactly one
    # loop instead of some being abandoned in a walk that cannot close.
    directed = np.vstack([triangles[:, [0, 1]], triangles[:, [1, 2]], triangles[:, [2, 0]]])
    present = {(int(a), int(b)) for a, b in directed}
    free = [(a, b) for a, b in present if (b, a) not in present]
    if not free:
        return []

    neighbours: dict[int, list[int]] = {}
    for a, b in free:
        neighbours.setdefault(a, []).append(b)

    # Walked edge by edge, not vertex by vertex: two holes can meet at a single vertex, and
    # marking that vertex used would abandon the second hole half-open — which is how 46 edges
    # survived the first attempt.
    unused = set(free)
    # Started from the edges in a fixed order. Taking whichever edge a set happened to yield made
    # the same surface decompose into four rings one run and five the next, because where the rim
    # branches the walk's first choice decides the split. A mesh that is not the same twice is not
    # a mesh we can test.
    order = sorted(unused)
    rings: list[list[int]] = []
    for edge in order:
        if edge not in unused:
            continue
        a, b = edge
        unused.discard(edge)
        ring = [a, b]
        closed = False
        while True:
            here = ring[-1]
            step = next(
                (v for v in sorted(neighbours.get(here, ())) if (here, v) in unused), None
            )
            if step is None:
                break
            unused.discard((here, step))
            if step == ring[0]:
                closed = True
                break
            ring.append(step)
        # Only a ring that came back to where it started bounds a hole. A walk that ran out of
        # edges is a torn rim, and filling it would invent a surface across open geometry — the
        # very thing that makes a flat MeshFix lid dangerous. Leave it open so it is visible.
        if closed and len(ring) >= 3:
            rings.append(ring)
    return rings


def fill_ring(vertices: np.ndarray, ring: list[int]) -> np.ndarray:
    """Triangles closing one hole, using only the vertices already on its rim.

    Adding no new vertices is the point: the fill shares every node with the triangles around it,
    so the surface closes without a seam, and a volume mesher that preserves its input has
    something conformal to preserve. The rim is flattened onto its own best-fit plane and clipped
    ear by ear — over rings this small (a few dozen nodes) that stays well behaved.
    """
    points = vertices[ring]
    centred = points - points.mean(axis=0)
    _, _, basis = np.linalg.svd(centred, full_matrices=False)
    flat = centred @ basis[:2].T
    if _signed_area(flat) < 0:
        ring, flat = ring[::-1], flat[::-1]

    remaining = list(range(len(ring)))
    out: list[tuple[int, int, int]] = []
    guard = 0
    while len(remaining) > 2 and guard < 10 * len(ring):
        guard += 1
        for k in range(len(remaining)):
            prev, here, nxt = (
                remaining[k - 1], remaining[k], remaining[(k + 1) % len(remaining)]
            )
            if _is_ear(flat, remaining, prev, here, nxt):
                out.append((ring[prev], ring[here], ring[nxt]))
                remaining.remove(here)
                break
        else:  # no ear found: close what is left as a fan rather than loop forever
            for k in range(1, len(remaining) - 1):
                out.append((ring[remaining[0]], ring[remaining[k]], ring[remaining[k + 1]]))
            break
    return np.array(out, dtype=np.int64).reshape(-1, 3)


def _signed_area(flat: np.ndarray) -> float:
    x, y = flat[:, 0], flat[:, 1]
    return float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y) / 2.0)


def _is_ear(flat: np.ndarray, remaining: list[int], prev: int, here: int, nxt: int) -> bool:
    """Whether this corner can be clipped: it turns the right way and hides no other corner."""
    a, b, c = flat[prev], flat[here], flat[nxt]
    if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 0:
        return False  # a reflex corner, not an ear
    others = [i for i in remaining if i not in (prev, here, nxt)]
    if not others:
        return True
    p = flat[others]
    inside = np.ones(len(p), dtype=bool)
    for u, v in ((a, b), (b, c), (c, a)):
        inside &= ((v[0] - u[0]) * (p[:, 1] - u[1]) - (v[1] - u[1]) * (p[:, 0] - u[0])) > 0
    return not inside.any()


def match_faces(shape: TopoDS_Shape, centres: np.ndarray) -> tuple[np.ndarray, int]:
    """Which CAD face each of gmsh's faces is, by where its centre of mass sits.

    gmsh imports the same B-rep through the same kernel, so the two face lists hold the same
    surfaces — but not necessarily in the same order. Centres of mass identify them, and the
    count that matched closely is returned so a mismatch is visible rather than assumed away.
    """
    from scipy.spatial import cKDTree

    own = []
    for face in faces_of(shape):
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(face, props)
        p = props.CentreOfMass()
        own.append((p.X(), p.Y(), p.Z()))

    distance, nearest = cKDTree(np.asarray(own, dtype=float)).query(centres)
    return nearest.astype(np.int64), int((distance < 1e-3).sum())


def weld(
    vertices: np.ndarray, triangles: np.ndarray, tolerance: float = 1e-6, return_keep: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    """Merge vertices that sit on top of each other, so faces meeting at an edge share nodes."""
    scale = max(float(np.ptp(vertices)), 1.0)
    keys = np.round(vertices / (tolerance * scale)).astype(np.int64)
    _, first, inverse = np.unique(keys, axis=0, return_index=True, return_inverse=True)
    merged = vertices[first]
    remapped = inverse[triangles]
    keep = (
        (remapped[:, 0] != remapped[:, 1])
        & (remapped[:, 1] != remapped[:, 2])
        & (remapped[:, 2] != remapped[:, 0])
    )
    if return_keep:
        # `inverse` says where each original vertex ended up, which anything holding vertex
        # indices from before the weld needs in order to still mean the same points afterwards.
        return merged, remapped[keep], keep, inverse
    return merged, remapped[keep]


def is_closed(surface: Surface) -> tuple[bool, int]:
    """Whether every edge is shared by exactly two triangles, and how many are not."""
    edges = np.vstack(
        [
            surface.triangles[:, [0, 1]],
            surface.triangles[:, [1, 2]],
            surface.triangles[:, [2, 0]],
        ]
    )
    edges = np.sort(edges, axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    bad = int((counts != 2).sum())
    return bad == 0, bad
