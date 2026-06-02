import os

from anthropic.types import MessageParam
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

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
    message_param: MessageParam = {
                "role": "user",
                "content": "What is python's patsy package? Answer in one sentence"
            }
    response_msg = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[message_param])

    print_message(response_msg, pricing, model)

    message_param: MessageParam = {
                "role": "user",
                "content": "Tell me more about that."
            }
    print()
    response_msg = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[message_param])
    print_message(response_msg, pricing, model)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
   main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
