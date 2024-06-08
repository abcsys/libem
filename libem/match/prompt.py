from libem.core.struct import Prompt

role = Prompt(
    default="You are an entity matcher that determine whether"
            "two entity descriptions refer to the same real-world entity.",
    options=[""],
)

rule = Prompt(
    default=Prompt.Rule(),
    options=[],
)

experience = Prompt(
    default=Prompt.Experience(),
    options=[],
)

output = Prompt(
    default="At the end, give your answer in the form of a single 'yes' or 'no'.",
    options=[],
)

query = Prompt(
    default="Entity 1: {left}.\nEntity 2: {right}.",
    options=[],
)
