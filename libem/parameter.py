from libem.core.struct import Parameter

model = Parameter(
    default="gpt-4o-2024-08-06",
    options=["gpt-4o","gpt-4o-mini", "gpt-4",
             "gpt-4-turbo", "gpt-3.5-turbo",
             "llama3"]
)
temperature = Parameter(
    default=0,
    options=[0.1, 0.5, 0.9, 1.4]
)
