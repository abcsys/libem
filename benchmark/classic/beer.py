import random

import libem
from libem.core.struct import Rules, Experiences
from libem.prepare.datasets import beer

from benchmark import util
from benchmark.classic import block_similarities


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
        'version': 0
    }
    
    if args.schema:
        kwargs['keep_null'] = True
        kwargs['fields'] = ["beer_name", "brew_factory_name", "style", "abv"]
    else:
        kwargs['keep_null'] = False
        kwargs['fields'] = ["brew_factory_name", "beer_name", "style", "abv"]

    kwargs.update(args.kwargs or {})

    # get dataset with kwargs
    train_set = beer.read_train(**kwargs)
    test_set = beer.read_test(**kwargs)
    if args.shuffle:
        test_set = list(test_set)
        random.shuffle(test_set)

    # set domain prompt
    if 'domain_prompt' in kwargs and kwargs['domain_prompt'] is True:
        libem.calibrate({
            "libem.match.prompt.query": "Do the two beer descriptions refer to the same real-world beer? "
                                        "Answer with 'Yes' if they do and 'No' if they do not.\n"
                                        "Beer 1: '{left}'\nBeer 2: '{right}'",
            "libem.match.prompt.rules": Rules(),
            "libem.match.prompt.experiences": Experiences(),
            "libem.match.prompt.output": ""
        })
    
    # set pre-trained similarity cutoff for blocking
    if args.block:
        libem.calibrate({
            "libem.block.parameter.similarity": args.similarity or block_similarities['beer']
        })

    return util.benchmark(train_set, test_set, args)
