#! /usr/bin/env python3

from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic
from utils import (add_user_message, get_response, print_message, print_price,
                   add_assistant_message)
from toolbox import Toolbox, create_result_block


def main():

    client = Anthropic()
    model = "claude-haiku-4-5"
    question = "What is the exact time, formatted as HH:MM:SS?"

    messages = []
    add_user_message(messages, question)

    response_message = get_response(client, model, messages, tools=[Toolbox.get_current_datetime_schema])
    print("-" * 120)
    print(response_message)
    print()
    print_message(response_message)
    print_price(response_message, model)

    # We must echo back  the full response content as the assistant message
    # — including both any text blocks and the tool_use block(s).
    # (In a simple chat we would echo back just the text, as in response_message.content[0].text)
    # The add_assistant_message will extract response_message.content
    add_assistant_message(messages, response_message)
    tool_result_block = create_result_block(response_message)

    messages.append({
        "role": "user",
        "content": tool_result_block
    })

    response_message = get_response(client, model, messages, tools=[Toolbox.get_current_datetime_schema])
    print("-" * 120)
    print_message(response_message)
    print_price(response_message, model)

if __name__ == '__main__':
    main()
