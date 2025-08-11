# This file defines the types used in this application.
from typing import TypedDict, Literal


class Message(TypedDict):
    role: str
    content: str

class TravelExperience(TypedDict):
    duration: int
    travel_experience: Literal["adventurous", "relaxing", "cultural", "luxury"]
    spend_level: Literal["budget", "average", "luxury"]

class CurrencyConversion(TypedDict):
    from_currency: str
    to_currency: str
    amount: float