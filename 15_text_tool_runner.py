#! /usr/bin/env python3
import json
from email import message_from_string
from urllib import response

from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic
from utils import (add_user_message, get_response, print_message, print_price,
                   add_assistant_message)

# Make the text edit schema based on the model version being used
def get_text_edit_schema(model):
    return {
        "type": "text_editor_20250728",
        "name": "str_replace_based_edit_tool",
    }

def main():

    client = Anthropic()
    model = "claude-haiku-4-5"
    max_turns = 10
    question = "Open the ./sandbox/main.py file and summarize its contents."

    messages = []
    add_user_message(messages, question)
    response_message = None

    available_tools = [get_text_edit_schema(model)]

    for _ in range(max_turns):
        response_message = get_response(client, model, messages, tools=available_tools)
        add_assistant_message(messages, response_message)
        print_message(response_message)

        if response_message.stop_reason != "tool_use":
            break

        tool_result_block = create_result_block(response_message)
        add_user_message(messages, tool_result_block)

    if response_message  and response_message.stop_reason == "tool_use":
        print(f"Warning: the conversation loop closed while the model still asked for tool usage")

    print()
    [print(msg) for msg in messages]

if __name__ == '__main__':
    main()
