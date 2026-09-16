/**
 * The Input Console: what this run reads, and what it made of it.
 *
 * The left column is `assets/` as it is on disk, with the files a run actually opens marked. The
 * right is the mesh built from them, coloured by the regions the deck drives — so a bearing seat
 * being the right patch of the right bore is something you look at, not something you take on
 * trust.
 */

import { useEffect, useMemo, useState } from "react";
import type { AssetIndex, DeckInfo } from "../api/fastcad";
import { api } from "../api/fastcad";
import type { Skin } from "../render/fe";
import { CameraLink, FeStage } from "../stage/FeStage";

/** One colour per region, so a seat is told apart from its neighbour at a glance. */
const REGION_COLOURS: [number, number, number][] = [
  [42, 118, 175],
  [214, 150, 40],
  [120, 74, 160],
  [47, 143, 69],
  [200, 67, 58],
  [34, 102, 204],
  [90, 98, 108],
];

function bytes(n: number): string {
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)} MB`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)} kB`;
  return `${n} B`;
}

export default function App() {
  const [assets, setAssets] = useState<AssetIndex | null>(null);
  const [deck, setDeck] = useState<DeckInfo | null>(null);
  const [skin, setSkin] = useState<Skin | null>(null);
  const [failed, setFailed] = useState<string | null>(null);
  const [hovered, setHovered] = useState<number | null>(null);
  const link = useMemo(() => new CameraLink(), []);

  useEffect(() => {
    api.assets().then(setAssets).catch((e) => setFailed(String(e)));
    api.deck().then(setDeck).catch(() => undefined);
    api.deckSkin().then(setSkin).catch(() => undefined);
  }, []);

  const colours = useMemo(
    () => (deck ? deck.groups.map((_, i) => REGION_COLOURS[i % REGION_COLOURS.length]) : undefined),
    [deck],
  );

  return (
    <div className="console">
      <aside>
        <h1>fastcad</h1>
        <p className="lede">
          What this run reads, and the mesh it built. Nothing here is typed in: the regions come
          from the solver deck, the sizes from the CAD.
        </p>

        <h2>
          Inputs {assets ? <span className="count">{assets.selected} of {assets.total} read</span> : null}
        </h2>
        {assets ? (
          <ul className="files">
            {assets.files.map((f) => (
              <li key={f.path} className={f.in_run ? "on" : "off"}>
                <span className="tick">{f.in_run ? "✓" : ""}</span>
                <span className="path">{f.path}</span>
                <span className="kind">{f.kind}</span>
                <span className="size">{bytes(f.bytes)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="waiting">{failed ?? "reading assets…"}</p>
        )}

        {deck ? (
          <>
            <h2>Mesh</h2>
            <dl className="facts">
              <dt>elements</dt><dd>{deck.mesh.elements.toLocaleString()} TET{deck.mesh.order === 2 ? "10" : "4"}</dd>
              <dt>nodes</dt><dd>{deck.mesh.nodes.toLocaleString()}</dd>
              <dt>unknowns</dt><dd>{deck.mesh.unknowns.toLocaleString()}</dd>
              <dt>boundary</dt><dd>{deck.mesh.boundary_triangles.toLocaleString()} triangles</dd>
            </dl>

            <h2>Regions the deck drives</h2>
            <table className="regions">
              <tbody>
                {deck.groups.map((g, i) => (
                  <tr
                    key={g.name}
                    className={hovered === i ? "lit" : undefined}
                    onMouseEnter={() => setHovered(i)}
                    onMouseLeave={() => setHovered(null)}
                  >
                    <td>
                      <span
                        className="swatch"
                        style={{ background: `rgb(${REGION_COLOURS[i % REGION_COLOURS.length].join(",")})` }}
                      />
                    </td>
                    <td className="name">{g.name}</td>
                    <td className="dia">{g.diameter_mm?.length ? `Ø${g.diameter_mm[0]}` : ""}</td>
                    <td className="tris">{g.triangles.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="note">
              {deck.bolts} bolt holes, tied together as one group. Diameters are the CAD's own,
              matched to the deck's node groups by axis and radius.
            </p>
          </>
        ) : null}
      </aside>

      <main>
        <FeStage
          skin={skin}
          mode="patches"
          groupColours={colours as ([number, number, number] | null)[] | undefined}
          edges={false}
          link={link}
          frameKey="baseline"
          hoveredGroup={hovered}
          caption={skin ? null : <span>building the mesh view…</span>}
        />
      </main>
    </div>
  );
}
