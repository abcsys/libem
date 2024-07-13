from libem.optimize.cost.openai import get_cost as get_cost_openai

def get_cost(model, num_input_tokens, num_output_tokens):
    if model == "llama3":
        return 0
    else:
        return get_cost_openai(model, num_input_tokens, num_output_tokens)

