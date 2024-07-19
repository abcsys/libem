import os
from pathlib import Path

_dir = os.path.dirname(os.path.realpath(__file__))
_output_dir = os.path.join(_dir, '_output')
result_dir = os.path.join(_output_dir, 'results')
analysis_dir = os.path.join(_output_dir, 'analysis')
figure_dir = os.path.join(_output_dir, 'figures')
table_dir = os.path.join(_output_dir, 'tables')

Path(result_dir).mkdir(parents=True, exist_ok=True)
Path(analysis_dir).mkdir(parents=True, exist_ok=True)
Path(figure_dir).mkdir(parents=True, exist_ok=True)
Path(table_dir).mkdir(parents=True, exist_ok=True)

from benchmark import classic

classic_benchmarks = {
    'abt-buy': classic.abt_buy.run,
    'amazon-google': classic.amazon_google.run,
    'beer': classic.beer.run,
    'dblp-acm': classic.dblp_acm.run,
    'dblp-scholar': classic.dblp_scholar.run,
    'fodors-zagats': classic.fodors_zagats.run,
    'itunes-amazon': classic.itunes_amazon.run,
    'walmart-amazon': classic.walmart_amazon.run,
}

challenges = {
    'classic.challenging': classic.challenging.run,
}

benchmarks = {
    **classic_benchmarks,
    **challenges,
}
