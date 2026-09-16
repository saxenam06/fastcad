"""agenticCAE's repair chain on the rib-free housing, with the parts we know were damaging replaced.

agenticCAE solved 490 designs on this geometry, and not because it is clean — measured, it has 4
faces gmsh cannot parametrise and 260 self-intersecting triangles, much like the production part.
It worked because of a repair pass we had been skipping entirely: weld nodes that are merely near
each other, then collapse the short edges that leaves, which is what removes the slivers that
become self-intersections.

Two things are replaced. MeshFix, which closed the unparametrisable faces with flat fans and
flattened holes up to 242 mm, is replaced by meshing those faces on their own surfaces. And the
volume mesh is built with one discrete surface per CAD face rather than one for the whole part,
so gmsh keeps every boundary triangle classified on the face it came from — association inherited
rather than projected.

    python scripts/ribfree_pipeline.py [element_mm]
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastcad.geometry import orient_consistently, solid_volume, surface_mesh  # noqa: E402

CANVAS = ROOT / "assets" / "target" / "cad" / "housing_ribfree.brep"

#: The settings that work, found by measurement on 2026-09-16 and kept here rather than passed in,
#: so the baseline is the same mesh every time it is built.
SIZE_MM = 20.0          # agenticCAE's element size, so the result is comparable with its designs
MIN_MM = 4.0            # size/5, as agenticCAE used
CURVATURE = 0           # off: the repair pass below absorbs the small-hole collapse this causes
WELD_MM = 0.5           # merge nodes merely NEAR each other; bounded by the thinnest wall
COLLAPSE_MM = 3.0       # then merge nodes sharing an edge; this is what removes the slivers
MAX_CLUSTER = 4         # refuse a merge that would pull a whole patch onto one point


def read_brep(path: Path):
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape

    shape = TopoDS_Shape()
    BRepTools.Read_s(shape, str(path), BRep_Builder())
    return shape


def merge(vertices, triangles, pairs, max_cluster=None):
    """Collapse each pair of nodes into one, and say which triangles survived.

    agenticCAE's `_union_merge` (mesh/surface.py), with the surviving-triangle mask returned as
    well, because here each triangle carries the CAD face it belongs to and that has to come
    through the merge with it.
    """
    parent = np.arange(len(vertices))
    size = np.ones(len(vertices), np.int64)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i, j in pairs:
        ri, rj = find(int(i)), find(int(j))
        if ri == rj:
            continue
        if max_cluster is not None and size[ri] + size[rj] > max_cluster:
            continue  # refuse: this merge would pull a whole patch onto one point
        lo, hi = min(ri, rj), max(ri, rj)
        parent[hi] = lo
        size[lo] += size[hi]

    root = np.array([find(i) for i in range(len(vertices))])
    unique, inverse = np.unique(root, return_inverse=True)
    out = np.zeros((len(unique), 3))
    count = np.zeros(len(unique))
    np.add.at(out, inverse, vertices)
    np.add.at(count, inverse, 1)
    out /= count[:, None]
    cells = inverse[triangles]
    keep = (cells[:, 0] != cells[:, 1]) & (cells[:, 1] != cells[:, 2]) & (cells[:, 0] != cells[:, 2])
    return out, cells[keep], keep


def repair(vertices, triangles, faces):
    """Weld what is near, then collapse what is short. Labels follow their triangles."""
    from scipy.spatial import cKDTree

    vertices, triangles, keep = merge(
        vertices, triangles, cKDTree(vertices).query_pairs(WELD_MM)
    )
    faces = faces[keep]

    edges = np.unique(
        np.sort(np.vstack([triangles[:, [0, 1]], triangles[:, [1, 2]], triangles[:, [2, 0]]]), axis=1),
        axis=0,
    )
    length = np.linalg.norm(vertices[edges[:, 0]] - vertices[edges[:, 1]], axis=1)
    order = np.argsort(length)  # shortest first, so a chain collapses inward
    vertices, triangles, keep = merge(
        vertices, triangles, edges[order][length[order] < COLLAPSE_MM], MAX_CLUSTER
    )
    faces = faces[keep]

    # Collapsing pulls neighbouring faces together until two of their triangles become the same
    # three nodes. Dropping the degenerate ones does not catch that: both are well formed, they
    # just sit on top of each other, on different CAD faces. gmsh calls them overlapping facets
    # and refuses the volume; every edge they share also counts four triangles instead of two.
    _, first = np.unique(np.sort(triangles, axis=1), axis=0, return_index=True)
    first.sort()
    dropped = len(triangles) - len(first)
    if dropped:
        print(f"  dropped {dropped} duplicate triangles left by the collapse")
    return vertices, triangles[first], faces[first]


def report(label, vertices, triangles):
    import collections

    import pymeshlab

    e = np.sort(np.vstack([triangles[:, [0, 1]], triangles[:, [1, 2]], triangles[:, [2, 0]]]), axis=1)
    _, counts = np.unique(e, axis=0, return_counts=True)
    bad = {k: v for k, v in sorted(collections.Counter(counts.tolist()).items()) if k != 2}
    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(vertex_matrix=vertices, face_matrix=triangles.astype(np.int32)))
    ms.compute_selection_by_self_intersections_per_face()
    crossing = ms.current_mesh().selected_face_number()
    print(f"{label}: {len(triangles):,} triangles, bad edges {bad or 'none'}, self-int {crossing}")
    return crossing, bad


def fill_volume(vertices, triangles, faces, size):
    """Tets inside the surface, with one discrete gmsh surface per CAD face.

    Keeping the faces apart is the whole point: gmsh then reports its boundary triangles per
    entity after the 3D mesh, so each one still names the CAD face it came from, and no
    projection is needed to find the bearing seats again.
    """
    import gmsh

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.AbortOnError", 0)
        gmsh.option.setNumber("General.NumThreads", 12)
        gmsh.model.add("ribfree")
        present = np.unique(faces)
        tags = {}
        for k, face in enumerate(present):
            tag = gmsh.model.addDiscreteEntity(2)
            tags[int(face)] = tag
            if k == 0:  # every node lives on the first entity; elements may reference any of them
                gmsh.model.mesh.addNodes(
                    2, tag, np.arange(1, len(vertices) + 1), vertices.ravel()
                )
        for face, tag in tags.items():
            cells = triangles[faces == face]
            gmsh.model.mesh.addElementsByType(tag, 2, [], (cells + 1).ravel())
        loop = gmsh.model.geo.addSurfaceLoop(list(tags.values()))
        gmsh.model.geo.addVolume([loop])
        gmsh.model.geo.synchronize()
        gmsh.option.setNumber("Mesh.MeshSizeMax", size)
        gmsh.option.setNumber("Mesh.Algorithm3D", 10)
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.logger.start()
        try:
            gmsh.model.mesh.generate(3)
        except Exception as error:  # noqa: BLE001 - gmsh reports through its log
            print("   3D raised:", str(error)[:120])
        kinds, _, _ = gmsh.model.mesh.getElements(3)
        errors = [line for line in gmsh.logger.get() if line.startswith("Error")]
        if 4 not in list(kinds):
            return None, 0, len(tags), errors

        node_tags, coords, _ = gmsh.model.mesh.getNodes()
        index = np.zeros(int(np.max(node_tags)) + 1, np.int64)
        index[np.asarray(node_tags, np.int64)] = np.arange(len(node_tags))
        nodes = np.asarray(coords, float).reshape(-1, 3)
        _, cells = gmsh.model.mesh.getElementsByType(4)
        cells = index[np.asarray(cells, np.int64).reshape(-1, 4)]

        # The boundary, still sorted by the CAD face each triangle belongs to. This is the whole
        # point of meshing with one discrete surface per face: the label is read off the entity
        # the triangle is still classified on, not worked out again from where it sits.
        skin, skin_face = [], []
        classified = 0
        for face, tag in tags.items():
            kinds2, _, blocks = gmsh.model.mesh.getElements(2, tag)
            for kind, block in zip(kinds2, blocks):
                if kind == 2:
                    cell = index[np.asarray(block, np.int64)].reshape(-1, 3)
                    skin.append(cell)
                    skin_face.append(np.full(len(cell), face, np.int64))
                    classified += 1
        return (
            (nodes, cells, np.vstack(skin), np.concatenate(skin_face)),
            classified,
            len(tags),
            errors,
        )
    finally:
        gmsh.finalize()


def main(size: float) -> int:
    import os

    curvature = int(os.environ.get("MESH_CURVATURE", CURVATURE))
    min_size = float(os.environ.get("MESH_MIN", MIN_MM))
    shape = read_brep(CANVAS)
    print(f"canvas: {CANVAS.name}, volume {solid_volume(shape) / 1e6:.4f} dm3 "
          f"(size {size} mm, min {min_size} mm, curvature {curvature})")

    t0 = time.time()
    surface, info = surface_mesh(
        CANVAS, shape, size=size, min_size=min_size, curvature=curvature, patch="surface"
    )
    print(f"surface meshed in {time.time() - t0:.0f} s: {info}")
    vertices = surface.vertices
    triangles = orient_consistently(vertices, surface.triangles)
    faces = surface.face_of_triangle
    report("  after gmsh + UV patch", vertices, triangles)

    t0 = time.time()
    vertices, triangles, faces = repair(vertices, triangles, faces)
    triangles = orient_consistently(vertices, triangles)
    print(f"  repaired in {time.time() - t0:.0f} s (weld {WELD_MM} mm, collapse {COLLAPSE_MM} mm)")
    crossing, bad = report("  after weld + collapse", vertices, triangles)

    # MeshFix, but only for the damage the collapse itself left. agenticCAE had to give it four
    # real holes to close and it spanned them with flat fans up to 242 mm across, which biased two
    # seat tilts by 20-53%. Here the UV patch has already closed those on their own surfaces, so
    # what is left for MeshFix is folds and duplicates a few millimetres wide. How far it actually
    # moves the surface is measured rather than trusted, and the labels are transferred back by
    # projection because MeshFix renumbers everything.
    import pymeshfix
    from scipy.spatial import cKDTree

    t0 = time.time()
    before = vertices[triangles].mean(axis=1)
    fixer = pymeshfix.MeshFix(vertices.astype(np.float64), triangles.astype(np.int32))
    fixer.repair(joincomp=True, remove_smallest_components=False)
    fixed_v = np.asarray(fixer.points, np.float64)
    fixed_t = np.asarray(fixer.faces, np.int64).reshape(-1, 3)
    moved, _ = cKDTree(vertices).query(fixed_v)
    _, nearest = cKDTree(before).query(fixed_v[fixed_t].mean(axis=1))
    faces = faces[nearest]
    vertices, triangles = fixed_v, orient_consistently(fixed_v, fixed_t)
    print(
        f"  MeshFix in {time.time() - t0:.0f} s: {len(triangles):,} triangles, "
        f"its vertices within {moved.max():.3f} mm of the surface it was given"
    )
    report("  after MeshFix", vertices, triangles)

    t0 = time.time()
    mesh, classified, total, errors = fill_volume(vertices, triangles, faces, size)
    if mesh is None:
        print(f"  gmsh 3D FAILED in {time.time() - t0:.0f} s; {len(errors)} errors")
        for line in errors[:3]:
            print("     ", line[:100])
        return 1

    nodes, cells, skin, skin_face = mesh
    print(
        f"  gmsh 3D in {time.time() - t0:.0f} s: {len(cells):,} tets, {len(nodes):,} nodes; "
        f"{classified} of {total} CAD faces still carry boundary triangles"
    )
    print(f"  TET10 would be about {3 * (len(nodes) + 6 * len(cells) // 2):,} unknowns")

    out = ROOT / "data" / "analysis" / "mesh" / "ribfree_tet4.npz"
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, nodes=nodes, tets=cells, skin=skin, skin_face=skin_face)
    print(f"  saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(float(sys.argv[1]) if len(sys.argv) > 1 else SIZE_MM))
