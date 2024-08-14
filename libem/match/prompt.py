from libem.core.struct import Prompt, Shots, Index
from libem.core.struct.prompt import (
    Shot, Rules, Experiences
)
from libem.match.parameter import model

"""System prompts"""
role = Prompt(
    default="You are an entity matcher that determines whether "
            "two entity descriptions refer to the same real-world entity.",
    options=[""],
)

rules = Prompt(
    default=Rules(),
    options=[],
)

experiences = Prompt(
    default=Experiences(),
    options=[],
)

output = Prompt(
    default=Index(
        lambda: "strict"
        if model() in {
            "llama3", "llama3.1",
            "gpt-4o-2024-08-06"
        }
        else "standard"
    ),
    options={
        "standard": "At the end, give your answer in the form of a "
                    "single 'yes' or 'no'.",
        "strict": "At the end, give your answer in the form of a "
                  "single 'yes' or 'no'. Nothing else.",
        "likelihood": "At the end, give your answer strictly in the "
                      "format of a single number between 0.0 and 1.0, "
                      "estimating the likelihood that the two entities "
                      "are the same.",
    },
)

"""Assistant prompts"""
shots = Shots(
    default=[Shot()]
)

"""User prompts"""
query = Prompt(
    default="Entity 1: {left}.\nEntity 2: {right}.",
    options=[],
)
