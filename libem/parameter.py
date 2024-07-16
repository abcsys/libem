from libem.core.struct import Parameter

model = Parameter(
    default="gpt-4o",
    options=["gpt-4-turbo", "gpt-3.5-turbo"]
)
temperature = Parameter(
    default=0,
    options=[0.1, 0.5, 0.9, 1.4]
)
guess = Parameter(
    default=False,
    options=[True, False]
)
always = Parameter(
    default=None,
    options=["yes", "no"]
)
