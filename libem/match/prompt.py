from libem.core.struct import Prompt, Shots, Index
from libem.core.struct.prompt import (
    Shot, Rules, Experiences
)
from libem.core.struct.pattern import (
    CoT, Confidence
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
            "llama3", "llama3.1", "llama3.2-3b", "llama3.2-1b", 
            "claude-3-5-sonnet-20240620",
        }
        else "standard"
    ),
    options={
        "standard": "Give your answer in the form of a "
                    "single 'yes' or 'no'.",
        "strict": "Give your answer in the form of a "
                  "single 'yes' or 'no'. Nothing else.",
        "likelihood": "Give your answer strictly in the "
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
