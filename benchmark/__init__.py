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

from benchmark.classic import classic_benchmarks
from benchmark.suite import benchmark_suites

benchmarks = {
    **classic_benchmarks,
}
