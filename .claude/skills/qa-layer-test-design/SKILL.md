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

If `revisionInstructions` are present:

1. Prefer `previousArtifactPath` and read the existing `test-layer-analysis.json` as the source of truth.
2. Use `previousOutput` only as fallback context when no artifact path is available.
3. Apply only the user's requested changes to the JSON structure.
4. Preserve unaffected TP IDs, tags, priorities, layers, AC mappings, assumptions, risks, and rationale.
5. Increment `revisionCount`.
6. Overwrite the same `test-layer-analysis.json` artifact path unless the caller explicitly requests a new artifact.
7. Return only a short revised review summary, not the full JSON and not a diff.

## Local Artifact Rules

Save the complete Phase 1 result before returning.

Use this directory:

```text
.ai-sdlc/workflow-state/{storyId}/
```

Use these files:

```text
test-layer-analysis.json
```

`test-layer-analysis.json` is the only Phase 1 source-of-truth artifact. Do not create a Markdown artifact for Phase 1.

To inspect the expected JSON shape, run:

```bash
python .claude/scripts/render_bdd_artifact.py schema phase1
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

Produce structured JSON, save it with the renderer script, then return a short review summary directly in your response.

1. Write Phase 1 data to a temporary JSON file using the schema exposed by the renderer.
2. Run:

   ```bash
   python .claude/scripts/render_bdd_artifact.py phase1 {inputJsonPath} .ai-sdlc/workflow-state/{storyId}
   ```

3. Return a short review summary using this format:

   ```markdown
   # Test Layering Draft Summary

   - JSON artifact: `.ai-sdlc/workflow-state/{storyId}/test-layer-analysis.json`
   - API test points: N
   - UI Component test points: N
   - UI Integration test points: N
   - UI/E2E test points: N
   - Smoke test points: N
   - Regression test points: N
   - Uncovered ACs: N

   Review highlights:
   - ...
   ```

Use this command if you need the exact field names:

```bash
python .claude/scripts/render_bdd_artifact.py schema phase1
```

Do not include an approval menu. `writebddfeatures` owns approval.
