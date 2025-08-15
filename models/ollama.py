import requests
from schemas.message import Messages


class Ollama:
    OLLAMA_API: str = "http://localhost:11434/v1/chat"
    HEADERS: dict = {"Content-Type": "application/json"}
    MODEL_NAME: str = "llama2"

    def __init__(self, messages: Messages):
        self.messages = messages

    def get_payload(self):
        return {
            "model": self.MODEL_NAME,
            "messages": self.messages,
            "stream": False
        }

    def initialize_client(self):
        print('Calling to Ollama API...')
        try:
            response = requests.post(
                self.OLLAMA_API,
                json=self.get_payload(),
                headers=self.HEADERS
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to connect to Ollama API: {e}")