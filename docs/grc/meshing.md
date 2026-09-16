# Meshing the housing, and keeping CAD faces attached to it

**Measured 2026-09-16.** Every number here came from a run on this repo's canvas, not from a paper.

## The problem

A bearing seat's coupling has to be applied to exactly the nodes on that bore. So every boundary
triangle in the volume mesh needs an auditable owner: the CAD face it came from.

The chain has three links:

```
CAD face  →  surface triangle  →  tet boundary face  →  mesh group
```

The first link is free: gmsh meshes each CAD face in its own parameter space, so a triangle is
*born* owning its face. The second is where it breaks — every volume mesher that improves a mesh
rebuilds its boundary, and the labels do not come with it.

## What works

Five steps. Each one was tried alone first, and alone each one fails.

```
1. gmsh 2D, face by face          labels born, not inferred
2. UV patch the faces gmsh skips  meshed on their own surface, not capped
3. weld 0.5 mm + collapse 3.0 mm  removes the slivers that become self-intersections
4. MeshFix                        local damage only
5. gmsh 3D on discrete surfaces   one entity per CAD face, so labels survive
```

On the rib-free canvas, at 20 mm:

| after | triangles | bad edges | self-intersecting |
|---|---|---|---|
| 1 + 2 | 98,314 | none | 106 |
| 3 | 92,450 | 28 open, 14 triple | 113 |
| 4 | 92,122 | **none** | **4** |
| 5 | 198,577 tets, 55,478 nodes | — | 1,538 of 1,538 faces still classified |

**Association is inherited, not recovered.** No projection, no nearest-neighbour search.

### Why each step is needed

**Step 2 — the faces gmsh cannot parametrise.** Four on this canvas (five on the production one):
full cylinders and a cone whose seam leaves their parameter-space boundary unclosed. gmsh meshes
their *edges* though, and those nodes are shared with the faces that did mesh, so the missing
triangles can be built on exactly those nodes and are conformal by construction. See
`src/fastcad/patching.py`.

**Step 3 — weld and collapse.** agenticCAE's pass (`mesh/surface.py`), and the one thing we had
been skipping all along. A proximity weld merges nodes that are merely near each other; an edge
collapse then merges nodes that already share an edge, shortest first, so it cannot bridge a wall
however large the tolerance. Together they remove the short-edge slivers that *become*
self-intersections. Both bounds matter: above ~2 mm the weld starts stitching opposite faces of a
web together, and past ~3 mm the collapse stops helping.

**Step 4 — MeshFix, and why it is safe here.** agenticCAE's docs record MeshFix flattening holes
up to 242 mm and biasing two bearing-seat tilts by 20–53%. That is real, and it is a consequence
of *ordering*, not of the tool: there, MeshFix was given four genuine holes to close and spanned
them with flat fans. Here step 2 has already closed those on their own surfaces, so all that is
left is folds and duplicates a few millimetres wide. Measured: **it moved vertices 0.000 mm.**

**Step 5 — one discrete surface per CAD face.** A single discrete surface for the whole part
would mesh just as well and lose every label. Adding one entity per face costs nothing and means
gmsh still reports its boundary triangles per entity after the 3D mesh.

## What does not work, and why

All of these were tried on both castings.

| route | result |
|---|---|
| gmsh 3D straight from the B-rep | 0 tets. 4–5 faces unparametrisable, unchanged by all 6 of gmsh's 2D algorithms, by STEP AP242 and IGES exports, and by `ShapeDivideClosed` / `ShapeFix_Shape` / `ShapeFix_Face` / `UnifySameDomain` |
| Netgen | surface meshes all faces with native CAD descriptors, then aborts: "boundary mesh is overlapping" |
| TetGen with facet markers | crashes. Needs a non-self-intersecting PLC, which neither casting gives |
| OCCT defeaturing to feed those | worse: 190 small faces removed, 5 bad faces became 11, self-intersections 442 → 458 |
| fTetWild `--tag` | verified on a fixture: tags are for boolean regions and never reach the output file |

