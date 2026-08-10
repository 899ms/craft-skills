#!/usr/bin/env python3
"""Validate the public logo-semantic-fusion behavioral eval suite."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

import yaml


class ValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def mapping(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be a mapping")
    return value


def sequence(value: Any, label: str) -> list[Any]:
    require(isinstance(value, list), f"{label} must be a list")
    return value


def text(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be non-empty text")
    return value


def exact_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    require(set(value) == allowed, f"{label} keys must equal {sorted(allowed)}")


def text_list(value: Any, label: str) -> list[str]:
    items = sequence(value, label)
    require(bool(items), f"{label} must not be empty")
    result = [text(item, f"{label}[]") for item in items]
    require(len(result) == len(set(result)), f"{label} entries must be unique")
    return result


def validate(path: Path) -> tuple[int, str]:
    payload = path.read_bytes()
    try:
        root = mapping(yaml.safe_load(payload), "root")
    except yaml.YAMLError as exc:
        raise ValidationError(f"cases YAML is invalid: {exc}") from exc

    exact_keys(root, {"schema_version", "suite", "description", "cases"}, "root")
    require(root.get("schema_version") == 1, "schema_version must equal 1")
    require(root.get("suite") == "logo-semantic-fusion", "suite must match the Skill id")
    text(root.get("description"), "description")

    cases = sequence(root.get("cases"), "cases")
    require(bool(cases), "cases must not be empty")
    seen_ids: set[str] = set()
    for index, raw_case in enumerate(cases):
        label = f"cases[{index}]"
        case = mapping(raw_case, label)
        exact_keys(case, {"id", "covers", "prompt", "expected"}, label)
        case_id = text(case.get("id"), f"{label}.id")
        require(case_id not in seen_ids, f"duplicate case id: {case_id}")
        seen_ids.add(case_id)
        text_list(case.get("covers"), f"{label}.covers")
        text(case.get("prompt"), f"{label}.prompt")

        expected = mapping(case.get("expected"), f"{label}.expected")
        exact_keys(
            expected,
            {"skill_use", "mode", "observable_behaviors", "forbidden_behaviors"},
            f"{label}.expected",
        )
        require(isinstance(expected.get("skill_use"), bool), f"{label}.expected.skill_use must be boolean")
        text(expected.get("mode"), f"{label}.expected.mode")
        text_list(expected.get("observable_behaviors"), f"{label}.expected.observable_behaviors")
        text_list(expected.get("forbidden_behaviors"), f"{label}.expected.forbidden_behaviors")

    return len(cases), hashlib.sha256(payload).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_cases.py <cases.yaml>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1]).resolve()
    try:
        count, digest = validate(path)
    except (OSError, UnicodeError, ValidationError) as exc:
        print(f"case_validation=failed: {exc}", file=sys.stderr)
        return 1
    print(f"case_validation=ok schema_version=1 cases={count} unique_ids={count} sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
