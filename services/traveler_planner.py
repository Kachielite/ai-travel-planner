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
        return (
            "You are a helpful travel planner. Provide accurate, concise, easy-to-understand recommendations.\n\n"
            "TOOLS AVAILABLE:\n"
            "1) Weather Tool – get forecast for the destination and trip dates.\n"
            "RESPONSE RULES:\n"
            "- Output in **Markdown** with clear headings, subheadings, bullets, and emojis where helpful.\n"
            "- If unsure, say so."
        )

    def create_user_prompt(self) -> str:
        return (
            f"You are an expert AI travel planner. Create a visually rich **Markdown** travel plan for:\n\n"
            f"- **Destination:** {self.trip_details.destination}\n"
            f"- **Travel Dates:** {self.trip_details.travel_from} to {self.trip_details.travel_to}\n"
            f"- **Experience Type:** {self.trip_details.travel_experience}\n"
            f"- **Budget Level:** {self.trip_details.spend_level}\n\n"
            "### What to include\n"
            "1. **Trip Overview** (season & weather expectations from the provided forecast; do not include raw data URIs)\n"
            "2. **Day-by-day itinerary** (morning/afternoon/evening)\n"
            "3. **Accommodations** matched to budget\n"
            "4. **Must-see attractions & activities** (short notes)\n"
            "5. **Local cuisine** suggestions\n"
            "6. **Transportation** within the city\n"
            "7. **Budget breakdown** (approximate, local currency)\n"
            "8. **Packing list** tailored to season/activities\n"
            "9. **Important travel tips** (safety, etiquette, weather notes)\n\n"
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
