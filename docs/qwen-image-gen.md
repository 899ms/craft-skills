# Qwen Image Gen: from request to inspected output

Install the complete `skills/qwen-image-gen` directory into your Agent's skill directory. For Codex, the default is `~/.codex/skills/`; back up an existing installation before replacing it. Invoke `$qwen-image-gen` after reloading the Agent.

The workflow distinguishes text-to-image, a local edit, and creating a new scene from a reference subject. It preserves literal text, identity/reference roles, and explicit creative constraints. A pose change must allow the corresponding body and clothing changes; a missing reference is not treated as an image the Agent has seen.

Aspect ratio is a parameter decision. Convert it into the actual backend's width and height, then inspect returned dimensions. The bundled offline workbench helper implements one protocol, not a universal Qwen API. It does not download weights or submit jobs.

```sh
python3 -B skills/qwen-image-gen/scripts/prepare_workbench_request.py rewrite.json --quality high --seed 0 --out request.json
python3 -B -m unittest discover -s skills/qwen-image-gen/tests -v
```

Keep prompt-only work separate from authorized generation. Report unsupported backend capabilities rather than silently dropping references or resolution requirements. Preserve originals and compare corrected versions; a successful job is not evidence that a defect is fixed.

## Evidence

- [Four controlled research comparisons](../skills/qwen-image-gen/assets/examples/ab/README.md), with [prompts and parameters](../skills/qwen-image-gen/assets/examples/ab/cases.json).
- [Portrait examples](../skills/qwen-image-gen/assets/examples/portraits/README.md), with original prompts and seeds.
- [Validation and limitations](../evals/qwen-image-gen/VALIDATION.md).

The research comparisons used an existing language model with the official PE templates. They are not a controlled evaluation of the released Skill or the official PE weights. Complex chair poses remained unsuccessful. The public example PNGs retain their pixel stream but omit runtime metadata; provenance is documented in [ASSET-LICENSE.md](../skills/qwen-image-gen/ASSET-LICENSE.md).
