from libem.core.struct import Option, Parameter

model = Parameter(
    default=0,
    options=[Option("gpt-4o"), Option("gpt-4-turbo"), Option("gpt-3.5-turbo")]
)
temperature = Parameter(
    default=0,
    options=[Option(0), Option(0.1), Option(0.5), Option(0.9), Option(1.4)]
)
