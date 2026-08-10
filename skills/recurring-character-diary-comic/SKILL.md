---
name: recurring-character-diary-comic
description: Plan, generate candidate panels for, compose, and audit short hand-drawn diary comics built around an existing authorized recurring character, with locked dialogue, field-addressable visual contracts, deterministic assembly, and artifact-level QA. Use when extending an established recurring-character comic series, turning a concrete anecdote or viewpoint into a 4–8 panel diary episode, auditing a comic page for identity, text, anatomy, prop, relation, or spatial defects, auditing broad or multi-defect comic-page requests before any repair, or replacing one failed panel without redrawing frozen passing panels. Do not use for standalone character or profile design, educational or knowledge-explainer comics, infographics, one-off illustrations, generic memes, imitation of a named living artist, use of a copyrighted franchise character without authorization, other unauthorized character or brand assets, wallpaper extraction, watermarking, or social-platform publishing.
---

# Recurring Character Diary Comic

Turn an anecdote, conversation, dream, or viewpoint into a self-contained comic episode while preserving a reusable character identity and inspecting the actual visual result.

## Load only the needed references

- Read [references/character-profile-schema.md](references/character-profile-schema.md) when creating or interpreting a recurring-character profile.
- Read [references/story-rhythm.md](references/story-rhythm.md) before selecting a premise, writing dialogue, or planning panels.
- Read [references/visual-task-contract.md](references/visual-task-contract.md) before locking visual constraints, scoring panel risk, choosing a generation route, or compiling panel prompts.
- Read [references/continuity-and-visual-qa.md](references/continuity-and-visual-qa.md) before auditing, repairing, or approving a rendered comic.
- Read [references/editorial-layout-gate.md](references/editorial-layout-gate.md) before selecting a technically accepted page as a README example, tutorial image, hero asset, portfolio piece, or other public-facing showcase.
- Read [references/compositor-manifest.md](references/compositor-manifest.md) and use [scripts/compose_panels.py](scripts/compose_panels.py) when assembling independent panels or rendering deterministic bubbles and Simplified Chinese text.
- Follow the available image-generation skill when generating or editing raster artwork.

## Choose the mode

- **Create:** require an existing authorized recurring-character identity, pass the premise gate, lock semantic intent, compile a visual task contract, generate candidate panels, compose, and inspect the final page.
- **Audit:** inspect an existing page against its character profile and approved script; report evidence without silently editing it.
- **Repair:** audit first. Prefer regenerating and deterministically replacing one failed independent panel. Use pixel-local editing only when the tool can constrain the named region and off-target preservation can be verified. Otherwise return a repair specification.

Do not expand the request into a brand system, publishing workflow, or unrelated illustration task.

## Establish rights and identity

1. Use only original characters, public-domain material, or references the user confirms they may use.
2. Refuse requests to reproduce a named living artist's style, use a copyrighted franchise character without authorization, or reproduce a third-party signature mark. Public-domain material and lawfully authorized references remain eligible; historical art references are not categorically excluded. Offer medium-level traits instead, such as graphite contours, restrained colored pencil, quiet natural color, or irregular diary-comic panels.
3. Normalize the supplied recurring-character identity into a complete profile before page generation. Separate:
   - identity invariants that must remain recognizable;
   - episode variables such as expression, pose, or temporary clothing;
   - optional marks or accessories that require their own exact reference;
   - forbidden drift.
4. Treat a standalone reference for a required mark or accessory as more authoritative than an incidental depiction inside a character sheet.
5. If no recurring character or usable identity reference exists, stop the episode workflow and return the profile requirements. Do not silently expand a comic request into standalone character design, and do not borrow a recognizable public figure or copyrighted franchise character without a confirmed rights basis.

## Build the episode

