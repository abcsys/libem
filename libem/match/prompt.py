from libem.core.struct import Prompt, Shots
from libem.core.struct.prompt import (
    Shot, Rules, Experiences
)
from libem.core.struct.pattern import (
    CoT, Confidence
)
from libem.match.parameter import output_format, likelihood, batch_size, tools

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
    if batch_size() > 1:
        output_string.append("For each pair of 'left' and 'right' entities,")
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
    default="Left entity: {left}.\nRight entity: {right}.",
)

def _multimodal_prompt(left_text: str, 
                       left_images: list, 
                       right_text: str, 
                       right_images: list[str]):
    prompt = []
    prompt.append({"type": "text", "text": f"Left entity:"})
    if left_text:
        prompt.append({"type": "text", "text": left_text})
    if left_images:
        prompt.extend([{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}} 
                        for img in left_images])
    prompt.append({"type": "text", "text": f"Right entity:"})
    if right_text:
        prompt.append({"type": "text", "text": right_text})
    if right_images:
        prompt.extend([{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}} 
                        for img in right_images])
    
    return prompt

multimodal_query = Prompt(
    default=_multimodal_prompt,
)

def _prompt_batch_prompt(left: list[str], right: list[str]):
    return Prompt.join(*[
        Prompt.join(
            f"{i + 1}:",
            query(
                left=l,
                right=r
            )
        )
        for i, (l, r) in enumerate(
            zip(left, right)
        )])

prompt_batch_query = Prompt(
    default=_prompt_batch_prompt,
)

def _multimodal_prompt_batch_prompt(left_text: list[str], 
                       left_images: list[list[str]], 
                       right_text: list[str], 
                       right_images: list[list[str]]):
    prompt = []
    
    for i, (l_t, l_i, r_t, r_i) in enumerate(zip(left_text, left_images, right_text, right_images)):
        prompt.append({"type": "text", "text": f"{i + 1}:"})
        prompt.extend(multimodal_query(l_t, l_i, r_t, r_i))
    
    return prompt

multimodal_prompt_batch_query = Prompt(
    default=_multimodal_prompt_batch_prompt,
)

def _record_batch_prompt(left: str, right: list[str]):
    left_prompt = Prompt.join("Left entity:", left)
    right_prompt = Prompt.join("Right entities:",
            *[f"{i + 1}:\n{r}"
            for i, r in enumerate(right)
        ])
    return Prompt.join(left_prompt, right_prompt)

record_batch_query = Prompt(
    default=_record_batch_prompt,
)

def _multimodal_record_batch_prompt(left_text: str, 
                       left_images: list, 
                       right_text: list[str], 
                       right_images: list[list[str]]):
    prompt = []
    prompt.append({"type": "text", "text": f"Left entity:"})
    if left_text:
        prompt.append({"type": "text", "text": left_text})
    if left_images:
        prompt.extend([{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}} 
                        for img in left_images])
    
    prompt.append({"type": "text", "text": f"Right entities:"})
    
    for i, (r_t, r_i) in enumerate(zip(right_text, right_images)):
        prompt.append({"type": "text", "text": f"{i + 1}:"})
        if r_t:
            prompt.append({"type": "text", "text": r_t})
        if r_i:
            prompt.extend([{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}} 
                            for img in r_i])
    
    return prompt

multimodal_record_batch_query = Prompt(
    default=_multimodal_record_batch_prompt,
)
