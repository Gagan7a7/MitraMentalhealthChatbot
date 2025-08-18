import json
from collections import defaultdict

def load_intents(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('intents', [])

def merge_intents(*intent_lists):
    merged = defaultdict(lambda: {'patterns': set(), 'responses': set()})
    for intents in intent_lists:
        for intent in intents:
            tag = intent['tag']
            merged[tag]['patterns'].update(intent.get('patterns', []))
            merged[tag]['responses'].update(intent.get('responses', []))
    # Convert sets back to lists
    return [
        {
            'tag': tag,
            'patterns': sorted(list(data['patterns'])),
            'responses': sorted(list(data['responses']))
        }
        for tag, data in merged.items()
    ]

def main():
    intents1 = load_intents('intents.json')
    intents2 = load_intents('data/intents1_cleaned.json')
    merged_intents = merge_intents(intents1, intents2)
    with open('intents_master.json', 'w', encoding='utf-8') as f:
        json.dump({'intents': merged_intents}, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
