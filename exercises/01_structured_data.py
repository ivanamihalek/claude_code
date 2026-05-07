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

def print_price(message, pricing, model):
    price = message.usage.input_tokens * pricing[model]["input"] + message.usage.input_tokens * pricing[model]["output"]
    print(f"The pleasure of getting this answer cost us {price:.1e} dollars")

"""
The key rules for Anthropic's structured output schema:

 * Every "type": "object" node — including nested ones inside array items — must have "additionalProperties": False.
 * Wrap the list in an envelope object — the top-level schema must be an object; you can't use "type": "array" at the root.
 * required keys must exactly match properties keys (your original bug was these mismatched).
"""


def build_schema() -> dict:
    """Return the json_schema for an array of AWS CLI commands."""
    command_item = {
        "type": "object",
        "properties": {
            "cli_tool":    {"type": "string"},
            "aws_service": {"type": "string"},
            "subcommand":  {"type": "string"},
        },
        "required": ["cli_tool", "aws_service", "subcommand"],
        "additionalProperties": False,  # required on every nested object
    }
    return {
        "type": "object",
        "properties": {
            "commands": {"type": "array", "items": command_item},
        },
        "required": ["commands"],
        "additionalProperties": False,  # required on top-level object too
    }

def main():
    client = Anthropic()
    model = "claude-sonnet-4-6"
    # https://claude.com/pricing#api
    pricing  = {
        "claude-haiku-4-5": {"input": 1.e-6, "output": 5.e-6},
        "claude-sonnet-4-6": {"input": 3.e-6, "output": 15.e-6},
        "claude-opus-4-7": {"input": 5.e-6, "output": 25.e-6}
    }

    question = "Generate three different sample AWS CLI commands. Each should be very short "

    output_config = {"format": {"type": "json_schema", "schema": build_schema()}}
    messages = []
    add_user_message(messages, question)
    response_message = get_response(client, model, messages, output_config=output_config)
    print("-"*120)
    print_message(response_message)
    print("-"*120)
    print_price(response_message, pricing, model)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
   main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
