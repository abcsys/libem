from libem.core.struct import Prompt

role = Prompt(
    default="You are Libem, an entity matcher that determine "
            "if two entity descriptions refer to the same entity.",
    options=[""],
)
