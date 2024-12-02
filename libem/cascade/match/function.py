import libem
import openai
import time
from libem.core.model.openai import reset
from libem.cascade.util import run as run_match


def run(train_set, test_set, args, model_choice="gpt-4o"):
    reset()
    
    results, stats = {}, {}

    libem.calibrate({
        "libem.match.parameter.model": model_choice,
        "libem.match.parameter.confidence": True
    }, verbose=True)
    args.model = model_choice
    
    stats, results = run_match(train_set, test_set, args)

    print("args", args)
    print("run matching using model", args.model)
    
    return stats, results