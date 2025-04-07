import libem
from benchmark.util import run_block
from libem.core.model.openai import reset
from libem.cascade.util import run as run_prematch

def run(train_set, test_set, args, model_choice="gpt-4o-mini"):
    reset()

    results, stats = {}, {}

    if model_choice == "block":
        test_set, stats['block'], results['block'] = run_block(test_set, args)

    else:
        libem.calibrate({
            "libem.match.parameter.model": model_choice,
            "libem.match.parameter.confidence": True
        }, verbose=True)
        args.model = model_choice
        
        stats, results = run_prematch(train_set, test_set, args)
    
    return stats, results