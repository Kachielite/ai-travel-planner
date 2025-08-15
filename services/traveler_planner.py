from models.open_ai import OpenAIModel
from models.ollama import Ollama
from schemas.trip_details import TripDetails
from tools.image import ImageGenerator
from tools.weather import WeatherTool
import base64
from io import BytesIO
import json
from typing import cast


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

    def extract_content(self, resp):
        if not resp:
            return None
        if isinstance(resp, dict):
            if 'message' in resp and isinstance(resp['message'], dict):
                return resp['message'].get('content')
            if 'content' in resp:
                return resp.get('content')
        return None

    @staticmethod
    def _ensure_text(value):
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, ensure_ascii=False, indent=2)
        except Exception:
            return str(value)

    def generate_travel_plan(self):
        get_messages = cast(list, self.get_message())
        get_tools = self.get_tools()
        model_choice = getattr(self.trip_details, 'model', 'openai').lower()

        # Step 1: Prepare tool-aware prompt
        if model_choice == 'llama2':
            tools_text = "\n\nTOOLS AVAILABLE:\n" + json.dumps(get_tools, indent=2)
            get_messages[0]["content"] += tools_text
            get_messages[0]["content"] += (
                "\n\nIf you need to use a tool, respond ONLY with JSON in the format:\n"
                '{"tool": "<tool_name>", "arguments": { ... }}\n'
                "Otherwise, respond with your final travel plan in Markdown."
            )

        updated_response = None  # This will hold tool execution results

        # Step 2: First model call
        if model_choice == 'gpt-4o-mini':
            response = OpenAIModel.initialize_client().chat.completions.create(
                model="gpt-4o-mini",
                messages=get_messages,
                tools=get_tools,
                max_tokens=2000,
                temperature=0.7
            )
            if not response.choices:
                return "No response from the model. Please check the configuration."

            message = response.choices[0].message

            tool_calls_payload = None
            if getattr(message, "tool_calls", None):
                tool_calls_payload = []
                for tc in message.tool_calls:
                    tool_calls_payload.append({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    })

            get_messages.append({
                "role": "assistant",
                "content": message.content or "",
                **({"tool_calls": tool_calls_payload} if tool_calls_payload else {})
            })

            updated_response = self.handle_tool(message)

        else:  # llama2
            ollama_instance = Ollama(get_messages)
            response = ollama_instance.initialize_client()

            first_reply = None
            if isinstance(response, dict):
                # Ollama chat mode
                if "message" in response and isinstance(response["message"], dict):
                    first_reply = response["message"].get("content", "")
                # Ollama generate mode (usually returns "response")
                elif "response" in response:
                    first_reply = response["response"]

            first_reply = first_reply or ""

            get_messages.append({"role": "assistant", "content": first_reply})

            try:
                tool_call = json.loads(first_reply)
                if isinstance(tool_call, dict) and "tool" in tool_call:
                    message = type("ToolMessage", (), {
                        "tool_calls": [
                            type("ToolCall", (), {
                                "function": type("Function", (), {
                                    "name": tool_call["tool"],
                                    "arguments": json.dumps(tool_call["arguments"])
                                }),
                                "id": "ollama-tool-1"
                            })
                        ]
                    })
                    updated_response = self.handle_tool(message)
                else:
                    return self._ensure_text(first_reply)
            except json.JSONDecodeError:
                return self._ensure_text(first_reply)

        # Step 3: If tool was called, run second round
        if updated_response:
            get_messages.extend(updated_response)
            if model_choice == 'gpt-4o-mini':
                travel_plan = OpenAIModel.initialize_client().chat.completions.create(
                    model="gpt-4o-mini",
                    messages=get_messages,
                    max_tokens=2000,
                    temperature=0.7
                )
                if travel_plan.choices and travel_plan.choices[0].message:
                    return self._ensure_text(travel_plan.choices[0].message.content)
            else:
                ollama_instance = Ollama(get_messages)
                final_response = ollama_instance.initialize_client()
                return self._ensure_text(final_response.get("choices", [{}])[0].get("message", {}).get("content", ""))

        return "No travel plan generated."
