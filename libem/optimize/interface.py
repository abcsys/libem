from libem.optimize.cost import cache, openai


def refresh_price_cache():
    cache.refresh_price_cache()


def get_openai_cost(model, num_input_tokens, num_output_tokens):
    return openai.get_cost(model, num_input_tokens, num_output_tokens)


from libem.optimize.function import profile

_ = profile
