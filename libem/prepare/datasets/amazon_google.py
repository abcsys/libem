import os
import json

import libem.prepare.datasets as datasets

path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, "amazon-google")
test_file = os.path.join(path, "test.ndjson")
train_file = os.path.join(path, "train.ndjson")
valid_file = os.path.join(path, "valid.ndjson")
description = "The Amazon-Google dataset for entity resolution derives " \
              "from the online retailers Amazon.com and the product search " \
              "service of Google accessible through the Google Base Data API. "

# sample data:
# {"id_left":"amazon_1191","title_left":"sims 2 glamour life stuff pack","manufacturer_left":"aspyr media","price_left":24.99,"cluster_id_left":810,
#  "id_right":"google_567","title_right":"aspyr media inc sims 2 glamour life stuff pack","manufacturer_right":null,"price_right":23.44,"cluster_id_right":810,
#  "label":1,"pair_id":"amazon_1191#google_567"}
def read(file, schema=True, price_diff=False):
    with open(file) as f:
        for line in f:
            data = json.loads(line.strip())
            parsed_data = {'left': {}, 'right': {}, 'label': data.get('label', None)}

            # clean the data
            trim = ["cluster_id_left", "cluster_id_right", "id_left", "id_right"]
            if schema:
                price_l, price_r = 0, 0
                for key, value in data.items():
                    if key in trim:
                        continue
                    if key.endswith('_left'):
                        new_key = key[:-5]  # Remove '_left'
                        parsed_data['left'][new_key] = value
                        
                        if new_key == 'price' and value != "" and value != None:
                            price_l = value
                    elif key.endswith('_right'):
                        new_key = key[:-6]  # Remove '_right'
                        parsed_data['right'][new_key] = value
                        
                        if new_key == 'price' and value != "" and value != None:
                            price_r = value
                
                if price_diff:
                    if price_l == 0 or price_r == 0:
                        parsed_data['right']['price_difference'] = None
                    else:
                        price_diff = int(200 * abs(price_r - price_l) / (price_l + price_r))
                        parsed_data['right']['price_difference'] = str(price_diff) + '%'
                    
                    
            else:
                # 'manufacturer title price'
                left_values, right_values = {}, {}
                for key, value in data.items():
                    if key in trim:
                        continue
                    # Change null values to empty str
                    if value is None:
                        value = ''
                    if key.endswith('_left'):
                        new_key = key[:-5]  # Remove '_left'
                        left_values[new_key] = str(value)
                    elif key.endswith('_right'):
                        new_key = key[:-6]  # Remove '_right'
                        right_values[new_key] = str(value)
                parsed_data['left'] = ' '.join([left_values['manufacturer'], left_values['title'], 
                                                left_values['price']])
                parsed_data['right'] = ' '.join([right_values['manufacturer'], right_values['title'], 
                                                 right_values['price']])

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
