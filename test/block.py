import libem

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

out = list(libem.block(iter(dataset_a), on='i'))
assert out == [{'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'apple'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'orange'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 8, 'j': 'apple'}, 'right': {'i': 8, 'j': 'orange'}},]
out = list(libem.block(iter(dataset_a), iter(dataset_b), on='i'))
assert out == [{'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'aple'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'aple'}}, 
               {'left': {'i': 1, 'j': 'orange'}, 'right': {'i': 1, 'j': 'aple'}}, 
               {'left': {'i': 2, 'j': 'apple'}, 'right': {'i': 2, 'j': 'apple'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}},]

out = list(libem.block(iter(dataset_a), iter(dataset_b), on=['i', 'j']))
assert out == [{'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 2, 'j': 'apple'}, 'right': {'i': 2, 'j': 'apple'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}},]

libem.calibrate({
    "libem.block.parameter.similarity": 70
})

out = list(libem.block(dataset_a, dataset_b, on='i'))
assert out == [{'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'aple'}}, 
               {'left': {'i': 1, 'j': 'apple'}, 'right': {'i': 1, 'j': 'aple'}}, 
               {'left': {'i': 2, 'j': 'apple'}, 'right': {'i': 2, 'j': 'apple'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}},]

libem.calibrate({
    "libem.block.parameter.similarity": 100
})

out = list(libem.block(dataset_a, dataset_b, on='i'))
assert out == [{'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}},  
               {'left': {'i': 2, 'j': 'apple'}, 'right': {'i': 2, 'j': 'apple'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}},]

out = list(libem.block(dataset_a, dataset_b))
assert out == [{'left': {'i': 2, 'j': 'apple'}, 'right': {'i': 2, 'j': 'apple'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 5, 'j': 'orange'}, 'right': {'i': 5, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}}, 
               {'left': {'i': 0, 'j': 'orange'}, 'right': {'i': 0, 'j': 'orange'}},]
