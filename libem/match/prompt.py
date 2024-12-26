from libem.core.struct import Prompt, Shots
from libem.core.struct.prompt import (
    Shot, Rules, Experiences
)
from libem.core.struct.pattern import (
    CoT, Confidence
)
from libem.match.parameter import output_format, likelihood, tools

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

# build the output instruction prompt
def build_prompt():
    output_string = []
    if output_format() != "structured":
        output_string.append("At the end,")
    if likelihood():
        output_string.append("Give your answer strictly in the " \
                            "format of a single number between 0.0 and 1.0, " \
                            "estimating the likelihood that the two entities " \
                            "are the same.")
    else:
        output_string.append("Give your answer in the form of a "
                            "single 'yes' or 'no'.")
    if output_format() == "strict":
        output_string.append("Nothing else.")
    if tools():
        output_string.append("If you are unsure, consider using a tool.")
    
    return ' '.join(output_string)
    
output = build_prompt

"""Assistant prompts"""
shots = Shots(
    default=[Shot()]
)

"""User prompts"""
query = Prompt(
    default="Entity 1: {left}.\nEntity 2: {right}.",
    options=[],
)
