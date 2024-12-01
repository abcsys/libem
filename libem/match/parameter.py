import libem
from libem.core.struct import Parameter, Index
from libem.tune.learn.icl import (
    similar_shots, random_shots, given_shots
)

# model call configurations
model = libem.parameter.model
temperature = libem.parameter.temperature
system_role = libem.parameter.system_role

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

output_type = Parameter(
    default=lambda: "structured" if model() in {
            "gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18",
        } 
        else "strict" if model() in {
            "llama3", "llama3.1", "llama3.2-3b", "llama3.2-1b",
            "claude-3-5-sonnet-20240620",
        }
        else "standard"
)

# give a likelihood score instead of "yes" or "no"
likelihood = Parameter(
    default=False
)

# structured (JSON) output
structured = Parameter(
    lambda: True if model() in {
        "gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18",
    }
    else False
)

# optional requests per minute limit
rpm = Parameter(
    default=-1
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
