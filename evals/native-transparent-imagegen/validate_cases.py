#!/usr/bin/env python3
"""Validate the native-transparent-imagegen behavioral eval schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


ALLOWED_ROUTES = {"trigger/generate", "trigger/audit", "no_trigger"}
REQUIRED_CASE_FIELDS = {
    "id",
    "route",
    "request",
    "expected_behavior",
    "must_not",
}


class ValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def nonempty_string(value: object, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be non-empty")
    return value


def nonempty_string_list(value: object, label: str) -> list[str]:
    require(isinstance(value, list) and bool(value), f"{label} must be a non-empty list")
    return [nonempty_string(item, f"{label}[]") for item in value]


def validate(path: Path) -> int:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), "root must be a mapping")
    require(data.get("schema_version") == 1, "schema_version must be 1")
    require(data.get("skill") == "native-transparent-imagegen", "skill name mismatch")
    require(set(data.get("allowed_routes", [])) == ALLOWED_ROUTES, "allowed_routes mismatch")
    cases = data.get("cases")
    require(isinstance(cases, list) and len(cases) >= 6, "at least six cases are required")

    ids: set[str] = set()
    seen_routes: set[str] = set()
    for index, raw_case in enumerate(cases):
        label = f"cases[{index}]"
        require(isinstance(raw_case, dict), f"{label} must be a mapping")
        require(set(raw_case) == REQUIRED_CASE_FIELDS, f"{label} fields mismatch")
        case_id = nonempty_string(raw_case["id"], f"{label}.id")
        require(case_id not in ids, f"duplicate case id: {case_id}")
        ids.add(case_id)
        route = nonempty_string(raw_case["route"], f"{label}.route")
        require(route in ALLOWED_ROUTES, f"{label}.route is invalid")
        seen_routes.add(route)
        nonempty_string(raw_case["request"], f"{label}.request")
        nonempty_string_list(raw_case["expected_behavior"], f"{label}.expected_behavior")
        nonempty_string_list(raw_case["must_not"], f"{label}.must_not")

    require(seen_routes == ALLOWED_ROUTES, "evals must cover every allowed route")
    print(f"eval_schema=ok skill=native-transparent-imagegen cases={len(cases)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return validate(args.cases)
    except (OSError, yaml.YAMLError, ValidationError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
