from typing import TypedDict, Literal


class TripDetails(TypedDict):
    destination: str
    travel_from: str  # format 'YYYY-MM-DD'
    travel_to: str  # format 'YYYY-MM-DD'
    travel_experience: Literal["adventurous", "relaxing", "cultural", "luxury"]
    spend_level: Literal["budget", "average", "luxury"]