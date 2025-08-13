from models.open_ai import OpenAIModel
from schemas.trip_details import TripDetails
from tools.image import ImageGenerator
from tools.weather import WeatherTool
import json
import base64
from io import BytesIO


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
        return (
            f"Create a detailed travel plan with the following requirements:\n\n"
            f"- Destination: {self.trip_details.destination}\n"
            f"- Travel dates: From {self.trip_details.travel_from} to {self.trip_details.travel_to}\n"
            f"- Experience type: {self.trip_details.travel_experience}\n"
            f"- Budget level: {self.trip_details.spend_level}\n\n"
            "Please provide:\n"
            "1. A day-by-day itinerary\n"
            "2. Recommended accommodations based on budget\n"
            "3. Must-see attractions and activities\n"
            "4. Local cuisine recommendations\n"
            "5. Transportation options\n"
            "6. Budget breakdown\n"
            "7. Packing suggestions\n"
            "8. Important travel tips"
        )

    def get_message(self):
        system_prompt = self.get_system_prompt()
        user_prompt = self.create_user_prompt()

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def get_tools(self):
        return [
            {"type": "function", "function": WeatherTool.get_tool_description()},
            {"type": "function", "function": ImageGenerator.get_tool_description()}
        ]

    def handle_tool(self, message):
        response = []
        tool_calls = message.tool_calls

        if not tool_calls:
            return None

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if tool_name == "get_weather":
                weather_tool = WeatherTool(
                    destination_city=tool_args["destination_city"],
                    travel_from=tool_args["travel_from"]
                )
                weather = weather_tool.get_weather()
                response.append({
                    "role": "tool",
                    "content": json.dumps(weather),
                    "tool_call_id": tool_call.id,
                })
            elif tool_name == "generate_image":
                image_tool = ImageGenerator(
                    destination_city=tool_args["destination_city"],
                    trip_dates=tool_args["trip_dates"]
                )
                image = image_tool.generate_image()
                # Convert PIL image to base64 string
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                markdown_img = f"![{tool_args['destination_city']}]('data:image/png;base64,{img_str}')"
                response.append({
                    "role": "tool",
                    "content": markdown_img,
                    "tool_call_id": tool_call.id,
                })
            else:
                print(f"Unknown tool call: {tool_name}")

        return response

    def generate_travel_plan(self):
        get_messages = self.get_message()
        get_tools = self.get_tools()

        response = OpenAIModel.initialize_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=get_messages,
            tools=get_tools,
            max_tokens=2000,
            temperature=0.7
        )

        if not response.choices:
            return "No response from the model. Please check the model configuration and try again."

        message = response.choices[0].message
        updated_response = self.handle_tool(message)

        if not updated_response:
            return "No tools were called in the response. Please check the model's output."

        get_messages.append({"role": "assistant", "content": message.content, "tool_calls": message.tool_calls})
        get_messages.extend(updated_response)

        travel_plan = OpenAIModel.initialize_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=get_messages,
            max_tokens=2000,
            temperature=0.7,
            stream=False
        )

        if travel_plan.choices and travel_plan.choices[0].message:
            return travel_plan.choices[0].message.content
        return "No travel plan generated."
