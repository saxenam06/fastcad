"""The mesh's outside, packed the way the viewer reads it.

Only the boundary goes to the browser — the triangles on the outside and the nodes they use —
with each triangle's region. A housing of 200,000 tetrahedra is a few megabytes this way instead
of tens, and nothing the viewer draws needs the inside.

The layout is fastcae's `FCSKIN01`, so its renderer reads ours without a change:

    "FCSKIN01"          8 bytes
    uint32              header length
    uint32              vertex count
    uint32              triangle count
    header              JSON, the group names
    float32[v][3]       positions, mm
    uint32[t][3]        triangles, indices into positions
    uint16[t]           the region of each triangle, 0xffff for none
    (pad to 4 bytes)
    uint32[v]           the mesh node each vertex is
"""

from __future__ import annotations

import json
import struct

import numpy as np

NONE = 0xFFFF
MAGIC = b"FCSKIN01"


def pack(nodes: np.ndarray, triangles: np.ndarray, group: np.ndarray, names: list[str]) -> bytes:
    """Pack a boundary into the viewer's format.

    `triangles` indexes `nodes`; only the nodes actually on the boundary are sent, and each one
    remembers which mesh node it was so a result can be looked up against the full mesh later.
    """
    used, remapped = np.unique(triangles, return_inverse=True)
    positions = np.ascontiguousarray(nodes[used], dtype=np.float32)
    cells = np.ascontiguousarray(remapped.reshape(-1, 3), dtype=np.uint32)
    regions = np.where(group < 0, NONE, group).astype(np.uint16)

    header = json.dumps({"groups": list(names)}).encode("utf-8")
    out = bytearray()
    out += MAGIC
    out += struct.pack("<III", len(header), len(positions), len(cells))
    out += header
    out += positions.tobytes()
    out += cells.tobytes()
    out += regions.tobytes()
    if len(cells) % 2:
        out += b"\0\0"  # keep the node array on a four-byte boundary
    out += np.ascontiguousarray(used, dtype=np.uint32).tobytes()
    return bytes(out)


def from_deck(path) -> bytes:
    """Pack the boundary of a deck mesh written by `scripts/make_deck_ribfree.py`."""
    mesh = np.load(path)
    return pack(
        mesh["nodes"],
        mesh["tris"][:, :3].astype(np.int64),
        mesh["group"].astype(np.int64),
        [str(n) for n in mesh["names"]],
    )
