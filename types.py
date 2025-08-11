# This file defines the types used in this application.
from typing import TypedDict


class Message(TypedDict):
    role: str
    content: str