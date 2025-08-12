from presentation.ui import UI
from schemas.trip_details import TripDetails
from services.traveler_planner import TravelPlanner


class App:
    def __init__(self):
        self.ui = UI(self.plan_trip)

    def plan_trip(self, destination: str, travel_from: str, travel_to: str,
                experience: str, spend_level: str) -> str:
        try:
            trip_details = TripDetails(
                destination=destination,
                travel_from=travel_from,
                travel_to=travel_to,
                travel_experience=experience,
                spend_level=spend_level
            )

            travel_planner = TravelPlanner(trip_details)

            response = travel_planner.generate_travel_plan()

            return response

        except Exception as e:
            return self._format_error_message(str(e))

    def _format_error_message(self, error: str) -> str:
        return (
            f"**Error:** An error occurred while planning your trip: {error}\n\n"
            "Please try again or check your inputs."
        )

    def start(self) -> None:
        print("🌍 Starting AI Travel Planner...")
        print("🚀 Launching Gradio interface...")
        self.ui.launch()


def main():
    app = App()
    app.start()


if __name__ == "__main__":
    main()
