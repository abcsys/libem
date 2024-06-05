import libem.parameter as libem
from libem.core.struct import Option, Parameter

model = libem.model.copy()
temperature = libem.temperature.copy()

tools = Parameter(
    default=1,
    options=[Option([]), Option(["libem.browse"])],
)
CoT = Parameter(
    default=0,
    options=[Option(False), Option(True)]
)
