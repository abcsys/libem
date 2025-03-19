from libem.core.struct import Parameter

similarity = Parameter(
    default=60,
    options=[]
)

batch_size = Parameter(
    default=10000,
    options=[]
)

default_ignore = Parameter(
    default=["id", "uuid"],
    options=[]
)