1. Apply the premise gate in `references/story-rhythm.md`. Prefer a concrete behavior over an abstract slogan.
2. Preserve the user's experience and viewpoint. Do not invent a different moral or turn the story into an advertisement.
3. Extract the setup, visual discovery, reactions, and final observation or reveal.
4. Choose 4–8 panels from the story rhythm. Avoid forcing an equal grid, and write the narrative job and intended visual weight of every panel before choosing its frame.
5. Let environments, objects, screens, or supporting characters carry beats when they communicate more clearly than another talking-head panel.
6. Give every supporting character a narrative job: trigger, contrast, witness, or interruption.
7. Write every approved string before generation. Lock spelling, punctuation, speaker, bubble ownership, and reading order.
8. Lock the semantic story contract first: observable behavior, psychology, reveal, exact dialogue, necessary cast, story-critical props, and required state changes.
9. Draft low-cost camera and evidence options before locking the render contract. A camera, crop, or bubble anchor is not immutable merely because it appeared in the first draft.
10. Produce a panel map containing the beat, cast, visible action evidence, camera, props, text anchor, relations, continuity state, intended visual weight, border treatment, and negative-space purpose for every panel. For each screen or paper, name its current reader and which surface the audience should see.
11. Before spending a stochastic art attempt, run a layout-feasibility preflight for every fixed frame. Project the S0/S1 evidence that must survive the crop, the bubble safe regions, and the protected action regions into the target frame. If one crop at the target aspect ratio cannot contain all of them at once, revise the S2 camera, crop plan, or panel proportion before generation. A full-source panel may pass while its composed crop fails.

## Compile the visual task contract

1. Give every character, prop, panel, state, and story-critical relation a stable semantic ID. Preserve the original user request and record whether each field came from the user, an authorized reference, the story method, or planner inference.
2. Classify constraints before generation:
   - **S0 story-critical:** required action, causal relation, cast, dialogue ownership, necessary prop, and final state;
   - **S1 identity-critical:** recognizable character invariants, anatomy, authorized marks, and continuity;
   - **S2 composition preference:** camera, crop, exact empty-space corner, panel proportion, texture nuance, and other replaceable implementation choices.
3. Treat S0 and S1 failures as blocking. Do not promote an S2 preference into a blocker unless changing it would break reading order, hide evidence, contradict the user, or violate an explicit approved requirement.
4. Express every critical relation as structured evidence: subject, predicate, object, contact points, visible proof, forbidden ambiguity, direction or force when relevant, and required next state. Mere overlap or co-occurrence is not proof of contact, insertion, reading direction, or causality.
5. Score each panel's risk from cast count, asymmetric identity, exact countable parts, directional objects, hand-object interaction, contact/insertion/flow, and cross-panel state changes. Record unknowns instead of guessing.
6. Use the route thresholds and predicate names in `references/visual-task-contract.md`. `whole-page` is allowed only when every eligibility rule passes. Use at least `panel-by-panel` for a directional reader or operator, an S0 `passes_through` or `inserted_into` relation, an S0 relation that produces another panel's state, or physical contact between two characters. Upgrade to `key-panel-first` only when a panel scores 6–10 or contains the decisive S0 causal relation.

## Generate candidate panels

1. Label every image input by role: identity reference, exact-mark reference, visual-medium reference, edit target, or supporting reference.
2. Do not use a reference with a known defect in any identity, anatomy, mark, or prop field that the target panel must preserve. A failed reference cannot be downgraded to a supporting reference for the same failing field.
3. For a low-risk whole-page route, use one bounded candidate followed by full-page QA. If it fails in more than one panel or any critical relation, switch to panel-by-panel generation rather than repeatedly redrawing the page.
4. For the panel route, lock the canvas, frame geometry, reading order, and evidence/lettering reservations first, then generate the highest-risk proof panel before ordinary narrative panels. Stop early if the story-critical relation cannot be made visible within the panel's attempt budget.
5. Compile a short prompt for only the current panel: relevant identity inputs, current state, one principal action or relation, camera/evidence view, medium, and at most the relevant forbidden ambiguities. Do not repeat the entire page contract in every panel prompt.
6. Translate asymmetric invariants into the current camera view: state which anatomical side is visible and whether an off-side feature should appear or be naturally hidden.
7. Keep the physical evidence of every required action visible. A relation panel should favor a close view and clear contact plane over simultaneously showing every face or environmental detail.
8. Use the same accepted identity and visual-medium reference bundle across the run. Do not swap a reference after marking the first panel `accepted-for-next-stage` without starting a new run and rechecking earlier panels.
9. Inspect every generated panel at original resolution against its stage contract. A full-source pass is necessary but not sufficient: select an exact crop at the target frame ratio and verify that the cropped pixels still contain every required S0/S1 state, identity cue, contact, speaker anchor, and protected region before marking the panel `accepted-for-next-stage`.
10. Treat an expected crop as S2 until an accepted source hash, decoded dimensions, exact crop, target frame, and protection regions are written into the compositor manifest. That manifest lock turns them into hard reproducibility inputs. Any later crop or frame change creates a new artifact and requires composition and inspection again.
11. When candidate sources pass at original resolution but the planned frame repeatedly cannot preserve their required evidence and lettering, preserve the failed run and start a successor run with revised S2 layout. The successor inherits the same task lineage's remaining stochastic budget; a new run identifier never resets generation counts. Pure layout changes and reuse of frozen sources cost no stochastic calls, while any additional art allowance requires explicit approval. Do not spend more stochastic attempts trying to satisfy an impossible crop.
12. Generate art without rendered text or speech bubbles. Compose only panels marked `accepted-for-next-stage` into the locked layout deterministically, then add bubbles and text as a separate stage.
13. Do not claim success from a prompt, plan, storyboard, candidate file, or tool-completion message alone.

