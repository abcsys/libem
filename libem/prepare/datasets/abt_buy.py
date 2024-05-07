import os
import json

import libem.prepare.datasets as datasets

path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, "abt-buy")
test_file = os.path.join(path, "test.ndjson")
train_file = os.path.join(path, "train.ndjson")
valid_file = os.path.join(path, "valid.ndjson")


# sample data:
# {"id_left":"abt_942","name_left":"sony bravia theater black micro system davis50b","description_left":"sony bravia theater black micro system davis50b 5.1-channel surround sound golf ball-sized speakers compact design s-air digital wireless capability hdmi connectivity bravia sync digital cinema sound ( dcs ) technology s-master digital amplifier portable audio enhancer black finish","price_left":null,"cluster_id_left":813,
# "id_right":"buy_949","name_right":"sony bravia dav-is50 \/ b home theater system","description_right":"dvd player , 5.1 speakers 1 disc ( s ) progressive scan 450w rms dolby digital ex , dolby pro logic , dolby pro logic ii","price_right":null,"cluster_id_right":813,
# "label":1,"pair_id":"abt_942#buy_949"}
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
