import libem

def assert_equal(list1, list2):
    ''' Check if two lists of dictionaries with potential nested dictionaries are equal. '''

    def normalize_dict(d):
        ''' Recursively convert a dictionary into a sorted tuple of key-value pairs. '''
        return tuple(sorted((k, normalize_value(v)) for k, v in d.items()))

    def normalize_value(v):
        ''' Normalize a value to handle nested dictionaries or lists. '''
        if isinstance(v, dict):
            return normalize_dict(v)
        elif isinstance(v, list):
            return tuple(sorted(normalize_value(i) for i in v))
        return v

    # Normalize the lists of dictionaries
    normalized_list1 = sorted(normalize_dict(d) for d in list1)
    normalized_list2 = sorted(normalize_dict(d) for d in list2)

    assert normalized_list1 == normalized_list2

dataset_a = [{'i': 1, 'j': 'apple'}, {'i': 2, 'j': 'apple'}, {'i': 10, 'j': 'apple'}, 
             {'i': 1, 'j': 'apple'}, {'i': 8, 'j': 'apple'}, {'i': 5, 'j': 'orange'}, 
             {'i': 5, 'j': 'orange'}, {'i': 8, 'j': 'orange'}, {'i': 0, 'j': 'orange'}, 
             {'i': 1, 'j': 'orange'}, ]

dataset_b = [{'i': 1, 'j': 'aple'}, {'i': 2, 'j': 'apple'}, {'i': 7, 'j': 'apple'}, 
             {'i': 3, 'j': 'apple'}, {'i': 4, 'j': 'apple'}, {'i': 0, 'j': 'orange'}, 
             {'i': 7, 'j': 'orange'}, {'i': 0, 'j': 'orange'}, {'i': 5, 'j': 'orange'}, 
             {'i': 6, 'j': 'orange'}, ]

libem.calibrate({
    "libem.block.parameter.similarity": 0
})

out = libem.block(iter(dataset_a), key='i')
expected  = [{'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'apple'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'orange'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 8, 'j': 'apple'}, 'right': {'i': 8, 'j': 'orange'}},]
assert_equal(out, expected)

out = libem.block(iter(dataset_a), iter(dataset_b), key='i')
expected  = [{'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'aple'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'aple'}}, 
               {'left': {'i': 1, 'j': 'orange'}, 'right': {'i': 1, 'j': 'aple'}}, 
               {'left': {'i': 2, 'j': 'apple'}, 'right': {'i': 2, 'j': 'apple'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}},]
assert_equal(out, expected)

out = libem.block(iter(dataset_a), iter(dataset_b), key=['i', 'j'])
expected  = [{'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 2, 'j': 'apple'}, 'right': {'i': 2, 'j': 'apple'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}},]
assert_equal(out, expected)

libem.calibrate({
    "libem.block.parameter.similarity": 50
})

out = libem.block(dataset_a, dataset_b, key='i')
expected  = [{'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'aple'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'aple'}}, 
               {'left': {'i': 2, 'j': 'apple'}, 'right': {'i': 2, 'j': 'apple'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}},]
assert_equal(out, expected)

libem.calibrate({
    "libem.block.parameter.similarity": 100
})

out = libem.block(dataset_a, dataset_b, key='i')
expected  = [{'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}},  
               {'left': {'i': 2, 'j': 'apple'}, 'right': {'i': 2, 'j': 'apple'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}},]
assert_equal(out, expected)

out = libem.block(dataset_a, dataset_b)
expected  = [{'left': {'i': 2, 'j': 'apple'}, 'right': {'i': 2, 'j': 'apple'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}},]
assert_equal(out, expected)
