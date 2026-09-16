/**
 * The shell: what a run reads, and the mesh it built from it.
 *
 * The same shape as fastcae's — the bar, the rail, the stage — because it is the same engineer
 * looking at the same housing, and a second layout for the same job would only be a second thing
 * to learn. The rail is `assets/` as it is on disk with the files a run opens marked, then the
 * mesh, then the regions the deck drives. The stage is the mesh itself, coloured by those regions,
 * so a bearing seat being the right patch of the right bore is something you look at.
 */

import { useEffect, useMemo, useState } from "react";
import type { AssetIndex, DeckInfo } from "../api/fastcad";
import { api } from "../api/fastcad";
import type { Skin } from "../render/fe";
import { CameraLink, FeStage } from "../stage/FeStage";
import { ART, PRODUCT, VENDOR, VIEWS } from "./product";
import type { View } from "./product";

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

export function App() {
  const [assets, setAssets] = useState<AssetIndex | null>(null);
  const [deck, setDeck] = useState<DeckInfo | null>(null);
  const [skin, setSkin] = useState<Skin | null>(null);
  const [failed, setFailed] = useState<string | null>(null);
  const [hovered, setHovered] = useState<number | null>(null);
  const [view, setView] = useState<View>("input");
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
  const canvas = assets?.canvas?.split("/").pop() ?? "no canvas";

  return (
    <div className="shell" data-open={true} style={{ gridTemplateColumns: "340px minmax(0, 1fr) 0px" }}>
      <header className="topbar">
        <img className="mark" src={ART.mark} alt="" aria-hidden="true" />
        <span className="lockup">
          <b>{VENDOR.name}</b>
          <em>{VENDOR.tagline}</em>
        </span>
        <span className="divider" />
        <span className="lockup">
          <b>{PRODUCT.name}</b>
        </span>
        <span className="divider" />
        <span className="lockup">
          <b>{canvas}</b>
          <em>{assets ? `${assets.selected} of ${assets.total} files read` : "reading…"}</em>
        </span>
        <nav className="stages main-tabs">
          {VIEWS.map((entry) => (
            <button
              key={entry.id}
              data-active={view === entry.id}
              data-ready={entry.ready}
              onClick={() => entry.ready && setView(entry.id)}
              title={entry.summary}
            >
              {entry.label}
            </button>
          ))}
        </nav>
        <span className="spacer" />
      </header>

      <div className="rail">
        <div className="rail-scroll">
          <section className="block">
            <h2>Inputs</h2>
            <p className="hint">
              Everything in <code>assets/</code>. Ticked is what a run opens — nothing else is read.
            </p>
            {assets ? (
              <ul className="files">
                {assets.files.map((f) => (
                  <li key={f.path} className={f.in_run ? "on" : "off"}>
                    <span className="tick">{f.in_run ? "✓" : "·"}</span>
                    <span className="path">{f.path}</span>
                    <span className="size">{bytes(f.bytes)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="hint">{failed ?? "reading assets…"}</p>
            )}
          </section>

          {deck ? (
            <>
              <section className="block">
                <h2>Mesh</h2>
                <dl className="facts">
                  <dt>elements</dt>
                  <dd>
                    {deck.mesh.elements.toLocaleString()} TET{deck.mesh.order === 2 ? "10" : "4"}
                  </dd>
                  <dt>nodes</dt>
                  <dd>{deck.mesh.nodes.toLocaleString()}</dd>
                  <dt>unknowns</dt>
                  <dd>{deck.mesh.unknowns.toLocaleString()}</dd>
                  <dt>boundary</dt>
                  <dd>{deck.mesh.boundary_triangles.toLocaleString()} triangles</dd>
                </dl>
              </section>

              <section className="block">
                <h2>Regions the deck drives</h2>
                <p className="hint">
                  Found by fitting each of the deck's node groups for an axis and radius, then
                  matching the CAD face that turns about the same line. The diameters are the CAD's.
                </p>
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
                            style={{
                              background: `rgb(${REGION_COLOURS[i % REGION_COLOURS.length].join(",")})`,
                            }}
                          />
                        </td>
                        <td className="name">{g.name}</td>
                        <td className="dia">{g.diameter_mm?.length ? `Ø${g.diameter_mm[0]}` : ""}</td>
                        <td className="tris">{g.triangles.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="hint">{deck.bolts} bolt holes, tied as one group.</p>
              </section>
            </>
          ) : null}
        </div>
      </div>

      <div className="stage">
        <div className="stage-body">
          <FeStage
            skin={skin}
            mode="patches"
            groupColours={colours as ([number, number, number] | null)[] | undefined}
            edges={false}
            link={link}
            frameKey="baseline"
            hoveredGroup={hovered}
            caption={skin ? null : <span>loading the mesh…</span>}
          />
        </div>
      </div>

      <footer className="titlebar">
        <span>{canvas}</span>
        <span className="spacer" />
        <span>{deck ? `${deck.mesh.elements.toLocaleString()} elements · ${deck.mesh.unknowns.toLocaleString()} unknowns` : ""}</span>
      </footer>
    </div>
  );
}

export default App;
