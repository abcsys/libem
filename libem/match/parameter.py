import libem
from libem.core.struct import Parameter, Index
from libem.tune.learn.icl import (
    similar_shots, random_shots, given_shots
)

# model call configurations
model = libem.parameter.model
temperature = libem.parameter.temperature
tools = Parameter(
    default=[],
    options={
        "common": [
            "libem.prepare",
            "libem.block",
            "libem.match",
            "libem.browse",
        ]
    },
)

# optional requests per minute limit
rpm = Parameter(
    default=0
)

# enable system prompt
system_prompt = Parameter(
    default=True
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

# input parsing
import json

dict_desc_encoding = Parameter(
    default=Index("str"),
    options={
        "str": str,
        "json": json.dumps,
    },
)

# debugging
guess = Parameter(
    default=False,
    options=[True, False]
)
always = Parameter(
    default=None,
    options=["yes", "no"]
)
