# Contributing

Craft Skills accepts focused workflow improvements, evals, original examples,
and new skills that show measurable value beyond a generic prompt.

## Propose a skill first

Open an issue before a large implementation. Include:

- one narrow user goal;
- direct, indirect, incomplete, and non-trigger request examples;
- the expected improvement over an agent without the skill;
- an eval plan using unseen tasks;
- the provenance and license of every public asset;
- material limitations and an intended maintenance owner.

## Submission requirements

A new skill must use a lowercase hyphenated directory under `skills/`, keep
`SKILL.md` concise, and place optional runtime material in `references/`,
`scripts/`, or `assets/`. Keep research archives, acquisition tools, source
media, and complete transcripts outside this repository.

Run:

```sh
python3 scripts/check_release.py
```

Include the relevant behavioral eval results and describe any forward test.
Passing deterministic checks does not replace artifact inspection or expert
review where a workflow requires it.

Maintainers may decline submissions that are too broad, redundant, weakly
tested, difficult to maintain, or dependent on imitating a creator's style.
