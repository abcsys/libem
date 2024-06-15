from libem.core.struct import Parameter

model = Parameter(
    default="gpt-4-turbo",
)
temperature = Parameter(
    default=0,
)
strategy = Parameter(
    default="rule-from-mistakes",
)
