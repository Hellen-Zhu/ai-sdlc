---
description: Read ADO User Stories, delegate BDD planning/authoring to bdd-agent, and write approved Gherkin .feature files into {E2E_DIR}/.
---

# Write BDD Feature Files

**Sub-project paths:** Resolve `{E2E_DIR}` lazily. Phase 1 test layering is design-only and must not inspect or validate the E2E project directory. Resolve `{E2E_DIR}` from root `CLAUDE.md` -> `# Repos` table only after Phase 1 is approved and before Phase 2 feature authoring. Check the `Optional` column at that point - **skip Phase 2+ for any E2E sub-project marked `Optional: Yes` that does not exist on disk**. Defaults: `be-app`, `fe-app`, `e2e-test`.

You are orchestrating BDD feature file generation for `{ADO_DISPLAY_NAME}` User Stories.
Delegate BDD analysis and feature authoring to **bdd-agent**, a senior BDD test engineer agent. This command owns all user approval gates and all final file writes.

> WARNING: **Phase 2+ requires `{E2E_DIR}`.** If `{E2E_DIR}` is `Optional: Yes` in CLAUDE.md and does not exist on disk after Phase 1 approval, stop and output:
> "E2E tests directory not present - /writebddfeatures skipped."

## Input

Detect the input mode from what the user provides:

| Mode | Detection rule |
|------|----------------|
| **JSON file mode** | starts with `/`, `./`, `~`, or ends with `.json` |
| **ADO mode** | ADO User Story ID, pure number, or starts with `ado:` |
| **Empty / invalid** | ask: **"Please provide an ADO User Story ID (e.g. #1234) or a JSON file path (e.g. `./workflow-state/L001.json`)"** |

---

## Step 1 - Load Workflow Context

**If JSON file mode:**

Use **Read** to get full content for the user story.

If `lastCompletedStage` is `"writebddfeatures.completed"` or `bddFeatureFiles` is non-empty, warn and **WAIT**:

```text
WARNING: BDD feature files already generated for #[story-id]: [bddFeatureFiles joined by ", "]
Run this again? (yes/no)
```

- `"no"` -> exit.
- `"yes"` -> start over at Step 2.

If `lastCompletedStage` is `"writebddfeatures.phase1.approved"` and `bddLayeringArtifact` exists on disk, offer resume:

```text
Found approved Phase 1 layering artifact for #[story-id]:
[bddLayeringArtifact]

Resume BDD feature authoring from Phase 2? (yes / rerun phase1 / stop)
```

- `"yes"` -> proceed directly to Step 3 using `bddLayeringArtifact`.
- `"rerun phase1"` -> proceed to Step 2.
- `"stop"` -> exit.

If `lastCompletedStage` is `"writebddfeatures.phase1.approved"` but `bddLayeringArtifact` is missing or not readable, warn that the checkpoint is incomplete and proceed to Step 2.

---

**If ADO mode:**

Use **ado-agent** (`FETCH_STORY`) for each story ID.

Do not ask **ado-agent** to validate `{E2E_DIR}`, search the E2E repository, list project files, or inspect existing feature files during Step 1. Step 1 loads story/workflow context only.

If the fetched story `bddFeatureFiles` is non-empty, warn and **WAIT**:

```text
WARNING: BDD feature files already generated for #[story-id] (tag: bdd-ready)
Run this again? (yes/no)
```

- `"no"` -> exit.
- `"yes"` -> start over at Step 2.

If the fetched story/workflow state has `lastCompletedStage: "writebddfeatures.phase1.approved"` and `bddLayeringArtifact` exists on disk, offer resume:

```text
Found approved Phase 1 layering artifact for #[story-id]:
[bddLayeringArtifact]

Resume BDD feature authoring from Phase 2? (yes / rerun phase1 / stop)
```

- `"yes"` -> proceed directly to Step 3 using `bddLayeringArtifact`.
- `"rerun phase1"` -> proceed to Step 2.
- `"stop"` -> exit.

If the checkpoint exists in workflow state but the artifact is missing or not readable, warn that Phase 1 cannot be resumed and proceed to Step 2.

---

## Orchestration Rule

There must be exactly one approval owner: this command.

There must also be exactly one skill invoker: **bdd-agent**.

