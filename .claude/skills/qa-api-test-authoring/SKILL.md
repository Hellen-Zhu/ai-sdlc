---
name: qa-api-test-authoring
description: Implement SC Genie API automation artifacts from approved @api BDD feature files. Use when api-test-agent receives an API feature file and must create or update YAML request/response data, reusable snippets, Java glue, and an authoring report without running tests.
---

# QA API Test Authoring

## Goal

Turn an approved `@api` `.feature` file into maintainable SC Genie API test artifacts.

This skill writes implementation files only. It does not run tests, update ADO, or ask for user approval.

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
8. Return an output report.

## Authoring Rules

- Preserve every `@TC-*` tag from the feature file.
- Map each generated file back to the scenario or TC ID that needs it.
- Prefer existing naming and folder conventions over new patterns.
- Keep API assertions at the business contract level: status, response fields, persisted state, audit or downstream effect.
- Avoid embedding environment-specific URLs, credentials, or secrets.
- When multiple scenarios share data, factor common fixtures instead of copying payloads.

## Quality Checks

Before returning:

- every API scenario has an implementation path or a reported blocker
- every new step has Java glue or a reused snippet
- YAML paths are under the project API data convention
- TC IDs are included in the report
- no UI-only behavior was implemented in API artifacts
- no tests were executed by this skill

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

## Blockers / Follow-up

- None, or specific blocker with file/scenario reference

## Orchestrator Addendum

- featureTag: @api
- testTypeTag: @api
- tc_ids: [@TC-...]
- file_status: created | updated | mixed | blocked
```
