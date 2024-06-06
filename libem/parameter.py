from libem.core.struct import Index, Parameter

model = Parameter(
    default=Index(0),
    options=["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
)
temperature = Parameter(
    default=Index(0),
    options=[0, 0.1, 0.5, 0.9, 1.4]
)
