"""Validate JSON-encoded YAML routing specifications, not image quality."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROUTES = {"generate", "plan", "audit", "no_trigger"}
FIELDS = {"id", "route", "request", "expected_behavior", "must_not"}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def unique_object(pairs):
    data = {}
    for key, value in pairs:
        require(key not in data, "duplicate JSON key")
        data[key] = value
    return data

def string(value):
    return isinstance(value, str) and bool(value.strip())

def validate_data(data):
    require(isinstance(data, dict), "root must be an object")
    require(set(data) == {"schema_version", "skill", "allowed_routes", "cases"}, "root fields mismatch")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "invalid version")
    require(data["skill"] == "single-path-process-diorama", "skill mismatch")
    routes = data["allowed_routes"]
    require(isinstance(routes, list) and all(string(r) for r in routes), "routes must be strings")
    require(len(routes) == len(ROUTES) and set(routes) == ROUTES, "routes mismatch")
    cases = data["cases"]
    require(isinstance(cases, list) and len(cases) >= 8, "at least eight cases required")
    ids, seen = set(), set()
    for case in cases:
        require(isinstance(case, dict) and set(case) == FIELDS, "case fields mismatch")
        require(string(case["id"]) and case["id"] not in ids, "invalid or duplicate id")
        ids.add(case["id"])
        require(string(case["route"]) and case["route"] in ROUTES, "invalid route")
        seen.add(case["route"])
        require(string(case["request"]), "empty request")
        for key in ("expected_behavior", "must_not"):
            require(isinstance(case[key], list) and bool(case[key]) and all(string(v) for v in case[key]), "invalid expectations")
    require(seen == ROUTES, "missing route coverage")
    return len(cases)

def main():
    try:
        require(len(sys.argv) == 2, "provide cases.yaml")
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        count = validate_data(data)
        print(f"eval_schema=ok skill=single-path-process-diorama cases={count}")
        return 0
    except (ValueError, OSError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
