from libem.core.struct import Index, Parameter
import libem.parameter as libem

model = libem.model.copy()
temperature = libem.temperature.copy()
engine = Parameter(
    default=Index(1),
    options=["google", "duckduckgo"],
)