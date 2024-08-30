import os
import pandas as pd

import benchmark as bm


def load(args) -> pd.DataFrame:
    '''
    kwargs:
        models (list[str]): models to include in the plot.
        benchmarks (list[str]): benchmarks to include in the plot, 
                                leave empty to include all benchmarks.
    '''
    
    models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 
              'gpt-4o', 'gpt-4o-mini', 'llama3', 'llama3.1']
    if args.kwargs and 'models' in args.kwargs:
        models = args.kwargs['models']
    
    benchmarks = []
    if args.kwargs and 'benchmarks' in args.kwargs:
        benchmarks = args.kwargs['benchmarks']
    
    # load in files, get newest result for each model if available
    files = {}
    for file in os.scandir(bm.result_dir):
        # extract suite and model name from result file name
        suite, name = file.name[20:25], file.name[26:-4]
        if suite == 'suite' and name in models:
            files[name] = file
    
    if len(files) == 0:
        raise ValueError("No suite resuts found. Run through "
                         "at least one benchmark suite before plotting.")
    
    # load all files into DataFrame
    dfs = []
    for k, v in files.items():
        df = pd.read_csv(v)
        df.loc[:, 'model'] = k
        dfs.append(df)
    results = pd.concat(dfs)
    
    # filter benchmarks
    if len(benchmarks) > 0:
        results = results[results['benchmark'].isin(benchmarks)]
    
    return results
