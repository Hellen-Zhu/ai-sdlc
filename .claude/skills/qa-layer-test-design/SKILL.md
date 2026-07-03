---
name: qa-layer-test-design
description: Design layered API, UI component, UI integration, and UI/E2E test points from a user story, acceptance criteria, and business rules. Use in BDD Phase 1 before feature authoring to produce an approval-ready test point list and coverage matrix.
---

# QA Layer Test Design

## Goal

Turn one user story into a reviewable layered test design that identifies what should be covered at API level, UI component level, UI integration level, and UI/E2E level, and what should not be duplicated across layers.

This skill produces test points only. It saves the Phase 1 draft artifact locally for review and Phase 2 input. It does not write Gherkin feature files and does not ask the user for approval.

## Inputs

Use the context provided by `bdd-agent`:

- `E2E_DIR`
- `story`
- `previousArtifactPath`, if present
- `revisionInstructions`, if present
- `previousOutput`, if present

Treat the story payload as authoritative. If fields are missing, infer conservatively from acceptance criteria and clearly list assumptions.

## Fresh Run

On a fresh run:

1. Read the complete story payload.
2. Extract story metadata:
   - story ID
   - title
   - module or business domain
   - actor or role
   - acceptance criteria
   - business rules
   - known tags or workflow state
3. Identify test conditions from explicit ACs and implied business rules.
4. Select the lowest reliable test layer for each condition.
5. Group related conditions into stable test points.
6. Assign test point IDs, tags, type, priority, and AC coverage.
7. Save the complete Phase 1 artifact locally.
8. Return a draft summary with artifact paths.

## Revision Run

If `revisionInstructions` and `previousOutput` are present:

1. Use `previousOutput` as the base.
2. If `previousArtifactPath` is present, read that artifact as the source of truth.
3. Apply only the user's requested changes.
4. Preserve unaffected TP IDs, tags, priorities, layers, and AC mappings.
5. Overwrite the local Phase 1 artifact with the complete updated content.
6. Return a draft summary with artifact paths, not a diff.

## Local Artifact Rules

Save the complete Phase 1 result before returning.

Use this directory:

```text
.ai-sdlc/workflow-state/{storyId}/
```

Use these files:

```text
test-layer-analysis.md
test-layer-analysis.json
```

`test-layer-analysis.md` must contain the full Markdown output contract below.

`test-layer-analysis.json` must contain structured data sufficient for Phase 2:

```json
{
  "storyId": "...",
  "title": "...",
  "moduleOrDomain": "...",
  "revisionCount": 0,
  "artifactVersion": "phase-1",
  "testPoints": [
    {
      "id": "TP-API-001",
      "layer": "API",
      "type": "positive",
      "priority": "smoke",
      "summary": "...",
      "acsCovered": ["AC1"],
      "tags": ["@api", "@smoke", "@positive"]
    }
  ],
  "coverageMatrix": [],
  "uncoveredAcs": [],
  "risksAndGaps": []
}
```

On revision, increment `revisionCount` if an existing JSON artifact is available. If not available, set `revisionCount` to `1`.

## Layer Selection Rules

Use the lowest useful layer that proves the behavior.

Choose **API** when the value is:

- service behavior
- request/response contract
- validation rule
- authorization rule at service boundary
- status transition
- data persistence
- idempotency or duplicate protection
- error handling
- downstream integration contract

Choose **UI Component** when the value is:

- behavior owned by a single component
- field-level validation display
- local enabled/disabled state
- role/status-specific component visibility
- modal, menu, table row action, form section, or widget behavior
- event/callback behavior that can be proven with mocked props
- visual state that is functional rather than screenshot/pixel-level

Choose **UI Integration** when the value is:

- a page or feature composed from multiple components
- route params, query params, providers, or global state affect behavior
- mocked API responses drive page behavior
- mutation result must update list/detail/cache state
- API error mapping must render correctly in the page
- feature flags, permissions, or store state affect a UI workflow without needing a real deployed backend

Choose **UI/E2E** when the value is:

- user-visible workflow
- navigation or routing
- browser interaction
- role-specific page/action visibility
- cross-page state consistency
- complete user journey
- deployed-environment smoke confidence
- behavior that must be proven through the actual UI

Choose multiple layers only when the story has distinct risks that require distinct proof:

- a business rule that should be proven directly at API level, and
- a component behavior that should be proven locally, and/or
- a page integration behavior that should be proven with mocked APIs/state, and/or
- a user journey or deployed-environment risk that cannot be covered by lower layers.

Avoid duplicate coverage. If a lower layer proves a rule fully, higher layers should verify only the integration or journey risk that lower layers cannot prove.

## Test Point Types

Classify each test point as one of:

- `positive`
- `negative`
- `edge`
- `permission`
- `regression`

