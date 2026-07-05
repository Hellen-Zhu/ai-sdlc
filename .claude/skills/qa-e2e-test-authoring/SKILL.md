---
name: qa-e2e-test-authoring
description: Implement SC Genie UI E2E automation artifacts from approved @playwright BDD feature files using the four-layer UI E2E architecture: feature scenario steps, flow layer, page/component layer, and locator/data artifacts. Use when e2e-test-agent receives a UI feature file and must create or update business flows, page/component operations, locators, YAML UI data, snippets, Java glue, run non-executing validation, and return an authoring report without executing real tests.
---

# QA E2E Test Authoring

## Goal

Turn an approved `@playwright` `.feature` file into maintainable SC Genie UI E2E test artifacts that respect the project's four-layer UI E2E architecture.

This skill writes implementation files and runs non-executing validation only. It does not execute real tests, update ADO, or ask for user approval.

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
10. Run non-executing validation: compile check plus Cucumber dry-run for the authored TC tags.
11. If validation fails, repair the authored artifacts inside this skill and re-run validation.
12. Return an output report only after validation passes or the internal validation repair loop is exhausted.

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

## Non-Executing Validation

Run validation after authoring artifacts and before returning the report. These checks are allowed because they do not execute scenario bodies.

1. **Compile check**

   Prefer:

   ```bash
   cd {E2E_DIR} && mvn test-compile
   ```

   If the project convention requires Maven test phase compilation instead, use:

   ```bash
   cd {E2E_DIR} && mvn test -DskipTests
   ```

2. **Cucumber dry-run**

   Build the tag expression from the authored `@TC-*` tags. Prefer TC tags over broad `@playwright` scope.

   ```bash
   cd {E2E_DIR} && mvn test -Dcucumber.options="--dry-run --tags {tagExpression}"
   ```

   The dry-run must verify feature syntax and step definition binding without launching the real UI journey.

If compile or dry-run fails, repair the authored artifacts inside this skill before returning. Do not hand validation failures to `/codetestcases` until you have attempted the internal repair loop.

## Internal Validation Repair Loop

Use this loop for compile errors, feature syntax errors, undefined steps, ambiguous steps, missing glue, broken imports, type errors, missing YAML references, locator/data path mismatches, layer-boundary violations found during validation, and dry-run binding failures.

1. Capture the failing command and relevant error output.
2. Classify the failure:
   - feature syntax
   - undefined or ambiguous step
   - Java compile error
   - missing or invalid YAML/data file
   - package/import/path mismatch
   - scenario-to-flow binding mismatch
   - flow-to-page/component binding mismatch
   - locator or page/component artifact mismatch
   - project setup issue outside the authored files
3. Repair only files owned by this authoring task.
4. Preserve the four-layer architecture while repairing.
5. Re-run compile check and dry-run.
6. Repeat until both validations pass or `validationRepairAttempts` reaches `3`.

Rules:

- Do not broaden tag scope while repairing. Keep validating the authored TC tags.
- Do not change business meaning or approved TC tags to make validation pass.
- Do not delete scenarios, bypass flow methods, call page/component methods directly from scenario glue, or skip steps to hide a failure.
- Do not move locators or low-level UI operations into scenario glue or flow.
- If the failure is caused by an external project setup issue, stop after confirming it is outside the authored files and report it as a blocker.
- If repair attempts are exhausted, return `file_status: blocked` and include the final failure output plus attempted fixes.

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
- compile validation was run or explicitly skipped with a reason
- Cucumber dry-run was run or explicitly skipped with a reason
- validation failures were repaired internally when possible
- no real tests were executed by this skill

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

## Non-Executing Validation

- Compile check: passed | failed | skipped
- Compile command: `{command or N/A}`
- Dry-run: passed | failed | skipped
- Dry-run command: `{command or N/A}`
- Undefined steps: None or list
- Feature syntax errors: None or list
- Repair attempts: N
- Repaired issues: None or list
- Final validation status: passed | failed | skipped

## Blockers / Follow-up

- None, or specific blocker after internal validation repair attempts are exhausted

## Orchestrator Addendum

- featureTag: @playwright
- testTypeTag: @playwright
- tc_ids: [@TC-...]
- file_status: created | updated | mixed | blocked
- validation_status: passed | failed | skipped
```
