import os
from dotenv import load_dotenv
from openai import OpenAI

from schemas.trip_details import TripDetails

load_dotenv(override=True)


class OpenAIModel:
    trip_details: TripDetails

    def __init__(self, trip_details: TripDetails):
        self.initialize_client()
        self.trip_details = trip_details


    @staticmethod
    def initialize_client():
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        return OpenAI(api_key=api_key)


