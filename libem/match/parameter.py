import libem
from libem.core.struct import Parameter
from libem.tune.learn.icl import (
    similar_shots, random_shots, given_shots
)

# model call configurations
model = libem.parameter.model
temperature = libem.parameter.temperature
tools = Parameter(
    default=[],
    options=["libem.browse", "libem.match", "libem.prepare"],
)

# chain-of-thought and confidence score
cot = Parameter(
    default=False
)
confidence = Parameter(
    default=False
)

# in-context learning
icl_strategy = Parameter(
    default=given_shots,
    options=[random_shots, similar_shots],
)
num_shots = Parameter(
    default=0,
)

# prompt-level batching
batch_size = query_per_prompt = Parameter(
    default=1
)

# execution modes
sync = Parameter(
    default=False,
)
