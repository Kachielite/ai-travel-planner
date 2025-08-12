# This file defines the types used in this application.
from typing import TypedDict, Literal


class Message(TypedDict):
    role: str
    content: str

class TravelExperience(TypedDict):
    destination: str
    travel_from: str  # format 'YYYY-MM-DD'
    travel_to: str  # format 'YYYY-MM-DD'
    travel_experience: Literal["adventurous", "relaxing", "cultural", "luxury"]
    spend_level: Literal["budget", "average", "luxury"]

class CurrencyConversion(TypedDict):
    from_currency: str
    to_currency: str
    amount: float