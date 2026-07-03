#!/usr/bin/env python3
"""Write BDD workflow artifacts from structured JSON.

Usage:
  python .claude/scripts/render_bdd_artifact.py phase1 input.json output_dir
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def render_phase1(data: dict[str, object], out_dir: Path) -> tuple[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "test-layer-analysis.json"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return (json_path,)


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] != "phase1":
        print(__doc__.strip(), file=sys.stderr)
        return 2
    input_path = Path(sys.argv[2])
    out_dir = Path(sys.argv[3])
    data = json.loads(input_path.read_text(encoding="utf-8"))
    paths = render_phase1(data, out_dir)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
