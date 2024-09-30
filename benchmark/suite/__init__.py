from benchmark.suite import (
    block,
    batch,
    llama3,
    openai,
)

suites = {
    'block': block.run,
    'batch': batch.run,
    'gpt-3.5-turbo': openai.run('gpt-3.5-turbo'),
    'gpt-4': openai.run('gpt-4'),
    'gpt-4-turbo': openai.run('gpt-4-turbo'),
    'gpt-4o': openai.run('gpt-4o'),
    'gpt-4o-mini': openai.run('gpt-4o-mini'),
    'o1': openai.run('o1-preview'),
    'o1-mini': openai.run('o1-mini'),
    'llama3': llama3.run,
}

from benchmark.suite.plot import (
    batch_size,
    challenging_ds,
    model_cost_trend,
    model_f1,
    model_throughput
)

suite_plots = {
    'batch-size': batch_size.plot,
    'challenging-ds': challenging_ds.plot,
    'model-cost-trend': model_cost_trend.plot,
    'model-f1': model_f1.plot,
    'model-throughput': model_throughput.plot
}
