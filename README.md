# 🌍 AI Travel Planner

A sophisticated AI-powered travel planning application that demonstrates the implementation of OpenAI function calling (tools) with a modern web interface. This project showcases how to integrate multiple AI tools to create intelligent, context-aware applications.

## 🎯 Project Overview

The AI Travel Planner is designed as a learning project to demonstrate how to implement and use tools when calling Large Language Models (LLMs). It combines OpenAI's GPT-4 with function calling capabilities, real-time weather data, and image generation to create comprehensive travel plans.

### Key Features

- 🤖 **AI-Powered Planning**: Uses GPT-4o-mini with function calling for intelligent travel recommendations
- 🌤️ **Real-Time Weather Integration**: Fetches live weather data using OpenWeatherMap API
- 🎨 **AI Image Generation**: Creates destination images using DALL-E 3
- 🖥️ **Modern Web Interface**: Built with Gradio for an intuitive user experience
- 📝 **Structured Output**: Generates detailed, markdown-formatted travel plans
- ✅ **Input Validation**: Comprehensive form validation with date logic checks

## 🛠️ Technical Architecture

### Project Structure

```
AITravelPlanner/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── models/
│   └── open_ai.py        # OpenAI client configuration
├── presentation/
│   └── ui.py             # Gradio web interface
├── schemas/
│   ├── trip_details.py   # Pydantic data models
│   ├── currency.py       # Currency-related schemas
│   └── message.py        # Message schemas
├── services/
│   └── traveler_planner.py # Core travel planning logic
└── tools/
    ├── weather.py        # Weather API integration
    ├── image.py          # Image generation tool
    └── currency.py       # Currency conversion tool
```

### Key Components

#### 1. **Function Calling Implementation** (`services/traveler_planner.py`)
- Demonstrates proper OpenAI function calling setup
- Tool registration and execution handling
- Multi-turn conversation management with tool responses

#### 2. **Weather Tool** (`tools/weather.py`)
- OpenWeatherMap API integration
- Real-time weather forecasting
- Structured tool description for LLM function calling

#### 3. **Image Generation Tool** (`tools/image.py`)
- DALL-E 3 integration for destination visualization
- Weather-aware image prompting
- Base64 image handling for web display
- *Note: Currently commented out in the main flow to save API tokens, but feel free to uncomment and experiment with it!*

#### 4. **Web Interface** (`presentation/ui.py`)
- Gradio-based responsive UI
- Form validation and error handling
- Real-time travel plan generation

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- OpenWeatherMap API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AITravelPlanner
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPEN_WEATHER_API_KEY=your_openweather_api_key_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the web interface**
   
   Open your browser and navigate to the URL shown in the terminal (typically `http://localhost:7860`)

### API Keys Setup

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API keys section
4. Generate a new API key
5. Add it to your `.env` file

#### OpenWeatherMap API Key
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key
4. Add it to your `.env` file

## 💡 How It Works: Function Calling Implementation

This project is an excellent example of implementing OpenAI's function calling feature. Here's how it works:

### Why Tools Make AI Models More Powerful

Adding tools to Large Language Models transforms them from text generators into intelligent agents that can:

🔍 **Access Real-Time Data**: Instead of relying on training data that may be outdated, tools allow the AI to fetch current information like weather forecasts, stock prices, or news updates.

🎯 **Provide Accurate, Specific Information**: Rather than generating potentially hallucinated responses, tools enable the AI to retrieve factual data from authoritative sources.

⚡ **Perform Actions**: Tools extend AI capabilities beyond conversation to actually doing things - sending emails, booking appointments, making API calls, or processing data.

🧠 **Make Context-Aware Decisions**: By combining multiple tool outputs, AI can make more informed decisions. For example, our travel planner uses weather data to suggest appropriate activities and clothing.

🔄 **Create Dynamic Responses**: Tool outputs can influence the AI's reasoning process, leading to more relevant and personalized responses based on real-world conditions.

**Example in Our Project**: Without tools, the AI might suggest "pack light clothing for Cape Town in December" based on general knowledge. With weather tools, it can say "pack light clothing and a light jacket - the forecast shows 25°C with possible evening showers on December 26th."

### 1. Tool Definition
Each tool defines its schema using OpenAI's function calling format:

```python
@staticmethod
def get_tool_description() -> dict:
    return {
        "name": "get_weather",
        "description": "Get current weather for a specified city",
        "parameters": {
            "type": "object",
            "properties": {
                "destination_city": {"type": "string"},
                "travel_from": {"type": "string"}
            },
            "required": ["destination_city", "travel_from"]
        }
    }
```

### 2. Tool Registration
Tools are registered with the OpenAI API call:

```python
response = OpenAI().chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=get_tools(),  # Tools registered here
    max_tokens=2000
)
```

### 3. Tool Execution
When the LLM decides to use a tool, the application executes it and returns results:

```python
def handle_tool(self, message):
    for tool_call in message.tool_calls:
        if tool_call.function.name == "get_weather":
            weather_tool = WeatherTool(...)
            weather_data = weather_tool.get_weather()
            # Return structured response back to LLM
```

### 4. Multi-turn Conversation
The application manages the conversation flow, allowing the LLM to use tool results in its final response.

## 🎨 Features Showcase

### Travel Plan Generation
- **Intelligent Itineraries**: Day-by-day plans based on preferences
- **Weather-Aware Recommendations**: Activities adjusted for forecasted conditions
- **Budget-Conscious Suggestions**: Recommendations matched to spending level
- **Local Insights**: Cuisine, transportation, and cultural tips

