# Recurring Character Diary Comic Skill

[English](recurring-character-diary-comic.md) | [简体中文](recurring-character-diary-comic.zh-CN.md)

[Back to the Craft Skills collection](../README.en.md)

An experimental Codex skill for creating, auditing, and repairing 4–8 panel
diary-comic episodes around an existing authorized recurring character.

It is not a comic-style prompt, a character-design tool, a workflow for
imitating a named living artist, or a publishing bot. It turns story facts,
identity invariants, cross-panel states, directional relations, and exact
dialogue into inspectable contracts, then separates textless art, page
composition, lettering, and final artifact review.

**Status: v0.1 experimental.** Structured workflows, compositor checks, and
behavioral evals do not guarantee that a black-box image model will render every
requirement correctly, and no acceptance state grants publication authority.

## When to use it

Use the skill when all of these are true:

- an established original, public-domain, or otherwise authorized recurring
  character already has a usable identity reference;
- the source is a concrete anecdote, conversation, dream, or viewpoint that can
  become a self-contained 4–8 panel episode;
- identity, exact dialogue, cross-panel state, or a physical relation must stay
  inspectable rather than being left to a single long prompt.

Do not use it for standalone character design, educational explainers,
infographics, one-off illustrations, generic memes, imitation of a named living
artist, unauthorized use of copyrighted franchise characters, watermarking, or
social-platform publishing. Public-domain characters, properly licensed
franchise material, and lawful references to historical artists are not
categorically excluded. When no usable recurring-character identity exists,
the workflow stops with profile requirements instead of quietly inventing a
permanent identity.

## Modes

| Mode | Intended result |
|---|---|
| `Create` | Lock the story and visual contracts, generate textless candidates, compose the page, add exact dialogue, and inspect the final artifact. |
| `Audit` | Inspect a supplied page and report identity, anatomy, text, relation, continuity, and layout evidence without editing it. |
| `Repair` | Audit first, then regenerate one failed independent panel or produce a constrained repair specification without redrawing passing content. |

## Install

```sh
git clone https://github.com/ZSeven-W/craft-skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R craft-skills/skills/recurring-character-diary-comic \
  "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart or reload the agent session if the skill is not discovered
immediately.

The deterministic compositor is an optional runtime component. It requires
Python 3.10 or newer and the pinned Pillow version:

```sh
python3 -m pip install -r \
  craft-skills/skills/recurring-character-diary-comic/scripts/requirements.txt

python3 \
  craft-skills/skills/recurring-character-diary-comic/scripts/self_test_compositor.py
```

Lettering also needs a locally available CJK font whose license permits the
intended use. No font is distributed with this repository. The example
manifest is a structural template, not a ready-to-render fixture.

## Invoke

Name the skill and mode explicitly when predictable routing matters.

### Create

```text
Use $recurring-character-diary-comic in Create mode.

I own the attached recurring-character references. Turn this anecdote into a
five-panel diary comic: she puts her lunch box beside the door so she cannot
forget it, then steps over it on the way out.

