#! /usr/bin/env python3
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()

from text_tool import TextEditorTool


from anthropic import Anthropic

from utils import add_user_message, get_response, print_message, print_price, add_assistant_message, create_result_block


# Make the text edit schema based on the model version being used
def get_web_search_schema():
    return {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 5,
        "allowed_domains": ["nih.gov"],
    }

def main():

    client = Anthropic()
    model = "claude-haiku-4-5"
    max_turns = 3
    # Use Direct Trigger Words: Include phrases like "Search the web for..." or
    # "Give me the latest live documentation for..." in your prompt, to force live search
    # question = "What are the recommendation for cardio exercise ?"  # -> replies from memory
    question = "As of 2026, what are the recommendation for cardio exercise ?"  # -> does the web search

    messages = []
    add_user_message(messages, question)
    response_message = None

    available_tools = [get_web_search_schema()]
    response_message = get_response(client, model, messages, tools=available_tools)
    for content in response_message.content:
        print()
        print(content)
    print()
    print_price(response_message, model)


if __name__ == '__main__':
    main()
