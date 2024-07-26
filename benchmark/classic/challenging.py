import random

from libem.prepare.datasets import challenging

from benchmark import util


def run(args):
    '''
    kwargs:
        version (int): the version of the dataset to use.
        keep_null (bool): if False, replace null values with empty str, else keep as 'None'.
        fields (list[str]): fields (and their order) to include in the output, 
                            empty to include all fields. Do not include _left/_right.
        domain_prompt (bool): if True, modifies the prompt to be domain-specific.
    '''
    random.seed(args.seed)

    # construct kwargs dict
    kwargs = {
        'schema': args.schema,
        'version': 1,
        'keep_null': args.schema,
        'price_diff': False
    }

    kwargs.update(args.kwargs or {})

    if args.block:
        raise NotImplementedError("Blocking is not supported for this dataset.")

    if args.num_shots:
        raise NotImplementedError("In-context learning is not supported for this dataset.")

    # get dataset with kwargs
    test_set = challenging.read_test(**kwargs)
    if args.shuffle:
        test_set = list(test_set)
        random.shuffle(test_set)

    return util.benchmark([], test_set, args)
