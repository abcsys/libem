from libem.core.struct import Parameter

model = Parameter(
    default="gpt-4-turbo",
    options=["gpt-4-0125-preview", "gpt-3.5-turbo"]
)
temperature = Parameter(
    default=0,
    options=[0.1, 0.5, 0.9, 1.4]
)
