import random

import libem
from libem.core.struct import Rules, Experiences
from libem.prepare.datasets import itunes_amazon

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
        'version': 0,
        'keep_null': args.schema,
        'fields': ["song_name", "artist_name", "album_name", "genre",
                   "price", "copyright", "time", "released"]
    }

    kwargs.update(args.kwargs or {})

    # get dataset with kwargs
    train_set = itunes_amazon.read_train(**kwargs)
    test_set = itunes_amazon.read_test(**kwargs)
    if args.shuffle:
        test_set = list(test_set)
        random.shuffle(test_set)

    # set domain prompt
    if 'domain_prompt' in kwargs and kwargs['domain_prompt'] is True:
        libem.calibrate({
            "libem.match.prompt.query": "Do the two song descriptions refer to the same real-world song? "
                                        "Answer with 'Yes' if they do and 'No' if they do not.\n"
                                        "Song 1: '{left}'\nSong 2: '{right}'",
            "libem.match.prompt.rules": Rules(),
            "libem.match.prompt.experiences": Experiences(),
            "libem.match.prompt.output": ""
        })
    
    # set pre-trained similarity cutoff for blocking
    if args.block:
        libem.calibrate({
            "libem.block.parameter.similarity": args.similarity or block_similarities['itunes-amazon']
        })
        
    return util.benchmark(train_set, test_set, args)
