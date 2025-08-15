from pydantic import BaseModel


class TripDetails(BaseModel):
    destination: str
    travel_from: str
    travel_to: str
    travel_experience: str
    spend_level: str
    budget_currency: str
    model: list[str] = ["gpt-4o-mini", "llama2"]

    class Config:
        arbitrary_types_allowed = True
