from libem.core.struct import Prompt, Shot

"""System prompts"""
role = Prompt(
    default="You are an entity matcher that determines whether "
            "two entity descriptions refer to the same real-world entity.",
    options=[""],
)

rules = Prompt(
    default=Prompt.Rules(),
    options=[],
)

experiences = Prompt(
    default=Prompt.Experiences(),
    options=[],
)

output = Prompt(
    default="At the end, give your answer in the form of a single 'yes' or 'no'.",
    options=[],
)

"""Assistant prompts"""
shots = Prompt(
    default=Prompt.Shots([Shot(), ]),
)

"""User prompts"""
query = Prompt(
    default="Entity 1: {left}.\nEntity 2: {right}.",
    options=[],
)
