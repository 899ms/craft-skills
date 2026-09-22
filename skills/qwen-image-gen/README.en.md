# Qwen Image Gen

An experimental Agent workflow for an existing Qwen-Image setup: preserve user intent, distinguish local edits from reference-guided creation, translate aspect-ratio decisions into backend parameters, and inspect actual outputs.

**v0.1.0 experimental candidate.** Your current Agent performs the rewrite. Image generation requires your own authorized connection; this package does not download models or provide a universal online client.

```text
Use $qwen-image-gen to prepare a 3:4 tea poster prompt. Preserve the exact
Chinese headline and price. Return a prompt and canvas decision; do not generate.
```

- [English guide](../../docs/qwen-image-gen.md)
- [Workflow](SKILL.md)
- [Controlled research examples](assets/examples/ab/README.md)
- [Portrait examples and prompts](assets/examples/portraits/README.md)
- [Validation scope](../../evals/qwen-image-gen/VALIDATION.md)
- [Optional application runtime](references/shared-runtime.md) (Node.js 18+, offline)

The optional Python request builder is offline and targets one specific workbench protocol. Its limits are not universal Qwen limits. Official PE weights and full system prompts are not redistributed. Anatomical correctness and identity retention still require output inspection.
