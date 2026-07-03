#!/usr/bin/env python3
"""Render BDD workflow artifacts from structured JSON.

Usage:
  python .claude/scripts/render_bdd_artifact.py phase1 input.json output_dir
  python .claude/scripts/render_bdd_artifact.py phase2 input.json output_dir
  python .claude/scripts/render_bdd_artifact.py schema phase1
  python .claude/scripts/render_bdd_artifact.py schema phase2
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PHASE1_SCHEMA: dict[str, Any] = {
    "storyId": "...",
    "title": "...",
    "moduleOrDomain": "...",
    "primaryActor": "...",
    "source": "...",
    "revisionCount": 0,
    "artifactVersion": "phase-1",
    "assumptions": [],
    "acceptanceCriteria": [{"id": "AC1", "text": "...", "notes": "..."}],
    "testPoints": [
        {
            "id": "TP-API-001",
            "layer": "API",
            "type": "positive",
            "priority": "smoke",
            "summary": "...",
            "acsCovered": ["AC1"],
            "tags": ["@api", "@smoke", "@positive"],
        }
    ],
    "layeringRationale": [
        {"id": "TP-API-001", "whyThisLayer": "...", "whyNotHigherOrLower": "..."}
    ],
    "coverageMatrix": [{"ac": "AC1", "coveredBy": ["TP-API-001"], "notes": "..."}],
    "uncoveredAcs": [],
    "risksAndGaps": [],
    "reviewHighlights": [],
}


PHASE2_SCHEMA: dict[str, Any] = {
    "storyId": "...",
    "featureFiles": [
        {
            "path": "features/api/domain/feature.feature",
            "mode": "create",
            "scenarioCount": 1,
            "smokeCount": 1,
            "regressionCount": 0,
        }
    ],
    "lowerLayerTestPoints": [
        {
            "id": "TP-UIC-001",
            "layer": "UI Component",
            "summary": "...",
            "acsCovered": ["AC1"],
            "reason": "Covered by component-level test, not BDD feature file",
        }
    ],
    "apiFeatureContent": "...",
    "uiFeatureContent": "...",
    "coverageMatrix": [{"ac": "AC1", "summary": "...", "coveredBy": ["@TC-MOD-API-001"]}],
    "uncoveredAcs": [],
    "authoringNotes": {
        "apiSnippetCatalog": "...",
        "uiSnippetCatalog": "...",
        "newSteps": [],
        "fileModeNotes": [],
    },
}


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def bullet(items: list[Any]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {text(item)}" for item in items)


def table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        rows = [["" for _ in headers]]
    header = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = "\n".join("| " + " | ".join(text(cell).replace("\n", "<br>") for cell in row) + " |" for row in rows)
    return "\n".join([header, sep, body])


def count_points(points: list[dict[str, Any]], *, layer: str | None = None, priority: str | None = None) -> int:
    total = 0
    for point in points:
        if layer and str(point.get("layer", "")).lower() != layer.lower():
            continue
        if priority and str(point.get("priority", "")).lower() != priority.lower():
            continue
        total += 1
    return total


def render_phase1(data: dict[str, Any], out_dir: Path) -> tuple[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "test-layer-analysis.json"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return (json_path,)


def render_phase2(data: dict[str, Any], out_dir: Path) -> tuple[Path]:
    feature_files = [f for f in as_list(data.get("featureFiles")) if isinstance(f, dict)]
    lower = [p for p in as_list(data.get("lowerLayerTestPoints")) if isinstance(p, dict)]
    coverage = [c for c in as_list(data.get("coverageMatrix")) if isinstance(c, dict)]
    notes = data.get("authoringNotes") or {}
    if not isinstance(notes, dict):
        notes = {"other": notes}

    md = f"""# BDD Feature Generation Result

## Feature Files To Write

{bullet([f'{f.get("path")} -> mode: {f.get("mode")} | {f.get("scenarioCount", 0)} scenarios (@smoke: {f.get("smokeCount", 0)}, @regression: {f.get("regressionCount", 0)})' for f in feature_files])}

## Lower-Layer Test Points Not Authored As Feature Files

{table(["TP ID", "Layer", "Summary", "ACs Covered", "Reason"], [[p.get("id"), p.get("layer"), p.get("summary"), p.get("acsCovered"), p.get("reason")] for p in lower])}

## API Feature Content

```gherkin
{text(data.get("apiFeatureContent"))}
```

## UI Feature Content

```gherkin
{text(data.get("uiFeatureContent"))}
```

## AC Coverage Matrix

{table(["AC #", "Summary", "Covered By"], [[c.get("ac"), c.get("summary"), c.get("coveredBy")] for c in coverage])}

## Uncovered ACs

{bullet(as_list(data.get("uncoveredAcs")))}

## Authoring Notes

- API snippet catalog: {text(notes.get("apiSnippetCatalog"))}
- UI/E2E snippet catalog: {text(notes.get("uiSnippetCatalog"))}
- New/unmatched step wording: {text(notes.get("newSteps") or "None")}
- File mode decisions / assumptions: {text(notes.get("fileModeNotes") or "None")}

## Phase 2 Summary

- Feature files to create: {sum(1 for f in feature_files if f.get("mode") == "create")}
- Feature files to append: {sum(1 for f in feature_files if f.get("mode") == "append")}
- API scenarios: {sum(int(f.get("scenarioCount", 0) or 0) for f in feature_files if "/api/" in str(f.get("path")))}
- UI/E2E scenarios: {sum(int(f.get("scenarioCount", 0) or 0) for f in feature_files if "/ui/" in str(f.get("path")))}
- UI Component test points not authored: {sum(1 for p in lower if p.get("layer") == "UI Component")}
- UI Integration test points not authored: {sum(1 for p in lower if p.get("layer") == "UI Integration")}
- Smoke scenarios: {sum(int(f.get("smokeCount", 0) or 0) for f in feature_files)}
- Regression scenarios: {sum(int(f.get("regressionCount", 0) or 0) for f in feature_files)}
- Recommended next step: approve this feature content or request revisions.
"""

    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "bdd-feature-authoring.md"
    md_path.write_text(md, encoding="utf-8")
    return (md_path,)


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "schema" and sys.argv[2] in {"phase1", "phase2"}:
        schema = PHASE1_SCHEMA if sys.argv[2] == "phase1" else PHASE2_SCHEMA
        print(json.dumps(schema, indent=2, ensure_ascii=False))
        return 0
    if len(sys.argv) != 4 or sys.argv[1] not in {"phase1", "phase2"}:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    phase = sys.argv[1]
    input_path = Path(sys.argv[2])
    out_dir = Path(sys.argv[3])
    data = json.loads(input_path.read_text(encoding="utf-8"))
    paths = render_phase1(data, out_dir) if phase == "phase1" else render_phase2(data, out_dir)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
