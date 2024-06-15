import os
import json
import random
from pathlib import Path
import libem.prepare.datasets as datasets
from libem.prepare.datasets import (abt_buy, amazon_google, beer, dblp_acm, 
                                    dblp_scholar, fodors_zagats, itunes_amazon, 
                                    walmart_amazon, challenging)

random.seed(42)

dataset_list = {
    'abt-buy': abt_buy,
    'amazon-google': amazon_google,
    'beer': beer,
    'dblp-acm': dblp_acm,
    'dblp-scholar': dblp_scholar,
    'fodors-zagats': fodors_zagats,
    'itunes-amazon': itunes_amazon,
    'walmart-amazon': walmart_amazon,
    'challenging': challenging,
}

# get a 100 sample 50-50 distribution of match-no match
for name, dataset in dataset_list.items():
    
    items = dataset.read_test()
    match, no_match = [], []
    
    for i in items:
        if i['label'] == 1:
            match.append(i)
        else:
            no_match.append(i)
        
    if len(match) < 50 or len(no_match) < 50:
        try:
            items = dataset.read_train()
            
            for i in items:
                if i['label'] == 1:
                    match.append(i)
                else:
                    no_match.append(i)
        except:
            pass
    
    if len(match) < 50 or len(no_match) < 50:
        try:
            items = dataset.read_valid()
            
            for i in items:
                if i['label'] == 1:
                    match.append(i)
                else:
                    no_match.append(i)
        except:
            pass
    
    out = random.sample(match, min(len(match), min(len(no_match), 50)))
    out.extend(random.sample(no_match, min(len(match), min(len(no_match), 50))))
    random.shuffle(out)
    
    # create /demo folder
    path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, name)
    folder = os.path.join(path, 'demo')
    Path(folder).mkdir(parents=True, exist_ok=True)
    
    # write README
    file = os.path.join(folder, 'README.md')
    with open(file, 'w') as f:
        f.write("Up to 100 samples with a 1:1 distribution of match vs no match for the purpose of libem arena demo.")
    
    file = os.path.join(folder, 'demo.ndjson')
    with open(file, 'w') as f:
        for o in out:
            f.write(json.dumps(o) + '\n')
