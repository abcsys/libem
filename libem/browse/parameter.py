from libem.core.struct import Index, Parameter

engine = Parameter(
    default=Index(1),
    options=["google", "duckduckgo"],
)
