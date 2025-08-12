from pydantic import BaseModel


class TripDetails(BaseModel):
    destination: str
    travel_from: str
    travel_to: str
    travel_experience: str
    spend_level: str

    class Config:
        arbitrary_types_allowed = True
