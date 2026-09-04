import copy
import json
import unittest
from pathlib import Path
from validate_cases import validate_data, unique_object

BASE = json.loads(Path(__file__).with_name("cases.yaml").read_text(encoding="utf-8"))

class SchemaTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_data(BASE), 8)

    def test_reject_mutations(self):
        mutations = [
            lambda d: d.update(schema_version=True),
            lambda d: d.update(skill="other"),
            lambda d: d.update(extra="unapproved"),
            lambda d: d.update(allowed_routes=["generate"]),
            lambda d: d["cases"][1].update(id=d["cases"][0]["id"]),
            lambda d: d["cases"][0].update(request=" "),
            lambda d: d["cases"][0].update(expected_behavior=[]),
            lambda d: d["cases"][0].update(must_not=[1]),
            lambda d: d["cases"][0].update(route="other"),
            lambda d: d["cases"][0].update(extra=True),
            lambda d: d.update(cases=d["cases"][:3]),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                data = copy.deepcopy(BASE)
                mutate(data)
                with self.assertRaises(ValueError):
                    validate_data(data)

    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}', object_pairs_hook=unique_object)

if __name__ == "__main__":
    unittest.main()
