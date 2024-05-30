import os
import json

import libem.prepare.datasets as datasets

path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, "beer")
test_file = os.path.join(path, "test.ndjson")
train_file = os.path.join(path, "train.ndjson")
valid_file = os.path.join(path, "valid.ndjson")
description = ""

# sample data:
# {"beer_name_left": "Bulleit Bourbon Barrel Aged G'Knight", "brew_factory_name_left": "Oskar Blues Grill & Brew", "style_left": "American Amber / Red Ale", "abv_left": "8.70 %",
# "beer_name_right": "Figure Eight Bourbon Barrel Aged Jumbo Love", "brew_factory_name_right": "Figure Eight Brewing", "style_right": "Barley Wine", "abv_right": "",
# "label": 0}
def read(file, schema=True):
    with open(file) as f:
        for line in f:
            data = json.loads(line.strip())
            parsed_data = {'left': {}, 'right': {}, 'label': data.get('label', None)}

            # clean the data
            if schema:
                for key, value in data.items():
                    if key.endswith('_left'):
                        new_key = key[:-5]  # Remove '_left'
                        parsed_data['left'][new_key] = value
                    elif key.endswith('_right'):
                        new_key = key[:-6]  # Remove '_right'
                        parsed_data['right'][new_key] = value
            else:
                left_values, right_values = {}, {}
                for key, value in data.items():
                    # Change null values to empty str
                    if value is None:
                        value = ''
                    if key.endswith('_left'):
                        new_key = key[:-5]  # Remove '_left'
                        left_values[new_key] = str(value)
                    elif key.endswith('_right'):
                        new_key = key[:-6]  # Remove '_right'
                        right_values[new_key] = str(value)
                parsed_data['left'] = ' '.join([left_values['brew_factory_name'], left_values['beer_name'], 
                                                left_values['style'], left_values['abv']])
                parsed_data['right'] = ' '.join([right_values['brew_factory_name'], right_values['beer_name'], 
                                                 right_values['style'], right_values['abv']])

            yield parsed_data


def read_test(schema=True):
    return read(test_file, schema)


def read_train(schema=True):
    return read(train_file, schema)


def read_valid():
    raise NotImplementedError


if __name__ == "__main__":
    import pprint
    pp = pprint.PrettyPrinter(sort_dicts=False)
    pp.pprint(next(read_test()))
    pp.pprint(next(read_test(schema=False)))
