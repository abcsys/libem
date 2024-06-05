from libem.core.struct import Option, Prompt

query = Prompt(
    default="Do the two entity descriptions refer to the same real-world entity?\n"
            "Entity 1: {left}.\nEntity 2: {right}."
)

rule = Prompt(
    default=0,
    options=[Option(Prompt.Rule()), Option(Prompt.Rule(rules=["Color distinguishes entities."]))],
)

experience = Prompt(
    default=Prompt.Experience(intro="Rules to follow:"),
)

output = Prompt(
    default=0,
    options=[Option("Answer with 'Yes' if they do and 'No' if they do not."),
             Option("Explain your answer step by step and end with 'yes' or 'no' only.")  # CoT
            ]
)
