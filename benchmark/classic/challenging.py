import random

import libem
from libem.core.struct import Prompt
from libem.prepare.datasets import challenging

from benchmark.util import run as benchmark_run


def benchmark(args):
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

    if args.kwargs is not None:
        if 'version' in args.kwargs:
            kwargs['version'] = args.kwargs['version']
        if 'keep_null' in args.kwargs:
            kwargs['keep_null'] = args.kwargs['keep_null']
        if 'fields' in args.kwargs:
            kwargs['fields'] = args.kwargs['fields']
        if 'price_diff' in args.kwargs:
            kwargs['price_diff'] = args.kwargs['price_diff']

    # get dataset with kwargs
    dataset = list(challenging.read_test(**kwargs))
    if args.shuffle:
        random.shuffle(dataset)

    benchmark_run(dataset, args)
