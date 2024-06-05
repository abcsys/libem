from libem.core.struct import Option, Parameter
import libem.parameter as libem

model = libem.model.copy()
temperature = libem.temperature.copy()
engine = Parameter(
    default=1,
    options=[Option("google"), Option("duckduckgo")],
)