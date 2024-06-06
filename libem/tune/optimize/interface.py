from libem.tune.optimize.cost import cache
from libem.tune.optimize.cost import openai


def refresh_price_cache():
    cache.refresh_price_cache()


def get_openai_cost(model, num_input_tokens, num_output_tokens):
    return openai.get_cost(model, num_input_tokens, num_output_tokens)
