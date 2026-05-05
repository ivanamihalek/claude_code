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

def get_response(client, model, messages):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
    )
    return message

def print_message(message, pricing, model):
    print(message.content[0].text)
    price = message.usage.input_tokens * pricing[model]["input"] + message.usage.input_tokens * pricing[model]["output"]
    print(f"The pleasure of getting this answer cost us {price:.1e} dollars")
    print()

def main():
    client = Anthropic()
    model = "claude-haiku-4-5"
    # https://claude.com/pricing#api
    pricing  = {
        "claude-haiku-4-5": {"input": 1.e-6, "output": 5.e-6},
        "claude-sonnet-4-6": {"input": 3.e-6, "output": 15.e-6}
    }
    messages = []
    add_user_message(messages,  "What is python's patsy package? Answer in one sentence")

    response_message = get_response(client, model, messages)
    print_message(response_message, pricing, model)

    add_assistant_message(messages, response_message.content[0].text)
    add_user_message(messages, "Add one more sentence")

    response_message = get_response(client, model, messages)
    print_message(response_message, pricing, model)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
   main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
