import libem.parameter as libem
from libem.core.struct import Parameter

model = libem.model
temperature = libem.temperature

tools = Parameter(
    default=["libem.browse"],
    options=[[], ],
)
