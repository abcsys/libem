import libem.parameter as libem
from libem.core.struct import Parameter

model = libem.model.copy()
temperature = libem.temperature.copy()

tools = Parameter(
    default=["libem.browse"],
    options=[[], ],
)
CoT = Parameter(default=False)
