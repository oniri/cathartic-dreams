import json as json_lib
from integrations.openai_api import call_openai_model
# from integrations.replicate_api import call_replicate_model

models = {
    'gpt-4o': {
        'full_name': 'gpt-4o',
        'source': 'openai',
        'cost_1000_tokens_inputs': 0.005,
        'cost_1000_tokens_outputs': 0.015,
    },
    'gpt-4o-mini': {
        'full_name': 'gpt-4o-mini',
        'source': 'openai',
        'cost_1000_tokens_inputs': 0.00015,
        'cost_1000_tokens_outputs': 0.0006,
    },
    'llama-3-70b': {
        'full_name': 'meta/meta-llama-3-70b-instruct',
        'source': 'replicate',
        'cost_1000_tokens_inputs': 0.00065,
        'cost_1000_tokens_outputs': 0.00275,
    },
    'llama-3.1-405b': {
        'full_name': 'meta/meta-llama-3.1-405b-instruct',
        'source': 'replicate',
        'cost_1000_tokens_inputs': 0.0095,
        'cost_1000_tokens_outputs': 0.0095,
    },
}

total_cost_session = 0


def call_model(prompt, model, json=False):
    if model['source'] == 'openai':
        return call_openai_model(prompt, model=model['full_name'], json=json)
    # elif model['source'] == 'replicate':
    #     return call_replicate_model(prompt, model=model['full_name'], json=json)
    else:
        return None


def call_and_parse(prompt, model, json=False):
    global total_cost_session

    response = call_model(prompt, model, json)

    if not response:
        return None

    cost = response['tokens_input'] * model['cost_1000_tokens_inputs'] / 1000 + response['tokens_output'] * model['cost_1000_tokens_outputs'] / 1000
    total_cost_session += cost
    # print(f"GPT Cost: ${cost:.3f} (Total: ${total_cost_session:.3f})")

    if json:
        return json_lib.loads(response['output'])
    else:
        return response['output']


def chat_response(prompt, model, json=False, max_retry=3):
    # print(f"GPT Call: {prompt}")

    attempts = 0
    while attempts < max_retry:
        try:
            response = call_and_parse(prompt, models[model], json)
            return response
        except Exception as e:
            print(f"GPT Call Failed: {e}")
            attempts += 1

    return None


def print_session_cost():
    global total_cost_session
    print(f"GPT total cost of session: ${total_cost_session:.3f}")
