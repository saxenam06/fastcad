/**
 * The shell: one model, four views onto it.
 *
 * The rail is the model and does not change with the tab. A bearing seat is not a fact belonging
 * to the Mesh tab — it is an entity the deck names, the CAD holds two faces of, the mesh covers
 * with triangles and the solver wrote an answer for. Keeping those as links, and keeping the
 * links in one place, is what lets any of them be reached from wherever you happen to be.
 *
 * Every link navigates. Clicking `face 890` goes to the CAD and lights face 890; clicking a mesh
 * group goes to the Mesh and lights it. The centre is only ever the view, and says what entity is
 * under the cursor.
 *
 * What is shown is what was chosen at Extract, and the server enforces that, not this file.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import type { AssetIndex, Entity, Link } from "../api/fastcad";
import { api, Declined } from "../api/fastcad";
import { ExtractStage } from "../stage/ExtractStage";
import type { Hovered } from "../stage/FeStage";
import { CameraLink, FeStage } from "../stage/FeStage";
import { ART, INPUT_TABS, PRODUCT, VENDOR, VIEWS } from "./product";
import type { InputTab, View } from "./product";

const REGION_COLOURS: [number, number, number][] = [
  [42, 118, 175], [214, 150, 40], [120, 74, 160],
  [47, 143, 69], [200, 67, 58], [34, 102, 204], [90, 98, 108],
];
const PICKED: [number, number, number] = [15, 61, 145];

function why(error: unknown, fallback: string): string {
  if (error instanceof Declined) return error.message;
  return error ? String(error) : fallback;
}

function useLoad<T>(load: () => Promise<T>, when: boolean, again = 0) {
  const [state, setState] = useState<{ value: T | null; error: unknown }>({ value: null, error: null });
  useEffect(() => {
    if (!when) return;
    let live = true;
    load()
      .then((v) => live && setState({ value: v, error: null }))
      .catch((e) => live && setState({ value: null, error: e }));
    return () => {
      live = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [when, again]);
  return state;
}

export function App() {
  const [view, setView] = useState<View>("extract");
  const [tab, setTab] = useState<InputTab>("cad");
  const [again, setAgain] = useState(0);
  const [assets, setAssets] = useState<AssetIndex | null>(null);
  const [chosen, setChosen] = useState<string | null>(null);
  const [hover, setHover] = useState<Hovered | null>(null);
  // The setup is drawn over the mesh by default: a mesh coloured by region says where the seats
  // are, not that 330 kN goes into one of them along a particular vector.
  const [setup, setSetup] = useState(true);
  const link = useMemo(() => new CameraLink(), []);

  const open = view !== "extract";
  const reload = useCallback(() => setAgain((n) => n + 1), []);

  useEffect(() => {
    api
      .assets()
      .then((a) => {
        setAssets(a);
        if (a.extracted) setView("input");
      })
      .catch(() => undefined);
  }, [again]);

  const model = useLoad(() => api.model(), open, again);
  const cad = useLoad(() => api.cad(), open && tab === "cad", again);
  const cadSkin = useLoad(() => api.cadSkin(), open && tab === "cad", again);
  const deck = useLoad(() => api.deck(), open && tab === "mesh", again);
  const deckSkin = useLoad(() => api.deckSkin(), open && tab === "mesh", again);
  const glyphs = useLoad(() => api.deckGlyphs(), open && tab === "mesh", again);
  const results = useLoad(() => api.results(), open && tab === "results", again);
  const resultSkin = useLoad(() => api.deckSkin(), open && tab === "results", again);
  const field = useLoad(() => api.resultsField(), open && tab === "results", again);

  /** Follow a link: go where the entity lives, and select it there. */
  const go = useCallback((entity: Link | Entity) => {
    setTab(entity.tab as InputTab);
    setChosen(entity.id);
    setHover(null);
  }, []);

  const entities = model.value?.entities ?? [];
  const regions = entities.filter((e) => e.id.startsWith("deck.region."));

  // What the selection means for each view: a face id lights that face; a region lights its faces
  // on the CAD and its group on the mesh.
  const faces = useMemo(() => {
    if (!chosen) return [];
    if (chosen.startsWith("cad.face.")) return [Number(chosen.slice("cad.face.".length))];
    const owner = regions.find((e) => chosen.startsWith(e.id));
    return (owner?.facts.faces as number[] | undefined) ?? [];
  }, [chosen, regions]);

  const region = useMemo(() => {
    if (!chosen || !deck.value) return null;
    const name = chosen.split(".").slice(2).join(".");
    const at = deck.value.groups.findIndex((g) => g.name === name);
    return at < 0 ? null : at;
  }, [chosen, deck.value]);

  const cadColours = useMemo(() => {
    if (!cad.value) return undefined;
    const out: ([number, number, number] | null)[] = new Array(cad.value.faces).fill(null);
    for (const f of faces) out[f] = PICKED;
    return out;
  }, [cad.value, faces]);

  const deckColours = useMemo(
    () => deck.value?.groups.map((_, i) => REGION_COLOURS[i % REGION_COLOURS.length]),
    [deck.value],
  );

  const canvas = assets?.canvas?.split("/").pop() ?? "no canvas";
  const drawing = assets?.files.find((f) => f.in_run && f.kind === "drawing")?.path ?? null;

  return (
    <div
      className="shell"
      data-open={open}
      style={open ? { gridTemplateColumns: "360px minmax(0, 1fr) 0px" } : undefined}
    >
      <header className="topbar">
        <img className="mark" src={ART.mark} alt="" aria-hidden="true" />
        <span className="lockup"><b>{VENDOR.name}</b><em>{VENDOR.tagline}</em></span>
        <span className="divider" />
        <span className="lockup"><b>{PRODUCT.name}</b></span>
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

      {!open ? <ExtractStage onExtracted={reload} /> : null}

      {open ? (
        <>
          <div className="rail">
            <div className="rail-scroll">
              <section className="block">
                <h2>Extracted</h2>
                <p className="hint">
                  Everything a run read, and what it is linked to. Click any link to go where that
                  entity lives and see it there.
                </p>
                {model.value?.missing.map((m) => (
                  <p className="hint" key={m.artifact}>· {m.reason}, so it contributes nothing</p>
                ))}
              </section>

              {entities.map((e) => (
                <section className="block entity" key={e.id} data-on={chosen === e.id}>
                  <button className="entity-head" onClick={() => setChosen(chosen === e.id ? null : e.id)}>
                    <span className="kind">{e.kind}</span>
                    <b>{e.label}</b>
                  </button>
                  <div className="eid">{e.id}</div>

                  {e.note ? <p className="hint">{e.note}</p> : null}

                  {chosen === e.id ? (
                    <dl className="why">
                      {Object.entries(e.facts).map(([k, v]) =>
                        v === null || v === undefined || (Array.isArray(v) && !v.length) ? null : (
                          <>
                            <dt key={k}>{k.replace(/_/g, " ")}</dt>
                            <dd key={`${k}v`}>
                              {Array.isArray(v)
                                ? v.length > 8
                                  ? `${v.length} values`
                                  : v.map((x) => (typeof x === "number" ? x.toLocaleString() : x)).join(", ")
                                : typeof v === "number"
                                  ? v.toLocaleString()
                                  : String(v)}
                            </dd>
                          </>
                        ),
                      )}
                    </dl>
                  ) : null}

                  {e.links.length ? (
                    <div className="links">
                      {e.links.map((l) => (
                        <button key={l.id} className="link" onClick={() => go(l)} title={l.id}>
                          {l.label}
                        </button>
                      ))}
                    </div>
                  ) : null}
                </section>
              ))}

              {model.error ? (
                <section className="block"><p className="hint">{why(model.error, "")}</p></section>
              ) : null}
            </div>
          </div>

          <div className="stage">
            <nav className="stage-tabs">
              {INPUT_TABS.map((t) => (
                <button key={t.id} data-active={tab === t.id} onClick={() => setTab(t.id)} title={t.summary}>
                  {t.label}
                </button>
              ))}
            </nav>

            <div className="stage-body">
              {tab === "drawing" ? (
                drawing ? (
                  <object data={`/api/file/${drawing}`} type="application/pdf" className="sheet">
                    <p className="middle">The drawing is at <code>{drawing}</code>.</p>
                  </object>
                ) : (
                  <p className="middle">No drawing was chosen at Extract, so there is none to show.</p>
                )
              ) : null}

              {tab === "cad" ? (
                cadSkin.value ? (
                  <FeStage
                    skin={cadSkin.value}
                    mode="patches"
                    groupColours={cadColours}
                    edges={false}
                    link={link}
                    frameKey="cad"
                    onHover={setHover}
                    caption={
                      hover ? (
                        <span>face {hover.name} · {hover.detail}</span>
                      ) : faces.length ? (
                        <span>{faces.length} face{faces.length === 1 ? "" : "s"} lit</span>
                      ) : (
                        <span>hover a face to identify it</span>
                      )
                    }
                  />
                ) : (
                  <p className="middle">{why(cadSkin.error, "reading the CAD…")}</p>
                )
              ) : null}

              {tab === "mesh" ? (
                deckSkin.value ? (
                  <FeStage
                    skin={deckSkin.value}
                    glyphs={setup ? glyphs.value : null}
                    showGlyphs={setup}
                    mode="patches"
                    groupColours={deckColours as ([number, number, number] | null)[] | undefined}
                    edges
                    link={link}
                    frameKey="mesh"
                    hoveredGroup={region}
                    onHover={setHover}
                    caption={
                      <span className="setup-bar">
                        <button data-on={setup} onClick={() => setSetup(!setup)}>
                          {setup ? "hide setup" : "show setup"}
                        </button>
                        {hover ? (
                          <>{hover.name} · {hover.detail}</>
                        ) : glyphs.value ? (
                          <>
                            {glyphs.value.held.reduce((n, h) => n + h.count, 0)} held ·{" "}
                            {glyphs.value.rigid.length} rigid ties ·{" "}
                            {glyphs.value.distributing.length} couplings ·{" "}
                            {glyphs.value.loads.length} loads
                          </>
                        ) : (
                          <>{deck.value?.mesh?.elements.toLocaleString()} elements</>
                        )}
                      </span>
                    }
                  />
                ) : (
                  <p className="middle">{why(deckSkin.error, "loading the mesh…")}</p>
                )
              ) : null}

              {tab === "results" ? (
                field.value && resultSkin.value ? (
                  <FeStage
                    skin={resultSkin.value}
                    values={field.value}
                    mode="contour"
                    edges={false}
                    link={link}
                    frameKey="results"
                    onHover={setHover}
                    caption={
                      <span>
                        displacement, mm — peak {Math.max(...field.value.values).toFixed(4)}
                        {results.value?.chosen ? "" : " · the deck's own signals were not chosen"}
                      </span>
                    }
                  />
                ) : (
                  <p className="middle">{why(field.error, "loading the result…")}</p>
                )
              ) : null}
            </div>
          </div>

          <footer className="titlebar">
            <span>{canvas}</span>
            <span className="spacer" />
            <span>{chosen ?? `${entities.length} entities extracted`}</span>
          </footer>
        </>
      ) : null}
    </div>
  );
}

export default App;
