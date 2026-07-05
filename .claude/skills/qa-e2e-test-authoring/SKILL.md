---
name: qa-e2e-test-authoring
description: Implement SC Genie UI E2E automation artifacts from approved @playwright BDD feature files using the four-layer UI E2E architecture: feature scenario steps, flow layer, page/component layer, and locator/data artifacts. Use when e2e-test-agent receives a UI feature file and must create or update business flows, page/component operations, locators, YAML UI data, snippets, Java glue, and an authoring report without running tests.
---

# QA E2E Test Authoring

## Goal

Turn an approved `@playwright` `.feature` file into maintainable SC Genie UI E2E test artifacts that respect the project's four-layer UI E2E architecture.

This skill writes implementation files only. It does not run tests, update ADO, or ask for user approval.

## Inputs

Use the context from `e2e-test-agent`:

- `E2E_DIR`
- UI feature file path

The feature file is the source of truth. Read it yourself; do not rely on inlined feature content.

## Workflow

For each UI feature file:

1. Validate that the path is under `{E2E_DIR}/src/test/resources/features/ui/` or `features/ui/`.
2. Read the feature file and extract:
   - feature-level tags
   - scenario tags, especially `@TC-*`
   - scenario names and Given/When/Then steps
   - Examples tables
3. Inspect existing project conventions before writing:
   - scenario step definitions or scenario snippets
   - flow snippets/classes that compose business flows and business assertions
   - page snippets/classes and component snippets/classes
   - element locators under page/component element folders
   - YAML UI data under `{E2E_DIR}/src/test/resources/data/ui/`
   - Java glue under UI/E2E step definition or glue folders
4. Map each feature step to an existing or new **flow-level** business action/assertion. Scenario glue must call flow methods only.
5. Map each flow action/assertion to page/component operations and page/component assertions.
6. Use browser inspection tools only when needed to confirm selectors, accessible names, navigation, or page state for the page/component layer. Prefer stable accessible locators and existing locator conventions.
7. Reuse existing snippets and glue when step wording or flow/page/component behavior already exists.
8. Create or update only the missing artifacts needed for the feature:
   - scenario glue or scenario snippets that call flow actions/assertions only
   - flow snippets/classes for business workflow composition and business assertions
   - page/component snippets/classes for element operations and page/component assertions
   - element locator JSON or equivalent locator artifacts
   - YAML UI data and expected visible outcomes
9. Do not change the `.feature` file unless a broken tag or impossible step prevents implementation; if so, report it instead of silently rewriting.
10. Return an output report.

## Four-Layer Architecture

UI E2E implementation must preserve this layering:

1. **Feature Scenario Layer**
   - Contains business-language Gherkin only.
   - Step definitions or scenario snippets may translate feature steps into calls to the flow layer.
   - Must not expose page names, component names, locators, clicks, typing, waits, CSS/XPath, or Playwright/browser details.
   - Must express business action, business result, and business-rule-compliant state.

2. **Flow Layer**
   - Owns business flow composition and business assertions.
   - Calls page/component layer operations and assertions.
   - May coordinate navigation, preconditions, multi-page journeys, and domain-level expected outcomes.
   - Must not contain raw locators, selector strings, click/type/fill/select mechanics, or low-level visibility assertions.

3. **Page / Component Layer**
   - Owns page-level and component-level operations and assertions.
   - Page layer can know URL-reachable page behavior, page entry, page-level assertions, and elements rendered in that page context.
   - Component layer owns cross-page reusable component behavior only; it must be page-agnostic and non-navigational.
   - This is the only code layer that should call element operations such as click, type, fill, select, assert visible, or read text.

4. **Locator / Data Artifact Layer**
   - Owns selectors, element metadata, test data, expected visible values, and YAML fixtures.
   - Keep locators stable and reusable. Prefer accessible names or project-standard element identifiers.

Dependency direction is one-way:

```text
Feature Scenario -> Flow -> Page/Component -> Locator/Data
```

Never call page/component methods directly from scenario glue when a flow method should exist. Never call locators directly from flow or scenario glue.

## Authoring Rules

- Preserve every `@TC-*` tag from the feature file.
- Map each generated file back to the scenario or TC ID that needs it.
- Prefer existing flow/page/component snippets before creating new ones.
- Keep scenario glue thin: feature steps call flow actions/assertions only.
- Put business assertions in the flow layer, implemented through page/component assertions.
- Put page state and component state assertions in page/component layer.
- Prefer user-facing locators and stable accessibility attributes over brittle CSS/XPath.
- Factor shared page/component locators instead of duplicating selector definitions.
- Avoid hard-coded environment data, credentials, or timing sleeps.

## Quality Checks

Before returning:

- every UI scenario has an implementation path or a reported blocker
- every new feature step has Java glue or a reused scenario snippet that calls flow only
- every flow method delegates UI mechanics to page/component layer
- no scenario glue contains page/component calls, locators, selectors, click/type/fill/select mechanics, sleeps, or browser details
- no flow method contains raw locators or low-level element operations
- locator files follow project naming and folder conventions
- YAML paths are under the project UI data convention
- TC IDs are included in the report
- no API-only behavior was implemented as UI artifacts unless the feature explicitly requires an end-to-end journey
- no tests were executed by this skill

## Output Contract

Return this Markdown report:

```markdown
# UI E2E Test Authoring Report

Feature file: `{featureFile}`

## Files Created / Updated

- `{path}` - created | updated - purpose - TC IDs: @TC-...

## Layered Implementation

- Scenario glue/snippets: list or None
- Flow layer changes: list or None
- Page/component layer changes: list or None
- Element locators: list or None
- YAML/data changes: list or None
- Reused snippets: list or None

## Layering Checks

- Scenario layer exposes UI details: yes | no
- Scenario glue calls flow only: yes | no
- Flow layer contains raw locators or click/type/fill/select mechanics: yes | no
- Page/component layer owns element operations/assertions: yes | no

## Scenario Coverage

- @TC-MOD-UI-001 - implemented | blocked - notes

## Blockers / Follow-up

- None, or specific blocker with file/scenario reference

## Orchestrator Addendum

- featureTag: @playwright
- testTypeTag: @playwright
- tc_ids: [@TC-...]
- file_status: created | updated | mixed | blocked
```
