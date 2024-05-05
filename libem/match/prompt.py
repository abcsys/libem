from libem.core.struct import Prompt

query = Prompt(
    default="Do these two entity descriptions refer to the same entity? "
            "Entity 1: {left} and Entity 2: {right}."
)
output = Prompt(
    default="Answer 'yes' or 'no' in lower case.",
    options=["Answer only 1 or 0."],
)
rule = Prompt(
    default="",
)
experience = Prompt(
    default="",
)
