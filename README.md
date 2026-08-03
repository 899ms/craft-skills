# Craft Skills

Research-backed, eval-driven skills for AI agents.

Craft Skills turns transferable craft knowledge into focused workflows with
explicit trigger boundaries, exit conditions, original examples, and forward
tests. It is not a video-summary archive, prompt dump, or style-cloning
collection.

Created and curated by [Fini Yang](https://github.com/finiking). Maintained by
[ZSeven](https://github.com/ZSeven-W).

## Skills

| Skill | Purpose | Status |
|---|---|---|
| [`logo-semantic-fusion`](skills/logo-semantic-fusion/SKILL.md) | Design and evaluate marks in which multiple meanings genuinely share geometry. [Read the guide and inspect the examples.](docs/logo-semantic-fusion.md) | v0.1 experimental |

[![Original Handoff semantic-fusion concept families](assets/examples/handoff/handoff-concept-sheet.png)](docs/logo-semantic-fusion.md)

“Experimental” means the workflow has structured tests and original examples;
it does not imply production readiness, trademark clearance, or professional
approval.

## Install

Clone the collection, then copy only the skill you want:

```sh
git clone https://github.com/ZSeven-W/craft-skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R craft-skills/skills/logo-semantic-fusion \
  "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart or reload the agent session if the skill is not discovered immediately.

## Release standard

Every published skill must:

- solve one narrow, reusable user goal;
- define both trigger and non-trigger boundaries;
- include applicability, exit, and evidence rules;
- use original examples and appropriately licensed assets;
- cover normal, incomplete, non-trigger, and edge cases in its evals;
- demonstrate improvement on unseen tasks, not only bundled examples;
- distinguish inspected artifacts from prompts or intended outputs;
- pass the repository's deterministic release checks;
- state material limitations and avoid unsupported professional or legal claims.

## Sources and media

Public educational material may inform a skill's methodology. Influential
sources are linked in that skill's provenance notes or third-party notice.
Attribution records research context and does not imply endorsement.

This repository does not include downloaded videos, audio, covers, screenshots,
transcripts, platform metadata, or third-party brand assets. Public examples
must be original or explicitly licensed. Research archives and acquisition
tools remain outside this repository and its release history.

## Contributing

Bug fixes, clearer instructions, additional evals, and original test cases are
welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing a new skill.

Do not submit automated source conversions, near-verbatim summaries, creator
style clones, scraped media, generic prompt collections, or outputs presented
as verified without artifact evidence.

## Validate

Run the deterministic release check from the repository root:

```sh
python3 scripts/check_release.py
```

## License

Original repository material is licensed under the
[Apache License 2.0](LICENSE). Linked or third-party material retains its
respective rights; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
