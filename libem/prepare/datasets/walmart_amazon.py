import os
import json

import libem.prepare.datasets as datasets

description = "The Walmart-Amazon dataset derives " \
              "from the online retailers Walmart.com and Amazon.com."


# sample data:
# {"id_left":"walmart_88","title_left":"balt wheasel easel adjustable melamine dry erase board white","category_left":"stationery & office machinery","brand_left":"balt","modelno_left":"33250","price_left":239.88,"cluster_id_left":463,
# "id_right":"amazon_3269","title_right":"balt inc. wheasel easel adjustable melamine dry erase board 28 3 4 x 59 1 2 white","category_right":"laminating supplies","brand_right":"mayline","modelno_right":null,"price_right":134.45,"cluster_id_right":463,
# "label":1,"pair_id":"walmart_88#amazon_3269"}
def read(file, schema=True, **kwargs):
    keep_null = 'keep_null' in kwargs and kwargs['keep_null']
    fields = kwargs['fields'] if 'fields' in kwargs else []
    price_diff = kwargs['price_diff'] if 'price_diff' in kwargs else False
    
    with open(file) as f:
        for line in f:
            data = json.loads(line.strip())
            parsed_data = {'left': None, 'right': None, 'label': data.get('label', None)}
            left_values, right_values = {}, {}

            # clean the data
            if schema:
                price_l, price_r = 0, 0
                for key, value in data.items():
                    # Change null values to empty str
                    if not keep_null and value is None:
                        value = ''
                    if key.endswith('_left'):
                        new_key = key[:-5]  # Remove '_left'
                        if len(fields) == 0 or new_key in fields:
                            left_values[new_key] = value
                        
                        if new_key == 'price' and value != "" and value != None:
                            price_l = value
                    elif key.endswith('_right'):
                        new_key = key[:-6]  # Remove '_right'
                        if len(fields) == 0 or new_key in fields:
                            right_values[new_key] = value
                        
                        if new_key == 'price' and value != "" and value != None:
                            price_r = value
                
                if len(fields) > 0:
                    parsed_data['left'] = {field: left_values[field] for field in fields}
                    parsed_data['right'] = {field: right_values[field] for field in fields}
                else:
                    parsed_data['left'] = left_values
                    parsed_data['right'] = right_values
                            
                if price_diff:
                    if price_l == 0 or price_r == 0:
                        parsed_data['right']['price_difference'] = None if keep_null else ''
                    else:
                        difference = int(200 * abs(price_r - price_l) / (price_l + price_r))
                        parsed_data['right']['price_difference'] = str(difference) + '%'
                        
            else:
                for key, value in data.items():
                    # Change null values to empty str
                    if not keep_null and value is None:
                        value = ''
                    if key.endswith('_left'):
                        new_key = key[:-5]  # Remove '_left'
                        if len(fields) == 0 or new_key in fields:
                            left_values[new_key] = str(value)
                    elif key.endswith('_right'):
                        new_key = key[:-6]  # Remove '_right'
                        if len(fields) == 0 or new_key in fields:
                            right_values[new_key] = str(value)
                            
                if len(fields) > 0:
                    parsed_data['left'] = ' '.join([left_values[field] for field in fields])
                    parsed_data['right'] = ' '.join([right_values[field] for field in fields])
                else:
                    parsed_data['left'] = ' '.join(left_values.values())
                    parsed_data['right'] = ' '.join(right_values.values())

            yield parsed_data


def read_test(schema=True, **kwargs):
    '''
    Yields processed records from the dataset one at a time.
    args:
        schema (bool): whether to include the schema or not.
    kwargs:
        version (int): the version of the dataset to use, default to 0.
        keep_null (bool): if False, replace null values with empty str, else keep as 'None'.
        price_diff (bool): if True, will include an additional field containing 
                           the price difference betwen the two entities or 
                           'None' if one or both prices are missing.
        fields (list[str]): fields (and their order) to include in the output, 
                            empty to include all fields. Do not include _left/_right.
    '''
    version = int(kwargs['version']) if 'version' in kwargs else 0
    path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, "walmart-amazon")
    test_file = os.path.join(os.path.join(path, f'v{version}'), 'test.ndjson')
    
    return read(test_file, schema, **kwargs)


def read_train(schema=True, **kwargs):
    '''
    Yields processed records from the dataset one at a time.
    args:
        schema (bool): whether to include the schema or not.
    kwargs:
        version (int): the version of the dataset to use, default to 0.
        keep_null (bool): if False, replace null values with empty str, else keep as 'None'.
        price_diff (bool): if True, will include an additional field containing 
                           the price difference betwen the two entities or 
                           'None' if one or both prices are missing.
        fields (list[str]): fields (and their order) to include in the output, 
                            empty to include all fields. Do not include _left/_right.
    '''
    version = int(kwargs['version']) if 'version' in kwargs else 0
    path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, "walmart-amazon")
    train_file = os.path.join(os.path.join(path, f'v{version}'), 'train.ndjson')
    
    return read(train_file, schema, **kwargs)


def read_valid():
    raise NotImplementedError


if __name__ == "__main__":
    import pprint

    pp = pprint.PrettyPrinter(sort_dicts=False)
    pp.pprint(next(read_test()))
    pp.pprint(next(read_test(schema=False)))
