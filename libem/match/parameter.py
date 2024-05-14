import libem.parameter as libem
from libem.core.struct import Parameter

model = libem.model
temperature = libem.temperature
seed = libem.seed

tools = Parameter(
    default=["libem.browse"],
    options=[[], ],
)
