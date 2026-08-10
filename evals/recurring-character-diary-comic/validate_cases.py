#!/usr/bin/env python3
"""Validate recurring-character-diary-comic behavioral eval schema v2."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from PIL import Image, UnidentifiedImageError


class ValidationError(ValueError):
    pass


ALLOWED_MEDIA_TYPES = {"image/png", "application/yaml", "application/json", "text/markdown"}
CONCRETE_ARTIFACT_VERDICTS = {"pass", "fail", "not-verified"}
MAX_FIXTURE_BYTES = 128 * 1024 * 1024
EDITORIAL_CHECK_IDS = {
    "reading_path",
    "beat_hierarchy",
    "panel_shape_rhythm",
    "border_language",
    "inset_integrity",
    "negative_space_intent",
    "final_beat_emphasis",
    "thumbnail_silhouette",
}
CARD_GRID_SIGNAL_IDS = {
    "uniform_panel_containers",
    "axis_aligned_row_stack",
    "repeated_rectangular_aspect_family",
    "detached_or_accidentally_cropped_inset",
    "non_narrative_dead_space",
    "weak_anchor_or_final_emphasis",
}
EDITORIAL_LAYOUT_VERDICTS = {"pass", "fail", "not-verified"}
EDITORIAL_EXPOSURES = {"showcase-ready", "internal-only"}
ALLOWED_BINDING_VISIBILITIES = {"model-visible", "runner-only"}
KNOWN_FIXTURE_ROLES = {
    "character-profile",
    "composition-ledger",
    "editorial-layout-record",
    "final-page",
    "identity-reference",
    "lead-character-profile",
    "lead-identity-reference",
    "locked-script",
    "locked-story-contract",
    "panel-map",
    "support-character-profile",
    "support-identity-reference",
    "unlettered-page",
    "visual-task-contract",
}
ROLE_MEDIA_TYPES = {
    "character-profile": {"application/json", "application/yaml", "text/markdown"},
    "composition-ledger": {"application/json"},
    "editorial-layout-record": {"application/yaml"},
    "final-page": {"image/png"},
    "identity-reference": {"image/png"},
    "lead-character-profile": {"application/json", "application/yaml", "text/markdown"},
    "lead-identity-reference": {"image/png"},
    "locked-script": {"application/json", "application/yaml", "text/markdown"},
    "locked-story-contract": {"application/json", "application/yaml", "text/markdown"},
    "panel-map": {"application/json", "application/yaml", "text/markdown"},
    "support-character-profile": {"application/json", "application/yaml", "text/markdown"},
    "support-identity-reference": {"image/png"},
    "unlettered-page": {"image/png"},
    "visual-task-contract": {"application/json", "application/yaml"},
}
KNOWN_CASE_SUITES = {
    "contract_tiering",
    "create_contract",
    "editorial_layout_negative",
    "layout_feasibility",
    "negative_artifact_audit",
    "relation_contract",
    "risk_route_override",
    "risk_routing",
    "routing_audit",
    "routing_create",
    "routing_negative",
    "routing_repair",
    "safety_boundary",
    "split_axis_artifact_audit",
}
ROOT_FIELDS = {
    "schema_version",
    "skill",
    "runner_contract",
    "sentinel_oracle",
    "editorial_layout_oracle",
    "route_oracle",
    "contract_oracle",
    "risk_oracle",
    "cases",
}
RUNNER_CONTRACT_FIELDS = {
    "model_visible",
    "oracle_hidden",
    "execution_kinds",
    "fixture_binding",
}
CONTRACT_ORACLE_FIELDS = {
    "expected_contract_semantics",
    "constraint_tiers",
    "critical_relation_fields",
}
CASE_REQUIRED_FIELDS = {
    "id",
    "suite",
    "execution_kind",
    "expected_route",
    "expected_risk",
    "fixture",
    "request",
    "expected_behavior",
    "must_not",
}
CASE_ALLOWED_FIELDS = CASE_REQUIRED_FIELDS | {
    "capability_binding",
    "expected_contract",
    "expected_editorial_failure_codes",
    "expected_editorial_layout_verdict",
    "expected_exposure",
    "expected_generation_route",
    "expected_raw_score",
    "expected_risk_override",
    "expected_verdict",
}
FIXTURE_BASE_FIELDS = {"status"}
FIXTURE_ARTIFACT_FIELDS = {
    "status",
    "required_inputs",
    "exposed_inputs",
    "hidden_oracle",
    "unresolved_verdict",
}
REQUIRED_INPUT_REQUIRED_FIELDS = {"role", "requirements", "allowed_media_types"}
REQUIRED_INPUT_ALLOWED_FIELDS = REQUIRED_INPUT_REQUIRED_FIELDS | {"minimum_dimensions", "visibility"}
EXPOSED_INPUT_REQUIRED_FIELDS = {"role", "path", "sha256", "media_type"}
EXPOSED_INPUT_ALLOWED_FIELDS = EXPOSED_INPUT_REQUIRED_FIELDS | {"dimensions", "visibility"}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
APNG_CONTROL_CHUNKS = {b"acTL", b"fcTL", b"fdAT"}
CHARACTER_PROFILE_ROLES = {
    "character-profile",
    "lead-character-profile",
    "support-character-profile",
}
STORY_RECORD_ROLES = {"locked-script", "locked-story-contract"}
PANEL_RECORD_ROLES = {"panel-map"}
ROLE_VALIDATED_RECORDS = (
    CHARACTER_PROFILE_ROLES
    | STORY_RECORD_ROLES
    | PANEL_RECORD_ROLES
    | {"visual-task-contract", "composition-ledger"}
)
HIDDEN_ORACLE_FIELDS = {
    "visibility",
    "expected_verdict_when_resolved",
    "expected_editorial_layout_verdict_when_resolved",
    "expected_exposure_when_resolved",
    "expected_editorial_failure_codes_when_resolved",
    "labels",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def mapping(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be a mapping")
    return value


def sequence(value: Any, label: str) -> list[Any]:
    require(isinstance(value, list), f"{label} must be a list")
    return value


def nonempty_string(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be a non-empty string")
    return value


def unique_ids(items: list[Any], label: str) -> set[str]:
    ids = [nonempty_string(mapping(item, f"{label}[]").get("id"), f"{label}[].id") for item in items]
    require(len(ids) == len(set(ids)), f"{label} ids must be unique")
    return set(ids)


def fixture_roles(items: list[Any], label: str) -> set[str]:
    roles = [
        nonempty_string(mapping(item, f"{label}[]").get("role"), f"{label}[].role")
        for item in items
    ]
    require(len(roles) == len(set(roles)), f"{label} roles must be unique")
    return set(roles)


def positive_pair(value: Any, label: str) -> tuple[int, int]:
    items = sequence(value, label)
    require(len(items) == 2, f"{label} must contain exactly two integers")
    require(
        all(isinstance(item, int) and not isinstance(item, bool) and item > 0 for item in items),
        f"{label} must contain positive integers",
    )
    return items[0], items[1]


def validate_closed_keys(
    value: dict[str, Any],
    required: set[str],
    allowed: set[str],
    label: str,
) -> None:
    missing = required - set(value)
    unexpected = set(value) - allowed
    require(not missing, f"{label} missing keys: {sorted(missing)}")
    require(not unexpected, f"{label} has unexpected keys: {sorted(unexpected)}")


def validate_case_wrapper(value: dict[str, Any], label: str) -> None:
    validate_closed_keys(value, CASE_REQUIRED_FIELDS, CASE_ALLOWED_FIELDS, label)
    require(value.get("suite") in KNOWN_CASE_SUITES, f"{label}.suite is invalid")


def validate_root_wrapper(value: dict[str, Any], label: str = "root") -> None:
    validate_closed_keys(value, ROOT_FIELDS, ROOT_FIELDS, label)


def validate_runner_contract_wrapper(value: dict[str, Any], label: str) -> None:
    validate_closed_keys(value, RUNNER_CONTRACT_FIELDS, RUNNER_CONTRACT_FIELDS, label)


def validate_contract_oracle_wrapper(value: dict[str, Any], label: str) -> None:
    validate_closed_keys(value, CONTRACT_ORACLE_FIELDS, CONTRACT_ORACLE_FIELDS, label)


def validate_fixture_wrapper(value: dict[str, Any], label: str) -> None:
    status = value.get("status")
    if status == "none":
        validate_closed_keys(value, FIXTURE_BASE_FIELDS, FIXTURE_BASE_FIELDS, label)
    elif status == "deferred":
        validate_closed_keys(
            value,
            {"status", "required_inputs", "exposed_inputs", "unresolved_verdict"},
            FIXTURE_ARTIFACT_FIELDS,
            label,
        )
    elif status == "resolved":
        validate_closed_keys(
            value,
            {"status", "required_inputs", "exposed_inputs"},
            FIXTURE_ARTIFACT_FIELDS - {"unresolved_verdict"},
            label,
        )
    else:
        validate_closed_keys(value, FIXTURE_BASE_FIELDS, FIXTURE_ARTIFACT_FIELDS, label)


def validate_required_input_wrapper(value: dict[str, Any], label: str) -> None:
    validate_closed_keys(
        value,
        REQUIRED_INPUT_REQUIRED_FIELDS,
        REQUIRED_INPUT_ALLOWED_FIELDS,
        label,
    )


def validate_exposed_input_wrapper(value: dict[str, Any], label: str) -> None:
    validate_closed_keys(
        value,
        EXPOSED_INPUT_REQUIRED_FIELDS,
        EXPOSED_INPUT_ALLOWED_FIELDS,
        label,
    )


def validate_static_png_chunks(payload: bytes, label: str) -> None:
    require(payload.startswith(PNG_SIGNATURE), f"{label} has an invalid PNG signature")
    offset = len(PNG_SIGNATURE)
    first_chunk = True
    saw_iend = False
    while offset < len(payload):
        require(len(payload) - offset >= 12, f"{label} has a truncated PNG chunk")
        chunk_length = int.from_bytes(payload[offset : offset + 4], "big")
        chunk_type = payload[offset + 4 : offset + 8]
        chunk_end = offset + 12 + chunk_length
        require(chunk_end <= len(payload), f"{label} has a truncated PNG chunk payload")
        if first_chunk:
            require(chunk_type == b"IHDR", f"{label} first PNG chunk must be IHDR")
            first_chunk = False
        require(
            chunk_type not in APNG_CONTROL_CHUNKS,
            f"{label} contains forbidden APNG control chunk {chunk_type.decode('ascii', errors='replace')}",
        )
        if chunk_type == b"IEND":
            require(chunk_length == 0, f"{label} IEND chunk must be empty")
            saw_iend = True
            offset = chunk_end
            break
        offset = chunk_end
    require(saw_iend, f"{label} is missing the IEND chunk")
    require(offset == len(payload), f"{label} has trailing bytes after IEND")


def validate_required_inputs(items: list[Any], label: str) -> dict[str, dict[str, Any]]:
    roles = fixture_roles(items, label)
    require(roles <= KNOWN_FIXTURE_ROLES, f"{label} contains unknown roles: {sorted(roles - KNOWN_FIXTURE_ROLES)}")
    specs: dict[str, dict[str, Any]] = {}
    for index, required_value in enumerate(items):
        required = mapping(required_value, f"{label}[{index}]")
        validate_required_input_wrapper(required, f"{label}[{index}]")
        nonempty_string(required.get("requirements"), f"{label}[{index}].requirements")
        media_types = sequence(required.get("allowed_media_types"), f"{label}[{index}].allowed_media_types")
        require(media_types, f"{label}[{index}].allowed_media_types must not be empty")
        for media_index, media_type in enumerate(media_types):
            nonempty_string(media_type, f"{label}[{index}].allowed_media_types[{media_index}]")
        require(
            len(media_types) == len(set(media_types)) and set(media_types) <= ALLOWED_MEDIA_TYPES,
            f"{label}[{index}].allowed_media_types contains duplicates or unsupported values",
        )
        require(
            set(media_types) <= ROLE_MEDIA_TYPES[required["role"]],
            f"{label}[{index}].allowed_media_types is invalid for role {required['role']!r}",
        )
        if "image/png" in media_types:
            positive_pair(required.get("minimum_dimensions"), f"{label}[{index}].minimum_dimensions")
        else:
            require("minimum_dimensions" not in required, f"{label}[{index}] non-raster role cannot set minimum_dimensions")
        visibility = required.get("visibility", "model-visible")
        require(visibility in ALLOWED_BINDING_VISIBILITIES, f"{label}[{index}].visibility is invalid")
        if required["role"] == "editorial-layout-record":
            require(visibility == "runner-only", f"{label}[{index}] editorial-layout-record must be runner-only")
        specs[required["role"]] = required
    require(set(specs) == roles, f"{label} role mapping is inconsistent")
    return specs


def validate_bound_payload(
    payload: bytes,
    media_type: str,
    binding: dict[str, Any],
    required: dict[str, Any],
    label: str,
) -> None:
    if media_type == "image/png":
        validate_static_png_chunks(payload, label)
        try:
            with Image.open(io.BytesIO(payload)) as image:
                require(image.format == "PNG", f"{label} declares image/png but decoded format is {image.format}")
                require(
                    getattr(image, "n_frames", 1) == 1 and not getattr(image, "is_animated", False),
                    f"{label} must be a static single-frame PNG",
                )
                actual_dimensions = image.size
                image.verify()
        except (OSError, SyntaxError, UnidentifiedImageError) as error:
            raise ValidationError(f"{label} is not a readable PNG: {error}") from error
        declared_dimensions = positive_pair(binding.get("dimensions"), f"{label}.dimensions")
        require(declared_dimensions == actual_dimensions, f"{label}.dimensions do not match decoded pixels")
        minimum_dimensions = positive_pair(required.get("minimum_dimensions"), f"{label}.minimum_dimensions")
        require(
            actual_dimensions[0] >= minimum_dimensions[0] and actual_dimensions[1] >= minimum_dimensions[1],
            f"{label} is below minimum original-resolution fixture dimensions {minimum_dimensions}",
        )
        return

    require("dimensions" not in binding, f"{label} non-raster binding cannot declare dimensions")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValidationError(f"{label} is not UTF-8 text") from error
    require(bool(text.strip()), f"{label} must not be empty")
    try:
        if media_type == "application/yaml":
            require(yaml.safe_load(text) is not None, f"{label} YAML must contain a document")
        elif media_type == "application/json":
            require(json.loads(text) is not None, f"{label} JSON must contain a value")
    except (yaml.YAMLError, json.JSONDecodeError) as error:
        raise ValidationError(f"{label} does not parse as {media_type}: {error}") from error


def validate_resolved_verdict(value: Any, label: str) -> None:
    require(value in CONCRETE_ARTIFACT_VERDICTS, f"{label} resolved fixture needs pass, fail, or not-verified")


def validate_sha256(value: Any, label: str) -> str:
    digest = nonempty_string(value, label)
    require(
        len(digest) == 64 and all(character in "0123456789abcdef" for character in digest),
        f"{label} must be 64 lowercase hexadecimal characters",
    )
    return digest


def parse_record_payload(payload: bytes, media_type: str, label: str) -> Any:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValidationError(f"{label} is not UTF-8 text") from error
    if media_type == "text/markdown":
        return text
    try:
        if media_type == "application/yaml":
            return yaml.safe_load(text)
        if media_type == "application/json":
            return json.loads(text)
    except (yaml.YAMLError, json.JSONDecodeError) as error:
        raise ValidationError(f"{label} does not parse as {media_type}: {error}") from error
    raise ValidationError(f"{label} uses unsupported record media type {media_type!r}")


def validate_markdown_record(
    value: Any,
    label: str,
    required_term_groups: tuple[tuple[str, ...], ...],
) -> str:
    text = nonempty_string(value, label)
    require(len(text.strip()) >= 80, f"{label} is too short to be an auditable record")
    require(
        any(line.lstrip().startswith("#") for line in text.splitlines()),
        f"{label} must contain a Markdown heading",
    )
    folded = text.casefold()
    for group in required_term_groups:
        require(
            any(term.casefold() in folded for term in group),
            f"{label} is missing a required record section ({'/'.join(group)})",
        )
    return text


def validate_character_profile_record(value: Any, label: str) -> Any:
    if isinstance(value, str):
        return validate_markdown_record(
            value,
            label,
            (
                ("character", "角色"),
                ("identity", "身份"),
                ("rights", "授权", "权利"),
                ("must keep", "invariant", "固定", "保持"),
            ),
        )

    profile = mapping(value, label)
    required = {
        "schema_version",
        "character_id",
        "rights_confirmation",
        "identity",
        "identity_references",
        "must_keep",
        "anatomy",
        "forbidden_drift",
    }
    require(required <= set(profile), f"{label} missing keys: {sorted(required - set(profile))}")
    require(profile["schema_version"] == 1, f"{label}.schema_version must be 1")
    nonempty_string(profile["character_id"], f"{label}.character_id")
    rights = mapping(profile["rights_confirmation"], f"{label}.rights_confirmation")
    require(rights.get("confirmed") is True, f"{label}.rights_confirmation.confirmed must be true")
    nonempty_string(rights.get("basis"), f"{label}.rights_confirmation.basis")
    require(sequence(rights.get("allowed_uses"), f"{label}.rights_confirmation.allowed_uses"), f"{label} needs allowed uses")
    identity = mapping(profile["identity"], f"{label}.identity")
    nonempty_string(identity.get("summary"), f"{label}.identity.summary")
    references = sequence(profile["identity_references"], f"{label}.identity_references")
    require(references, f"{label}.identity_references must not be empty")
    for index, reference_value in enumerate(references):
        reference = mapping(reference_value, f"{label}.identity_references[{index}]")
        nonempty_string(reference.get("id"), f"{label}.identity_references[{index}].id")
        nonempty_string(reference.get("source"), f"{label}.identity_references[{index}].source")
        nonempty_string(reference.get("rights_basis"), f"{label}.identity_references[{index}].rights_basis")
    must_keep = sequence(profile["must_keep"], f"{label}.must_keep")
    require(must_keep, f"{label}.must_keep must not be empty")
    for index, item in enumerate(must_keep):
        nonempty_string(item, f"{label}.must_keep[{index}]")
    anatomy = mapping(profile["anatomy"], f"{label}.anatomy")
    nonempty_string(anatomy.get("body_plan"), f"{label}.anatomy.body_plan")
    forbidden = sequence(profile["forbidden_drift"], f"{label}.forbidden_drift")
    require(forbidden, f"{label}.forbidden_drift must not be empty")
    for index, item in enumerate(forbidden):
        nonempty_string(item, f"{label}.forbidden_drift[{index}]")
    return profile


def validate_story_record(value: Any, label: str) -> Any:
    if isinstance(value, str):
        return validate_markdown_record(
            value,
            label,
            (
                ("locked", "锁定", "contract", "合同"),
                ("panel", "格", "场景"),
                ("dialogue", "对白", "台词"),
            ),
        )

    record = mapping(value, label)
    require({"panels", "dialogue"} <= set(record), f"{label} needs panels and dialogue")
    require(
        any(key in record for key in ("story", "premise", "spine", "observable_behavior")),
        f"{label} needs a locked story premise",
    )
    panels = sequence(record["panels"], f"{label}.panels")
    require(panels, f"{label}.panels must not be empty")
    unique_ids(panels, f"{label}.panels")
    dialogue = sequence(record["dialogue"], f"{label}.dialogue")
    for index, line_value in enumerate(dialogue):
        line = mapping(line_value, f"{label}.dialogue[{index}]")
        nonempty_string(line.get("panel"), f"{label}.dialogue[{index}].panel")
        nonempty_string(line.get("speaker"), f"{label}.dialogue[{index}].speaker")
        nonempty_string(line.get("exact_text"), f"{label}.dialogue[{index}].exact_text")
    return record


def validate_panel_record(value: Any, label: str) -> Any:
    if isinstance(value, str):
        return validate_markdown_record(
            value,
            label,
            (
                ("panel", "格"),
                ("reading order", "阅读顺序"),
                ("frame", "canvas", "布局", "画布"),
            ),
        )

    record = mapping(value, label)
    panels = sequence(record.get("panels"), f"{label}.panels")
    require(panels, f"{label}.panels must not be empty")
    panel_ids = unique_ids(panels, f"{label}.panels")
    reading_order = sequence(record.get("reading_order"), f"{label}.reading_order")
    require(reading_order and set(reading_order) == panel_ids, f"{label}.reading_order must cover every panel exactly once")
    require(len(reading_order) == len(set(reading_order)), f"{label}.reading_order must be unique")
    require("canvas" in record or "canvas_size" in record, f"{label} needs canvas geometry")
    if "canvas_size" in record:
        positive_pair(record["canvas_size"], f"{label}.canvas_size")
    else:
        canvas = mapping(record["canvas"], f"{label}.canvas")
        positive_pair(canvas.get("size"), f"{label}.canvas.size")
    for index, panel_value in enumerate(panels):
        panel = mapping(panel_value, f"{label}.panels[{index}]")
        frame = sequence(panel.get("frame"), f"{label}.panels[{index}].frame")
        require(
            len(frame) == 4
            and all(isinstance(item, int) and not isinstance(item, bool) for item in frame)
            and frame[2] > frame[0]
            and frame[3] > frame[1],
            f"{label}.panels[{index}].frame must be a positive [x0,y0,x1,y1] box",
        )
    return record


def validate_composition_ledger_record(
    value: Any,
    exposed_by_role: dict[str, dict[str, Any]],
    label: str,
) -> dict[str, Any]:
    ledger = mapping(value, label)
    required = {
        "schema_version",
        "compositor_version",
        "manifest_sha256",
        "canvas_size",
        "input_stage",
        "composition_stage",
        "output_stage",
        "panels",
        "artifacts",
        "unlettered_sha256",
        "output_sha256",
    }
    require(required <= set(ledger), f"{label} missing keys: {sorted(required - set(ledger))}")
    require(ledger["schema_version"] == 1, f"{label}.schema_version must be 1")
    nonempty_string(ledger["compositor_version"], f"{label}.compositor_version")
    validate_sha256(ledger["manifest_sha256"], f"{label}.manifest_sha256")
    positive_pair(ledger["canvas_size"], f"{label}.canvas_size")
    require(ledger["input_stage"] == "unlettered-panel", f"{label}.input_stage must be unlettered-panel")
    require(ledger["composition_stage"] == "unlettered-page", f"{label}.composition_stage must be unlettered-page")
    require(ledger["output_stage"] in {"unlettered-page", "lettered-final"}, f"{label}.output_stage is invalid")
    unlettered_sha = validate_sha256(ledger["unlettered_sha256"], f"{label}.unlettered_sha256")
    output_sha = validate_sha256(ledger["output_sha256"], f"{label}.output_sha256")

    panels = sequence(ledger["panels"], f"{label}.panels")
    require(panels, f"{label}.panels must not be empty")
    unique_ids(panels, f"{label}.panels")
    reading_orders: list[int] = []
    for index, panel_value in enumerate(panels):
        panel = mapping(panel_value, f"{label}.panels[{index}]")
        require(panel.get("stage") == "unlettered-panel", f"{label}.panels[{index}].stage mismatch")
        validate_sha256(panel.get("source_sha256"), f"{label}.panels[{index}].source_sha256")
        order = panel.get("reading_order")
        require(isinstance(order, int) and not isinstance(order, bool) and order > 0, f"{label}.panels[{index}].reading_order is invalid")
        reading_orders.append(order)
    require(len(reading_orders) == len(set(reading_orders)), f"{label}.panels reading_order must be unique")

    artifacts = sequence(ledger["artifacts"], f"{label}.artifacts")
    require(artifacts, f"{label}.artifacts must not be empty")
    artifacts_by_stage: dict[str, dict[str, Any]] = {}
    for index, artifact_value in enumerate(artifacts):
        artifact = mapping(artifact_value, f"{label}.artifacts[{index}]")
        stage = nonempty_string(artifact.get("stage"), f"{label}.artifacts[{index}].stage")
        require(stage in {"unlettered-page", "lettered-final"}, f"{label}.artifacts[{index}].stage is invalid")
        require(stage not in artifacts_by_stage, f"{label}.artifacts stages must be unique")
        nonempty_string(artifact.get("path"), f"{label}.artifacts[{index}].path")
        validate_sha256(artifact.get("sha256"), f"{label}.artifacts[{index}].sha256")
        artifacts_by_stage[stage] = artifact
    require("unlettered-page" in artifacts_by_stage, f"{label} needs an unlettered-page artifact")
    require(ledger["output_stage"] in artifacts_by_stage, f"{label} needs an artifact for output_stage")
    require(artifacts_by_stage["unlettered-page"]["sha256"] == unlettered_sha, f"{label} unlettered artifact hash mismatch")
    require(artifacts_by_stage[ledger["output_stage"]]["sha256"] == output_sha, f"{label} output artifact hash mismatch")
    if "unlettered-page" in exposed_by_role:
        require(unlettered_sha == exposed_by_role["unlettered-page"].get("sha256"), f"{label} must bind the exposed unlettered-page SHA-256")
    if "final-page" in exposed_by_role:
        require(output_sha == exposed_by_role["final-page"].get("sha256"), f"{label} must bind the exposed final-page SHA-256")
    return ledger


def validate_role_record(
    role: str,
    payload: bytes,
    media_type: str,
    exposed_by_role: dict[str, dict[str, Any]],
    label: str,
) -> Any:
    require(role in ROLE_VALIDATED_RECORDS, f"{label} has no role-specific validator")
    value = parse_record_payload(payload, media_type, label)
    if role in CHARACTER_PROFILE_ROLES:
        return validate_character_profile_record(value, label)
    if role in STORY_RECORD_ROLES:
        return validate_story_record(value, label)
    if role in PANEL_RECORD_ROLES:
        return validate_panel_record(value, label)
    if role == "visual-task-contract":
        contract = mapping(value, label)
        validate_contract(contract, label)
        return contract
    if role == "composition-ledger":
        return validate_composition_ledger_record(value, exposed_by_role, label)
    raise AssertionError(f"unreachable role validator: {role}")


def validate_hidden_oracle(value: Any, label: str) -> dict[str, Any]:
    hidden = mapping(value, label)
    unexpected = set(hidden) - HIDDEN_ORACLE_FIELDS
    require(not unexpected, f"{label} has unexpected keys: {sorted(unexpected)}")
    require(hidden.get("visibility") == "runner-only", f"{label}.visibility must be runner-only")
    validate_resolved_verdict(
        hidden.get("expected_verdict_when_resolved"),
        f"{label}.expected_verdict_when_resolved",
    )
    labels = sequence(hidden.get("labels"), f"{label}.labels")
    require(labels, f"{label}.labels must not be empty")
    for index, item in enumerate(labels):
        nonempty_string(item, f"{label}.labels[{index}]")
    require(len(labels) == len(set(labels)), f"{label}.labels must be unique")

    editorial_fields = {
        "expected_editorial_layout_verdict_when_resolved",
        "expected_exposure_when_resolved",
        "expected_editorial_failure_codes_when_resolved",
    }
    if editorial_fields & set(hidden):
        require(
            {
                "expected_editorial_layout_verdict_when_resolved",
                "expected_exposure_when_resolved",
            }
            <= set(hidden),
            f"{label} hidden editorial oracle needs verdict and exposure",
        )
        require(
            hidden["expected_editorial_layout_verdict_when_resolved"] in EDITORIAL_LAYOUT_VERDICTS,
            f"{label}.expected_editorial_layout_verdict_when_resolved is invalid",
        )
        require(
            hidden["expected_exposure_when_resolved"] in EDITORIAL_EXPOSURES,
            f"{label}.expected_exposure_when_resolved is invalid",
        )
        hidden_codes = sequence(
            hidden.get("expected_editorial_failure_codes_when_resolved", []),
            f"{label}.expected_editorial_failure_codes_when_resolved",
        )
        for index, code in enumerate(hidden_codes):
            nonempty_string(code, f"{label}.expected_editorial_failure_codes_when_resolved[{index}]")
        require(len(hidden_codes) == len(set(hidden_codes)), f"{label} hidden editorial failure codes must be unique")
    return hidden


def validate_editorial_layout_record(
    value: Any,
    final_binding: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    record = mapping(value, label)
    require(record.get("gate_version") == "editorial-layout-v1", f"{label}.gate_version mismatch")

    artifact = mapping(record.get("artifact"), f"{label}.artifact")
    require(artifact.get("role") == "lettered-final", f"{label}.artifact.role must be lettered-final")
    nonempty_string(artifact.get("path"), f"{label}.artifact.path")
    artifact_sha = nonempty_string(artifact.get("sha256"), f"{label}.artifact.sha256")
    require(
        len(artifact_sha) == 64 and all(character in "0123456789abcdef" for character in artifact_sha),
        f"{label}.artifact.sha256 must be lowercase hexadecimal",
    )
    artifact_dimensions = positive_pair(artifact.get("dimensions"), f"{label}.artifact.dimensions")
    require(artifact_sha == final_binding.get("sha256"), f"{label} must bind the exposed final-page SHA-256")
    require(artifact_dimensions == tuple(final_binding.get("dimensions", [])), f"{label} dimensions must match final-page")
    inspected_original = artifact.get("inspected_at_original_resolution")
    reviewed_normal = artifact.get("normal_reading_size_reviewed")
    require(isinstance(inspected_original, bool), f"{label}.artifact.inspected_at_original_resolution must be boolean")
    require(isinstance(reviewed_normal, bool), f"{label}.artifact.normal_reading_size_reviewed must be boolean")

    axes = mapping(record.get("axes"), f"{label}.axes")
    require(axes.get("contract_fidelity") in CONCRETE_ARTIFACT_VERDICTS, f"{label}.axes.contract_fidelity is invalid")
    editorial_verdict = axes.get("editorial_layout")
    exposure = axes.get("exposure")
    require(editorial_verdict in EDITORIAL_LAYOUT_VERDICTS, f"{label}.axes.editorial_layout is invalid")
    require(exposure in EDITORIAL_EXPOSURES, f"{label}.axes.exposure is invalid")

    checks = sequence(record.get("checks"), f"{label}.checks")
    check_ids = unique_ids(checks, f"{label}.checks")
    require(check_ids == EDITORIAL_CHECK_IDS, f"{label}.checks must contain the exact editorial check vocabulary")
    check_results: dict[str, str] = {}
    for index, check_value in enumerate(checks):
        check = mapping(check_value, f"{label}.checks[{index}]")
        require(check.get("result") in EDITORIAL_LAYOUT_VERDICTS, f"{label}.checks[{index}].result is invalid")
        nonempty_string(check.get("evidence"), f"{label}.checks[{index}].evidence")
        check_results[check["id"]] = check["result"]

    card_grid = mapping(record.get("card_grid"), f"{label}.card_grid")
    signals = mapping(card_grid.get("signals"), f"{label}.card_grid.signals")
    require(set(signals) == CARD_GRID_SIGNAL_IDS, f"{label}.card_grid.signals vocabulary mismatch")
    require(all(isinstance(value, bool) for value in signals.values()), f"{label}.card_grid.signals values must be boolean")
    observed_count = sum(bool(value) for value in signals.values())
    require(card_grid.get("signal_count") == observed_count, f"{label}.card_grid.signal_count mismatch")
    require(isinstance(card_grid.get("accidental"), bool), f"{label}.card_grid.accidental must be boolean")
    require(card_grid["accidental"] == (observed_count >= 3), f"{label}.card_grid.accidental must follow the three-signal threshold")

    blockers = sequence(record.get("blocking_defects"), f"{label}.blocking_defects")
    blocker_ids = unique_ids(blockers, f"{label}.blocking_defects") if blockers else set()
    for index, blocker_value in enumerate(blockers):
        blocker = mapping(blocker_value, f"{label}.blocking_defects[{index}]")
        linked_checks = sequence(blocker.get("check_ids"), f"{label}.blocking_defects[{index}].check_ids")
        require(linked_checks and set(linked_checks) <= EDITORIAL_CHECK_IDS, f"{label}.blocking_defects[{index}] has invalid check_ids")
        nonempty_string(blocker.get("evidence"), f"{label}.blocking_defects[{index}].evidence")

    if editorial_verdict == "pass":
        require(inspected_original and reviewed_normal, f"{label} pass requires original-resolution and normal-size review")
        require(set(check_results.values()) == {"pass"}, f"{label} pass requires every editorial check to pass")
        require(not blockers and not card_grid["accidental"], f"{label} pass cannot retain blockers or accidental-card-grid")
    elif editorial_verdict == "fail":
        require(inspected_original and reviewed_normal, f"{label} fail requires original-resolution and normal-size review")
        require("fail" in check_results.values(), f"{label} fail requires at least one failed editorial check")
        require(bool(blockers), f"{label} fail requires at least one blocking defect")
    else:
        require("not-verified" in check_results.values(), f"{label} not-verified needs at least one unverified check")

    if card_grid["accidental"]:
        require(editorial_verdict == "fail", f"{label} accidental-card-grid forces editorial fail")
        require("accidental-card-grid" in blocker_ids, f"{label} accidental-card-grid needs a matching blocker")

    expected_exposure = (
        "showcase-ready"
        if axes["contract_fidelity"] == "pass" and editorial_verdict == "pass"
        else "internal-only"
    )
    require(exposure == expected_exposure, f"{label}.axes.exposure does not match the two verdict axes")
    require(record.get("publication_authority_inferred") is False, f"{label} must not infer publication authority")
    return record


def validate_resolved_bindings(
    case_path: Path,
    required_specs: dict[str, dict[str, Any]],
    exposed_inputs: list[Any],
    label: str,
) -> dict[str, Any]:
    exposed_roles = fixture_roles(exposed_inputs, f"{label}.exposed_inputs")
    require(
        exposed_roles <= KNOWN_FIXTURE_ROLES,
        f"{label}.exposed_inputs contains unknown roles: {sorted(exposed_roles - KNOWN_FIXTURE_ROLES)}",
    )
    require(exposed_roles == set(required_specs), f"{label}.exposed_inputs must bind every required role exactly once")
    fixture_root = case_path.parent.resolve()
    exposed_by_role: dict[str, dict[str, Any]] = {}
    payload_by_role: dict[str, bytes] = {}
    for index, exposed_value in enumerate(exposed_inputs):
        exposed = mapping(exposed_value, f"{label}.exposed_inputs[{index}]")
        validate_exposed_input_wrapper(exposed, f"{label}.exposed_inputs[{index}]")
        relative = Path(nonempty_string(exposed.get("path"), f"{label}.exposed_inputs[{index}].path"))
        require(not relative.is_absolute(), f"{label}.exposed_inputs[{index}].path must be relative")
        resolved = (fixture_root / relative).resolve()
        try:
            resolved.relative_to(fixture_root)
        except ValueError as error:
            raise ValidationError(f"{label}.exposed_inputs[{index}].path escapes the eval directory") from error
        require(resolved.is_file(), f"{label}.exposed_inputs[{index}].path is not a readable file")
        media_type = nonempty_string(exposed.get("media_type"), f"{label}.exposed_inputs[{index}].media_type")
        required = required_specs[exposed["role"]]
        require(
            media_type in ROLE_MEDIA_TYPES[exposed["role"]],
            f"{label}.exposed_inputs[{index}].media_type is invalid for role {exposed['role']!r}",
        )
        require(media_type in required["allowed_media_types"], f"{label}.exposed_inputs[{index}].media_type is not allowed for its role")
        visibility = exposed.get("visibility", "model-visible")
        require(visibility in ALLOWED_BINDING_VISIBILITIES, f"{label}.exposed_inputs[{index}].visibility is invalid")
        require(
            visibility == required.get("visibility", "model-visible"),
            f"{label}.exposed_inputs[{index}].visibility does not match its role",
        )
        expected_sha = nonempty_string(exposed.get("sha256"), f"{label}.exposed_inputs[{index}].sha256")
        require(
            len(expected_sha) == 64 and all(character in "0123456789abcdef" for character in expected_sha),
            f"{label}.exposed_inputs[{index}].sha256 must be lowercase hexadecimal",
        )
        try:
            payload = resolved.read_bytes()
        except OSError as error:
            raise ValidationError(f"{label}.exposed_inputs[{index}].path cannot be read: {error}") from error
        require(len(payload) <= MAX_FIXTURE_BYTES, f"{label}.exposed_inputs[{index}] exceeds fixture size limit")
        require(hashlib.sha256(payload).hexdigest() == expected_sha, f"{label}.exposed_inputs[{index}] hash mismatch")
        validate_bound_payload(payload, media_type, exposed, required, f"{label}.exposed_inputs[{index}]")
        exposed_by_role[exposed["role"]] = exposed
        payload_by_role[exposed["role"]] = payload

    special_records: dict[str, Any] = {}
    for role in sorted(ROLE_VALIDATED_RECORDS & set(exposed_by_role)):
        special_records[role] = validate_role_record(
            role,
            payload_by_role[role],
            exposed_by_role[role]["media_type"],
            exposed_by_role,
            f"{label}.{role}",
        )
    if "editorial-layout-record" in exposed_by_role:
        require("final-page" in exposed_by_role, f"{label} editorial-layout-record requires final-page")
        record_binding = exposed_by_role["editorial-layout-record"]
        require(record_binding["media_type"] == "application/yaml", f"{label} editorial-layout-record must be YAML")
        try:
            record_value = yaml.safe_load(payload_by_role["editorial-layout-record"].decode("utf-8"))
        except (UnicodeError, yaml.YAMLError) as error:
            raise ValidationError(f"{label} cannot parse editorial-layout-record: {error}") from error
        special_records["editorial-layout-record"] = validate_editorial_layout_record(
            record_value,
            exposed_by_role["final-page"],
            f"{label}.editorial-layout-record",
        )
    return special_records


def root_entity(ref: str) -> str:
    return ref.split(".", 1)[0]


def validate_contract(contract: dict[str, Any], label: str) -> None:
    required = {
        "contract_version", "task_id", "artifact_type", "sources", "story", "entities",
        "states", "relations", "panels", "global_rules", "unknowns", "routing",
    }
    require(required <= set(contract), f"{label} missing keys: {sorted(required - set(contract))}")
    require(contract["contract_version"] == "comic-v2", f"{label}.contract_version must be comic-v2")
    require(contract["artifact_type"] == "recurring-character-diary-comic", f"{label}.artifact_type mismatch")

    sources = sequence(contract["sources"], f"{label}.sources")
    source_ids = unique_ids(sources, f"{label}.sources")
    entities = sequence(contract["entities"], f"{label}.entities")
    entity_ids = unique_ids(entities, f"{label}.entities")
    states = sequence(contract["states"], f"{label}.states")
    state_ids = unique_ids(states, f"{label}.states")
    relations = sequence(contract["relations"], f"{label}.relations")
    relation_ids = unique_ids(relations, f"{label}.relations")
    panels = sequence(contract["panels"], f"{label}.panels")
    panel_ids = unique_ids(panels, f"{label}.panels")

    for index, state_value in enumerate(states):
        state = mapping(state_value, f"{label}.states[{index}]")
        require(state.get("panel") in panel_ids, f"{label}.states[{index}].panel is unresolved")
        require(state.get("entity") in entity_ids, f"{label}.states[{index}].entity is unresolved")
        for fact_index, fact_value in enumerate(sequence(state.get("facts"), f"{label}.states[{index}].facts")):
            fact = mapping(fact_value, f"{label}.states[{index}].facts[{fact_index}]")
            require(fact.get("level") in {"S0", "S1", "S2"}, f"{label} state fact has invalid level")
            if fact.get("level") in {"S0", "S1"}:
                require(fact.get("source") in source_ids, f"{label} state fact source is unresolved")

    for index, relation_value in enumerate(relations):
        relation = mapping(relation_value, f"{label}.relations[{index}]")
        relation_required = {"id", "panel", "subject", "predicate", "object", "level", "source", "evidence"}
        require(relation_required <= set(relation), f"{label}.relations[{index}] missing required fields")
        require(relation["panel"] in panel_ids, f"{label}.relations[{index}].panel is unresolved")
        require(root_entity(str(relation["subject"])) in entity_ids, f"{label}.relations[{index}].subject is unresolved")
        require(root_entity(str(relation["object"])) in entity_ids, f"{label}.relations[{index}].object is unresolved")
        require(relation["level"] in {"S0", "S1", "S2"}, f"{label}.relations[{index}].level is invalid")
        if relation["level"] in {"S0", "S1"}:
            require(relation["source"] in source_ids, f"{label}.relations[{index}].source is unresolved")
        evidence = mapping(relation["evidence"], f"{label}.relations[{index}].evidence")
        require(sequence(evidence.get("required"), f"{label}.relations[{index}].evidence.required"), f"{label} relation needs positive evidence")
        require(sequence(evidence.get("forbidden_proxies"), f"{label}.relations[{index}].evidence.forbidden_proxies"), f"{label} relation needs forbidden proxies")
        if "leads_to" in relation:
            require(relation["leads_to"] in state_ids, f"{label}.relations[{index}].leads_to is unresolved")

    for index, panel_value in enumerate(panels):
        panel = mapping(panel_value, f"{label}.panels[{index}]")
        for state_id in sequence(panel.get("required_states", []), f"{label}.panels[{index}].required_states"):
            require(state_id in state_ids, f"{label}.panels[{index}] references unknown state {state_id!r}")
        for relation_id in sequence(panel.get("required_relations", []), f"{label}.panels[{index}].required_relations"):
            require(relation_id in relation_ids, f"{label}.panels[{index}] references unknown relation {relation_id!r}")

    for index, rule_value in enumerate(sequence(contract["global_rules"], f"{label}.global_rules")):
        rule = mapping(rule_value, f"{label}.global_rules[{index}]")
        require(rule.get("level") in {"S0", "S1", "S2"}, f"{label}.global_rules[{index}].level is invalid")
        if rule.get("level") in {"S0", "S1"}:
            require(rule.get("source") in source_ids, f"{label}.global_rules[{index}].source is unresolved")

    routing = mapping(contract["routing"], f"{label}.routing")
    require(routing.get("mode") in {"whole-page", "panel-by-panel", "key-panel-first"}, f"{label}.routing.mode is invalid")
    for panel_id in sequence(routing.get("proof_panels", []), f"{label}.routing.proof_panels"):
        require(panel_id in panel_ids, f"{label}.routing.proof_panels references unknown panel {panel_id!r}")


def validate_cases(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise ValidationError(f"cannot load {path}: {error}") from error
    root = mapping(data, "root")
    validate_root_wrapper(root)
    require(root.get("schema_version") == 2, "schema_version must be 2")
    require(root.get("skill") == "recurring-character-diary-comic", "skill mismatch")

    runner = mapping(root.get("runner_contract"), "runner_contract")
    validate_runner_contract_wrapper(runner, "runner_contract")
    execution_kinds = set(mapping(runner.get("execution_kinds"), "runner_contract.execution_kinds"))
    fixture_rules = mapping(runner.get("fixture_binding"), "runner_contract.fixture_binding")
    fixture_statuses = set(sequence(fixture_rules.get("allowed_statuses"), "fixture_binding.allowed_statuses"))
    sentinels = mapping(root.get("sentinel_oracle"), "sentinel_oracle")
    allowed_risks = set(sequence(sentinels.get("risk"), "sentinel_oracle.risk"))
    allowed_verdicts = set(sequence(sentinels.get("verdict"), "sentinel_oracle.verdict"))
    require(allowed_risks == {"L1", "L2", "L3", "not-applicable", "not-classified"}, "sentinel risk vocabulary mismatch")
    require(allowed_verdicts == {"pass", "fail", "not-verified", "fixture-dependent"}, "sentinel verdict vocabulary mismatch")
    route_oracle = mapping(root.get("route_oracle"), "route_oracle")
    allowed_routes = set(sequence(route_oracle.get("allowed_routes"), "route_oracle.allowed_routes"))
    require(allowed_routes == {"trigger/create", "trigger/audit", "trigger/repair", "no_trigger"}, "route vocabulary mismatch")
    editorial_oracle = mapping(root.get("editorial_layout_oracle"), "editorial_layout_oracle")
    allowed_editorial_verdicts = set(sequence(editorial_oracle.get("allowed_verdicts"), "editorial_layout_oracle.allowed_verdicts"))
    allowed_exposures = set(sequence(editorial_oracle.get("allowed_exposures"), "editorial_layout_oracle.allowed_exposures"))
    require(
        allowed_editorial_verdicts == EDITORIAL_LAYOUT_VERDICTS | {"fixture-dependent"},
        "editorial layout verdict vocabulary mismatch",
    )
    require(
        allowed_exposures == EDITORIAL_EXPOSURES | {"not-evaluated"},
        "editorial exposure vocabulary mismatch",
    )
    require(
        set(sequence(editorial_oracle.get("required_check_ids"), "editorial_layout_oracle.required_check_ids")) == EDITORIAL_CHECK_IDS,
        "editorial required check vocabulary mismatch",
    )
    require(
        set(sequence(editorial_oracle.get("card_grid_signal_ids"), "editorial_layout_oracle.card_grid_signal_ids")) == CARD_GRID_SIGNAL_IDS,
        "editorial card-grid signal vocabulary mismatch",
    )
    contract_oracle = mapping(root.get("contract_oracle"), "contract_oracle")
    validate_contract_oracle_wrapper(contract_oracle, "contract_oracle")
    risk_oracle = mapping(root.get("risk_oracle"), "risk_oracle")
    levels = mapping(risk_oracle.get("levels"), "risk_oracle.levels")
    expected_levels = {
        "L1": ("low", "0-2", "whole-page"),
        "L2": ("medium", "3-5", "panel-by-panel"),
        "L3": ("high", "6-10", "key-panel-first"),
    }
    require(set(levels) == set(expected_levels), "risk level vocabulary mismatch")
    for level_id, (label_name, score_band, generation_route) in expected_levels.items():
        level = mapping(levels[level_id], f"risk_oracle.levels.{level_id}")
        require(level.get("label") == label_name, f"risk_oracle.levels.{level_id}.label mismatch")
        require(level.get("numeric_score_band") == score_band, f"risk_oracle.levels.{level_id}.numeric_score_band mismatch")
        require(level.get("generation_route") == generation_route, f"risk_oracle.levels.{level_id}.generation_route mismatch")
        nonempty_string(level.get("description"), f"risk_oracle.levels.{level_id}.description")
    nonempty_string(levels["L3"].get("classification_override"), "risk_oracle.levels.L3.classification_override")
    generation_route_map = mapping(risk_oracle.get("generation_routes"), "risk_oracle.generation_routes")
    generation_routes = set(generation_route_map)
    require(generation_routes == {"whole-page", "panel-by-panel", "key-panel-first"}, "generation route vocabulary mismatch")
    for route_id, route_description in generation_route_map.items():
        nonempty_string(route_description, f"risk_oracle.generation_routes.{route_id}")

    cases = sequence(root.get("cases"), "cases")
    case_ids = unique_ids(cases, "cases")
    deferred = 0
    hidden_positive = 0
    risk_overrides = 0
    split_axis_cases = 0
    accidental_card_grid_negatives = 0
    for index, case_value in enumerate(cases):
        case = mapping(case_value, f"cases[{index}]")
        label = f"cases[{index}]({case.get('id')})"
        validate_case_wrapper(case, label)
        for field in ("suite", "execution_kind", "expected_route", "expected_risk", "request"):
            nonempty_string(case.get(field), f"{label}.{field}")
        require(sequence(case.get("expected_behavior"), f"{label}.expected_behavior"), f"{label} needs expected_behavior")
        require(sequence(case.get("must_not"), f"{label}.must_not"), f"{label} needs must_not")
        require(case["execution_kind"] in execution_kinds, f"{label}.execution_kind is invalid")
        require(case["expected_route"] in allowed_routes, f"{label}.expected_route is invalid")
        require(case["expected_risk"] in allowed_risks, f"{label}.expected_risk is invalid")
        if "expected_verdict" in case:
            require(case["expected_verdict"] in allowed_verdicts, f"{label}.expected_verdict is invalid")
        editorial_fields = {
            "expected_editorial_layout_verdict",
            "expected_exposure",
            "expected_editorial_failure_codes",
        }
        has_editorial_oracle = bool(editorial_fields & set(case))
        if has_editorial_oracle:
            require(
                {"expected_editorial_layout_verdict", "expected_exposure"} <= set(case),
                f"{label} editorial oracle needs verdict and exposure",
            )
            require(
                case["expected_editorial_layout_verdict"] in allowed_editorial_verdicts,
                f"{label}.expected_editorial_layout_verdict is invalid",
            )
            require(case["expected_exposure"] in allowed_exposures, f"{label}.expected_exposure is invalid")
            failure_codes = sequence(case.get("expected_editorial_failure_codes", []), f"{label}.expected_editorial_failure_codes")
            for code_index, code in enumerate(failure_codes):
                nonempty_string(code, f"{label}.expected_editorial_failure_codes[{code_index}]")
            require(len(failure_codes) == len(set(failure_codes)), f"{label}.expected_editorial_failure_codes must be unique")

        fixture = mapping(case.get("fixture"), f"{label}.fixture")
        validate_fixture_wrapper(fixture, f"{label}.fixture")
        status = fixture.get("status")
        require(status in fixture_statuses, f"{label}.fixture.status is invalid")
        if case["execution_kind"] == "artifact-bound":
            require(status in {"resolved", "deferred"}, f"{label} artifact-bound fixture must be resolved or deferred")
            required_inputs = sequence(fixture.get("required_inputs"), f"{label}.fixture.required_inputs")
            require(required_inputs, f"{label} needs fixture inputs")
            required_specs = validate_required_inputs(required_inputs, f"{label}.fixture.required_inputs")
            exposed_inputs = sequence(fixture.get("exposed_inputs"), f"{label}.fixture.exposed_inputs")
            if status == "deferred":
                deferred += 1
                require(not exposed_inputs, f"{label} deferred fixture must not expose partial bindings")
                require(case.get("expected_verdict") == "fixture-dependent", f"{label} deferred fixture must be fixture-dependent")
                require(fixture.get("unresolved_verdict") == "not-verified", f"{label} deferred fixture must resolve unavailable evidence to not-verified")
                if has_editorial_oracle:
                    require(
                        case["expected_editorial_layout_verdict"] == "fixture-dependent",
                        f"{label} deferred editorial fixture must be fixture-dependent",
                    )
                    require(case["expected_exposure"] == "not-evaluated", f"{label} deferred editorial exposure must be not-evaluated")
                    require(not failure_codes, f"{label} deferred editorial fixture cannot retain resolved failure codes")
            else:
                special_records = validate_resolved_bindings(path, required_specs, exposed_inputs, f"{label}.fixture")
                validate_resolved_verdict(case.get("expected_verdict"), f"{label}.expected_verdict")
                if has_editorial_oracle:
                    require(
                        "editorial-layout-record" in special_records,
                        f"{label} resolved editorial oracle requires editorial-layout-record",
                    )
                    record = special_records["editorial-layout-record"]
                    axes = mapping(record.get("axes"), f"{label}.editorial-layout-record.axes")
                    require(axes["contract_fidelity"] == case["expected_verdict"], f"{label} contract-fidelity axis mismatch")
                    require(
                        axes["editorial_layout"] == case["expected_editorial_layout_verdict"],
                        f"{label} editorial-layout axis mismatch",
                    )
                    require(axes["exposure"] == case["expected_exposure"], f"{label} editorial exposure mismatch")
                    record_codes = {
                        mapping(item, f"{label}.editorial-layout-record.blocking_defects[]")["id"]
                        for item in sequence(record.get("blocking_defects"), f"{label}.editorial-layout-record.blocking_defects")
                    }
                    require(record_codes == set(failure_codes), f"{label} editorial failure-code oracle mismatch")
                    if case["expected_verdict"] == "pass" and axes["editorial_layout"] == "fail" and axes["exposure"] == "internal-only":
                        split_axis_cases += 1
                    if "accidental-card-grid" in record_codes:
                        accidental_card_grid_negatives += 1
                else:
                    require(
                        "editorial-layout-record" not in special_records,
                        f"{label} editorial-layout-record requires explicit editorial oracle fields",
                    )
            hidden = fixture.get("hidden_oracle")
            if hidden is not None:
                hidden = validate_hidden_oracle(hidden, f"{label}.fixture.hidden_oracle")
                if status == "resolved":
                    require(
                        hidden["expected_verdict_when_resolved"] == case["expected_verdict"],
                        f"{label} hidden and resolved contract verdicts disagree",
                    )
                if hidden.get("expected_verdict_when_resolved") == "pass":
                    hidden_positive += 1
                hidden_editorial = hidden.get("expected_editorial_layout_verdict_when_resolved")
                if hidden_editorial is not None:
                    hidden_codes = sequence(
                        hidden.get("expected_editorial_failure_codes_when_resolved", []),
                        f"{label}.fixture.hidden_oracle.expected_editorial_failure_codes_when_resolved",
                    )
                    if status == "resolved" and has_editorial_oracle:
                        require(
                            hidden_editorial == case["expected_editorial_layout_verdict"],
                            f"{label} hidden and resolved editorial verdicts disagree",
                        )
                        require(
                            hidden.get("expected_exposure_when_resolved") == case["expected_exposure"],
                            f"{label} hidden and resolved editorial exposures disagree",
                        )
                        require(set(hidden_codes) == set(failure_codes), f"{label} hidden and resolved editorial codes disagree")
                    if status == "deferred":
                        if (
                            hidden.get("expected_verdict_when_resolved") == "pass"
                            and hidden_editorial == "fail"
                            and hidden.get("expected_exposure_when_resolved") == "internal-only"
                        ):
                            split_axis_cases += 1
                        if "accidental-card-grid" in hidden_codes:
                            accidental_card_grid_negatives += 1
        else:
            require(status == "none", f"{label} non-artifact case must use fixture.status none")

        if case["execution_kind"] == "capability-bound":
            capability = mapping(case.get("capability_binding"), f"{label}.capability_binding")
            require(capability.get("status") == "resolved", f"{label} capability binding must be resolved")
            mapping(capability.get("exposed_facts"), f"{label}.capability_binding.exposed_facts")

        risk = case["expected_risk"]
        if risk in levels:
            expected_generation = nonempty_string(case.get("expected_generation_route"), f"{label}.expected_generation_route")
            require(expected_generation == mapping(levels[risk], f"risk_oracle.levels.{risk}")["generation_route"], f"{label} risk/route mismatch")
            require(expected_generation in generation_routes, f"{label} generation route is undefined")
            raw_score = case.get("expected_raw_score")
            override = case.get("expected_risk_override")
            if override is not None:
                risk_overrides += 1
                require(override == "decisive-s0-causal-relation", f"{label}.expected_risk_override is invalid")
                require(risk == "L3" and expected_generation == "key-panel-first", f"{label} risk override must classify as L3 key-panel-first")
                require(
                    isinstance(raw_score, int) and not isinstance(raw_score, bool) and 0 <= raw_score <= 5,
                    f"{label} decisive-S0 override needs expected_raw_score 0..5",
                )
            elif raw_score is not None:
                require(isinstance(raw_score, int) and not isinstance(raw_score, bool), f"{label}.expected_raw_score must be an integer")
                numeric_bands = {"L1": range(0, 3), "L2": range(3, 6), "L3": range(6, 11)}
                require(raw_score in numeric_bands[risk], f"{label}.expected_raw_score is outside its risk band")
        else:
            require("expected_generation_route" not in case, f"{label} sentinel risk cannot define a generation route")
            require("expected_raw_score" not in case, f"{label} sentinel risk cannot define expected_raw_score")
            require("expected_risk_override" not in case, f"{label} sentinel risk cannot define expected_risk_override")

        if "expected_contract" in case:
            validate_contract(mapping(case["expected_contract"], f"{label}.expected_contract"), f"{label}.expected_contract")

    require(risk_overrides >= 1, "cases must cover the decisive-S0 lower-score risk override")
    require(split_axis_cases >= 1, "cases must cover contract-fidelity pass plus editorial-layout fail")
    require(accidental_card_grid_negatives >= 1, "cases must cover an accidental-card-grid negative")

    return {
        "schema_version": root["schema_version"],
        "cases": len(cases),
        "unique_ids": len(case_ids),
        "deferred_fixtures": deferred,
        "hidden_positive_oracles": hidden_positive,
        "risk_overrides": risk_overrides,
        "split_axis_cases": split_axis_cases,
        "accidental_card_grid_negatives": accidental_card_grid_negatives,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="cases.yaml")
    args = parser.parse_args()
    try:
        summary = validate_cases(Path(args.path).resolve())
    except ValidationError as error:
        print(f"case_validation=failed: {error}", file=sys.stderr)
        return 1
    print("case_validation=ok " + " ".join(f"{key}={value}" for key, value in summary.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
