/**
 * fastcad's calls. Three questions: what the run reads, what it built, and the mesh itself.
 *
 * The mesh comes as its outside only, in the same packed layout fastcae's renderer already
 * reads, so nothing about drawing it had to be written again.
 */

import type { Skin } from "../render/fe";

export interface AssetRow {
  path: string;
  kind: string;
  bytes: number;
  in_run: boolean;
}

export interface AssetIndex {
  root: string;
  canvas: string | null;
  files: AssetRow[];
  selected: number;
  total: number;
}

export interface GroupRow {
  name: string;
  triangles: number;
  faces: number[];
  diameter_mm: number[];
  force_N: number[] | null;
}

export interface DeckInfo {
  mesh: {
    nodes: number;
    elements: number;
    unknowns: number;
    boundary_triangles: number;
    order: number;
  };
  groups: GroupRow[];
  bolts: number;
}

async function json<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path}: ${response.status} ${await response.text()}`);
  return (await response.json()) as T;
}

/** Unpack FCSKIN01. The layout is described in src/fastcad/skin.py. */
async function skin(path: string): Promise<Skin> {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  const buffer = await response.arrayBuffer();
  const magic = new TextDecoder().decode(new Uint8Array(buffer, 0, 8));
  if (magic !== "FCSKIN01") throw new Error(`unexpected mesh format "${magic}"`);
  const view = new DataView(buffer);
  const headerLength = view.getUint32(8, true);
  const vertices = view.getUint32(12, true);
  const triangles = view.getUint32(16, true);
  let offset = 20;
  const header = JSON.parse(new TextDecoder().decode(new Uint8Array(buffer, offset, headerLength)));
  offset += headerLength;
  const positions = new Float32Array(buffer, offset, vertices * 3);
  offset += vertices * 12;
  const tris = new Uint32Array(buffer, offset, triangles * 3);
  offset += triangles * 12;
  const groups = new Uint16Array(buffer, offset, triangles);
  offset += triangles * 2 + (triangles % 2) * 2;
  const nodes = new Uint32Array(buffer, offset, vertices);
  return { positions, triangles: tris, groups, nodes, groupNames: header.groups as string[] };
}

export const api = {
  assets: () => json<AssetIndex>("/api/assets"),
  deck: () => json<DeckInfo>("/api/deck"),
  deckSkin: () => skin("/api/deck/mesh"),
};
