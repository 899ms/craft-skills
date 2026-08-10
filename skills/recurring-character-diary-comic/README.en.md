# recurring-character-diary-comic

[简体中文](README.md) | [English](README.en.md)

An experimental Agent Skill for creating, auditing, and locally repairing
4–8 panel diary comics around an existing authorized recurring character.

It is more than a style prompt: the workflow locks story facts, recurring
identity, cross-panel states, directional relations, and exact dialogue before
generation. It then separates textless art, deterministic composition,
Simplified Chinese lettering, contract QA, and editorial-layout review.

[![Generated-original irregular diary-comic example](../../assets/examples/recurring-character-diary-comic/recurring-character-diary-comic-cover.png)](../../docs/recurring-character-diary-comic.md)

**Status: v0.1 experimental.** Technical acceptance, showcase readiness, user
acceptance, and publication authority remain separate states.

## When to use it

Use it when an original, public-domain, or explicitly authorized recurring
character already has a usable identity reference, and the input can become a
self-contained 4–8 panel anecdote, conversation, dream, or viewpoint.

Do not use it for standalone character design, educational explainers,
infographics, one-off illustrations, generic memes, imitation of a named living
artist, unauthorized franchise characters, watermarking, or social publishing.

## Modes

| Mode | Result |
|---|---|
| `Create` | Lock story and visual contracts, generate bounded candidates, compose, letter, and inspect the final page. |
| `Audit` | Inspect an existing artifact and report evidence without silently editing it. |
| `Repair` | Audit first, then replace one failed panel or return a constrained repair specification. |

## Install

```sh
git clone https://github.com/ZSeven-W/craft-skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R craft-skills/skills/recurring-character-diary-comic \
  "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Optional deterministic composition requires Python 3.10+ and the pinned
Pillow version:

```sh
python3 -m pip install -r \
  craft-skills/skills/recurring-character-diary-comic/scripts/requirements.txt
python3 \
  craft-skills/skills/recurring-character-diary-comic/scripts/self_test_compositor.py
```

A suitably licensed local CJK font is required for Chinese lettering; fonts are
not distributed in this repository.

## Quick start

```text
Use $recurring-character-diary-comic in Create mode.

I own the generation and editing rights for the attached recurring character.
Turn this anecdote into a five-panel diary comic. Lock the story, identity
invariants, speakers, and exact dialogue first. Generate textless panels, inspect
their original pixels and target crops, then compose and letter deterministically.
Do not add a logo, watermark, or publish anything.
```

## What the workflow enforces

1. A premise gate favors visible behavior and a small reveal over slogans.
2. A character profile separates identity invariants, episode variables, and
   forbidden drift.
3. Story and visual contracts classify story-critical `S0`, identity-critical
   `S1`, and replaceable composition `S2` requirements.
4. Risk routing selects `whole-page`, `panel-by-panel`, or `key-panel-first`.
5. Layout preflight proves that crops preserve faces, hands, actions, speaker
   anchors, and protected regions before more art attempts are spent.
6. Art is generated without text or bubbles by default, then composed and
   lettered deterministically.
7. QA inspects original panels, selected crops, the unlettered page, and the
   lettered final artifact.
8. Repair cannot redraw unrelated passing content and claim to be local.

Generation budgets are lineage-wide: starting a new run does not reset the
total, per-panel, or no-improvement limits.

## Two independent acceptance axes

- `contract_fidelity` covers story, identity, anatomy, relations, continuity,
  exact text, and final artifact hashes.
- `editorial_layout` covers reading path, beat hierarchy, panel-shape rhythm,
  border language, reaction panels, negative space, ending emphasis, and the
  thumbnail silhouette.

A technically correct page may still be rejected as a public showcase when it
looks like a uniform card grid, contains accidental dead space, or gives the
ending insufficient visual weight.

## Deterministic composition

The optional compositor binds source hashes, crops, frames, protected regions,
font bytes, bubbles, and exact Simplified Chinese strings. It supports irregular
polygons, bounded rotation, explicit overlap, z-order, and deterministic paper
matte. Unknown manifest keys fail closed.

```sh
python3 \
  "${CODEX_HOME:-$HOME/.codex}/skills/recurring-character-diary-comic/scripts/compose_panels.py" \
  --manifest /path/to/compositor-manifest.json
```

Byte-identical claims are limited to the same recorded OS/runtime build,
Python, Pillow, raster stack, font bytes, manifest, and panel bytes.

## Validation

```sh
python3 -m pip install -r \
  evals/recurring-character-diary-comic/requirements.txt
python3 evals/recurring-character-diary-comic/self_test_validate_cases.py
python3 evals/recurring-character-diary-comic/validate_cases.py \
  evals/recurring-character-diary-comic/cases.yaml
python3 skills/recurring-character-diary-comic/scripts/self_test_compositor.py
python3 scripts/check_release.py
```

Artifact-bound public eval cases remain `deferred` when their internal raster
fixtures are intentionally not distributed. Deferred is neither pass nor fail.

## Rights and publication boundary

Users must have the required generation, editing, and publication rights for
all character references, marks, fonts, text, portraits, brands, and outputs.
This repository does not include private profiles, held-out pages, generation
history, downloaded source media, or private stories.

## More

- [Agent workflow and trigger boundaries](SKILL.md)
- [Full English guide](../../docs/recurring-character-diary-comic.md)
- [中文完整方法说明](../../docs/recurring-character-diary-comic.zh-CN.md)
- [Public eval notes](../../evals/recurring-character-diary-comic/README.md)
- [Back to Craft Skills](../../README.en.md)
- [License](../../LICENSE) · [Third-party notices](../../THIRD_PARTY_NOTICES.md)
