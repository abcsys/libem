from libem.core.struct import Index, Prompt

query = Prompt(
    default="Do the two entity descriptions refer to the same real-world entity?\n"
            "Entity 1: {left}.\nEntity 2: {right}."
)

rule = Prompt(
    default=Index(0),
    options=[Prompt.Rule(), Prompt.Rule(rules=["Color distinguishes entities."])],
)

experience = Prompt(
    default=Prompt.Experience(intro="Rules to follow:"),
)

output = Prompt(
    default=Index(0),
    options=["Answer with 'Yes' if they do and 'No' if they do not.",
             "Explain your answer step by step. "
             "Then give a confidence score from 1 to 5, with 1 being just a guess "
             "and 5 being extremely confident, give the score only, do not justify. "
             "Finally, give your final answer in the form of a single 'yes' or 'no' only.",  # CoT
            ]
)
