"""Check that the routing schema rejects unusable evaluation specifications."""
import copy
import json
from pathlib import Path
from validate_cases import validate_data

original = json.loads(Path(__file__).with_name('cases.yaml').read_text())
assert validate_data(original) == 8
for mutation in ('duplicate_id', 'unknown_route', 'empty_expectation', 'wrong_skill'):
    data = copy.deepcopy(original)
    if mutation == 'duplicate_id':
        data['cases'][1]['id'] = data['cases'][0]['id']
    elif mutation == 'unknown_route':
        data['cases'][0]['route'] = 'publish'
    elif mutation == 'empty_expectation':
        data['cases'][0]['expected_behavior'] = []
    else:
        data['skill'] = 'other-skill'
    try:
        validate_data(data)
    except ValueError:
        continue
    raise AssertionError('invalid case accepted: ' + mutation)
print('eval_schema_self_test=ok cases=4')
