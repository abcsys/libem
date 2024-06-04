from libem.core.struct import Parameter
import libem.parameter as libem

model = libem.model.copy()
temperature = libem.temperature.copy()
engine = Parameter(
    default="duckduckgo",
    options=["google", "duckduckgo"],
)