### Sample Output

Here's an example of a travel plan generated by the AI Travel Planner:

<details>
<summary>🇿🇦 Cape Town Adventure Travel Plan (Click to expand)</summary>

# Cape Town Adventure Travel Plan

## Trip Overview
**Season:** Summer in Cape Town (December)  
**Weather Expectations:** Warm and sunny days, with average temperatures ranging from 20°C to 30°C (68°F to 86°F). Occasional light showers possible but generally dry.

## Day-by-Day Itinerary

### Day 1: Arrival (2025-12-25)
**Morning:**
- Arrive at Cape Town International Airport
- Check-in at accommodation

**Afternoon:**
- Explore the V&A Waterfront
- Take a ride on the Cape Wheel for stunning views

**Evening:**
- Dinner at a local budget-friendly eatery like The V&A Waterfront Food Market

### Day 2: Table Mountain & Beaches (2025-12-26)
**Morning:**
- Hike up Table Mountain or take the cable car (budget option)

**Afternoon:**
- Relax at Clifton Beach or Camps Bay

**Evening:**
- Sunset at the beach with a picnic dinner

### Day 3: Adventure in Nature (2025-12-27)
**Morning:**
- Day trip to Cape Point and Cape of Good Hope

**Afternoon:**
- Go for a hike along the trails for breathtaking views

**Evening:**
- Return to the city and dinner at Kalk Bay (try local fish)

### Day 4: Winelands Exploration (2025-12-28)
**Morning:**
- Visit the Stellenbosch or Franschhoek wine regions

**Afternoon:**
- Wine tasting at budget-friendly vineyards

**Evening:**
- Dinner at a local bistro in Stellenbosch

### Day 5: Departure (2025-12-29)
**Morning:**
- Last-minute shopping at Greenmarket Square

**Afternoon:**
- Check out of accommodation and depart for the airport

## Accommodations
**Budget Options:**
- The Backpack: Affordable hostel with a social vibe
- Mojo Hotel: Vibrant atmosphere near the beach
- Cape Town Lodge: Budget hotel with convenient access to attractions

## Must-See Attractions & Activities
- **Table Mountain:** Iconic flat-topped mountain
- **Cape of Good Hope:** Stunning coastal views and hiking trails
- **Boulders Beach:** Famous for its penguin colony
- **V&A Waterfront:** Shopping, dining, and entertainment

## Local Cuisine Suggestions
- **Bunny Chow:** A hollowed-out loaf filled with curry
- **Bobotie:** A Cape Malay dish with spiced minced meat
- **Braai:** South African barbecue, try it at a local eatery
- **Koeksisters:** Sweet, syrupy pastries for dessert

## Transportation within the City
- **MyCiTi Bus:** Affordable public transport option for getting around
- **Uber:** Convenient and budget-friendly for rides
- **Bicycles:** Rent bikes for exploring the waterfront and nearby areas

## Budget Breakdown (Approximate)
- **Accommodation:** ZAR 500/night (ZAR 2000 total)
- **Food:** ZAR 200/day (ZAR 800 total)
- **Activities:** ZAR 600 total (including hikes and entrance fees)
- **Transportation:** ZAR 400 total
- **Total Estimated Budget:** ZAR 3800

## Packing List
**Clothing:**
- Lightweight, breathable clothing
- Swimsuit
- Hiking shoes
- Sunhat and sunglasses

**Essentials:**
- Sunscreen
- Reusable water bottle
- Backpack for day trips

**Miscellaneous:**
- Camera for capturing memories

## Important Travel Tips
- **Safety:** Keep valuables secure, especially in crowded areas
- **Etiquette:** Greet locals with a friendly "hello" and respect cultural customs
- **Weather Notes:** Stay hydrated and wear sunscreen due to the strong sun

Enjoy your adventurous trip to Cape Town! 🌍✈️🏞️

</details>

### User Experience
- **Input Validation**: Date logic, required fields, and format checking
- **Visual Feedback**: Loading indicators and error messages
- **Responsive Design**: Works on desktop and mobile devices
- **Rich Output**: Markdown-formatted plans with emojis and structure

## 📚 Learning Objectives

This project demonstrates:

1. **Function Calling Setup**: How to properly configure and use OpenAI's function calling
2. **Tool Integration**: Connecting external APIs as AI tools
3. **Error Handling**: Robust error management for API calls and validation
4. **UI Development**: Building user-friendly interfaces for AI applications
5. **Data Validation**: Using Pydantic for type safety and validation
6. **API Integration**: Working with multiple external services
7. **Conversation Management**: Handling multi-turn AI conversations with tools

## 🔧 Dependencies

- **openai>=1.0.0**: OpenAI API client for GPT and DALL-E
- **gradio>=4.0.0**: Web interface framework
- **python-dotenv>=1.0.0**: Environment variable management
- **pydantic>=2.0.0**: Data validation and settings management
- **requests>=2.31.0**: HTTP requests for API calls
- **pillow~=11.3.0**: Image processing for DALL-E integration
- **pyowm~=3.3.0**: OpenWeatherMap API client

## 🤝 Contributing

This project is designed for learning purposes. Feel free to:

- Add new tools (currency conversion, flight booking, etc.)
- Improve the UI design
- Add more sophisticated error handling
- Implement streaming responses
- Add unit tests

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Support

If you encounter any issues or have questions about implementing function calling with OpenAI:

1. Check the [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
2. Review the code comments and implementation examples
3. Open an issue in this repository

---

**Happy Learning and Safe Travels! 🧳✈️**
