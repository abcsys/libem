from libem.core.struct import Prompt

query = Prompt(
    default="Do the two entity descriptions refer to the same real-world entity?\n"
            "Entity 1: {left}.\nEntity 2: {right}.",
    options=[""],
)

rule = Prompt(
    default=Prompt.Rule(rules=["Color distinguishes entities."]),
)

experience = Prompt(
    default=Prompt.Experience(),
)

output = Prompt(
    default="Answer with 'Yes' if they do and 'No' if they do not.",
    options=["Explain your answer step by step and end with 'yes' or 'no' only."  # CoT
             "Answer only 1 or 0.",
             "Answer with 'yes' or 'no' only, in lower case.", ],
)
