import libem
import random


def run(args, dataset, num_pairs=None):
    random.seed(42)

    # construct kwargs dict
    kwargs = {
        'version': 0,
    }
    
    if num_pairs:
        args.num_pairs = num_pairs

    train_set = dataset.read_train(**kwargs)
    test_set = dataset.read_test(**kwargs)
    test_set = list(test_set)
    
    if num_pairs: 
        test_set = test_set[:num_pairs]
    print(f"Number of test pairs: {len(test_set)}")
    random.shuffle(test_set)

    return train_set, test_set, 