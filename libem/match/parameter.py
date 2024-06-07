import libem.parameter as libem
from libem.core.struct import Parameter

model = libem.model
temperature = libem.temperature

tools = Parameter(
    default=[],
    options=[],
)

cot = chain_of_thought = Parameter(
    default=False
)
confidence = Parameter(
    default=False
)