Lock the story, identity invariants, and all dialogue first. Generate textless
panels, inspect their native-resolution crops, then compose and letter the page
deterministically. Do not add a logo, watermark, or publish anything.
```

### Audit

```text
Use $recurring-character-diary-comic in Audit mode. Do not edit the attached
final page. Inspect identity, exact dialogue, hands, directional objects,
cross-panel state, and reading order at original resolution. Report
contract_fidelity, editorial_layout, and exposure separately.
```

### Repair

```text
Use $recurring-character-diary-comic in Repair mode. Only address the extra
finger on the lead character's left hand in panel 4. Keep every other panel,
face, outfit, line of dialogue, bubble, layout, and color unchanged. If the
available editor cannot prove off-target preservation, return a repair
specification instead of regenerating the whole page.
```

## What the workflow enforces

1. **Premise gate.** Prefer a visible behavior, an unspoken motivation, and a
   mild reveal over an abstract slogan.
2. **Story contract.** Lock the observable beats, cast, props, state changes,
   speaker ownership, punctuation, and exact dialogue before image generation.
3. **Visual contract.** Give important characters, objects, states, and
   relations stable IDs, then classify requirements as story-critical `S0`,
   identity-critical `S1`, or replaceable composition preference `S2`.
4. **Risk route.** Use whole-page generation only for eligible low-risk pages.
   Use panel-by-panel generation for longer or multi-character episodes, and
   generate the decisive causal panel first when the relation is difficult.
5. **Layout preflight.** Prove that the intended crop can retain all required
   faces, hands, actions, speaker anchors, and protected regions before spending
   another stochastic art attempt.
6. **Textless art first.** Keep bubbles and text out of image-model output by
   default. Freeze accepted panel inputs, then assemble and letter them with the
   compositor.
7. **Artifact QA.** Inspect the actual original-resolution panel, selected crop,
   unlettered page, and lettered final. A correct prompt or successful command
   is not acceptance evidence.
8. **Bounded repair.** Replace one failed panel or a verifiably constrained
   region; never hide a broad redraw behind the word “repair.”

## Technical acceptance versus showcase quality

The skill keeps two review axes separate:

- `contract_fidelity` checks story, identity, anatomy, relations, continuity,
  exact text, and the named final-artifact hash;
- `editorial_layout` checks reading path, beat hierarchy, panel-shape rhythm,
  border language, inset integrity, intentional negative space, final-beat
  emphasis, and the thumbnail silhouette.

A page can pass the technical contract and still fail as a public example if it
looks like a uniform card grid, contains an accidentally cropped reaction
strip, wastes space without narrative intent, or gives the ending too little
weight. `accepted`, `showcase-ready`, user approval, and publication authority
remain separate states.

## Deterministic composition

The optional compositor reads a locked manifest, verifies source hashes and
geometry, assembles independent panels, protects action regions, and renders
approved bubbles and exact Simplified Chinese text. It supports rectangular and
irregular panel footprints, bounded rotation, explicit overlap, z-order, and a
deterministic paper matte. Unknown manifest keys fail closed so misspelled
geometry fields are not silently ignored.

```sh
python3 \
  "${CODEX_HOME:-$HOME/.codex}/skills/recurring-character-diary-comic/scripts/compose_panels.py" \
  --manifest /path/to/compositor-manifest.json
```

The compositor records its inputs, font snapshot, runtime versions, geometry,
and output hashes. Byte-identical repeatability is claimed only within the same
recorded OS and runtime build using the same Python, Pillow, raster libraries,
font bytes, manifest bytes, and panel bytes. Cross-platform or cross-library
byte identity is not promised.

## Public evals

The public suite is documented in
[`evals/recurring-character-diary-comic`](../evals/recurring-character-diary-comic/README.md).
It covers routing, Create/Audit/Repair boundaries, rights safety, story and
visual contracts, risk routes, relation evidence, layout feasibility, and the
two-axis publication gate.

```sh
python3 -m pip install -r \
  evals/recurring-character-diary-comic/requirements.txt

python3 evals/recurring-character-diary-comic/self_test_validate_cases.py
python3 evals/recurring-character-diary-comic/validate_cases.py \
  evals/recurring-character-diary-comic/cases.yaml
python3 scripts/check_release.py
```

Artifact-bound cases are intentionally `deferred` because the public package
does not distribute internal raster fixtures. Deferred is neither pass nor fail
and must not be reported as completed visual testing.

## Source, rights, and media policy

This release contains method text, code, templates, and public-safe behavioral
tests. It does not contain user characters, internal held-out pages, tutorial
production assets, generation histories, downloaded source media, or private
stories.

Treat production ledgers as private build evidence until they have been
reviewed and sanitized. A ledger can contain local source, font, and output
paths even when the resulting comic page is safe to publish.

Users must have the rights needed to generate, edit, and publish every supplied
character, reference, distinctive mark, and line of text. Apache-2.0 covers
only repository material the contributors may license; it does not license
user inputs, third-party fonts, likenesses, brands, model outputs, or linked
material. See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Package layout

```text
skills/recurring-character-diary-comic/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/
└── templates/

evals/recurring-character-diary-comic/
├── README.md
├── cases.yaml
├── requirements.txt
├── self_test_validate_cases.py
└── validate_cases.py
```

## License

Original project material is available under the
[Apache License 2.0](../LICENSE), subject to the rights boundaries above.
