import os
from datetime import datetime

from dotenv import load_dotenv
from pyowm import OWM

load_dotenv(override=True)

class WeatherTool:
    destination_city: str
    travel_from: str  # format 'YYYY-MM-DD'

    def __init__(self, destination_city: str, travel_from: str):
        self.destination_city = destination_city
        self.travel_from = travel_from

    @staticmethod
    def get_tool_description() -> dict:
        return {
            "name": "get_weather",
            "description": "Get the current weather for a specified city over a defined period. Call this tool to get weather information for a specific city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination_city": {
                        "type": "string",
                        "description": "The city that the user wants to travel to",
                    },
                    "travel_from": {
                        "type": "string",
                        "description": "Departure date of the trip in 'YYYY-MM-DD' format",
                        "example": "2023-10-01"
                    }
                },
                "required": ["destination_city", "travel_from"],
                "additionalProperties": False
            }
        }

    def get_weather(self) -> dict:
        print("Fetching weather information...")
        api_key = os.getenv("OPEN_WEATHER_API_KEY")

        if not api_key:
            raise ValueError("OPEN_WEATHER_API_KEY environment variable is not set. Please set it in your .env file.")
        elif api_key.strip() != api_key:
            raise ValueError("OPEN_WEATHER_API_KEY must not contain leading or trailing whitespace. Please check your API key.")
        else:
            print("OpenWeather API key is valid and loaded successfully.")

        owm = OWM(api_key)
        mgr = owm.weather_manager()

        trip_date = datetime.strptime(self.travel_from, "%Y-%m-%d")
        forecast = mgr.forecast_at_place(self.destination_city, '3h')
        weather_on_trip = None
        for weather in forecast.forecast.weathers:
            if weather.reference_time('date').date() == trip_date.date():
                weather_on_trip = weather
                break

        if weather_on_trip:
            print(f"Weather on {self.travel_from} in {self.destination_city}: {weather_on_trip.status}, "
                  f"Temperature: {weather_on_trip.temperature('celsius')['temp']}°C, "
                  f"Humidity: {weather_on_trip.humidity}%, Wind Speed: {weather_on_trip.wind()['speed']} m/s")
            return {
                "city": self.destination_city,
                "temperature": weather_on_trip.temperature('celsius')['temp'],
                "status": weather_on_trip.status,
                "humidity": weather_on_trip.humidity,
                "wind_speed": weather_on_trip.wind()['speed'],
                "travel_from": self.travel_from
            }
        else:
            print(f"No weather forecast available for {self.destination_city} on {self.travel_from}.")
            return {
                "city": self.destination_city,
                "message": "No forecast available for the specified trip date.",
                "travel_from": self.travel_from
            }


