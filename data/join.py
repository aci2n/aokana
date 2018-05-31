import json

files = [
    'aokana_entries.json',
    'bokupia_entries.json'
]

result = {}

for file in files:
    with open(file) as stream:
        data = json.load(stream)
        result.update(data)

with open('entries.json', 'w') as stream:
    json.dump(result, stream)