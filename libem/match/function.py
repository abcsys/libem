from libem.core.model import run
from libem.browse import function as browse
from libem.parameter import model


def match(left, right):
    return run(
        prompt=f"Do these two entity descriptions refer to the same entity? "
               f"Entity 1: {left} and Entity 2: {right}. Answer only yes or no.",
        model=model.default,
        tools=[browse]
    )
