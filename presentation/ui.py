from typing import Callable
import gradio as gr
from datetime import datetime, date


class UI:
    prompt_function: Callable[[str, str, str, str, str], str]

    def __init__(self, prompt_function: Callable[[str, str, str, str, str], str]):
        self.prompt_function = prompt_function

    def validate_and_process(self, destination, travel_from, travel_to, experience, spend_level):
        """Validate inputs before calling the main prompt function"""
        errors = []

        # Validate destination
        if not destination or not destination.strip():
            errors.append("Destination city is required")

        # Validate date strings and convert them
        travel_from_date = None
        travel_to_date = None

        if not travel_from or not travel_from.strip():
            errors.append("Travel start date is required")
        else:
            try:
                travel_from_date = datetime.strptime(travel_from.strip(), "%Y-%m-%d").date()
            except ValueError:
                errors.append("Travel start date must be in YYYY-MM-DD format")

        if not travel_to or not travel_to.strip():
            errors.append("Travel end date is required")
        else:
            try:
                travel_to_date = datetime.strptime(travel_to.strip(), "%Y-%m-%d").date()
            except ValueError:
                errors.append("Travel end date must be in YYYY-MM-DD format")

        # Validate date logic if both dates are valid
        if travel_from_date and travel_to_date:
            # Check if end date is after start date
            if travel_to_date <= travel_from_date:
                errors.append("Travel end date must be after start date")

            # Check if start date is not in the past
            today = date.today()
            if travel_from_date < today:
                errors.append("Travel start date cannot be in the past")

        if errors:
            error_message = "**Validation Errors:**\n" + "\n".join(f"- {error}" for error in errors)
            return error_message

        # Call the original prompt function with validated inputs
        return self.prompt_function(destination.strip(), travel_from.strip(), travel_to.strip(), experience, spend_level)

    def launch(self):
        view = gr.Interface(
            fn=self.validate_and_process,
            inputs=[
                gr.Textbox(label="Destination city", placeholder="e.g., Paris, Tokyo, New York"),
                gr.Textbox(label="Travel from (YYYY-MM-DD)", placeholder="2024-12-25", info="Enter departure date"),
                gr.Textbox(label="Travel to (YYYY-MM-DD)", placeholder="2024-12-30", info="Enter return date"),
                gr.Dropdown(["adventurous", "relaxing", "cultural", "luxury"], label="Travel Experience"),
                gr.Dropdown(["budget", "average", "luxury"], label="Spend Level"),
            ],
            outputs=[gr.Markdown(label="Trip Plan")],
            flagging_mode="never",
            title="AI Travel Planner",
            description="Plan your perfect trip with AI assistance. Please fill in all fields to get started."
        )
        return view.launch()