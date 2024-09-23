from benchmark.suite import (
    block,
    batch,
    gpt_35_turbo,
    gpt_4,
    gpt_4_turbo,
    gpt_4o,
    gpt_4o_mini,
    o1,
    llama3,
)

suites = {
    'block': block.run,
    'batch': batch.run,
    'gpt-3.5-turbo': gpt_35_turbo.run,
    'gpt-4': gpt_4.run,
    'gpt-4-turbo': gpt_4_turbo.run,
    'gpt-4o': gpt_4o.run,
    'gpt-4o-mini': gpt_4o_mini.run,
    'o1': o1.run,
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
