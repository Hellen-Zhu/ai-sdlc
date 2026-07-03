---
name: qa-bdd-feature-authoring
description: Author business-readable BDD Gherkin feature content from approved layered test points. Use in BDD Phase 2 after test layering approval to produce feature file paths, write modes, Gherkin blocks, and AC coverage.
---

# QA BDD Feature Authoring

## Goal

Turn approved BDD-suitable layered test points into BDD feature authoring output that can be reviewed and then written by `/writebddfeatures`.

This skill creates approved candidate content only. It does not write final `.feature` files and does not ask the user for approval.

## Inputs

Use the context provided by `bdd-agent`:

- `E2E_DIR`
- `story`
- `approvedTestPoints`
- `layeringArtifactPath`, if present
- `revisionInstructions`, if present
- `previousOutput`, if present

Treat `approvedTestPoints` or `layeringArtifactPath` as the scope boundary. Prefer `layeringArtifactPath` when provided, and read the Phase 1 JSON/Markdown artifact before authoring. Do not add, remove, or relayer test points unless the revision instructions explicitly request it.

Only API and UI/E2E test points produce `.feature` content. UI Component and UI Integration test points remain part of the approved test strategy, but they are lower-layer test points and must not be converted into Gherkin feature files by this skill.

## Fresh Run

On a fresh run:

1. Read the complete story payload and approved test points.
   - If `layeringArtifactPath` is provided, read that artifact first.
   - If a sibling JSON artifact exists, prefer it for structured test point extraction.
2. Split approved test points by layer:
   - API: test points tagged `@api` or layer `API`
   - UI Component: test points tagged `@ui-component` or layer `UI Component`
   - UI Integration: test points tagged `@ui-integration` or layer `UI Integration`
   - UI/E2E: test points tagged `@playwright`, layer `UI/E2E`, or layer `E2E`
3. Determine target feature identity for each BDD-generated layer: API and UI/E2E.
4. Determine file mode for each BDD target feature:
   - `create` when the feature file should be newly created
   - `append` when a suitable feature file already exists
   - `not generated` when there are no approved test points for that layer
5. Author Gherkin for each generated layer.
6. Build an AC coverage matrix from approved test points.
7. Return the complete Phase 2 output.

## Revision Run

If `revisionInstructions` and `previousOutput` are present:

1. Use `previousOutput` as the base.
2. Apply only the user's requested changes.
3. Preserve unaffected file paths, file modes, TC IDs, tags, scenario names, and coverage mappings.
4. Return the complete updated Phase 2 output, not a diff.

## Feature File Path Rules

Feature file paths must be relative to `{E2E_DIR}/src/test/resources/features/` unless project context states otherwise.

Use these default path shapes:

- API: `features/api/{businessDomain}/{featureName}.feature`
- UI/E2E: `features/ui/{businessDomain}/{featureName}.feature`

Derive:

- `businessDomain` from story module/domain, normalized to kebab-case
- `featureName` from story title or capability, normalized to kebab-case

Do not invent separate feature files for every scenario. Group scenarios by coherent business capability.

## File Mode Rules

Use `create` when:

- no existing suitable feature file is known, or
- the approved scope describes a new feature capability.

Use `append` when:

- an existing feature file is known from story context, workflow state, repo inspection, or prior output, and
- the new scenarios belong under that existing `Feature:`.

Use `not generated` when:

- that layer has no approved test points.
- that layer has only UI Component or UI Integration test points, which are not authored as BDD `.feature` files by this skill.

For append mode, output only new `Scenario` or `Scenario Outline` blocks for that layer. Do not output top-level tags, `Feature:`, description, or `Background:` for append mode.

## TC ID Rules

Assign stable TC IDs:

- API: `TC-<MODULE>-API-NNN`
- UI/E2E: `TC-<MODULE>-UI-NNN`

Use the module tag or story module to derive `<MODULE>`. Normalize to uppercase alphanumeric. If module is unknown, use `MOD`.

Keep TC IDs stable during revision. Add new IDs at the end of the relevant sequence.

## Gherkin Rules

Write business-readable Gherkin.

Use:

- `Feature:` for create mode
- `Background:` only when multiple scenarios truly share business preconditions
- `Scenario:` for simple cases
- `Scenario Outline:` only when examples materially reduce duplication
- tags above each scenario

