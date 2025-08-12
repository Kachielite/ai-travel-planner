import base64
import os
from io import BytesIO
from PIL import Image
from PIL.ImageFile import ImageFile
from dotenv import load_dotenv
from openai import OpenAI as OpenAIClient

from tools import weather
from types.message import Message

load_dotenv(override=True)

class PromptOpenAI:
    messages: Message
    model: str = "gpt-4o-mini"
    api_key = os.getenv("OPENAI_API_KEY")

    def __init__(self, messages: Message, model: str = "gpt-4o-mini"):
        self.messages = messages
        self.model = model

    def get_openai_client(self) -> OpenAIClient:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")
        elif not self.api_key.startswith("sk-proj-"):
            raise ValueError("OPENAI_API_KEY must start with 'sk-proj-'. Please check your API key.")
        elif self.api_key.strip() != self.api_key:
            raise ValueError(
                "OPENAI_API_KEY must not contain leading or trailing whitespace. Please check your API key.")
        else:
            print("OpenAI API key is valid and loaded successfully.")
        return OpenAIClient(api_key=self.api_key)

    def get_response(self) -> str:
        response = self.get_openai_client().chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=False,
        )
        if not response.choices:
            raise ValueError("No choices returned from OpenAI API.")
        return response.choices[0].message.content

    def generate_image(self, destination_city: str, trip_dates: str) -> ImageFile:
        weather_tool = weather.WeatherTool(destination_city, trip_dates)
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
            f"Generate a realistic image of {weather_data['city']} on {weather_data['trip_dates']} "
            f"showing {weather_desc}. "
            f"Make sure the scenery reflects the weather and time of year, "
            f"with iconic landmarks and natural seasonal colors."
        )

        response = self.get_openai_client().images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json",
        )

        if not response.data:
            raise ValueError("No image data returned from OpenAI API.")

        image_base64 = response.data[0].b64_json
        image_data = base64.b64decode(image_base64)
        return Image.open(BytesIO(image_data))
