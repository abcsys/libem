from libem.core.struct.prompt import Prompt

CoT = chain_of_thought = Prompt(
    default="Explain your answer step by step.",
)

Explanation = Prompt(
    default="Explain your answer in brief.",
)

Confidence = Prompt(
    default="At the end, give a confidence score from 0.0 to 1.0, "
            "do not justify.",
)