Each generated scenario should include:

- layer tag (`@api` or `@playwright`)
- module/domain tag if available
- priority tag (`@smoke` or `@regression`)
- type tag (`@positive`, `@negative`, `@permission`, or `@edge`) when useful
- TC ID tag, for example `@TC-MOD-API-001`
- Given/When/Then steps that describe behavior, not implementation mechanics

Avoid:

- CSS selectors, data-testid, button coordinates, or component names
- implementation class names or endpoint internals unless API-level business wording requires an API action
- excessive UI click-by-click scripting
- vague steps such as "Then it works"
- unapproved scenarios

## API Scenario Guidance

API scenarios should focus on business behavior at the service boundary:

- valid request succeeds and persists expected state
- invalid request is rejected with business-meaningful error
- unauthorized or forbidden action is blocked
- status transition rules are enforced
- duplicate or idempotent action behaves correctly

Use business API language, for example:

```gherkin
Given an eligible trade exists for approval
When the maker submits the trade for approval
Then the trade status is Pending Approval
And the submission is recorded for audit
```

## UI/E2E Scenario Guidance

UI/E2E scenarios should focus on user journeys and visible outcomes:

- user can complete the critical workflow
- page state, status, and navigation reflect the business outcome
- role-specific actions are visible or blocked
- list/detail consistency is proven after a real action

Use business UI language, for example:

```gherkin
Given a maker is viewing a draft trade
When the maker submits the trade
Then the trade details page shows Pending Approval
And the trade appears in the approval queue
```

## Coverage Rules

Every API and UI/E2E approved test point must map to at least one generated scenario unless its layer is `not generated`.

Every scenario must map back to one or more ACs through the approved test point.

UI Component and UI Integration approved test points must appear in the coverage matrix as lower-layer coverage, not as generated BDD scenarios.

List uncovered ACs as `None` only when all ACs are covered by generated or intentionally retained existing scenarios.

## Quality Checks

Before returning output, verify:

- paths and modes are present for API and UI/E2E entries
- UI Component and UI Integration test points are not converted into `.feature` scenarios
- `not generated` layers have no Gherkin block
- create mode includes complete feature content
- append mode includes only new scenario blocks
- scenario tags include layer, priority, and TC ID
- TC IDs are unique and layer-appropriate
- Gherkin is business-readable
- no unapproved test points were added
- AC coverage matrix is consistent with approved test points

## Output Contract

Return raw Markdown only. Do not wrap the whole response in a code block.

Use this exact structure:

````markdown
# BDD Feature Generation Result

## Feature Files To Write

* features/api/{businessDomain}/{featureName}.feature -> mode: create | append | not generated | <N> scenarios (@smoke: N, @regression: N)
* features/ui/{businessDomain}/{featureName}.feature -> mode: create | append | not generated | <N> scenarios (@smoke: N, @regression: N)

## Lower-Layer Test Points Not Authored As Feature Files

| TP ID | Layer | Summary | ACs Covered | Reason |
|-------|-------|---------|-------------|--------|
| TP-UIC-001 | UI Component | ... | AC1 | Covered by component-level test, not BDD feature file |
| TP-UII-001 | UI Integration | ... | AC2 | Covered by integration-level test, not BDD feature file |

## API Feature Content

```gherkin
{complete API feature content for create mode; new scenario/scenario outline blocks only for append mode; omit this block when API mode is not generated}
```

## UI Feature Content

```gherkin
{complete UI feature content for create mode; new scenario/scenario outline blocks only for append mode; omit this block when UI mode is not generated}
```

## AC Coverage Matrix

| AC # | Summary | Covered By |
|------|---------|------------|
| AC1  | ...     | @TC-MOD-API-001, @TC-MOD-UI-001, TP-UIC-001 |

## Uncovered ACs

- [List uncovered ACs with reason, or "None"]

## Authoring Notes

- [List file mode decisions, assumptions, existing-file dependencies, or "None"]

## Phase 2 Summary

- Feature files to create: N
- Feature files to append: N
- API scenarios: N
- UI/E2E scenarios: N
- UI Component test points not authored: N
- UI Integration test points not authored: N
- Smoke scenarios: N
- Regression scenarios: N
- Recommended next step: approve this feature content or request revisions.
````

Do not include an approval menu. `writebddfeatures` owns approval.
