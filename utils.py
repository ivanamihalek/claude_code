def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def get_response(client, model, messages, system_prompt=None, temperature=None, output_config=None):
    params = { 'model': model, 'max_tokens' : 1000, 'messages' : messages}
    if system_prompt is not None:
        params["system"] = system_prompt
    if temperature is not None:
        params["temperature"] = temperature
    if output_config is not None:
        params["output_config"] = output_config

    return_message = client.messages.create(**params)
    return return_message


def print_message(message):
    print(message.content[0].text)


def print_price(message, model):
    # https://claude.com/pricing#api
    pricing  = {
        "claude-haiku-4-5": {"input": 1.e-6, "output": 5.e-6},
        "claude-sonnet-4-6": {"input": 3.e-6, "output": 15.e-6},
        "claude-opus-4-7": {"input": 5.e-6, "output": 25.e-6}
    }
    price = message.usage.input_tokens * pricing[model]["input"] + message.usage.input_tokens * pricing[model]["output"]
    print(f"The pleasure of getting this answer cost us {price:.1e} dollars")
