from dotenv import load_dotenv

load_dotenv()
from anthropic import Anthropic
from anthropic.types import ToolParam
from utils import add_user_message, get_response, print_message, print_price
from typing import TypedDict
from datetime import datetime, timedelta


def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise Exception("date_format cannot be empty")

    return datetime.now().strftime(date_format)


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


def main():
    client = Anthropic()
    model = "claude-haiku-4-5"
    question = ("What is the exact time, formatted as HH:MM:SS?")

    messages = []
    add_user_message(messages, question)
    response_message = get_response(client, model, messages)
    print("-" * 120)
    print_message(response_message)
    print("-"*120)
    print_price(response_message, model)


if __name__ == '__main__':
    main()
