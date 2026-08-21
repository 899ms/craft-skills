#!/usr/bin/env python3
"""Public-safe synthetic checks for resolved eval fixture validation."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import struct
import sys
import tempfile
import warnings
import zlib
from collections.abc import Callable
from pathlib import Path

from PIL import Image

sys.dont_write_bytecode = True

from validate_cases import (
    ValidationError,
    validate_bound_payload,
    validate_case_wrapper,
    validate_contract_oracle_wrapper,
    validate_editorial_layout_record,
    validate_exposed_input_wrapper,
    validate_fixture_wrapper,
    validate_hidden_oracle,
    validate_required_inputs,
    validate_role_record,
    validate_root_wrapper,
    validate_runner_contract_wrapper,
    validate_resolved_bindings,
    validate_resolved_verdict,
)


def must_fail(action: Callable[[], object], label: str) -> None:
    try:
        action()
    except ValidationError:
        return
    raise AssertionError(f"expected ValidationError: {label}")


def png_bytes(size: tuple[int, int]) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, "white").save(buffer, format="PNG")
    return buffer.getvalue()


def jpeg_bytes(size: tuple[int, int]) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, "white").save(buffer, format="JPEG")
    return buffer.getvalue()


def apng_bytes(size: tuple[int, int]) -> bytes:
    buffer = io.BytesIO()
    first = Image.new("RGB", size, "white")
    second = Image.new("RGB", size, "black")
    first.save(
        buffer,
        format="PNG",
        save_all=True,
        append_images=[second],
        duration=100,
        loop=0,
    )
    return buffer.getvalue()


def with_png_control_chunks(
    payload: bytes,
    chunks: list[tuple[bytes, bytes]],
) -> bytes:
    ihdr_length = int.from_bytes(payload[8:12], "big")
    insert_at = 8 + 12 + ihdr_length
    encoded_chunks = []
    for chunk_type, chunk_data in chunks:
        crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
        encoded_chunks.append(
            struct.pack(">I", len(chunk_data))
            + chunk_type
            + chunk_data
            + struct.pack(">I", crc)
        )
    return payload[:insert_at] + b"".join(encoded_chunks) + payload[insert_at:]


def with_png_control_chunk(payload: bytes, chunk_type: bytes, chunk_data: bytes) -> bytes:
    return with_png_control_chunks(payload, [(chunk_type, chunk_data)])


def main() -> int:
    payload = png_bytes((960, 1200))
    required = {
        "role": "final-page",
        "requirements": "original-resolution PNG",
        "allowed_media_types": ["image/png"],
        "minimum_dimensions": [960, 960],
    }
    validate_bound_payload(
        payload,
        "image/png",
        {"dimensions": [960, 1200]},
        required,
        "valid-png",
    )
    must_fail(
        lambda: validate_bound_payload(
            payload,
            "image/png",
            {"dimensions": [960, 1199]},
            required,
            "bad-declared-size",
        ),
        "declared dimensions must match decoded dimensions",
    )
    must_fail(
        lambda: validate_bound_payload(
            png_bytes((959, 1200)),
            "image/png",
            {"dimensions": [959, 1200]},
            required,
            "low-resolution-preview",
        ),
        "raster must meet minimum dimensions",
    )
    must_fail(
        lambda: validate_bound_payload(
            payload[:-12],
            "image/png",
            {"dimensions": [960, 1200]},
            required,
            "corrupt-png",
        ),
        "corrupt PNG must become a structured validation failure",
    )
    must_fail(
        lambda: validate_bound_payload(
            apng_bytes((960, 1200)),
            "image/png",
            {"dimensions": [960, 1200]},
            required,
            "animated-png",
        ),
        "raster fixtures must be static single-frame PNGs",
    )
    single_frame_apng_control = with_png_control_chunks(
        payload,
        [
            (b"acTL", struct.pack(">II", 1, 0)),
            (
                b"fcTL",
                struct.pack(">IIIIIHHBB", 0, 960, 1200, 0, 0, 1, 10, 0, 0),
            ),
        ],
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with Image.open(io.BytesIO(single_frame_apng_control)) as image:
            assert image.n_frames == 1 and not image.is_animated
    must_fail(
        lambda: validate_bound_payload(
            single_frame_apng_control,
            "image/png",
            {"dimensions": [960, 1200]},
            required,
            "single-frame-acTL-png",
        ),
        "acTL must be rejected even when Pillow reports one static frame",
    )
    for chunk_type, chunk_data in (
        (b"fcTL", bytes(26)),
        (b"fdAT", bytes(4)),
    ):
        must_fail(
            lambda chunk_type=chunk_type, chunk_data=chunk_data: validate_bound_payload(
                with_png_control_chunk(payload, chunk_type, chunk_data),
                "image/png",
                {"dimensions": [960, 1200]},
                required,
                f"png-with-{chunk_type.decode('ascii')}",
            ),
            f"{chunk_type.decode('ascii')} APNG control chunk must be rejected",
        )
    validate_bound_payload(
        b"speaker: lead\ntext: exact\n",
        "application/yaml",
        {},
        {"allowed_media_types": ["application/yaml"]},
        "valid-yaml",
    )
    must_fail(
        lambda: validate_bound_payload(
            b"{not-json}",
            "application/json",
            {},
            {"allowed_media_types": ["application/json"]},
            "invalid-json",
        ),
        "declared structured media must parse",
    )
    validate_resolved_verdict("pass", "resolved-verdict")
    must_fail(
        lambda: validate_resolved_verdict(None, "missing-resolved-verdict"),
        "resolved artifact case cannot omit expected_verdict",
    )

    hidden_oracle = {
        "visibility": "runner-only",
        "expected_verdict_when_resolved": "fail",
        "labels": ["synthetic-contract-defect"],
    }
    validate_hidden_oracle(hidden_oracle, "valid-non-editorial-hidden-oracle")
    missing_hidden_verdict = dict(hidden_oracle)
    del missing_hidden_verdict["expected_verdict_when_resolved"]
    must_fail(
        lambda: validate_hidden_oracle(missing_hidden_verdict, "missing-hidden-verdict"),
        "non-editorial hidden oracle cannot omit expected_verdict_when_resolved",
    )
    misspelled_hidden_verdict = dict(hidden_oracle)
    del misspelled_hidden_verdict["expected_verdict_when_resolved"]
    misspelled_hidden_verdict["expected_verdit_when_resolved"] = "fail"
    must_fail(
        lambda: validate_hidden_oracle(misspelled_hidden_verdict, "misspelled-hidden-verdict"),
        "hidden oracle rejects misspelled expected_verdict_when_resolved",
    )
    invalid_hidden_verdict = dict(hidden_oracle, expected_verdict_when_resolved="fixture-dependent")
    must_fail(
        lambda: validate_hidden_oracle(invalid_hidden_verdict, "invalid-hidden-verdict"),
        "hidden oracle verdict must be concrete",
    )

    root_wrapper = {
        "schema_version": 2,
        "skill": "recurring-character-diary-comic",
        "runner_contract": {},
        "sentinel_oracle": {},
        "editorial_layout_oracle": {},
        "route_oracle": {},
        "contract_oracle": {},
        "risk_oracle": {},
        "cases": [],
    }
    validate_root_wrapper(root_wrapper)
    must_fail(
        lambda: validate_root_wrapper(dict(root_wrapper, extra="typo"), "root-extra-key"),
        "root must reject unknown keys",
    )
    misspelled_contract_oracle = dict(root_wrapper)
    del misspelled_contract_oracle["contract_oracle"]
    misspelled_contract_oracle["contract_orcale"] = {}
    must_fail(
        lambda: validate_root_wrapper(misspelled_contract_oracle, "contract-oracle-typo"),
        "root must reject contract_orcale",
    )

    runner_wrapper = {
        "model_visible": [],
        "oracle_hidden": [],
        "execution_kinds": {},
        "fixture_binding": {},
    }
    validate_runner_contract_wrapper(runner_wrapper, "valid-runner-wrapper")
    misspelled_model_visible = dict(runner_wrapper)
    del misspelled_model_visible["model_visible"]
    misspelled_model_visible["model_visibile"] = []
    must_fail(
        lambda: validate_runner_contract_wrapper(misspelled_model_visible, "model-visible-typo"),
        "runner contract must reject model_visibile",
    )

    contract_oracle_wrapper = {
        "expected_contract_semantics": "partial subset",
        "constraint_tiers": {},
        "critical_relation_fields": [],
    }
    validate_contract_oracle_wrapper(contract_oracle_wrapper, "valid-contract-oracle-wrapper")
    must_fail(
        lambda: validate_contract_oracle_wrapper(
            dict(contract_oracle_wrapper, constraint_tier={}),
            "contract-oracle-extra-key",
        ),
        "contract oracle must reject unknown keys",
    )

    case_wrapper = {
        "id": "synthetic-case",
        "suite": "routing_create",
        "execution_kind": "semantic",
        "expected_route": "trigger/create",
        "expected_risk": "L1",
        "fixture": {"status": "none"},
        "request": "Synthetic request",
        "expected_behavior": ["route"],
        "must_not": ["publish"],
    }
    validate_case_wrapper(case_wrapper, "valid-case-wrapper")
    must_fail(
        lambda: validate_case_wrapper(dict(case_wrapper, suite="typo-suite"), "invalid-suite"),
        "case suite must use the fixed vocabulary",
    )
    must_fail(
        lambda: validate_case_wrapper(dict(case_wrapper, expected_verdit="pass"), "case-field-typo"),
        "case wrapper must reject expected_verdit",
    )

    validate_fixture_wrapper({"status": "none"}, "valid-none-fixture")
    must_fail(
        lambda: validate_fixture_wrapper({"statuz": "none"}, "fixture-status-typo"),
        "fixture wrapper must reject statuz",
    )
    deferred_fixture = {
        "status": "deferred",
        "required_inputs": [],
        "exposed_inputs": [],
        "unresolved_verdict": "not-verified",
    }
    must_fail(
        lambda: validate_fixture_wrapper(
            dict(deferred_fixture, hidden_orcale=hidden_oracle),
            "hidden-wrapper-typo",
        ),
        "fixture wrapper must reject hidden_orcale",
    )

    known_required_input = {
        "role": "character-profile",
        "requirements": "schema-valid character profile",
        "allowed_media_types": ["application/yaml"],
    }
    validate_required_inputs([known_required_input], "valid-required-input")
    must_fail(
        lambda: validate_required_inputs(
            [dict(known_required_input, allowd_media_types=["application/yaml"])],
            "required-input-field-typo",
        ),
        "required input must reject allowd_media_types",
    )
    must_fail(
        lambda: validate_required_inputs(
            [dict(known_required_input, role="final-pgae")],
            "deferred-unknown-role",
        ),
        "deferred required input must reject misspelled roles",
    )
    must_fail(
        lambda: validate_required_inputs(
            [{
                "role": "final-page",
                "requirements": "original-resolution raster",
                "allowed_media_types": ["application/json"],
            }],
            "role-media-mismatch",
        ),
        "known roles must retain their fixed media vocabulary",
    )
    must_fail(
        lambda: validate_resolved_bindings(
            Path("cases.yaml"),
            {"final-pgae": dict(known_required_input, role="final-pgae")},
            [{"role": "final-pgae"}],
            "resolved-unknown-role",
        ),
        "resolved exposed input must reject misspelled roles before resolving a file",
    )

    exposed_input = {
        "role": "character-profile",
        "path": "profile.yaml",
        "sha256": "0" * 64,
        "media_type": "application/yaml",
    }
    validate_exposed_input_wrapper(exposed_input, "valid-exposed-input")
    must_fail(
        lambda: validate_exposed_input_wrapper(
            dict(exposed_input, expected_verdict="pass"),
            "exposed-input-oracle-injection",
        ),
        "exposed input must reject embedded oracle fields",
    )

    zero_sha = "0" * 64
    one_sha = "1" * 64
    record_bindings = {
        "unlettered-page": {"sha256": zero_sha},
        "final-page": {"sha256": one_sha},
    }
    character_profile = {
        "schema_version": 1,
        "character_id": "lead",
        "rights_confirmation": {
            "confirmed": True,
            "basis": "generated-original",
            "allowed_uses": ["evaluation"],
        },
        "identity": {"summary": "Synthetic recurring lead for validator self-test."},
        "identity_references": [{
            "id": "lead-ref",
            "source": "lead.png",
            "rights_basis": "generated-original",
        }],
        "must_keep": ["round glasses"],
        "anatomy": {"body_plan": "adult human biped"},
        "forbidden_drift": ["missing glasses"],
    }
    visual_contract = {
        "contract_version": "comic-v3",
        "task_id": "self-test",
        "artifact_type": "recurring-character-diary-comic",
        "sources": [{"id": "story"}],
        "story": {"spine": "A tiny observable reversal."},
        "entities": [{"id": "lead"}],
        "states": [{
            "id": "lead-p1",
            "panel": "p1",
            "entity": "lead",
            "facts": [{"level": "S0", "source": "story"}],
        }],
        "relations": [],
        "panels": [{"id": "p1", "required_states": ["lead-p1"], "required_relations": []}],
        "global_rules": [{"id": "one-panel", "level": "S0", "source": "story"}],
        "unknowns": [],
        "routing": {"mode": "page-native", "high_risk_focus_panels": []},
    }
    composition_ledger = {
        "schema_version": 1,
        "compositor_version": "self-test",
        "manifest_sha256": "2" * 64,
        "canvas_size": [960, 1200],
        "input_stage": "unlettered-panel",
        "composition_stage": "unlettered-page",
        "output_stage": "lettered-final",
        "panels": [{
            "id": "p1",
            "stage": "unlettered-panel",
            "source_sha256": "3" * 64,
            "reading_order": 1,
        }],
        "artifacts": [
            {"stage": "unlettered-page", "path": "unlettered.png", "sha256": zero_sha},
            {"stage": "lettered-final", "path": "final.png", "sha256": one_sha},
        ],
        "unlettered_sha256": zero_sha,
        "output_sha256": one_sha,
    }
    locked_story_markdown = """# Locked story contract

