import libem.parameter as libem
from libem.core.struct import Index, Parameter

model = libem.model
temperature = libem.temperature

tools = Parameter(
    default=Index(1),
    options=[[], ["libem.browse"]],
)
cot = Parameter(
    default=Index(0),
    options=[False, True]
)

confidence = Parameter(
    default=Index(0),
    options=[False, True]
)
