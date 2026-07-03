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
3. Generate or read the API/UI snippet catalogs.
4. Determine target feature identity for each BDD-generated layer: API and UI/E2E.
5. Determine file mode for each BDD target feature:
   - `create` when the feature file should be newly created
   - `append` when a suitable feature file already exists
   - `not generated` when there are no approved test points for that layer
6. Author Gherkin for each generated layer, reusing matching snippets wherever possible.
7. Build an AC coverage matrix from approved test points.
8. Return the complete Phase 2 output.

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

## Snippet Reuse Rules

Before authoring Gherkin, generate or read the snippet catalog for both API and UI/E2E layers.

### Generate Catalogs

If `snippet_index_generate.sh` exists, run it before authoring.

Look for the script in this order:

```text
{E2E_DIR}/snippet_index_generate.sh
{E2E_DIR}/scripts/snippet_index_generate.sh
./snippet_index_generate.sh
./scripts/snippet_index_generate.sh
```

Use the project's script contract if documented. If no contract is documented, run the script from its containing directory with Bash:

```bash
bash snippet_index_generate.sh
```

If the script supports explicit layer flags or output paths, generate both API and UI catalogs. Do not guess destructive flags.

### Find Catalogs

After running the script, or if the script is absent, search for snippet catalogs under `{E2E_DIR}` and the project root.

Prefer files whose names or paths indicate:

- `api` + `snippet`
- `ui` + `snippet`
- `e2e` + `snippet`
- `catalog`
- `snippet_index`

Read the relevant catalog(s) before writing Gherkin.

### Reuse Policy

Prefer existing snippets over new step wording.

For each intended Given/When/Then step:

1. Search the relevant layer catalog first:
   - API scenarios use the API snippet catalog.
   - UI/E2E scenarios use the UI/E2E snippet catalog.
2. Reuse an existing snippet when its business meaning matches the intended step.
3. Adapt only parameter values, quoted text, identifiers, and examples.
4. Preserve snippet wording, tense, and placeholder style as much as possible.
5. Do not create a semantically duplicate step with different wording.
6. Create new wording only when no suitable snippet exists.

When creating new wording:

- keep it business-readable
- keep it general enough to become reusable
- avoid implementation details
- note it in `Authoring Notes` as a new/unmatched step

### Snippet Traceability

In `Authoring Notes`, include:

- snippet catalog paths used
- whether API snippets were generated/read
- whether UI/E2E snippets were generated/read
- any scenarios or steps that required new wording because no matching snippet existed

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

Do not hand-write final Markdown tables. Produce structured JSON, then use the renderer script to create the review output.

1. Write Phase 2 data to a temporary JSON file using the schema exposed by the renderer.
2. Run:

   ```bash
   python .claude/scripts/render_bdd_artifact.py phase2 {inputJsonPath} .ai-sdlc/workflow-state/{storyId}
   ```

3. Read `.ai-sdlc/workflow-state/{storyId}/bdd-feature-authoring.md`.
4. Return that Markdown verbatim.

Use this command if you need the exact field names:

```bash
python .claude/scripts/render_bdd_artifact.py schema phase2
```

Do not include an approval menu. `writebddfeatures` owns approval.
