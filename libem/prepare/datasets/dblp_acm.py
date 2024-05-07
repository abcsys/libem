import os
import json

import libem.prepare.datasets as datasets

path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, "dblp-acm")
test_file = os.path.join(path, "test.ndjson")
train_file = os.path.join(path, "train.ndjson")
valid_file = os.path.join(path, "valid.ndjson")


# sample data:
# {"id_left":"dblp_1835","title_left":"wavelet-based histograms for selectivity estimation","authors_left":"jeffrey scott vitter , yossi matias , min wang","venue_left":"sigmod conference","year_left":1998,"cluster_id_left":2110,
# "id_right":"acm_184","title_right":"wavelet-based histograms for selectivity estimation","authors_right":"yossi matias , jeffrey scott vitter , min wang","venue_right":"international conference on management of data","year_right":1998,"cluster_id_right":2110,
# "label":1,"pair_id":"dblp_1835#acm_184"}
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
