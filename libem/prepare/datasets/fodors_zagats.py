import os
import json

import libem.prepare.datasets as datasets

path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, "fodors-zagats")
test_file = os.path.join(path, "test.ndjson")
train_file = os.path.join(path, "train.ndjson")
valid_file = os.path.join(path, "valid.ndjson")
description = "The Abt-Buy dataset for entity resolution derives from the online retailers Abt.com and Buy.com."

# sample data:
# {"name_left": "citrus", "addr_left": "' 6703 melrose ave. '", "city_left": "` los angeles '", "phone_left": "213/857-0034", "type_left": "californian", "class_left": "6",
# "name_right": "` le chardonnay ( los angeles ) '", "addr_right": "' 8284 melrose ave. '", "city_right": "` los angeles '", "phone_right": "213-655-8880", "type_right": "` french bistro '", "class_right": "12",
# "label": 0}
def read(file, schema=True):
    with open(file) as f:
        for line in f:
            data = json.loads(line.strip())
            parsed_data = {'left': {}, 'right': {}, 'label': data.get('label', None)}

            # clean the data
            trim = []
            if schema:
                for key, value in data.items():
                    if key in trim:
                        continue
                    if key.endswith('_left'):
                        new_key = key[:-5]  # Remove '_left'
                        parsed_data['left'][new_key] = value
                    elif key.endswith('_right'):
                        new_key = key[:-6]  # Remove '_right'
                        parsed_data['right'][new_key] = value
            else:
                left_values, right_values = [], []
                for key, value in data.items():
                    if key in trim:
                        continue
                    # Change null values to empty str
                    if value is None:
                        value = ''
                    if key.endswith('_left'):
                        left_values.append(str(value))
                    elif key.endswith('_right'):
                        right_values.append(str(value))
                parsed_data['left'] = ' '.join(left_values)
                parsed_data['right'] = ' '.join(right_values)

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
