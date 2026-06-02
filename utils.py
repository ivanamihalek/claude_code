import json
from ast import Dict
from symtable import Class
from typing import Any, List, Tuple

from anthropic import Anthropic
from anthropic.types import ToolUseBlock, TextBlock, Message

from toolbox import Toolbox


def add_user_message(messages, request: Message | Any):
    user_message = {"role": "user",
                    "content": request.content if isinstance(request, Message)  else request}
    messages.append(user_message)


def add_assistant_message(messages, response: Message | Any):
    assistant_message = {"role": "assistant",
                         "content": response.content if isinstance(response, Message)  else response}
    messages.append(assistant_message)


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

def text_from_message(message: Message):
    return "\n".join(
        [block.text for block in message.content if block.type == "text"]
    )

def print_message(message):
    for content in message.content:
        if type(content) == TextBlock:
            print("text:", content.text)
        elif type(content) == ToolUseBlock:
            print("tool:", content.name)
            print("input:", content.input)


def print_price(message, model):
    # https://claude.com/pricing#api
    pricing  = {
        "claude-haiku-4-5": {"input": 1.e-6, "output": 5.e-6},
        "claude-sonnet-4-6": {"input": 3.e-6, "output": 15.e-6},
        "claude-opus-4-7": {"input": 5.e-6, "output": 25.e-6}
    }
    price = message.usage.input_tokens * pricing[model]["input"] + message.usage.input_tokens * pricing[model]["output"]
    print(f"The pleasure of getting this answer cost us {price:.1e} dollars")


def get_required_tools(message) -> List[Tuple]:
    # see doc/02_on_tooluseblock.py
    tool_input_tuples = []
    for content in message.content:
        if isinstance(content, ToolUseBlock):
            if content.name == 'str_replace_based_edit_tool':
                identifier =  content.id
                command = content.input['command']
                arguments = {k:v for k, v in content.input.items() if k != 'command'}
                tool_input_tuples.append((identifier, command, arguments))
            else:
                tool_input_tuples.append((content.id, content.name, content.input))
    return tool_input_tuples


def create_result_block(response_message, tool_class) -> List[Dict]:
    tool_input_tuples = get_required_tools(response_message)
    tool_result_block = []
    for tool_use_id, fn_name, args in tool_input_tuples:
        try:
            result = getattr(tool_class(), fn_name)(**args)
            is_error = False
        except Exception as e:
            result = str(e)
            is_error = True
        tool_result = {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": json.dumps(result) ,
            "is_error": is_error
        }
        tool_result_block.append(tool_result)

    return tool_result_block
