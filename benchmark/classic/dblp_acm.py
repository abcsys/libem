import random
import libem
from libem.core.struct import Prompt
from libem.prepare.datasets import dblp_acm

from benchmark.util import run as benchmark_run

random.seed(libem.LIBEM_SEED)


def benchmark(args):
    '''
    kwargs:
        version (int): the version of the dataset to use.
        keep_null (bool): if False, replace null values with empty str, else keep as 'None'.
        fields (list[str]): fields (and their order) to include in the output, 
                            empty to include all fields. Do not include _left/_right.
        domain_prompt (bool): if True, modifies the prompt to be domain-specific.
    '''
    # construct kwargs dict
    kwargs = {
        'schema': args.schema,
        'version': 1
    }
    if args.schema:
        kwargs['keep_null'] = True
        kwargs['fields'] = ["title", "authors", "venue", "year"]
    else:
        kwargs['keep_null'] = False
        kwargs['fields'] = ["authors", "title", "venue", "year"]

    if args.kwargs is not None:
        if 'version' in args.kwargs:
            kwargs['version'] = args.kwargs['version']
        if 'keep_null' in args.kwargs:
            kwargs['keep_null'] = args.kwargs['keep_null']
        if 'fields' in args.kwargs:
            kwargs['fields'] = args.kwargs['fields']

    # get dataset with kwargs
    dataset = list(dblp_acm.read_test(**kwargs))
    if args.shuffle:
        random.shuffle(dataset)

    # set domain prompt
    if 'domain_prompt' in kwargs and kwargs['domain_prompt'] is True:
        libem.calibrate({
            "libem.match.prompt.query": "Do the two publications refer to the same real-world publication? "
                                        "Answer with 'Yes' if they do and 'No' if they do not.\n"
                                        "Publication 1: '{left}'\nPublication 2: '{right}'",
            "libem.match.prompt.rule": Prompt.Rule(),
            "libem.match.prompt.experience": Prompt.Experience(),
            "libem.match.prompt.output": ""
        })

    benchmark_run(dataset, args)
