import libem.parameter as libem
from libem.core.struct import Index, Parameter

model = libem.model.copy()
temperature = libem.temperature.copy()

tools = Parameter(
    default=Index(1),
    options=[[], ["libem.browse"]],
)
CoT = Parameter(
    default=Index(0),
    options=[False, True]
)
