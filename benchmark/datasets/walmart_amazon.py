import random
import benchmark
import libem
from libem.core.struct import Prompt
from libem.prepare.datasets import walmart_amazon

random.seed(libem.LIBEM_SEED)

def benchmark_walmart_amazon(args):
    '''
    kwargs:
        version (int): the version of the dataset to use, default to 0.
        keep_null (bool): if False, replace null values with empty str, else keep as 'None'.
        price_diff (bool): if True, will include an additional field containing 
                           the price difference betwen the two entities or 
                           'None' if one or both prices are missing.
        fields (list[str]): fields (and their order) to include in the output, 
                            empty to include all fields. Do not include _left/_right.
        domain_prompt (bool): if True, modifies the prompt to be domain-specific.
    '''
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
    dataset = list(walmart_amazon.read_test(**kwargs))
    if args.shuffle:
        random.shuffle(dataset)
    
    # set domain prompt
    if 'domain_prompt' in kwargs and kwargs['domain_prompt'] is True:
        libem.calibrate({
            "libem.match.prompt.query": "Do the two product descriptions refer to the same real-world product? "
                                        "Answer with 'Yes' if they do and 'No' if they do not.\n"
                                        "Product 1: '{left}'\nProduct 2: '{right}'",
            "libem.match.prompt.rule": Prompt.Rule(rules=["Color distinguishes entities."]),
            "libem.match.prompt.experience": Prompt.Experience(),
            "libem.match.prompt.output": ""
            })

    benchmark.benchmark(dataset, args)
