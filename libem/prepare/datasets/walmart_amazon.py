import os
import json

import libem.prepare.datasets as datasets

path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, "walmart-amazon")
test_file = os.path.join(path, "test.ndjson")
train_file = os.path.join(path, "train.ndjson")
valid_file = os.path.join(path, "valid.ndjson")


# sample data:
# {"id_left":"walmart_88","title_left":"balt wheasel easel adjustable melamine dry erase board white","category_left":"stationery & office machinery","brand_left":"balt","modelno_left":"33250","price_left":239.88,"cluster_id_left":463,
# "id_right":"amazon_3269","title_right":"balt inc. wheasel easel adjustable melamine dry erase board 28 3 4 x 59 1 2 white","category_right":"laminating supplies","brand_right":"mayline","modelno_right":null,"price_right":134.45,"cluster_id_right":463,
# "label":1,"pair_id":"walmart_88#amazon_3269"}
def read(file, schema=True):
    with open(file) as f:
        for line in f:
            data = json.loads(line.strip())
            parsed_data = {'left': {}, 'right': {}, 'label': data.get('label', None)}

            # clean the data
            trim = ["cluster_id_left", "cluster_id_right", "id_left", "id_right"]
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
                    # Skip null values
                    if value is None:
                        continue
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