## Handle text reliably

1. Use deterministic bubble and text composition by default when an available tool supports the required language. The image model should normally produce textless, bubble-free panel art.
2. Record speaker anchor, bubble order, safe region, and protected action regions in the panel manifest. Set the exact bubble position during deterministic composition inside the approved safe region instead of requiring the image model to reserve one arbitrary corner.
3. Compare the composed dialogue character by character with the locked script. Reject misspellings, rewritten wording, extra text, wrong speaker attribution, ambiguous order, or action-obscuring bubbles.
4. Record the art and lettering as separate artifact stages, including compositor inputs, font or renderer, coordinates, and output hash when available.
5. Do not describe a page as final while required text or composition-scope preservation remains unverified.

## Inspect and repair

1. Apply the contract-fidelity gate in `references/continuity-and-visual-qa.md` at original resolution. If the page may be shown as an example or public-facing asset, also apply the independent gate in `references/editorial-layout-gate.md` to the same final hash at normal reading size.
2. Declare the artifact stage before judging it: `identity-reference`, `unlettered-panel`, `unlettered-page`, `lettered-final`, or `repair-candidate`. Do not fail an intentionally unlettered stage for missing dialogue.
3. Enumerate each panel's cast, visible hands, directional props, relation evidence, state transitions, and approved strings instead of relying on a general impression.
4. For every critical relation, verify positive visible evidence. Trace the contact geometry, current reader or operator, direction or force vector, and next state. Do not infer a relation from nearby objects.
5. Classify each contract-fidelity stage outcome as `pass`, `fail`, or `not-verified`; mark defects with the contract field, severity, evidence locator, and next action. Record editorial layout separately instead of upgrading or downgrading the S0/S1 result for aesthetic reasons.
6. Prefer regenerating one failed independent panel and replacing it in the deterministic composition. This is `panel regeneration`, not a pixel-local repair; unchanged panels must retain their recorded inputs and hashes.
7. For an actual pixel-local repair, define the allowed region, compare the repaired image with the pre-edit version outside it, and reject the first attempt that globally redraws, reflows, or restyles unrelated pixels.
8. Recheck the corrected panel or region and then the composed page. Return to the accepted pre-edit artifact when a repair introduces drift; do not repair the repair.
9. Stop on explicit acceptance, on the contract's bounded attempt limit, or when two consecutive attempts fail to improve the named field without damaging locked content. Report the blocker rather than silently weakening the contract.

## Deliver evidence

For a completed creation, deliver:

- the character profile or the profile identifier used;
- the locked semantic story contract, dialogue, visual task contract, and panel map;
- the risk route and attempt ledger;
- panel artifacts marked `accepted-for-next-stage`, or their identifiers and hashes;
- the final page artifact;
- a concise QA record listing the checks actually performed;
- when the artifact is a candidate example, the structured editorial-layout record and `showcase-ready` or `internal-only` exposure;
- unresolved limitations, if any.

Keep evidence and decision states distinct:

- `planned`: story and panel map exist;
- `generated`: a reference, panel, or page artifact exists but may be unchecked;
- `inspected`: the named checks were performed on the artifact, with a `pass`, `fail`, or `not-verified` result;
- `accepted-for-next-stage`: a non-final artifact passed the checks required for its next stage;
- `accepted`: the terminal run passed every S0/S1 check on the reviewed final-artifact hash;
- `showcase-ready`: the same accepted final hash also passed every editorial-layout check and the accidental card-grid test;
- `internal-only`: the artifact may remain useful for engineering or regression evidence but is blocked from examples because contract fidelity or editorial layout failed or was not verified;
- `user-approved`: an optional user decision recorded separately from technical acceptance and from any authority to publish.

Never promote `planned` or `generated` work to `inspected`, `accepted`, or `showcase-ready` without visual evidence. `accepted` alone is not a public-example verdict. User approval of disclosed limitations does not convert a technically failed or not-verified run into `accepted`, and none of these states grants publication authority.