**The common cause.** Both castings' tessellations self-intersect at ~0.08%, and the rate is
constant across every mesh density (190 at 233k triangles, 442 at 584k, 558 at 690k). It is not a
grading artifact and no meshing setting reaches zero. Every exact-preserving mesher requires a
clean PLC, so all of them fail for the same reason — which is why the repair pass, not a
different mesher, is the answer.

## Two defects that pass every check

Worth knowing because both were found late, after hours of meshing on top of them.

**Curvature sizing is not optional.** With `Mesh.MeshSizeFromCurvature = 0`, a Ø10 hole gets
elements wider than the hole and collapses into a flat, double-sided ribbon — 36 edges shared by
four triangles on the production canvas. The mesh looks fine and the bore is a hexagon. Either
turn curvature sizing on, or let the weld-and-collapse pass clean up after it, but not neither.

**A surface can be manifold and still be unusable.** pymeshlab reported 0 non-manifold edges, 0
boundary edges, 0 holes — and Manifold rejected the same surface as `NotManifold`, because 62
edges had their two triangles traversing them the *same* way. An outward normal is undefined
across a winding flip. `orient_consistently` in `src/fastcad/geometry.py` fixes it in 4 s, and
nothing else we ran detects it.

## The canvas

`assets/target/cad/housing_ribfree.brep`, 1,753 faces, 121.3737 dm³ — the production casting with
its ribs removed, and the geometry agenticCAE generated and solved 490 designs on.

It is not cleaner than the production export in the way one would expect: 4 unparametrisable faces
against 5, and the same self-intersection rate. What it has is **no non-manifold edges** where the
production export has 36–43, and that is the property the volume meshers need.

## The baseline

198,577 TET10 elements, 1,067,028 unknowns. Code_Aster, 89 s. Reactions balance the applied loads
to 0.1 N in 306 kN.

Peak displacement **21.32 mm**, concentrated in the annulus around the main bearing bore
(radius 270→392 mm, exactly that bore's axial extent). That is not a defect: the deleted ribs were
the load path from that bore to the outer wall, and 330 kN goes through it. Putting that structure
back is what fastcad is for, so the baseline is deliberately a poor design.

Treat 21.32 mm as a stiffness index for ranking variants, not a physical prediction — a linear
solve at that deflection is well past yield locally.

**The pipeline is validated on ribbed geometry, not on this.** Run on the production canvas it
gives 0.3658 mm against agenticCAE's recorded 0.3906 mm for its design e56235 — 6% apart. That is
what says the chain is right; the rib-free number is then the geometry's own answer.

## Regions

The six bearing seats and 25 bolt holes are found from the baseline deck's own node groups, never
from a table: each group's nodes are fitted for an axis and radius, and matched to the CAD face
turning about the same line at the same radius. See `src/fastcad/deck.py`, `regions.py`.

Resolved diameters: Ø541.0, Ø360.03, Ø180.0, Ø200.0, Ø180.0, Ø272.0, and Ø26.0/26.5 for the bolts,
all confirmed against the CAD rather than asserted.

Two traps found doing this:

- **the axis is not the direction the nodes vary least in.** That is true only for a bore wider
  than it is deep. A bolt hole is the opposite, which is why all 25 went missing at first. On a
  cylinder the two radial spreads are equal and the axial one is its own number, so the axis is
  the odd one out either way.
- **the centroid of a group is not a point on its axis** when the nodes cover the bore unevenly.
  Fitting the circle instead moved the match error from ~2.6 mm to ~0.1 mm.

## Open

- **The deck's labels are codes** — `BORE_AX1_S4`, not "HSS rear bearing seat" — because that deck
  was machine-written. There is no vocabulary in the artifacts to extract, so the names have to be
  asked for at sign-off.
- **`solve_aster.py` carries a hardcoded seat-name → xy table.** It works because our names match,
  and it breaks the moment a bore moves. It must read the axis from the measured region.
- **Element count is driven by the boundary.** A graded size field — fine on seats and bolt holes,
  coarse on plain walls — is the lever if a variant needs to stay under the solver's card limit.
