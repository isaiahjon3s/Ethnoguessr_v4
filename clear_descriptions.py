import json

with open('phenotype_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for entry in data:
    entry['description'] = ''

with open('phenotype_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('All descriptions cleared.') 