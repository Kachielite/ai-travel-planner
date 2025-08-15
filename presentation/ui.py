from typing import Callable
import gradio as gr
from datetime import datetime, date


class UI:
    prompt_function: Callable[[str, str, str, str, str, str], str]

    def __init__(self, prompt_function: Callable[[str, str, str, str, str, str], str]):
        self.prompt_function = prompt_function

    def validate_and_process(self, destination, travel_from, travel_to, experience, spend_level, model="gpt-4o-mini") -> str:
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

        # Call the prompt function and return the result directly (no streaming)
        return self.prompt_function(destination.strip(), travel_from.strip(), travel_to.strip(), experience, spend_level, model)

    def launch(self, share=False):
        with gr.Blocks(title="AI Travel Planner", css="""
            #travel-output {
                border-radius: 8px;
                background: rgba(255,255,255,0.1);
                color: white;
                font-family: 'Segoe UI', sans-serif;
                font-size: 1rem;
                border: none;
                padding: 1rem;
                min-height: 435px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                resize: none;
                overflow-y: auto;
            }
            #travel-output h1, #travel-output h2, #travel-output h3, #travel-output h4, #travel-output h5, #travel-output h6 {
                color: #ffd700;
            }
        """) as interface:
            gr.Markdown("# 🌍 AI Travel Planner")
            gr.Markdown("Plan your perfect trip with AI assistance!")

            with gr.Row():
                with gr.Column(scale=1):
                    destination = gr.Textbox(
                        label="🏙️ Destination city",
                        placeholder="e.g., Paris, Tokyo, New York"
                    )

                    with gr.Row():
                        travel_from = gr.Textbox(
                            label="📅 Travel from (YYYY-MM-DD)",
                            placeholder="2024-12-25"
                        )
                        travel_to = gr.Textbox(
                            label="📅 Travel to (YYYY-MM-DD)",
                            placeholder="2024-12-30"
                        )

                    experience = gr.Dropdown(
                        ["adventurous", "relaxing", "cultural", "luxury"],
                        label="🎯 Travel Experience"
                    )
                    spend_level = gr.Dropdown(
                        ["budget", "average", "luxury"],
                        label="💰 Spend Level"
                    )

                    with gr.Row():
                        model = gr.Dropdown(
                            ["gpt-4o-mini", "llama2"],
                            label="🤖 AI Model",
                            value="gpt-4o-mini"
                        )

                    submit_btn = gr.Button("🚀 Plan My Trip", variant="primary", size="lg")

                with gr.Column(scale=2):
                    with gr.Group(elem_classes=["travel-output"]):
                        output = gr.Markdown(
                            value="👋 Welcome! Fill in your travel details and click 'Plan My Trip' to get started.",
                            label="✈️ Your Travel Plan",
                            elem_id = "travel-output"
                        )

            submit_btn.click(
                fn=self.validate_and_process,
                inputs=[destination, travel_from, travel_to, experience, spend_level, model],
                outputs=[output],
                show_progress="full"  # show loading spinner during processing
            )

        return interface.launch(share=share)
