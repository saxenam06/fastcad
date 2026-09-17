"""Serve the Input Console.

    .venv\\Scripts\\python.exe scripts/serve.py [port]

Run through the interpreter rather than a console script, so nothing has to be on PATH and
PowerShell's execution policy never comes into it. The package is found here the same way every
other script in this folder finds it.

With `ui/dist` built the whole console is on this one port. While working on the UI, run
`npm --prefix ui run dev` as well and use its port instead; it proxies /api back here.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(port: int) -> int:
    import uvicorn

    built = ROOT / "ui" / "dist" / "index.html"
    print(f"fastcad on http://localhost:{port}")
    print("  api      /api/assets, /api/deck, /api/deck/mesh")
    print(f"  console  {'served here' if built.exists() else 'not built — npm --prefix ui run build'}")
    uvicorn.run("fastcad.api:app", host="0.0.0.0", port=port, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 8022))
