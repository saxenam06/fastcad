/**
 * Choose what a run reads.
 *
 * Pick the folder, open it, and tick the files. The ticks start where the rule that reads
 * extensions and locations would put them, but that rule is guessing at intent — pressing Extract
 * is what decides, and from then on the product reads what was ticked and says so.
 *
 * Nothing is copied or moved. The folder on disk is the input; this records which of it counts.
 */

import { useCallback, useEffect, useState } from "react";
import type { Folder, FolderRow } from "../api/fastcad";
import { api } from "../api/fastcad";

function size(bytes: number): string {
  if (bytes >= 1e6) return `${(bytes / 1e6).toFixed(1)} MB`;
  if (bytes >= 1e3) return `${Math.round(bytes / 1e3)} kB`;
  return `${bytes} B`;
}

interface Props {
  onExtracted: () => void;
}

export function ExtractStage({ onExtracted }: Props) {
  const [folders, setFolders] = useState<FolderRow[]>([]);
  const [active, setActive] = useState<string | null>(null);
  const [folder, setFolder] = useState<Folder | null>(null);
  const [ticked, setTicked] = useState<Set<string>>(new Set());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .folders()
      .then((r) => {
        setFolders(r.folders);
        // One folder is the common case, so it is already chosen; more than one waits to be told.
        if (r.folders.length === 1) setActive(r.folders[0].name);
      })
      .catch((e) => setError(String(e)));
  }, []);

  const open = useCallback((name: string) => {
    setError(null);
    api
      .folder(name)
      .then((f) => {
        setFolder(f);
        setTicked(new Set(f.files.filter((x) => x.chosen).map((x) => x.path)));
      })
      .catch((e) => setError(String(e)));
  }, []);

  const toggle = (path: string) =>
    setTicked((current) => {
      const next = new Set(current);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });

  const extract = () => {
    setBusy(true);
    setError(null);
    api
      .extract([...ticked])
      .then(() => onExtracted())
      .catch((e) => {
        setError(String(e));
        setBusy(false);
      });
  };

  return (
    <div className="upload">
      <div className="upload-inner">
        {folders.length > 1 ? (
          <div className="project-tabs">
            {folders.map((f) => (
              <button key={f.name} data-active={f.name === active} onClick={() => { setActive(f.name); setFolder(null); }}>
                {f.path}
              </button>
            ))}
          </div>
        ) : null}

        {!folder ? (
          <div className="panel">
            <div className="panel-head">
              <h1>{active ? `assets/${active}` : "Choose a folder"}</h1>
              <span className="mono dim">
                {active
                  ? `${folders.find((f) => f.name === active)?.files ?? 0} files`
                  : "under assets/"}
              </span>
            </div>
            <p className="hint">
              The folder is the input. Opening it lists what is there so the files a run reads can
              be ticked — nothing is copied, and nothing outside it is ever read.
            </p>
            {error ? <div className="error-inline">{error}</div> : null}
            <div className="panel-foot">
              <button className="primary" disabled={!active} onClick={() => active && open(active)}>
                Upload
              </button>
              {!active ? <span className="dim">pick a folder</span> : null}
            </div>
          </div>
        ) : (
          <div className="panel">
            <div className="panel-head">
              <h1>{folder.path}</h1>
              <span className="mono dim">
                {ticked.size} of {folder.files.length} chosen
              </span>
            </div>
            <p className="hint">
              Ticked is what a run will read. The ticks start where the file's kind and place
              suggest; change any of them — what you press Extract with is what the product uses.
            </p>

            <div className="fields">
              {folder.files.map((f) => (
                <label className="pick" key={f.path} data-on={ticked.has(f.path)}>
                  <input
                    type="checkbox"
                    checked={ticked.has(f.path)}
                    onChange={() => toggle(f.path)}
                  />
                  <span className="mono path">{f.path}</span>
                  <span className="kind dim">{f.kind}</span>
                  <span className="mono dim size">{size(f.bytes)}</span>
                </label>
              ))}
            </div>

            {error ? <div className="error-inline">{error}</div> : null}

            <div className="panel-foot">
              <button className="primary" disabled={ticked.size === 0 || busy} onClick={extract}>
                {busy ? "Extracting…" : "Extract"}
              </button>
              <button className="ghost" onClick={() => setFolder(null)} disabled={busy}>
                Back
              </button>
              {ticked.size === 0 ? <span className="dim">nothing chosen</span> : null}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
