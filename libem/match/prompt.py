from libem.core.struct import Prompt

query = Prompt(
    default="Do the two entity descriptions refer to the same real-world entity?\n"
            "Entity 1: {left}.\nEntity 2: {right}.",
    options=[""],
)

rule = Prompt(
    default=Prompt.Rule(),
    options=[Prompt.Rule(rules=["Color distinguishes entities."])],
)

experience = Prompt(
    default=Prompt.Experience(intro="Rules to follow:"),
)

output = Prompt(
    default="Answer with 'Yes' if they do and 'No' if they do not.",
    options=["Explain your answer step by step. " \
             "Then give a confidence score from 1 to 10, with 1 being just a guess " \
             "and 10 being extremely confident, give the score only, do not justify. " \
             "Finally, give your final answer in the form of a single 'yes' or 'no' only.",  # CoT
             "Answer only 1 or 0.",
             "Answer with 'yes' or 'no' only, in lower case.",]
)