## Panels

Panel p1 contains the observable setup and panel p2 contains the reversal.

## Locked dialogue

The approved dialogue is recorded exactly with its speaker and panel owner.
"""
    panel_map_markdown = """# Panel map

## Canvas and reading order

The canvas is 960 by 1200. Reading order is p1 then p2.

## Panel frames

Panel p1 and panel p2 each have explicit frame geometry and protected regions.
"""
    validate_role_record(
        "character-profile",
        json.dumps(character_profile).encode("utf-8"),
        "application/json",
        record_bindings,
        "valid-character-profile",
    )
    validate_role_record(
        "visual-task-contract",
        json.dumps(visual_contract).encode("utf-8"),
        "application/json",
        record_bindings,
        "valid-visual-task-contract",
    )
    validate_role_record(
        "composition-ledger",
        json.dumps(composition_ledger).encode("utf-8"),
        "application/json",
        record_bindings,
        "valid-composition-ledger",
    )
    validate_role_record(
        "locked-story-contract",
        locked_story_markdown.encode("utf-8"),
        "text/markdown",
        record_bindings,
        "valid-locked-story-contract",
    )
    validate_role_record(
        "panel-map",
        panel_map_markdown.encode("utf-8"),
        "text/markdown",
        record_bindings,
        "valid-panel-map",
    )
    for role, media_type in (
        ("character-profile", "application/yaml"),
        ("visual-task-contract", "application/yaml"),
        ("composition-ledger", "application/json"),
        ("locked-script", "text/markdown"),
        ("panel-map", "application/json"),
    ):
        must_fail(
            lambda role=role, media_type=media_type: validate_role_record(
                role,
                b"{}\n",
                media_type,
                record_bindings,
                f"empty-{role}",
            ),
            f"empty mapping cannot satisfy the {role} role schema",
        )

    final_binding = {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "dimensions": [960, 1200],
    }
    editorial_record = {
        "gate_version": "editorial-layout-v1",
        "artifact": {
            "role": "lettered-final",
            "path": "page.png",
            "sha256": final_binding["sha256"],
            "dimensions": [960, 1200],
            "inspected_at_original_resolution": True,
            "normal_reading_size_reviewed": True,
        },
        "axes": {
            "contract_fidelity": "pass",
            "editorial_layout": "fail",
            "exposure": "internal-only",
        },
        "checks": [
            {"id": "reading_path", "result": "pass", "evidence": "clear order"},
            {"id": "beat_hierarchy", "result": "fail", "evidence": "anchor is weak"},
            {"id": "panel_shape_rhythm", "result": "fail", "evidence": "uniform cards"},
            {"id": "border_language", "result": "fail", "evidence": "same border"},
            {"id": "inset_integrity", "result": "pass", "evidence": "no inset defect"},
            {"id": "negative_space_intent", "result": "pass", "evidence": "space is intentional"},
            {"id": "final_beat_emphasis", "result": "pass", "evidence": "ending is clear"},
            {"id": "thumbnail_silhouette", "result": "fail", "evidence": "card grid silhouette"},
        ],
        "card_grid": {
            "signals": {
                "uniform_panel_containers": True,
                "axis_aligned_row_stack": True,
                "repeated_rectangular_aspect_family": True,
                "detached_or_accidentally_cropped_inset": False,
                "non_narrative_dead_space": False,
                "weak_anchor_or_final_emphasis": False,
            },
            "signal_count": 3,
            "accidental": True,
        },
        "blocking_defects": [{
            "id": "accidental-card-grid",
            "check_ids": ["beat_hierarchy", "panel_shape_rhythm", "border_language", "thumbnail_silhouette"],
            "evidence": "three card-grid signals",
        }],
        "publication_authority_inferred": False,
    }
    validate_editorial_layout_record(editorial_record, final_binding, "valid-editorial-record")
    bad_count = copy.deepcopy(editorial_record)
    bad_count["card_grid"]["signal_count"] = 2
    must_fail(
        lambda: validate_editorial_layout_record(bad_count, final_binding, "bad-card-grid-count"),
        "card-grid signal count must be derived from booleans",
    )
    bad_exposure = copy.deepcopy(editorial_record)
    bad_exposure["axes"]["exposure"] = "showcase-ready"
    must_fail(
        lambda: validate_editorial_layout_record(bad_exposure, final_binding, "bad-editorial-exposure"),
        "technical pass plus editorial fail must remain internal-only",
    )
    missing_grid_blocker = copy.deepcopy(editorial_record)
    missing_grid_blocker["blocking_defects"][0]["id"] = "generic-layout-fail"
    must_fail(
        lambda: validate_editorial_layout_record(missing_grid_blocker, final_binding, "missing-grid-blocker"),
        "accidental-card-grid needs its named blocker",
    )
    inferred_authority = copy.deepcopy(editorial_record)
    inferred_authority["publication_authority_inferred"] = True
    must_fail(
        lambda: validate_editorial_layout_record(inferred_authority, final_binding, "inferred-publication-authority"),
        "editorial gate cannot infer publication authority",
    )

    with tempfile.TemporaryDirectory(prefix="comic-case-validator-") as temporary:
        root = Path(temporary)
        eval_dir = root / "eval"
        eval_dir.mkdir()
        case_path = eval_dir / "cases.yaml"
        case_path.write_text("schema_version: 2\n", encoding="utf-8")
        fixture = eval_dir / "page.png"
        fixture.write_bytes(payload)
        exposed = [{
            "role": "final-page",
            "path": "page.png",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "media_type": "image/png",
            "dimensions": [960, 1200],
        }]
        validate_resolved_bindings(case_path, {"final-page": required}, exposed, "fixture")

        outside = root / "outside.png"
        outside.write_bytes(payload)
        escaping = [dict(exposed[0], path="../outside.png")]
        must_fail(
            lambda: validate_resolved_bindings(case_path, {"final-page": required}, escaping, "fixture"),
            "binding path cannot escape eval directory",
        )
        wrong_hash = [dict(exposed[0], sha256="0" * 64)]
        must_fail(
            lambda: validate_resolved_bindings(case_path, {"final-page": required}, wrong_hash, "fixture"),
            "binding hash must match frozen bytes",
        )
        wrong_media = [dict(exposed[0], media_type="application/json")]
        must_fail(
            lambda: validate_resolved_bindings(case_path, {"final-page": required}, wrong_media, "fixture"),
            "binding media type must be allowed for its role",
        )
        runner_only_required = dict(required, visibility="runner-only")
        must_fail(
            lambda: validate_resolved_bindings(case_path, {"final-page": runner_only_required}, exposed, "fixture"),
            "runner-only role cannot be exposed as model-visible",
        )
        runner_only_exposed = [dict(exposed[0], visibility="runner-only")]
        validate_resolved_bindings(case_path, {"final-page": runner_only_required}, runner_only_exposed, "fixture")
        jpeg_payload = jpeg_bytes((960, 1200))
        disguised_jpeg = eval_dir / "disguised.png"
        disguised_jpeg.write_bytes(jpeg_payload)
        wrong_format = [dict(
            exposed[0],
            path="disguised.png",
            sha256=hashlib.sha256(jpeg_payload).hexdigest(),
        )]
        must_fail(
            lambda: validate_resolved_bindings(case_path, {"final-page": required}, wrong_format, "fixture"),
            "decoded image format must match image/png declaration",
        )

    print("PASS case-validator self-test: closed wrappers, fixed suite/role/media vocabularies, raw static-PNG chunks, fixture integrity, exact hidden oracles, role-specific records, split editorial axes, and publication boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
