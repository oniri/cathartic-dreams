from openai import OpenAI
from env import env

client = OpenAI(
    api_key=env('OPENAI_API_KEY'),
)


def call_openai_model(prompt, model, json=False):
    global total_cost_session

    messages = [
        {'role': 'user', 'content': prompt},
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"} if json else None,
    )
    text = response.choices[0].message.content

    return {
        'output': text,
        'tokens_input': response.usage.prompt_tokens,
        'tokens_output': response.usage.completion_tokens
    }