from libem.core.struct import Parameter

model = Parameter(
    default="gpt-4o-2024-08-06",
    options=["o1-preview", "gpt-4o","gpt-4o-mini", "gpt-4",
             "gpt-4-turbo", "gpt-3.5-turbo",
             "llama3", "llama3.1", "llama3.2", "claude-3-5-sonnet-20240620"]
)

temperature = Parameter(
    default=lambda: 1
        if model() in {"o1-preview"}
        else 0,
    options=[0.1, 0.5, 0.9, 1.4]
)

# enable system prompt
system_role = Parameter(
    default=lambda: "user"
        if model() in {"o1-preview"}
        else "system"
)
