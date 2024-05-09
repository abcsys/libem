from libem.core.struct import Prompt

query = Prompt(
    default="Do these two entity descriptions refer to the same entity? "
            "Entity 1: {left} and Entity 2: {right}.",
)

rule = Prompt(
    default=Prompt.Rule(rules=["Color distinguishes entities."]),
)

experience = Prompt(
    default="",
)

output = Prompt(
    default="If it's straightforward to answer, just answer with 'yes' or 'no' "
            "in a new line. If there are browsing results, you must first explain "
            "your answer step by step, and then end with 'yes' or 'no' "
            "in a new line.",
)
