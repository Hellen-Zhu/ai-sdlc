---
name: qa-bdd-test-execution
description: Build and run SC Genie Maven/Cucumber commands for authored BDD test artifacts. Use after API/UI authoring reports are approved to choose tag scope, execute tests sequentially, capture full output, and return a repair-loop-ready execution report.
---

# QA BDD Test Execution

## Goal

Run the authored BDD scenarios with the narrowest reliable Cucumber tag scope and return complete results for `/codetestcases`.

This skill runs tests and reports results. It does not author files, repair failures, update ADO, or ask for user approval.

## Inputs

Use the context from `/codetestcases`:

- `E2E_DIR`
- `authoring_results`: one entry per authoring agent that ran
- `env`, optional: `sit` when requested; otherwise default to `dev`

Each authoring result should include `featureTag`, `testTypeTag`, `tc_ids`, and `file_status`.

## Scope Selection

Choose the narrowest stable tag expression:

1. If one or more TC IDs are present, run by TC ID tags.
2. If TC IDs are absent but `testTypeTag` is present, run by test type tag such as `@api` or `@playwright`.
3. If both are absent, stop and report a blocker; do not run the whole suite.

Group commands by compatible tag scope. Prefer fewer commands only when it does not hide which TC failed.

Skip entries with `file_status: blocked` and report them as not run.

## Command Rules

Run from `{E2E_DIR}`.

Default command shape:

```bash
mvn clean test -Dcucumber.options="--tags {tagExpression}"
```

If `env` is provided, apply the project convention if known. If unknown, prefer the least invasive system property:

```bash
mvn clean test -Denv={env} -Dcucumber.options="--tags {tagExpression}"
```

Do not invent destructive cleanup commands. Do not run unrelated modules unless the project convention requires it.

## Execution Workflow

1. Validate `{E2E_DIR}` exists.
2. Extract TC IDs, feature tags, test type tags, and blocked entries from `authoring_results`.
3. Build the command list.
4. Run commands sequentially.
5. Capture each command, exit code, duration if available, and full stdout/stderr.
6. Classify result:
   - `passing` when all executed commands pass and no blocking authoring entries remain
   - `failing` when any command exits non-zero
   - `blocked` when no safe command can be built or all entries are blocked
7. Return the execution report.

## Output Contract

Return this Markdown report:

````markdown
# BDD Test Execution Report

Status: passing | failing | blocked
Environment: dev | sit | other

## Commands Run

- `{command}` - passed | failed | skipped

## Results

- Passed: N
- Failed: N
- Skipped / not run: N
- TC IDs covered: @TC-...

## Failure Details

For each failed command:

```text
{full command output or the relevant captured output if the tool output is extremely large}
```

## Repair Loop Payload

- failing_tc_ids: [@TC-...]
- test_type: api | ui | mixed | unknown
- run_commands: [...]
- status: passing | failing | blocked
- full_output_captured: yes | no
````