This command must not read, invoke, summarize, or inspect `.claude/skills/*` directly. It only sends invocation context to **bdd-agent**, displays the returned output verbatim, and appends this command's approval prompt.

**bdd-agent** applies the required skill internally and returns its phase output plus a handoff block. Do not ask for approval inside bdd-agent, and do not let bdd-agent write final `.feature` files.

---

## Step 2 - Test Layering Analysis + Approval

STOP: DESIGN-ONLY AGENT INVOCATION - Pass ONLY the structured context below to **bdd-agent**. Do NOT add extra skill instructions, phase descriptions, output format requirements, module tag hints, E2E paths, or any other text.

Phase 1 must not resolve `{E2E_DIR}`, validate directories, run shell discovery commands, inspect existing feature files, generate snippet catalogs, or scan source code. It designs layered test points from the loaded story only.

Invoke **bdd-agent** for Phase 1 with this context and nothing else:

```yaml
phase: 1
story: {already loaded story payload}
goal: design layered test points from this user story, save the Phase 1 JSON artifact, and return an approval-ready review summary with proposed test points, layer decisions, assumptions, risks, and artifact path
```

STOP: VERBATIM PASS-THROUGH - NO EXCEPTIONS:
Copy the bdd-agent output exactly as received. Do NOT reformat, condense, summarize, reorder, or add any text before the approval prompt.
If you find yourself rewriting any sentence, stop and paste the original.

Display bdd-agent **Complete Output** to the user, including the approval-ready layering summary and local artifact path, followed by this command's approval prompt.

Output the bdd-agent result as raw Markdown (no blockquote wrapping) so that tables render correctly.

**Approval required:**
- **approve** - Layering plan is correct, proceed to generate Feature files
- **revise** - Adjustments needed (e.g., move test points between layers, change test point IDs/tags, add/remove test points - please specify), re-invoke bdd-agent Phase 1.
- **stop** - Cancel this generation

Wait for user response:
- **approve** -> save a Phase 1 checkpoint, then proceed to Step 3 with the approved Phase 1 artifact path
- **revise** -> re-invoke bdd-agent Phase 1 with this context:

  ```yaml
  phase: 1
  story: {already loaded story payload}
  goal: revise the complete layering analysis using the user's requested changes
  revisionInstructions: {user's exact instructions}
  previousOutput: {verbatim Phase 1 output just displayed}
  previousArtifactPath: {Phase 1 artifact path, if available}
  ```

  Display the regenerated output verbatim; loop back to this approval prompt.
- **stop** -> end pipeline: `"Pipeline terminated."`

### Phase 1 Checkpoint

Immediately after Phase 1 approval and before resolving `{E2E_DIR}`, save a resumable checkpoint.

**If ADO mode:** use **ado-agent** (`SAVE`) to update:

- `lastCompletedStage`: `"writebddfeatures.phase1.approved"`
- `bddLayeringArtifact`: `{approved Phase 1 artifact path}`
- `bddLayeringApprovedAt`: `{current timestamp}`
- `bddFeatureFiles`: keep existing value, do not overwrite

**If JSON file mode:** use **Edit** to update the source JSON file with the same fields.

Do not add `bdd-ready` tags and do not update `bddFeatureFiles` at this checkpoint. Those belong only after feature files are written.

---

## Step 3 - BDD Feature Authoring + Approval

Before invoking **bdd-agent** for Phase 2, resolve `{E2E_DIR}` from root `CLAUDE.md` -> `# Repos` table and verify the E2E directory only once.

If `{E2E_DIR}` is optional and missing, stop with:

```text
E2E tests directory not present - /writebddfeatures skipped.
```

Phase 2 is the first phase allowed to inspect existing feature files, generate/read snippet catalogs, and decide whether to create or append feature files.

STOP: AGENT INVOCATION ONLY - Pass ONLY the structured context below to **bdd-agent**. Do NOT add extra skill instructions, phase descriptions, output format requirements, or any other text.

Invoke **bdd-agent** for Phase 2 with this context and nothing else:

```yaml
phase: 2
E2E_DIR: {resolved E2E_DIR}
story: {already loaded story payload}
layeringArtifactPath: {approved Phase 1 artifact path from Step 2, or bddLayeringArtifact when resuming}
approvedTestPoints: {approved Phase 1 artifact content or extracted Test Point List, only if artifact path is unavailable}
goal: author BDD feature content from the approved test points and return the complete feature authoring result for approval
```

