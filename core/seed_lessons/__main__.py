"""``python -m core.seed_lessons`` — validate the lesson data (no Django needed)."""
from core.seed_lessons import expected_keys, load, validate

data = load()
issues = validate(data)
missing = [k for k in expected_keys() if k not in data]
for issue in issues:
    print('PROBLEM', issue)
print(f'{len(data)} offerings, {len(issues)} problem(s), {len(missing)} missing')
if missing:
    print('missing:', missing)
