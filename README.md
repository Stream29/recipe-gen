# Recipe Generator and Nutrition Analyzer

A Python application that uses a Language Learning Model (LLM) to generate cooking recipes based on user-specified ingredients and dietary preferences. The application also analyzes the nutritional content of the recipes and offers suggestions for modifications.

## Features

- Generate recipes based on available ingredients
- Specify dietary preferences (e.g., low-carb, vegan)
- Set nutritional goals (e.g., muscle gain, weight loss)
- Get nutritional analysis of recipes
- Listen to recipes as audio using text-to-speech

## Project Structure

```
recipe-gen/
├── app/                    # Core application logic
│   ├── recipe_generator.py # Recipe generation using LLM
│   └── tts_service.py      # Text-to-speech conversion
├── server/                 # Flask server
│   └── app.py              # Server implementation
├── frontend/               # Frontend UI
│   ├── templates/          # HTML templates
│   │   └── index.html      # Main page
│   └── static/             # Static resources
│       ├── css/            # CSS styles
│       │   └── style.css   # Main stylesheet
│       └── js/             # JavaScript
│           └── script.js   # Client-side functionality
├── api-example/            # Example API usage
├── main.py                 # Application entry point
└── README.md               # This file
```

## Prerequisites

- Python 3.8 or higher
- DashScope API key (for LLM and TTS)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/recipe-gen.git
   cd recipe-gen
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your DashScope API key:
   ```
   # On Windows
   set DASHSCOPE_API_KEY=your_api_key_here
   
   # On macOS/Linux
   export DASHSCOPE_API_KEY=your_api_key_here
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Enter your ingredients, dietary preferences, and nutritional goals, then click "Generate Recipe".

4. View the generated recipe, nutritional information, and suggestions.

5. Click "Play Recipe Audio" to listen to the recipe.

## API Endpoints

- `POST /api/generate-recipe`: Generate a recipe based on ingredients and preferences
- `POST /api/stream-recipe`: Stream a recipe generation response
- `POST /api/text-to-speech`: Convert text to speech and return an audio URL
- `POST /api/stream-tts`: Stream text-to-speech conversion
- `POST /api/download-tts`: Convert text to speech and provide a downloadable file

## License

This project is licensed under the MIT License - see the LICENSE file for details.