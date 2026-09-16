/**
 * The shell: what a run reads, and the mesh it built from it.
 *
 * The same shape as fastcae's — the bar, the rail, the stage — because it is the same engineer
 * looking at the same housing, and a second layout for the same job would only be a second thing
 * to learn. The rail is `assets/` as it is on disk with the files a run opens marked, then the
 * mesh, then the regions the deck drives. The stage is the mesh itself, coloured by those regions,
 * so a bearing seat being the right patch of the right bore is something you look at.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import type { AssetIndex, DeckInfo } from "../api/fastcad";
import { api } from "../api/fastcad";
import type { Skin } from "../render/fe";
import { ExtractStage } from "../stage/ExtractStage";
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
  const [opened, setOpened] = useState<string | null>(null);
  const [view, setView] = useState<View>("extract");
  const link = useMemo(() => new CameraLink(), []);

  const load = useCallback(() => {
    // Failures are shown, not swallowed. A stage that says "loading" forever because a fetch threw
    // is worse than one that says what went wrong.
    api.assets().then(setAssets).catch((e) => setFailed(String(e)));
    api.deck().then(setDeck).catch((e) => setFailed(String(e)));
    api.deckSkin().then(setSkin).catch((e) => setFailed(String(e)));
  }, []);

  useEffect(() => {
    // Straight to Input if something was extracted before; otherwise there is nothing to show yet.
    api
      .assets()
      .then((a) => {
        setAssets(a);
        if (a.extracted) {
          setView("input");
          load();
        }
      })
      .catch((e) => setFailed(String(e)));
  }, [load]);

  const extracted = () => {
    setView("input");
    load();
  };

  const colours = useMemo(
    () => (deck ? deck.groups.map((_, i) => REGION_COLOURS[i % REGION_COLOURS.length]) : undefined),
    [deck],
  );
  const canvas = assets?.canvas?.split("/").pop() ?? "no canvas";

  const open = view !== "extract";

  return (
    <div
      className="shell"
      data-open={open}
      // Only once something is extracted: Extract is one column, and an inline three-column
      // template would override the rule that makes it so.
      style={open ? { gridTemplateColumns: "340px minmax(0, 1fr) 0px" } : undefined}
    >
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
              // Input and after need something extracted first; Extract itself is always there.
              disabled={!entry.ready || (entry.id !== "extract" && !assets?.extracted)}
              onClick={() => entry.ready && setView(entry.id)}
              title={entry.summary}
            >
              {entry.label}
            </button>
          ))}
        </nav>
        <span className="spacer" />
      </header>

      {!open ? <ExtractStage onExtracted={extracted} /> : null}

      {open ? (
      <>
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
                      <>
                        <tr
                          key={g.name}
                          className={hovered === i ? "lit" : undefined}
                          onMouseEnter={() => setHovered(i)}
                          onMouseLeave={() => setHovered(null)}
                          onClick={() => setOpened(opened === g.name ? null : g.name)}
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
                        {opened === g.name ? (
                          <tr key={`${g.name}-why`}>
                            <td />
                            <td colSpan={3}>
                              <dl className="why">
                                <dt>matched on</dt>
                                <dd>
                                  {g.faces.length} CAD face{g.faces.length === 1 ? "" : "s"}
                                  {g.faces.length <= 6 ? ` (${g.faces.join(", ")})` : ""}
                                </dd>
                                <dt>axis agreed to</dt>
                                <dd>{g.match_mm?.toFixed(3)} mm</dd>
                                {g.axis ? (
                                  <>
                                    <dt>axis</dt>
                                    <dd>({g.axis.map((v) => v.toFixed(3)).join(", ")})</dd>
                                    <dt>through</dt>
                                    <dd>({g.axis_point?.map((v) => v.toFixed(1)).join(", ")})</dd>
                                  </>
                                ) : null}
                                <dt>fitted from</dt>
                                <dd>{g.deck_nodes?.toLocaleString()} deck nodes</dd>
                                {g.deck_bands?.map((b, k) => (
                                  <>
                                    <dt key={`b${k}`}>band {k + 1}</dt>
                                    <dd key={`bv${k}`}>
                                      Ø{b.diameter_mm} × {b.length_mm} mm, {b.nodes.toLocaleString()} nodes
                                    </dd>
                                  </>
                                ))}
                                <dt>patch area</dt>
                                <dd>{g.area_mm2?.toLocaleString()} mm²</dd>
                                {g.force_N ? (
                                  <>
                                    <dt>force</dt>
                                    <dd>({g.force_N.map((v) => Math.round(v).toLocaleString()).join(", ")}) N</dd>
                                    <dt>applied at</dt>
                                    <dd>{g.reference}</dd>
                                  </>
                                ) : null}
                                {g.count ? (
                                  <>
                                    <dt>holes</dt>
                                    <dd>{g.count}, tied to their own reference nodes</dd>
                                  </>
                                ) : null}
                              </dl>
                            </td>
                          </tr>
                        ) : null}
                      </>
                    ))}
                  </tbody>
                </table>
                <p className="hint">
                  Click a region for what the match was based on. {deck.bolts} bolt holes are driven
                  as one group.
                </p>
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
            caption={skin ? null : <span>{failed ?? "loading the mesh…"}</span>}
          />
        </div>
      </div>

      <footer className="titlebar">
        <span>{canvas}</span>
        <span className="spacer" />
        <span>{deck ? `${deck.mesh.elements.toLocaleString()} elements · ${deck.mesh.unknowns.toLocaleString()} unknowns` : ""}</span>
      </footer>
      </>
      ) : null}
    </div>
  );
}

export default App;
