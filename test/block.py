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

    assert normalized_list1 == normalized_list2, list1

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
    "libem.block.parameter.similarity": 60
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

text_only_a = ['apple', 'appl', 'orange', 'apple']
text_only_b = ['orange', 'lemon']
text_only_c = ['aple', 'orang']

out = libem.block(text_only_a)
expected = [{'left': 'apple', 'right': 'apple'}]
assert_equal(out, expected)

out = libem.block(text_only_a, text_only_b, text_only_c)
expected = [{'left': 'orange', 'right': 'orange'}]
assert_equal(out, expected)

libem.calibrate({
    "libem.block.parameter.similarity": 60
})

out = libem.block(text_only_a)
expected = [{'left': 'apple', 'right': 'appl'},
            {'left': 'apple', 'right': 'apple'},
            {'left': 'appl', 'right': 'apple'}]
assert_equal(out, expected)

out = libem.block(text_only_a, text_only_b, text_only_c)
expected = [{'left': 'orange', 'right': 'orange'},
            {'left': 'apple', 'right': 'aple'},
            {'left': 'appl', 'right': 'aple'},
            {'left': 'orange', 'right': 'orang'},
            {'left': 'apple', 'right': 'aple'},
            {'left': 'orange', 'right': 'orang'}]
assert_equal(out, expected)


import os
import cv2
import numpy as np
from libem.struct import MultimodalRecord

current_directory = os.path.dirname(os.path.abspath(__file__))

def get_image(name):
    return cv2.imread(os.path.join(current_directory, f"images/{name}.jpg"))

multimodal = [
        MultimodalRecord(text={"name": "apple", "color": "red"}, 
                             images=get_image("apple")),
        MultimodalRecord(text={"name": "lemon", "color": "yellow"}, 
                             images=[get_image("lemon")]),
        MultimodalRecord(text={"name": "fuji apple"})
    ]

libem.calibrate({
    "libem.block.parameter.similarity": 40
})

out = libem.block(multimodal)
text_fields = [{'left': o['left'].text, 'right': o['right'].text} for o in out]
expected = [{'left': {'name': 'apple', 'color': 'red'},
             'right': {'name': 'fuji apple'}}]
assert_equal(text_fields, expected)
assert np.array_equal(out[0]['left'].images, get_image("apple"))
assert out[0]['right'].images is None

multimodal.append(get_image("orange1"))

out = libem.block(multimodal)
assert len(out) == 4

print("All tests passed.")
