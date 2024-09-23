from libem.optimize.cost import cache

model_info = None
null_model_info = {
    'input_cost_per_token': 0,
    'output_cost_per_token': 0
}


def get_model_info(model=None):
    if model is None:
        return cache.load_openai()
    else:
        return cache.load_openai().get(model, null_model_info)


def get_input_cost(model, num_tokens):
    if num_tokens is None or num_tokens <= 0:
        return 0

    global model_info
    if model_info is None:
        model_info = get_model_info(model)
    return model_info['input_cost_per_token'] * num_tokens


def get_output_cost(model, num_tokens):
    if num_tokens is None or num_tokens <= 0:
        return 0

    global model_info
    if model_info is None:
        model_info = get_model_info(model)
    return model_info['output_cost_per_token'] * num_tokens


def get_cost(model, num_input_tokens, num_output_tokens):
    return get_input_cost(model, num_input_tokens) + get_output_cost(model, num_output_tokens)


if __name__ == "__main__":
    print(get_cost('gpt-4o', 1000, 100))
