import os
from dotenv import load_dotenv
from openai import OpenAI as OpenAIClient

from types import Message

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")


def get_openai_client():
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")
    elif not api_key.startswith("sk-proj-"):
        raise ValueError("OPENAI_API_KEY must start with 'sk-proj-'. Please check your API key.")
    elif api_key.strip() != api_key:
        raise ValueError("OPENAI_API_KEY must not contain leading or trailing whitespace. Please check your API key.")
    else:
        print("OpenAI API key is valid and loaded successfully.")
    return OpenAIClient(api_key=api_key)


class PromptLLM:
    messages: Message
    model: str = "gpt-4o-mini"

    def __init__(self, messages: Message, model: str = "gpt-4o-mini"):
        self.messages = messages
        self.model = model

    def get_response(self) -> str:
        response = get_openai_client().chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=False,
        )
        if not response.choices:
            raise ValueError("No choices returned from OpenAI API.")
        return response.choices[0].message.content




