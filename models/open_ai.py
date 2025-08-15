import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)


class OpenAIModel:
    def __init__(self):
        self.initialize_client()


    @staticmethod
    def initialize_client():
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        return OpenAI(api_key=api_key)


