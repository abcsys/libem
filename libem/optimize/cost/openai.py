from libem.optimize.cost import cache

model_info = None


def get_model_info(model=None):
    if model is None:
        return cache.load_openai()
    else:
        return cache.load_openai().get(model, None)


def get_input_cost(model, num_tokens):
    global model_info
    if model_info is None:
        model_info = get_model_info(model)
    return model_info['input_cost_per_token'] * num_tokens


def get_output_cost(model, num_tokens):
    global model_info
    if model_info is None:
        model_info = get_model_info(model)
    return model_info['output_cost_per_token'] * num_tokens


def get_cost(model, num_input_tokens, num_output_tokens):
    return get_input_cost(model, num_input_tokens) + get_output_cost(model, num_output_tokens)


if __name__ == "__main__":
    print(get_cost('gpt-4o', 1000, 100))
