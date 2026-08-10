# Visual Task Contract for recurring-character comics

Use this contract for the v2 creation path when a comic contains recurring
identity, cross-panel continuity, directional objects, or physical causality.
It applies the useful part of
[Context Scaling](https://heheyas.github.io/context-scaling/)—a small set of
addressable facts connected to rendered evidence—without introducing a
universal design schema. See also the
[research paper](https://arxiv.org/abs/2607.29679).

This file defines two records:

- an immutable `ComicVisualTaskContract`, locked before art generation;
- a mutable `ComicRunRecord`, which records routing, artifacts, attempts, checks,
  and the final outcome.

## Contents

- [Scope and non-goals](#scope-and-non-goals)
- [Constraint levels](#constraint-levels)
- [Minimal contract shape](#minimal-contract-shape)
- [Addressable entities, states, and relations](#addressable-entities-states-and-relations)
- [Provenance and unknowns](#provenance-and-unknowns)
- [Panel risk score](#panel-risk-score)
- [Generation routing](#generation-routing)
- [Artifact stages and evidence ledger](#artifact-stages-and-evidence-ledger)
- [Layout feasibility and freeze point](#layout-feasibility-and-freeze-point)
- [Bounded attempts](#bounded-attempts)
- [Completion rule](#completion-rule)
- [Compact execution sequence](#compact-execution-sequence)

The contract is not a longer prompt. Compile only the relevant slice into each
generation or review call. Keep the approved script, character profiles, and
source material as authoritative inputs rather than copying all their prose into
every call.

## Scope and non-goals

The contract covers only short recurring-character diary comics. It does not
attempt to model arbitrary design documents, brand systems, videos, UI screens,
or image-generation provider settings.

It is designed to answer five practical questions:

1. Which story and identity facts are immutable?
2. Which entity state must be visible in each panel?
3. Which relation must the pixels prove rather than merely suggest?
4. Which panel is risky enough to require isolated generation?
5. Which exact artifact was inspected, rejected, or accepted?

Rights confirmation and a valid character profile remain generation
preconditions. Refer to the profile by stable identifier; do not duplicate the
entire character schema here.

## Constraint levels

Classify requirements by their acceptance consequence, not by how easy they are
to describe.

| Level | Meaning | Typical comic requirements | Acceptance effect |
| --- | --- | --- | --- |
| `S0` | Story truth | panel count and order, required beat, exact dialogue and speaker, key prop count/state, directional reader, physical causal chain, forbidden extra text | Blocking |
| `S1` | Identity and embodiment truth | recurring identity, asymmetric feature, anatomy, plausible grip/contact, approved mark and wardrobe | Blocking |
| `S2` | Presentation preference | camera suggestion, exact bubble-reserve corner, texture, palette nuance, border shape, optional background detail | Non-blocking; use for ranking candidates |

All unresolved `S0` and `S1` checks prevent `Pass`. An `S2` mismatch must be
reported but does not invalidate otherwise correct story and identity evidence.
If a compositional request truly must decide acceptance, classify it as `S0`
before the contract is locked; do not promote it after seeing a candidate.

Rights, authorization, and contradictory hard requirements are preflight gates,
not `S0`/`S1`/`S2` preferences. Generation must not begin while any is invalid.

## Minimal contract shape

Store the contract as YAML or equivalent structured data. Use the public-safe
[example contract](../templates/visual-task-contract.example.yaml) as a shape,
then omit unused optional fields instead of filling them with invented values.
The required top-level groups are `sources`, `story`, `entities`, `states`,
`relations`, `dialogue`, `panels`, `global_rules`, `unknowns`, `routing`, and
`attempt_budget`. The example is illustrative; calculate risk from the rules
below rather than copying its score.

## Addressable entities, states, and relations

### Entities

Give every story-relevant character, prop, directional surface, environment, and
locked text line a stable identifier. Do not create entities for incidental
background decoration.

An entity should contain only recognition facts needed across panels. Character
identity belongs in the referenced character profile. Repeat only the exact
invariants needed by a particular panel slice.

### States

Use a state when an entity's observable condition matters in one panel or
changes across panels. Each fact has:

- `field`: a narrow addressable property such as `location`, `orientation`,
  `owner`, `contents`, `assembly`, `visibility`, or `damage`;
- `value`: the expected observable value;
- `level`: `S0`, `S1`, or `S2`;
- `source`: one source identifier.

Prefer `mug.location: inside-sink` to “the mishap has happened.” Do not encode
emotion as an object state when it cannot be inspected visually.

### Relations

Use relations for facts that cannot be verified by inventory alone. The compact
predicate vocabulary is:

- spatial: `inside`, `on`, `beside`, `behind`, `aligned_with`;
- contact: `holds`, `touches`, `connected_to`, `passes_through`,
  `inserted_into`;
- direction: `faces`, `points_toward`, `read_by`, `operated_by`;
- movement: `moves_toward`, `pulls`, `pours_into`, `transfers_to`.

Add a new predicate only when none of these can express the acceptance check.
Do not use vague predicates such as `interacts_with`, `uses_correctly`, or
`looks_at_naturally`.

Every `S0` physical or directional relation must declare:

- the visible contact, opening, surface, or direction that proves it;
- forbidden proxies that might look plausible at thumbnail size;
- the expected resulting state when it participates in a causal chain.

Object co-occurrence is not relation evidence. A towel next to a mug does not
prove `passes_through`; a tab beside a slot does not prove `inserted_into`; a
printed page visible to the audience does not prove it faces the named reader.

### Evidence checks

Compile each `S0`/`S1` fact and relation into one addressable check:

```yaml
- check_id: relation-towel-drags-mug
  target: relation:towel-drags-mug
  panel: p3
  expected: "threaded contact plus tension toward the sink"
  method: original-resolution-visual-review
  result: pending
```

Use deterministic checks for file hashes, panel count where machine-readable,
lettering strings, text regions, and outside-mask pixel preservation. Use
original-resolution visual review for identity, anatomy, contact, orientation,
and causal evidence. A prompt containing the right field is not evidence.

## Provenance and unknowns

Every `S0` and `S1` item must point to one of the declared sources. Allowed
source kinds are:

- `user`;
- `story-contract`;
- `character-profile`;
- `authorized-reference`;
- `skill-rule`;
- `planner-inference`.

Planner inference may propose `S2` defaults. It may not silently invent an
`S0`/`S1` fact, change a character invariant, or resolve a conflict. Promote an
inference only after it is supported by another authoritative source and record
that source.

Record uncertainty instead of converting it to confident prose:

```yaml
unknowns:
  - id: unknown-reader-p2
    field: relation:instruction-card.faces
    affects: S0
    reason: "the approved story does not identify the current reader"
    resolution: ask-or-block
    status: open
```

An open `S0` or `S1` unknown blocks contract locking and generation. An open
`S2` unknown may use a conservative default, but the chosen default and source
must remain visible in the contract. Never rewrite an unknown after generation
to match what the image model happened to draw.

## Panel risk score

Score every panel before selecting a generation route. Add each applicable
factor once per panel, then cap the score at 10.

| Risk factor | Points |
| --- | ---: |
| State must continue from or produce a different panel state | +1 |
| Exact count, unique small mark, or easily duplicated prop | +1 |
| Visible asymmetric identity feature | +1 |
| Fully visible hand, precise grip, or tool operation | +1 |
| Two or more characters physically interact | +1 |
| Spatial contact/containment must be visually exact | +1 |
| Directional screen, paper, sign, control, or reader relationship | +2 |
| Physical causality such as threading, insertion, pulling, pouring, or transfer | +3 |

Do not add text-rendering risk when approved text is added deterministically.
If text is intentionally delegated to an image model, add `+2` and record the
deviation from the default pipeline.

Interpret scores as:

- `0–2`: low risk;
- `3–5`: medium risk;
- `6–10`: high risk.

The score predicts generation isolation; it does not lower the acceptance gate.
Keep this raw score unchanged. For routing and eval labels, classify a raw
`0–5` panel as effective high risk (`L3`) when it contains the story's decisive
`S0` causal relation; record the override reason as
`decisive-s0-causal-relation`. Do not invent extra risk factors merely to push
the raw score into `6–10`.

## Generation routing

Choose and lock one of these routes before art generation:

### `whole-page`

Allowed only when all of the following are true:

- at most four panels;
- every panel scores `0–2` and the page total is at most 6;
- no `S0` cross-panel causal relation;
- no directional reading object;
- no multi-character physical interaction;
- no threading, insertion, transfer, or similarly exact contact action.

Generate art without text or bubbles. Deterministic lettering remains a later
stage.

### `panel-by-panel`

Use when any panel scores `3–5`, the page has more than four panels, multiple
characters require distinct identity/dialogue ownership, or whole-page
eligibility fails. Generate each panel as an independent artifact and compose
only panels marked `accepted-for-next-stage` with a deterministic layout step.

Each panel call receives only:

- that panel's beat, cast, states, relations, and negative evidence;
- applicable character invariants and references;
- the immediately preceding state and required next state;
- medium direction and framing preference;
- the no-text/no-mark rule.

Do not paste the entire page contract into every panel prompt.

### `key-panel-first`

This is a specialization of `panel-by-panel`. Use it when any panel scores
`6–10` or contains the story's decisive `S0` causal relation. Generate and
inspect the highest-risk proof panel first. If the proof panel exhausts its
budget, stop the run before spending calls on ordinary setup panels.

The following always force at least `panel-by-panel`, regardless of the numeric
score:

- `passes_through` or `inserted_into` as an `S0` relation;
- a directional surface whose current reader/operator matters;
- an `S0` relation whose result must become another panel's state;
- physical contact between two characters.

## Artifact stages and evidence ledger

Keep the locked contract immutable. Record produced files and review results in
a separate `ComicRunRecord`:

```yaml
run_version: comic-run-v2
run_id: "<unique id>"
contract_ref: "<path or artifact id>"
contract_sha256: "<hash of locked contract>"
route: key-panel-first
art_generations_used: 0
task_lineage_id: "<stable story-task id>"
parent_run_ids: []
task_lineage_art_generations_used: 0
task_lineage_stochastic_budget: 10
artifacts: []
outcome: in-progress
```

`art_generations_used` counts the current run; the task-lineage counter is
cumulative across layout-driven successor runs and is the value checked against
the approved stochastic budget.

Each artifact ledger entry contains:

```yaml
- artifact_id: panel-p3-v1
  stage: unlettered-panel
  path: "<artifact path>"
  sha256: "<file hash>"
  dimensions: [1536, 1024]
  derived_from: [lead-reference-v2]
  attempt: 1
  status: accepted-for-next-stage
  inspected_at_original_resolution: true
  composition_binding:
    source_crop: [80, 60, 1456, 960]
    target_frame: [40, 600, 1160, 1120]
    evidence_check: pass
    manifest_ref: null
    manifest_sha256: null
  checks:
    - {check_id: relation-towel-drags-mug, result: pass}
  unresolved: []
```

An `unlettered-panel` marked `accepted-for-next-stage` must carry a
`composition_binding` containing the inspected source crop, target frame, and
evidence result. When the compositor manifest is locked, fill its reference and
hash. Changing the crop, frame, source dimensions, or manifest binding returns
the panel to `inspected` until the cropped artifact is checked again; it cannot
inherit the earlier next-stage acceptance.

Use these run checkpoints in order:

1. `story-locked` — semantic beats, cast, states, and exact dialogue fixed;
2. `layout-preflight` — canvas and reading order fixed; draft frames, evidence
   reservations, safe regions, and protected regions jointly pass feasibility;
3. `contract-locked` — all sources resolve; no open `S0`/`S1` unknown; route,
   budget, and the preflighted render contract are frozen;
4. `identity-reference` — required identity/mark references inspected and
   accepted for generation;
5. `proof-panel-art` — high-risk `unlettered-panel` artifacts generated and inspected when routed;
6. `panel-art` or `whole-page-art` — `unlettered-panel` or `unlettered-page` candidates generated and inspected;
7. `page-composite` — panels marked `accepted-for-next-stage` arranged into an `unlettered-page` deterministically;
8. `art-inspection` — full unlettered page checked at original resolution;
9. `deterministic-lettering` — bubbles and exact approved strings rendered into a `lettered-final` artifact;
10. `final-inspection` — lettering, ownership, reading order, occlusion, and all
   earlier `S0`/`S1` checks rechecked on the final pixels;
11. `accepted`, `rejected`, or `not-verified` — terminal run outcome.

An artifact status is one of `generated`, `inspected`, `accepted-for-next-stage`,
`rejected`, or `not-verified`. `accepted-for-next-stage` is not final page
acceptance. A generated file cannot jump directly to `accepted-for-next-stage`,
and a run cannot become `accepted` before final inspection.

Each artifact's `stage` is one of `identity-reference`, `unlettered-panel`,
`unlettered-page`, `lettered-final`, or `repair-candidate`. Run checkpoints and
artifact stages are separate: for example, the `proof-panel-art` checkpoint
produces and inspects an `unlettered-panel` artifact.

Record artifact paths, hashes, dimensions, parent artifacts, and original-
resolution inspection state. Retain rejected attempts; do not overwrite them
with later candidates.

## Layout feasibility and freeze point

Treat layout as an evidence container, not only a visual arrangement.

Before stochastic generation, reserve the target frame for all required content:

- project the expected bounds of every S0/S1 state, identity cue, contact point,
  directional surface, and speaker anchor into the target frame;
- reserve bubble safe regions and expand protected action regions by the planned
  stroke, collision margin, and resampling halo;
- reject or revise the S2 camera, crop plan, or panel proportion when no crop at
  the target aspect ratio can contain all required evidence and lettering at
  once.

After a source panel passes at original resolution, choose the exact source crop
and repeat the check on actual pixels. A full-source pass never authorizes a crop
that removes required identity, anatomy, contact, state, or dialogue ownership
evidence.

An expected crop remains an S2 plan until the compositor manifest records the
accepted source hash, decoded dimensions, exact crop, target frame, safe regions,
and protected regions. Once that manifest is locked, those values are hard
reproducibility inputs. Changing any of them produces a new manifest and page
artifact and requires fresh unlettered and final inspection.

If original-resolution candidates pass but the planned frame repeatedly fails
this feasibility check, preserve the failed run and begin a new run with revised
S2 layout. Record the parent run and carry forward the task lineage's cumulative
`art_generations_used` and remaining stochastic budget; changing the run ID must
not reset either value. Pure deterministic layout changes and reuse of frozen
sources consume no stochastic calls. Any increase beyond the already approved
task-lineage budget requires explicit approval. Do not consume additional
stochastic attempts on a geometrically impossible crop.

## Bounded attempts

Lock the stochastic budget with the contract. Recommended defaults are:

- at most 2 identity-reference attempts per required character;
- at most 2 whole-page art attempts when using `whole-page`;
- at most 2 art attempts per panel when using a panel route;
- at most 1 localized repair per artifact and named defect, only when the edit
  tool can constrain the target region;
- at most 10 stochastic art generations for one 4–8 panel task lineage,
  including layout-driven successor runs;
- stop after 2 consecutive attempts fail to improve the named blocking check.

Deterministic layout and lettering corrections do not consume stochastic art
calls, but every changed output receives a new artifact identifier and a new
inspection.

Apply these stop rules:

1. Reject a local repair immediately if it changes pixels outside the allowed
   region; return to the saved baseline.
2. Stop the run when a required proof panel exhausts its budget.
3. Stop when the page-wide budget is exhausted, even if unused panel budgets
   remain.
4. Never weaken `S0`/`S1`, change evidence wording, or reclassify a failed rule
   to make a candidate pass.
5. Every successor run preserves its parent record and inherits the same task-
   lineage generation count. Continuing after exhaustion requires a new run
   identifier and an explicitly approved additional budget; a new identifier
   alone never restores allowance.

## Completion rule

A run is `accepted` only when:

- all `S0` and `S1` checks pass on the final original-resolution artifact;
- no blocking unknown or unresolved issue remains;
- deterministic lettering matches every locked string and speaker;
- the final artifact hash is the hash that was actually reviewed;
- no local repair introduced off-target drift.

Use `rejected` when a blocking defect remains. Use `not-verified` when the named
artifact, source, reference, or original-resolution pixels are unavailable.
Visual attractiveness and prompt compliance claims never substitute for these
checks.

## Compact execution sequence

```text
authorized sources
  -> lock semantic story, cast, states, and exact dialogue
  -> draft canvas, frames, crop/evidence reservations, and text-safe regions
  -> pass whole-page layout-feasibility preflight
  -> lock the visual contract
  -> score panels and freeze route/budget
  -> generate highest-risk proof panel when required
  -> generate and accept art units
  -> deterministic page composition
  -> original-resolution art inspection
  -> deterministic bubbles and lettering
  -> final original-resolution inspection
  -> accepted / rejected / not-verified
```

This protocol is successful when it makes failures addressable and stops wasted
generation early. It does not guarantee that a black-box image model will
render every structured relation correctly.
