import os
import json

import libem.prepare.datasets as datasets

dataset_names = ['beer', 'fodors-zagats', 'itunes-amazon', 'walmart-amazon', 
                 'dblp-scholar', 'dblp-acm', 'abt-buy', 'amazon-google']

def open_json(path):
    with open(path, "r", encoding='ISO-8859-1') as f:
        data = json.load(f)
    return data

def add_quotes_to_keys(dataset_name, s):
    s = s.replace('\\', '').replace('""', 'null')
    if dataset_name == 'itunes-amazon':
        return s.replace('Song_Name:', '"Song_Name":')\
                .replace('Artist_Name:', '"Artist_Name":')\
                .replace('Album_Name:', '"Album_Name":')\
                .replace('Genre:', '"Genre":').replace('Price:', '"Price":')\
                .replace('CopyRight:', '"CopyRight":').replace('Time:', '"Time":')\
                .replace('Released:', '"Released":')
    elif dataset_name == 'beer':
        return s.replace('Beer_Name:', '"Beer_Name":')\
                .replace('Brew_Factory_Name:', '"Brew_Factory_Name":')\
                .replace('Style:', '"Style":')\
                .replace('ABV:', '"ABV":')
    elif dataset_name == 'fodors-zagats':
        return s.replace('name:', '"name":')\
                .replace('addr:', '"addr":')\
                .replace('city:', '"city":')\
                .replace('type:', '"type":')\
                .replace('class:', '"class":')\
                .replace('phone:', '"phone":')
    elif dataset_name == 'walmart-amazon':
        return s.replace('title:', '"title":')\
                .replace('category:', '"category":')\
                .replace('brand:', '"brand":')\
                .replace('modelno:', '"modelno":')\
                .replace('price:', '"price":')
    elif dataset_name == 'dblp-scholar' or dataset_name == 'dblp-acm':
        return s.replace('title:', '"title":')\
                .replace('authors:', '"authors":')\
                .replace('venue:', '"venue":')\
                .replace('year:', '"year":')
    elif dataset_name == 'abt-buy':
        return s.replace('name:', '"name":')\
                .replace('description:', '"description":')\
                .replace('price:', '"price":')
    elif dataset_name == 'amazon-google':
        return s.replace('title:', '"title":')\
                .replace('manufacturer:', '"manufacturer":')\
                .replace('price:', '"price":')\

for name in dataset_names:
    path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, name)
    path = os.path.join(path, 'v0')
    original_path = os.path.join(path, 'original')
    files = ['test', 'train', 'valid']
    
    for file in files:
        with open(os.path.join(path, file + '.ndjson'), 'w') as out:
            for item in open_json(os.path.join(original_path, file + '.json')):
                left = json.loads('{' + add_quotes_to_keys(name, item[0]) + '}')
                right = json.loads('{' + add_quotes_to_keys(name, item[1]) + '}')
                parsed_data = {}

                for key, value in left.items():
                    new_key = key.lower() + '_left'
                    parsed_data[new_key] = value
                for key, value in right.items():
                    new_key = key.lower() + '_right'
                    parsed_data[new_key] = value
                parsed_data['label'] = int(item[2])
                out.write(json.dumps(parsed_data) + '\n')
    