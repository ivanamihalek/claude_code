import os

from dotenv import load_dotenv
load_dotenv()
from anthropic import Anthropic

def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

def get_response(client, model, messages, system_prompt=None, temperature=None):
    params = { 'model': model, 'max_tokens' : 1000, 'messages' : messages}
    if system_prompt is not None:
        params["system"] = system_prompt
    if temperature is not None:
        params["temperature"] = temperature

    return_message = client.messages.create(**params)
    return return_message

def print_message(message):
    print(message.content[0].text)

def print_price(message, pricing, model):
    price = message.usage.input_tokens * pricing[model]["input"] + message.usage.input_tokens * pricing[model]["output"]
    print(f"The pleasure of getting this answer cost us {price:.1e} dollars")


def main():
    client = Anthropic()
    model = "claude-sonnet-4-6"
    # https://claude.com/pricing#api
    pricing  = {
        "claude-haiku-4-5": {"input": 1.e-6, "output": 5.e-6},
        "claude-sonnet-4-6": {"input": 3.e-6, "output": 15.e-6},
        "claude-opus-4-7": {"input": 5.e-6, "output": 25.e-6}
    }

    question = "Generate a very short event bridge rule as json"
    sysprompt = "Do not include any markdown  (e.g. '```json') or comments in your answers"


    messages = []
    add_user_message(messages, question)
    response_message = get_response(client, model, messages, system_prompt=sysprompt)
    print("-"*120)
    print_message(response_message)
    print("-"*120)
    print_price(response_message, pricing, model)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
   main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
