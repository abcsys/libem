from libem.core.struct import Prompt

query = Prompt(
    default="Do the two entity descriptions refer to the same real-world entity?\n"
            "Entity 1: {left}.\nEntity 2: {right}.",
    options=[],
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
    default="Give your answer in the form of a single 'yes' or 'no' only.",
    options=[],
)
