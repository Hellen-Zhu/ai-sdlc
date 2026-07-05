---
name: qa-api-test-authoring
description: Implement SC Genie API automation artifacts from approved @api BDD feature files. Use when api-test-agent receives an API feature file and must create or update YAML request/response data, reusable snippets, Java glue, run non-executing validation, and return an authoring report without executing real tests.
---

# QA API Test Authoring

## Goal

Turn an approved `@api` `.feature` file into maintainable SC Genie API test artifacts.

This skill writes implementation files and runs non-executing validation only. It does not execute real tests, update ADO, or ask for user approval.

## Inputs

Use the context from `api-test-agent`:

- `E2E_DIR`
- API feature file path

The feature file is the source of truth. Read it yourself; do not rely on inlined feature content.

## Workflow

For each API feature file:

1. Validate that the path is under `{E2E_DIR}/src/test/resources/features/api/` or `features/api/`.
2. Read the feature file and extract:
   - feature-level tags
   - scenario tags, especially `@TC-*`
   - scenario names and Given/When/Then steps
   - Examples tables
3. Inspect existing project conventions before writing:
   - YAML data under `{E2E_DIR}/src/test/resources/data/api/`
   - API snippets under snippet-related API folders
   - Java glue under API step definition or glue folders
   - existing naming, package, fixture, request, response, and assertion patterns
4. Reuse existing snippets and glue when step wording already exists.
5. Create or update only the missing artifacts needed for the feature:
   - YAML test data for requests, responses, expected errors, and domain fixtures
   - reusable API snippets for repeated request/assertion flows
   - Java glue or step definitions for unmatched steps
6. Keep test data business-readable and stable. Avoid duplicating large payloads when the project has reusable fixtures.
7. Do not change the `.feature` file unless a broken tag or impossible step prevents implementation; if so, report it instead of silently rewriting.
8. Run non-executing validation: compile check plus Cucumber dry-run for the authored TC tags.
9. If validation fails, repair the authored artifacts inside this skill and re-run validation.
10. Return an output report only after validation passes or the internal validation repair loop is exhausted.

## Authoring Rules

- Preserve every `@TC-*` tag from the feature file.
- Map each generated file back to the scenario or TC ID that needs it.
- Prefer existing naming and folder conventions over new patterns.
- Keep API assertions at the business contract level: status, response fields, persisted state, audit or downstream effect.
- Avoid embedding environment-specific URLs, credentials, or secrets.
- When multiple scenarios share data, factor common fixtures instead of copying payloads.

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

   Build the tag expression from the authored `@TC-*` tags. Prefer TC tags over broad `@api` scope.

   ```bash
   cd {E2E_DIR} && mvn test -Dcucumber.options="--dry-run --tags {tagExpression}"
   ```

   The dry-run must verify feature syntax and step definition binding without running real test actions.

If compile or dry-run fails, repair the authored artifacts inside this skill before returning. Do not hand validation failures to `/codetestcases` until you have attempted the internal repair loop.

## Internal Validation Repair Loop

Use this loop for compile errors, feature syntax errors, undefined steps, ambiguous steps, missing glue, broken imports, type errors, missing YAML references, and dry-run binding failures.

1. Capture the failing command and relevant error output.
2. Classify the failure:
   - feature syntax
   - undefined or ambiguous step
   - Java compile error
   - missing or invalid YAML/data file
   - package/import/path mismatch
   - snippet/glue naming mismatch
   - project setup issue outside the authored files
3. Repair only files owned by this authoring task.
4. Re-run compile check and dry-run.
5. Repeat until both validations pass or `validationRepairAttempts` reaches `3`.

Rules:

- Do not broaden tag scope while repairing. Keep validating the authored TC tags.
- Do not change business meaning or approved TC tags to make validation pass.
- Do not delete scenarios or skip steps to hide a failure.
- If the failure is caused by an external project setup issue, stop after confirming it is outside the authored files and report it as a blocker.
- If repair attempts are exhausted, return `file_status: blocked` and include the final failure output plus attempted fixes.

## Quality Checks

Before returning:

- every API scenario has an implementation path or a reported blocker
- every new step has Java glue or a reused snippet
- YAML paths are under the project API data convention
- TC IDs are included in the report
- no UI-only behavior was implemented in API artifacts
- compile validation was run or explicitly skipped with a reason
- Cucumber dry-run was run or explicitly skipped with a reason
- validation failures were repaired internally when possible
- no real tests were executed by this skill

## Output Contract

Return this Markdown report:

```markdown
# API Test Authoring Report

Feature file: `{featureFile}`

## Files Created / Updated

- `{path}` - created | updated - purpose - TC IDs: @TC-...

## Snippets / Glue

- Reused snippets: list or None
- New snippets: list or None
- Java glue changes: list or None

## Scenario Coverage

- @TC-MOD-API-001 - implemented | blocked - notes

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

- featureTag: @api
- testTypeTag: @api
- tc_ids: [@TC-...]
- file_status: created | updated | mixed | blocked
- validation_status: passed | failed | skipped
```
