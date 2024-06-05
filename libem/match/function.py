import time

import libem
from libem.match import prompt, parameter
from libem.core.struct import Prompt
from libem.core import model

schema = {
    "type": "function",
    "function": {
        "name": "match",
        "description": "Perform entity matching given two entity description.",
        "parameters": {
            "type": "object",
            "properties": {
                "left": {
                    "type": "string",
                    "description": "Description of the first entity",
                },
                "right": {
                    "type": "string",
                    "description": "Description of the second entity",
                },
            },
            "required": ["left", "right"],
        },
    }
}


def func(left, right):
    start = time.time()
    match_prompt = Prompt.join(
        prompt.query(
            left=left,
            right=right
        ),
        prompt.rule(),
        prompt.experience(),
        prompt.output(),
    )
    model_output = model.call(
        prompt=match_prompt,
        tools=parameter.tools(),
        model=parameter.model(),
        temperature=parameter.temperature(),
        seed=libem.LIBEM_SEED,
    )
    pred = parse_output(model_output)
    libem.trace.add({"match": {"left": left, "right": right, "model_output": model_output,
                               "pred": pred, "prompt": match_prompt,
                               "latency": time.time() - start}})
    return pred


def parse_output(output: str) -> str:
    libem.debug("Match raw output:", output)
    output = [line.lower() for line in output.split("\n")]
    confidence, answer = None, None
    
    # parse answer
    answer = "yes" if "yes" in output[-1] else "no"
    
    # parse confidence score if CoT is True
    if parameter.CoT():
        for i, line in enumerate(reversed(output)):
            if 'confidence score' in line:
                confidence = ''.join(filter(str.isdigit, line))
                
                # catch cases when score is on a new line
                if len(confidence) == 0:
                    confidence = ''.join(filter(str.isdigit, output[i-1]))
                return answer, int(confidence)
    
    return answer
