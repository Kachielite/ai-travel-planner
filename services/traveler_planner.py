from models.open_ai import OpenAIModel
from schemas.trip_details import TripDetails
from tools.image import ImageGenerator
from tools.weather import WeatherTool


class TravelPlanner:
    def __init__(self, trip_details: TripDetails):
        self.trip_details = trip_details

    @staticmethod
    def get_system_prompt() -> str:
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
        return system_prompt

    def create_user_prompt(self) -> str:
        return f"""
        Create a detailed travel plan with the following requirements:

        - Destination: {self.trip_details.destination}
        - Travel dates: From {self.trip_details.travel_from} to {self.trip_details.travel_to}
        - Experience type: {self.trip_details.travel_experience}
        - Budget level: {self.trip_details.spend_level}

        Please provide:
        1. A day-by-day itinerary
        2. Recommended accommodations based on budget
        3. Must-see attractions and activities
        4. Local cuisine recommendations
        5. Transportation options
        6. Budget breakdown
        7. Packing suggestions
        8. Important travel tips
        """

    def generate_travel_plan(self) -> str:
        print("Generating travel plan...")
        try:
            user_prompt = self.create_user_prompt()
            system_prompt = self.get_system_prompt()
            tools = [{"type": "function", "function": WeatherTool.get_tool_description()},
                     {"type": "function", "function": ImageGenerator.get_tool_description()}]

            response = OpenAIModel.initialize_client().chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.7,
                tools=tools,
            )

            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise Exception("No response received from OpenAI API")

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
