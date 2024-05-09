from libem.core.struct import Prompt

query = Prompt(
    default="Do these two entity descriptions refer to the same entity? "
            "Entity 1: {left} and Entity 2: {right}.",
    options=[""],
)

rule = Prompt(
    default="- Color distinguishes entities."
            "- When browse results are similar they are "
            "very likely to be the same entity.",
    options=[""],
)

experience = Prompt(
    default="",
    options=[""],
)

output = Prompt(
    default="If it's trivial to answer, just answer with 'yes' or 'no' "
            "in a new line, otherwise explain your answer step by step, "
            "and then end with 'yes' or 'no' only in a new line.",  # CoT
    options=["Answer only 1 or 0.",
             "Answer with 'yes' or 'no' only, in lower case.", ],
)
