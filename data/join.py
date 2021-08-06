import json

result = {}

for file in ['aokana_entries.json', 'bokupia_entries.json', 'tsumihika_entries.json', "aiyoku_entries.json", "tsukisome_entries.json"]:
    with open(file) as stream:
        result.update(json.load(stream))

with open('entries.json', 'w') as stream:
    json.dump(result, stream)