Use `permission` for role, entitlement, ownership, and forbidden-action checks.
Use `edge` for boundary values, unusual states, or alternate data combinations.
Use `regression` when the point protects previously fragile or high-value behavior but is not a primary happy/guard path.

## Smoke vs Regression

Mark a test point as `smoke` only when failure should block a release or deployment:

- primary happy path
- P0 business status transition
- critical permission guard
- production-safe availability check
- core integration that must work in every release

Mark a test point as `regression` when it is valuable but broader, slower, lower risk, or better suited to nightly/extended runs.

Prefer a small smoke set. Do not mark every important scenario as smoke.

## Test Point ID Rules

Use stable IDs:

- API: `TP-API-001`, `TP-API-002`, ...
- UI Component: `TP-UIC-001`, `TP-UIC-002`, ...
- UI Integration: `TP-UII-001`, `TP-UII-002`, ...
- UI/E2E: `TP-E2E-001`, `TP-E2E-002`, ...

Keep numbering stable during revision. Add new IDs at the end of the relevant layer sequence.

## Tag Rules

Use tags that Phase 2 can translate into feature file annotations:

- API test points must include `@api`
- UI Component test points must include `@ui-component`
- UI Integration test points must include `@ui-integration`
- UI/E2E test points must include `@playwright`
- smoke test points must include `@smoke`
- regression test points must include `@regression`
- include module/domain tag if available, for example `@payments`
- include type tags where useful, for example `@positive`, `@negative`, `@permission`

## Coverage Rules

Every acceptance criterion must be either:

- covered by at least one test point, or
- listed in `Uncovered ACs` with a reason.

Do not invent acceptance criteria. If an implied rule matters, label it as an assumption or implied condition.

## Quality Checks

Before returning output, verify:

- every TP maps to at least one AC or explicit assumption
- every AC appears in the coverage matrix
- no UI/E2E test duplicates API, component, or integration coverage without a user-journey reason
- component and integration candidates are not escalated to UI/E2E unless real browser/deployed workflow confidence is required
- smoke set is intentionally small
- negative and permission cases focus on business-critical guards
- IDs are stable and layer-specific
- tags are present and consistent
- assumptions and gaps are explicit

## Output Contract

Save the full artifact locally, then return raw Markdown only. Do not wrap the whole response in a code block.

The returned response should be a draft summary and artifact pointer, not the full artifact. Use this exact structure:

```markdown
# Test Layering Draft Summary

## Artifact

- Markdown: `.ai-sdlc/workflow-state/{storyId}/test-layer-analysis.md`
- JSON: `.ai-sdlc/workflow-state/{storyId}/test-layer-analysis.json`

## Summary

- Story ID:
- Title:
- API test points: N
- UI Component test points: N
- UI Integration test points: N
- UI/E2E test points: N
- Smoke test points: N
- Regression test points: N
- Uncovered ACs: N

## Review Highlights

- [Highest-value layering decisions]
- [Important assumptions]
- [Risks or gaps]

## Next Step

Review the artifact, then approve this layering plan or request revisions.
```

The saved `test-layer-analysis.md` artifact must use this exact structure:


```markdown
# Test Layering Analysis

## Story Summary

- Story ID:
- Title:
- Module / Domain:
- Primary Actor:
- Source:

## Assumptions

- [List assumptions, or "None"]

## Acceptance Criteria

| AC # | Acceptance Criterion | Notes |
|------|----------------------|-------|
| AC1  | ...                  | ...   |

## Layered Test Points

| TP ID | Layer | Type | Priority | Summary | ACs Covered | Tags |
|-------|-------|------|----------|---------|-------------|------|
| TP-API-001 | API | positive | smoke | ... | AC1 | @api @smoke @positive |
| TP-UIC-001 | UI Component | positive | regression | ... | AC1 | @ui-component @regression @positive |
| TP-UII-001 | UI Integration | negative | regression | ... | AC2 | @ui-integration @regression @negative |
| TP-E2E-001 | UI/E2E | positive | smoke | ... | AC1 | @playwright @smoke @positive |

## Layering Rationale

| TP ID | Why This Layer | Why Not Higher / Lower |
|-------|----------------|------------------------|
| TP-API-001 | ... | ... |

## AC Coverage Matrix

| AC # | Covered By | Coverage Notes |
|------|------------|----------------|
| AC1  | TP-API-001, TP-UIC-001, TP-E2E-001 | ... |

## Uncovered ACs

- [List uncovered ACs with reason, or "None"]

## Risks And Gaps

- [List risks, dependencies, missing data, environment constraints, or "None"]

## Phase 1 Summary

- API test points: N
- UI Component test points: N
- UI Integration test points: N
- UI/E2E test points: N
- Smoke test points: N
- Regression test points: N
- Recommended next step: approve this layering plan or request revisions.
```

Do not include an approval menu. `writebddfeatures` owns approval.
