import os
import json

import libem.prepare.datasets as datasets

path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, "itunes-amazon")
test_file = os.path.join(path, "test.ndjson")
train_file = os.path.join(path, "train.ndjson")
valid_file = os.path.join(path, "valid.ndjson")
description = ""

# sample data:
# {"song_name_left": "Elevator ( feat . Timbaland )", "artist_name_left": "Flo Rida", "album_name_left": "Mail On Sunday ( Deluxe Version )", "genre_left": "Hip-Hop/Rap , Music , Dirty South", "price_left": "$ 1.99", "copyright_left": "2008 Atlantic Recording Corporation for the United States and WEA International Inc. for the world outside of the United States", "time_left": "3:55", "released_left": "17-Mar-08",
# "song_name_right": "Money Right ( feat . Rick Ross & Brisco ) [ Explicit ]", "artist_name_right": "Flo Rida", "album_name_right": "Mail On Sunday [ Explicit ]", "genre_right": "Rap & Hip-Hop", "price_right": "$ 1.29", "copyright_right": "2013 Warner Bros. . Records Inc.", "time_right": "3:17", "released_right": "March 17 , 2008",
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
                left_values, right_values = [], []
                for key, value in data.items():
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
