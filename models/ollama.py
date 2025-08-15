import requests


class Ollama:
    CHAT_API = "http://localhost:11434/api/chat"
    HEADERS = {"Content-Type": "application/json"}
    MODEL_NAME = "llama2"

    def __init__(self, messages: list):
        for m in messages:
            if m.get("content") is None:
                m["content"] = ""
        self.messages = messages

    def get_payload(self):
        return {
            "model": self.MODEL_NAME,
            "messages": self.messages,
            "stream": False
        }

    def initialize_client(self):
        print(f"Calling Ollama API in CHAT mode with {len(self.messages)} messages...")
        payload = self.get_payload()

        try:
            response = requests.post(
                self.CHAT_API,
                json=payload,
                headers=self.HEADERS
            )

            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to connect to Ollama API: {e}")

