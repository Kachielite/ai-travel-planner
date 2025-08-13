import base64
from io import BytesIO
from PIL import Image
from PIL.ImageFile import ImageFile

from models.open_ai import OpenAIModel
from tools import weather


class ImageGenerator:
    destination_city: str
    trip_dates: str

    def __init__(self, destination_city: str, trip_dates: str):
        self.destination_city = destination_city
        self.trip_dates = trip_dates

    @staticmethod
    def get_tool_description() -> dict:
        return {
            "name": "generate_image",
            "description": "Generate a realistic image of the destination city on the specified trip dates, reflecting the typical weather conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination_city": {
                        "type": "string",
                        "description": "The city that the user wants to travel to"
                    },
                    "trip_dates": {
                        "type": "string",
                        "description": "The date of the trip in 'YYYY-MM-DD' format",
                        "example": "2023-10-01 - 2023-10-10"
                    }
                },
                "required": ["destination_city", "trip_dates"],
                "additionalProperties": False
            }
        }

    def generate_image(self) -> ImageFile:
        weather_tool = weather.WeatherTool(self.destination_city, self.trip_dates)
        weather_data = weather_tool.get_weather()

        if "message" in weather_data:
            weather_desc = "typical seasonal weather"
        else:
            weather_desc = (
                f"{weather_data['status'].lower()} skies, about "
                f"{weather_data['temperature']}°C, humidity {weather_data['humidity']}%, "
                f"wind speed {weather_data['wind_speed']} m/s"
            )

        prompt = (
            f"Generate a realistic image of {weather_data['city']} on {weather_data['travel_from']} "
            f"showing {weather_desc}. "
            f"Make sure the scenery reflects the weather and time of year, "
            f"with iconic landmarks and natural seasonal colors."
        )

        response = OpenAIModel.initialize_client().images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="512x512",  # Reduced size for UI rendering and lower token usage
            response_format="b64_json",
        )

        if not response.data:
            raise ValueError("No image data returned from OpenAI API.")

        image_base64 = response.data[0].b64_json
        image_data = base64.b64decode(image_base64)
        return Image.open(BytesIO(image_data))