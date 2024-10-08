import random

import libem
from libem.core.struct import Rules, Experiences
from libem.prepare.datasets import walmart_amazon

from benchmark import util
from benchmark.classic import block_similarities


def run(args):
    '''
    kwargs:
        version (int): the version of the dataset to use, default to 0.
        keep_null (bool): if False, replace null values with empty str, else keep as 'None'.
        price_diff (bool): if True, will include an additional field containing 
                           the price difference between the two entities or
                           'None' if one or both prices are missing.
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
    
    if args.schema:
        kwargs['fields'] = ["title", "category", "brand", "modelno", "price"]
    else:
        kwargs['fields'] = ["brand", "title", "modelno", "price"]

    kwargs.update(args.kwargs or {})

    # get dataset with kwargs
    train_set = walmart_amazon.read_train(**kwargs)
    test_set = walmart_amazon.read_test(**kwargs)
    if args.shuffle:
        test_set = list(test_set)
        random.shuffle(test_set)

    # set domain prompt
    if 'domain_prompt' in kwargs and kwargs['domain_prompt'] is True:
        libem.calibrate({
            "libem.match.prompt.query": "Do the two product descriptions refer to the same real-world product? "
                                        "Answer with 'Yes' if they do and 'No' if they do not.\n"
                                        "Product 1: '{left}'\nProduct 2: '{right}'",
            "libem.match.prompt.rules": Rules(rules=["Color distinguishes entities."]),
            "libem.match.prompt.experiences": Experiences(),
            "libem.match.prompt.output": ""
        })
    
    # set pre-trained similarity cutoff for blocking
    if args.block:
        libem.calibrate({
            "libem.block.parameter.similarity": args.similarity or block_similarities['walmart-amazon']
        })
        
    return util.benchmark(train_set, test_set, args)
