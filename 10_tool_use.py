#! /usr/bin/env python3
import json

from dotenv import load_dotenv

load_dotenv()
from anthropic import Anthropic
from anthropic.types import ToolParam
from utils import add_user_message, get_response, print_message, print_price, get_required_tools, add_assistant_message
from typing import TypedDict
from datetime import datetime, timedelta

class Toolbox:

    get_current_datetime_schema: ToolParam = {
        "name": "get_current_datetime",
        "description": "Returns the current date and time formatted according to the specified format string.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": "A strftime-compatible format string (e.g. '%Y-%m-%d %H:%M:%S'). Must not be empty.",
                    "default": "%Y-%m-%d %H:%M:%S"
                }
            },
            "required": []
        }
    }

    def get_current_datetime(self, date_format="%Y-%m-%d %H:%M:%S"):
        if not date_format:
            raise Exception("date_format cannot be empty")

        return datetime.now().strftime(date_format)



def main():

    client = Anthropic()
    model = "claude-haiku-4-5"
    question = ("What is the exact time, formatted as HH:MM:SS?")

    messages = []
    add_user_message(messages, question)

    response_message = get_response(client, model, messages, tools=[Toolbox.get_current_datetime_schema])
    print("-" * 120)
    print_message(response_message)
    print("-"*120)
    print_price(response_message, model)
    # TODO we are here - what should the assistant message look like here?
    add_assistant_message(messages, response_message)

    tool_input_tuples = get_required_tools(response_message)
    tool_result_block = []
    for tool_use_id, fn_name, args in tool_input_tuples:
        try:
            result = getattr(Toolbox(), fn_name)(**args)
            is_error = False
        except Exception as e:
            result = e
            is_error = True
        tool_result = {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": json.dumps(result),
            "is_error": is_error
        }
        tool_result_block.append(tool_result)

    messages.append({
        "role": "user",
        "content": tool_result_block
    })

    response_message = get_response(client, model, messages, tools=[Toolbox.get_current_datetime_schema])
    print("-" * 120)
    print_message(response_message)
    print("-" * 120)
    print_price(response_message, model)

if __name__ == '__main__':
    main()
