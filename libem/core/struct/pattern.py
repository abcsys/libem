from libem.core.struct.prompt import Prompt

CoT = chain_of_thought = Prompt(
    default="Explain your answer step by step.",
)

Explanation = Prompt(
    default="Explain your answer in brief.",
)

Confidence = Prompt(
    default="Give a confidence score from 0 to 100, with 0 being a guess "
            "and 100 being confident, give the score only, do not justify.",
)
