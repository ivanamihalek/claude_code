#! /usr/bin/env python3
import json

from dotenv import load_dotenv

load_dotenv()
from anthropic import Anthropic
from anthropic.types import ToolParam
from utils import add_user_message, get_response, print_message, print_price
from toolbox import get_required_tools
from datetime import datetime

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

def get_response(client: Anthropic, model, messages, system_prompt=None, temperature=None, output_config=None, tools=None):
    params = { 'model': model, 'max_tokens' : 1000, 'messages' : messages}
    if system_prompt is not None:
        params["system"] = system_prompt
    if temperature is not None:
        params["temperature"] = temperature
    if output_config is not None:
        params["output_config"] = output_config
    if tools is not None:
        params["tools"] = tools

    return_message = client.messages.create(**params)
    return return_message


def main():

    client = Anthropic()
    model = "claude-haiku-4-5"
    question = "What is the exact time, formatted as HH:MM:SS?"

    messages = []
    add_user_message(messages, question)

    response_message = get_response(client, model, messages, tools=[Toolbox.get_current_datetime_schema])
    assistant_message = {}  # THE QUESTION: WHAT SHOULD BE  IN THIS DICTIONARY?
    messages.append(assistant_message)

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



if __name__ == '__main__':
    main()
