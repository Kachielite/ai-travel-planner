from typing import TypedDict, List

class Message(TypedDict):
    role: str
    content: str

Messages = List[Message]
