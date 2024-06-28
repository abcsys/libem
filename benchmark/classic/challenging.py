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

    # get dataset with kwargs
    if args.train:
        raise NotImplementedError("Training data not available for this dataset.")
    else:
        dataset = list(challenging.read_test(**kwargs))
    if args.shuffle:
        random.shuffle(dataset)

    util.benchmark(dataset, args)
