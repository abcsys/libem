import os
import json
import string

import libem
from libem.core.struct import Prompt

path = os.path.join(os.path.dirname(__file__), '..', '..', 'libem-results-053024')
abt_buy = os.path.join(path, "abt-buy-gpt-4o-with-schema.json")
amazon_google = os.path.join(path, "amazon-google-gpt-4o-with-schema.json")
beer = os.path.join(path, "beer-gpt-4o-with-schema.json")
dblp_acm = os.path.join(path, "dblp-acm-gpt-4o-with-schema.json")
dblp_scholar = os.path.join(path, "dblp-scholar-gpt-4o-with-schema.json")
fodors_zagats = os.path.join(path, "fodors-zagats-gpt-4o-with-schema.json")
itunes_amazon = os.path.join(path, "itunes-amazon-gpt-4o-with-schema.json")
walmart_amazon = os.path.join(path, "walmart-amazon-gpt-4o-with-schema.json")

def read(file):
    with open(file) as f:
        data = json.load(f)
        fp, fn = [], []
        for example in data['results']:
            if example['pred'] == 'yes' and example['label'] == 0:
                fp.append(example)
            elif example['pred'] == 'no' and example['label'] == 1:
                fn.append(example)
    return fp, fn

def addRules(e1, e2):
    keys = []
    for key in e1.keys():
        if not e1[key] or not e2[key]:
            keys.append(key)
    rules = [f"If {key} is missing for one of the entities, ignore {key}." for key in keys]
    return rules 

if __name__ == "__main__":
    libem.LIBEM_LOG_LEVEL = 0  # debug

    fp, fn = read(itunes_amazon) # choose dataset
    num_fp, num_fn = 0, 0
    num_fp_r, num_fn_r = 0, 0
    
    print('False Positives:')
    for example in fp:
        print(example)
        libem.calibrate({
            "libem.match.parameter.tools": [],  # turn off browse etc.
            "libem.match.prompt.output": "Explain your answer step by step and end with 'yes' or 'no' only."
        })
        pred = libem.match(example['entity_1'], example['entity_2'])
        processed_pred = pred.strip().translate(str.maketrans('', '', string.punctuation)).lower()
        if 'yes' in processed_pred:
            num_fp += 1
            libem.calibrate({
                "libem.match.parameter.tools": [],
                "libem.match.prompt.rule": Prompt.Rule(addRules(example['entity_1'], example['entity_2'])),
                "libem.match.prompt.output": "Explain your answer step by step and end with 'yes' or 'no' only."
            })
            pred = libem.match(example['entity_1'], example['entity_2'])
            processed_pred = pred.strip().translate(str.maketrans('', '', string.punctuation)).lower()
            if 'yes' in processed_pred:
                num_fp_r += 1
            
    print('\nFalse Negatives:')
    for example in fn:
        print(example)
        libem.calibrate({
            "libem.match.parameter.tools": [],  # turn off browse etc.
            "libem.match.prompt.output": "Explain your answer step by step and end with 'yes' or 'no' only."
        })
        pred = libem.match(example['entity_1'], example['entity_2'])
        processed_pred = pred.strip().translate(str.maketrans('', '', string.punctuation)).lower()
        if 'no' in processed_pred:
            num_fn += 1
            libem.calibrate({
                "libem.match.parameter.tools": [],
                "libem.match.prompt.rule": Prompt.Rule(addRules(example['entity_1'], example['entity_2'])),
                "libem.match.prompt.output": "Explain your answer step by step and end with 'yes' or 'no' only."
            })
            pred = libem.match(example['entity_1'], example['entity_2'])
            processed_pred = pred.strip().translate(str.maketrans('', '', string.punctuation)).lower()
            if 'no' in processed_pred:
                num_fn_r += 1

    
    print(f"Number of false positives after chain of thoughts: {num_fp}")
    print(f"Number of false positives after adding rules: {num_fp_r}")
    print(f"Number of false negatives after chain of thoughts: {num_fn}")
    print(f"Number of false negatives after adding rules: {num_fn_r}")
