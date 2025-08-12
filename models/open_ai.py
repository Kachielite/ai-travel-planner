import os
from dotenv import load_dotenv
from openai import OpenAI as OpenAIClient

from types.message import Messages

load_dotenv(override=True)

class PromptOpenAI:
    messages: Messages
    model: str = "gpt-4o-mini"
    tools: list

    def __init__(self, messages: Messages, model: str = "gpt-4o-mini", tools: list = None):
        self.messages = messages
        self.model = model
        self.tools = tools if tools is not None else []

    @staticmethod
    def get_openai_client() -> OpenAIClient:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")
        elif not api_key.startswith("sk-proj-"):
            raise ValueError("OPENAI_API_KEY must start with 'sk-proj-'. Please check your API key.")
        elif api_key.strip() != api_key:
            raise ValueError(
                "OPENAI_API_KEY must not contain leading or trailing whitespace. Please check your API key.")
        else:
            print("OpenAI API key is valid and loaded successfully.")
        return OpenAIClient(api_key=api_key)

    def get_response(self) -> str:
        chat_params = {
            "model": self.model,
            "messages": self.messages,
            "stream": False,
        }

        if self.tools:
            chat_params["tools"] = self.tools

        response = self.get_openai_client().chat.completions.create(**chat_params)
        if not response.choices:
            raise ValueError("No choices returned from OpenAI API.")
        return response.choices[0].message.content
