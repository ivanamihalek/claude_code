#! /usr/bin/env python3
import json
from email import message_from_string
from urllib import response

from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic
from utils import (add_user_message, get_response, print_message, print_price,
                   add_assistant_message)
from toolbox import Toolbox, create_result_block, get_required_tools


def main():

    client = Anthropic()
    model = "claude-haiku-4-5"
    max_turns = 3
    question = "What is the exact time, formatted as HH:MM? What is the current time in the SS format?"

    messages = []
    add_user_message(messages, question)
    response_message = None

    for _ in range(max_turns):
        response_message = get_response(client, model, messages, tools=[Toolbox.get_current_datetime_schema])
        add_assistant_message(messages, response_message)
        print_message(response_message)

        if response_message.stop_reason != "tool_use":
            break

        tool_result_block = create_result_block(response_message)
        add_user_message(messages, tool_result_block)

    if response_message  and response_message.stop_reason == "tool_use":
        print(f"Warning: the conversation loop closed while the model still asked for tool usage")

    [print(msg) for msg in messages]

if __name__ == '__main__':
    main()
