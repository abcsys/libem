from libem.core.struct import Prompt, Rules

description = Prompt(
    default="Browse the web to find additional information for "
            "a given entity."
)

rules = Prompt(
    default=Rules([
        "Use only when you think it would help with the matching task."
    ])
)
