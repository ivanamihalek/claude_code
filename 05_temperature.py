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

def get_response(client, model, messages, system_prompt=None, temperature=1.0):
    params = { 'model': model, 'max_tokens' : 1000,
               'messages' : messages, 'temperature' : temperature}
    if system_prompt is not None:
        params["system"] = system_prompt

    return_message = client.messages.create(**params)
    return return_message

def print_message(message, pricing, model):
    print(message.content[0].text)
    price = message.usage.input_tokens * pricing[model]["input"] + message.usage.input_tokens * pricing[model]["output"]
    print(f"The pleasure of getting this answer cost us {price:.1e} dollars")
    print()

def main():
    client = Anthropic()
    model = "claude-sonnet-4-6"
    # https://claude.com/pricing#api
    pricing  = {
        "claude-haiku-4-5": {"input": 1.e-6, "output": 5.e-6},
        "claude-sonnet-4-6": {"input": 3.e-6, "output": 15.e-6},
        "claude-opus-4-7": {"input": 5.e-6, "output": 25.e-6}
    }
    question = "What is python's patsy package? Answer in two sentences."
    sysprompt = "Be casual and sarcastic."

    for temp_step in range(6):
        messages = []
        temperature = temp_step * 0.2
        print(f"--------------- {temperature} ---------------")
        add_user_message(messages, question)
        response_message = get_response(client, model, messages,
                                        system_prompt=sysprompt, temperature=temperature)
        print_message(response_message, pricing, model)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
   main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
