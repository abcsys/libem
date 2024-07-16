from libem.optimize.cost import openai


def get_cost(model, *args, **kwargs):
    if model == "llama3":
        return 0
    else:
        return openai.get_cost(model, *args, **kwargs)
