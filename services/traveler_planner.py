from models.open_ai import OpenAIModel
from models.ollama import Ollama
from schemas.trip_details import TripDetails
from tools.image import ImageGenerator
from tools.weather import WeatherTool
import base64
from io import BytesIO
import re, json


class TravelPlanner:
    def __init__(self, trip_details: TripDetails):
        self.trip_details = trip_details

    @staticmethod
    def get_system_prompt() -> str:
        return (
            "You are a helpful travel planner. Provide accurate, concise, easy-to-understand recommendations.\n\n"
            "TOOLS AVAILABLE:\n"
            "1) Weather Tool – get forecast for the destination and trip dates.\n"
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
            "7. **Budget breakdown** (approximate, in US dollars)\n"
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


    def parse_ollama_tool_call(self, response):
        weather = None
        image = None
        match = re.search(r'\{\s*"tool_call".*?\}', str(response), re.DOTALL)
        if match:
            try:
                tool_call_json = json.loads(match.group(0))
                tool_call = tool_call_json.get("tool_call")

                tool_name = tool_call.get('name')
                tool_args = tool_call.get('arguments', {})

                if tool_name == "get_weather":
                    weather_tool = WeatherTool(
                        destination_city=tool_args.get("destination_city"),
                        travel_from=tool_args.get("travel_from")
                    )
                    weather = weather_tool.get_weather()
                elif tool_name == "generate_image":
                    image_tool = ImageGenerator(
                        destination_city=tool_args.get("destination_city"),
                        trip_dates=tool_args.get("trip_dates")
                    )
                    image = image_tool.generate_image()
                    # Convert PIL image to base64 string
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    weather = f"![{tool_args['destination_city']}]('data:image/png;base64,{img_str}')"
            except Exception:
                return None
        return weather, image

    def extract_content(self, resp):
        if not resp:
            return None
        if isinstance(resp, dict):
            # Ollama OpenAI-compatible /chat endpoint often returns {'message': {'role': 'assistant', 'content': '...'}, ...}
            if 'message' in resp and isinstance(resp['message'], dict):
                return resp['message'].get('content')
            # Fallback: some wrappers may put content at top-level
            if 'content' in resp:
                return resp.get('content')
        return None

    def generate_travel_plan(self):
        get_messages = self.get_message()
        get_tools = self.get_tools()
        model_choice = getattr(self.trip_details, 'model', 'openai').lower()


        if model_choice == 'ollama':
            # First call to Ollama with initial user + system prompt
            ollama_instance = Ollama(get_messages)
            response = ollama_instance.initialize_client()

            assistant_content = self.extract_content(response)
            if assistant_content:
                get_messages.append({"role": "assistant", "content": assistant_content})

            # Try to detect tool call instructions embedded in response
            weather_result, image_result = self.parse_ollama_tool_call(response)

            tool_messages_added = False
            if weather_result:
                # Append weather tool output
                get_messages.append({
                    "role": "tool",
                    "content": json.dumps(weather_result),
                    "tool_call_id": "ollama-weather-1"
                })
                tool_messages_added = True
            if image_result:
                # image_result already markdown
                get_messages.append({
                    "role": "tool",
                    "content": image_result,
                    "tool_call_id": "ollama-image-1"
                })
                tool_messages_added = True

            if tool_messages_added:
                # Second call so model can incorporate tool outputs into final plan
                ollama_instance = Ollama(get_messages)
                final_response = ollama_instance.initialize_client()
                final_content = self.extract_content(final_response)
                return final_content or final_response
            else:
                return assistant_content or response
        else:
            # Default to OpenAI
            response = OpenAIModel.initialize_client().chat.completions.create(
                model="gpt-4o-mini",
                messages=get_messages,
                tools=get_tools,
                max_tokens=2000,
                temperature=0.7
            )

            if not response.choices:
                return "No response from the model. Please check the model configuration and try again."\

            message = response.choices[0].message
            updated_response = self.handle_tool(message)

            if not updated_response:
                return "No tools were called in the response. Please check the model's output."\

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
