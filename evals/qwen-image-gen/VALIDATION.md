# Validation scope — v0.1.0 experimental candidate

Date: 2026-09-22.

## Deterministic checks

- The optional offline request builder has 10 executable tests: exact/approximate ratios, explicit canvas overrides, reference-byte preservation, unsupported edit sizes/multiple references, numeric/schema validation, private output permissions and overwrite refusal.
- The optional Node.js shared runtime has 12 tests covering deterministic bundle digests, rule/code version changes, path boundaries, separation of private context, required edit context, and rejection of model-supplied execution fields. Run `node --test skills/qwen-image-gen/tests/test_runtime.mjs` from the repository root. Runtime version 0.2.1 retains the existing module's version line while adopting the renamed Skill ID; it is distinct from this first public experimental package version.
- `validate_cases.py` checks case structure and route coverage; it does not score model behavior.
- The collection release checker verifies package layout, links, selected asset hashes/dimensions, and documented origins.

## Independent offline forward trial

A separate Agent received the Skill and eight new user requests, without the parent's expected answers or proposed fixes. It was restricted to offline prompt work and the request builder. Exact responses are retained in [forward-test.md](forward-test.md); machine-specific temporary paths are replaced with portable labels, with no substantive response edits.

Observed behaviors reviewed by the author:

- Literal tea-poster text and a separate portrait aspect ratio were preserved without submitting generation.
- Missing-reference edits and three-persona-scene drafts were explicitly provisional; no image inspection was invented.
- Unsupported two-reference/4K editing was explained as a backend limitation, with proposed alternatives kept unexecuted.
- The unrelated Midjourney request did not use the Qwen adapter.
- Transparency guidance distinguished real Alpha and evidence of native origin from a drawn checkerboard.
- Contradictory front/back pose requirements were identified before execution.
- The offline helper actually returned 1152×2048 and `submitted:false`. Because the request omitted the rewritten text, the evaluator used a disclosed placeholder; this is a parameter demonstration, not a production image request.

This trial checks task handling. It did not generate images, compare against an unskilled baseline, or prove a general quality gain. The explicit absence of a controlled unseen-image baseline remains a release limitation.

## Earlier image evidence

The four A/B research pairs use an existing language model with official PE templates, holding image-generation settings fixed. Three showed visible improvements and the chair-pose pair remained unsuccessful. These examples informed the Skill; they are not an independent evaluation of the final Skill. Portrait examples demonstrate subjects and rendering, not success rates.

## Before promoting beyond experimental

Run fresh image-level cases with and without the Skill on an identified backend; hold generation parameters fixed, inspect original outputs, and retain failures. Revalidate any backend-specific size or reference capability instead of treating the included workbench adapter as universal.
