from models.open_ai import PromptOpenAI
from tools.image import ImageGenerator
from tools.weather import WeatherTool
from types.message import Messages
from types.trip_details import TripDetails


class TravelPlanner:
    trip_details: TripDetails
    system_prompt: str = (
        "You are a helpful travel planner. Your role is to assist users in planning their trips "
        "by providing accurate, relevant, and easy-to-understand recommendations based on their trip details.\n\n"
        "You have access to two tools:\n"
        "1. **Weather Tool** – Retrieve accurate weather forecasts for the destination city and trip dates.\n"
        "2. **Image Generation Tool** – Create a realistic image of the destination city on the specified trip dates, "
        "reflecting the expected weather conditions.\n\n"
        "When responding:\n"
        "- Use the weather tool to get forecast details.\n"
        "- Use the image tool to generate an image that visually represents the location and weather.\n"
        "- Present your answer in **Markdown format**.\n"
        "- Include the generated image in the response (Markdown syntax: `![alt text](image_url)`).\n"
        "- If you do not know something, clearly say so rather than guessing.\n"
        "- Ensure all advice is accurate, concise, and user-friendly."
    )
    weather_tool = WeatherTool.get_tool_description()
    image_tool = ImageGenerator.get_tool_description()

    def __init__(self, trip_details: TripDetails):
        self.trip_details = trip_details

    def get_tools(self):
        return [{"type": "function", "function": self.weather_tool},
                {"type": "function", "function": self.image_tool}]

    def user_prompt(self) -> str:
        td = self.trip_details
        return (
            f"{self.system_prompt}\n\n"
            f"User trip details:\n"
            f"- Destination: {td['destination']}\n"
            f"- Travel dates: {td['travel_from']} to {td['travel_to']}\n"
            f"- Travel experience preference: {td['travel_experience']}\n"
            f"- Spending level: {td['spend_level']}\n\n"
            "Provide recommendations that match these preferences."
        )

    def get_trip_details(self) -> str:
        message: Messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt()},
        ]

        response = PromptOpenAI(message, "gpt-4o-mini", self.get_tools()).get_response()
        if not response:
            raise ValueError("No response received from OpenAI API.")
        return response