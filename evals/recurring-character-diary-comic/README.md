# Recurring Character Diary Comic public evals

This directory contains the public-safe behavioral and schema tests for
`recurring-character-diary-comic`.

The exported suite covers Create, Audit, Repair, negative routing, rights
safety, story and visual contracts, page-native routing, risk-focused relation
evidence, three-skeleton layout selection, editorial-layout review, and
accidental card-grid failure. Risk labels never silently authorize panel
decomposition.
Artifact-bound cases are intentionally marked `deferred` because the public
package does not distribute the private raster fixtures.

Names and story beats that appear in semantic cases are generated-original,
fictional test data. They do not include or license any internal character
profile, prompt history, raster artifact, or publication asset.

`deferred` is neither pass nor fail. It preserves the expected contract and
hidden-oracle boundary without claiming that visual testing ran on an artifact
that is absent from this repository.

Use Python 3.10 or newer. Install the pinned validator dependencies and run:

```sh
python3 -m pip install -r evals/recurring-character-diary-comic/requirements.txt
python3 evals/recurring-character-diary-comic/self_test_validate_cases.py
python3 evals/recurring-character-diary-comic/validate_cases.py \
  evals/recurring-character-diary-comic/cases.yaml
```

Do not add internal run records, prompts, character references, generated
pages, QA crops, or publication assets to this directory. New public visual
fixtures require separate rights review, artifact-level QA, and release-checker
approval.
