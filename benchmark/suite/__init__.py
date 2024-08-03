from benchmark.suite import (
    block,
    batch,
    gpt_35_turbo,
    gpt_4,
    gpt_4_turbo,
    gpt_4o,
    gpt_4o_mini,
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
    'llama3': llama3.run,
}