import libem.parameter as libem
from libem.core.struct import Parameter

model = libem.model
temperature = libem.temperature

tools = Parameter(
    default=[],
    options=[],
)

# chain-of-thought and confidence score
cot = Parameter(
    default=False
)
confidence = Parameter(
    default=False
)

# prompt-level batching
batch_size = query_per_prompt = Parameter(
    default=1
)

quiet = Parameter(
    default=True,
)