STOP: VERBATIM PASS-THROUGH - NO EXCEPTIONS:
Copy the bdd-agent output exactly as received. Do NOT reformat, condense, summarize, reorder, or add any text before the approval prompt.
If you find yourself rewriting any sentence, stop and paste the original.

bdd-agent returns the **complete** result. Output it as raw Markdown (no blockquote wrapping) so that tables and gherkin blocks render correctly.

**Approval required:**
- **approve** - Feature content is correct, write to files
- **revise** - Adjustments needed (e.g., modify scenario steps, change parameters, add/remove scenarios - please specify), re-invoke bdd-agent Phase 2.
- **stop** - Cancel this generation

Wait for user response:
- **approve** -> proceed to Step 4
- **revise** -> re-invoke bdd-agent Phase 2 with this context:

  ```yaml
  phase: 2
  E2E_DIR: {resolved E2E_DIR}
  story: {already loaded story payload}
  layeringArtifactPath: {approved Phase 1 artifact path from Step 2, or bddLayeringArtifact when resuming}
  approvedTestPoints: {approved Phase 1 artifact content or extracted Test Point List, only if artifact path is unavailable}
  goal: revise the complete BDD feature authoring result using the user's requested changes
  revisionInstructions: {user's exact instructions}
  previousOutput: {verbatim Phase 2 output just displayed}
  ```

  Display the regenerated output verbatim; loop back to this approval prompt.
- **stop** -> end pipeline: `"Pipeline terminated."`

---

## Step 4: Write Feature Files

Use only the approved Phase 2 output from **bdd-agent**. Ignore the handoff block when writing files.

Prefer the `feature_write_plan` fenced block when present. It is not a persisted artifact; it is the deterministic write payload embedded in the approved Phase 2 response.

If `feature_write_plan` is absent, extract the gherkin content from the approved Phase 2 output.

Determine the target paths:
- Use the feature file paths reported in `feature_write_plan`, or in the approved Phase 2 output when the write plan is absent.
- Use the file modes reported in `feature_write_plan`, or in the approved Phase 2 output when the write plan is absent.
- Do not re-derive feature names, domains, or target paths in the orchestrator.
- If a feature file has zero scenarios or `mode: not generated`, do not create a file for that layer.

### For each feature file with scenarios (API and/or UI):

1. **Create directory if needed:**

   ```bash
   mkdir -p $(dirname {targetPath})
   ```

2. **Apply the approved file mode:**

   - **create** -> Write the complete feature content as a new file. If the file already exists unexpectedly, stop and ask for review.
   - **append** -> Read the existing file and append ONLY the approved new Scenario/Scenario Outline blocks. Do not append top-level tags, `Feature:`, descriptions, or `Background:`.
   - **not generated** -> Skip this layer.

3. **Write** using Write tool (new) or Edit tool (append)

---

## Step 5 - Save Workflow Context

**If ADO mode:**

Use **ado-agent** (`ADD_COMMENT`) with the coverage summary from Step 4:

Use the approved Phase 2 coverage matrix and written file list from Step 4.

Use **ado-agent** (`UPDATE_TAGS`) to add `bdd-ready` to `System.Tags`.

Use **ado-agent** (`SAVE`): `lastCompletedStage: "writebddfeatures.completed"`, `branch`, `module`, `bddFeatureFiles` (append all newly written file paths to existing array - do not overwrite), `bddType`, `tcTags`, keep `bddLayeringArtifact`.

**If JSON file mode:**

Use **Edit** to update the source JSON file: `lastCompletedStage: "writebddfeatures.completed"`, `bddFeatureFiles` (read current array value, append all newly written file paths, write back - do not overwrite), `bddType`, `tcTags`, keep `bddLayeringArtifact`.

---

## Step 6 - Summary

- Feature files created (full paths)
- Total: N @smoke, N @regression (N @positive, N @negative)
- Run command for the generated tests
- Next steps:
  - Continue BDD: `/writebddfeatures #[next-story-id]`
  - Start implementation: `/codeuserstory #[story-id]`
