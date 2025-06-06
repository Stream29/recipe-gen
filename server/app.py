import os
import json
import tempfile
from flask import Flask, request, jsonify, send_file, render_template, Response, stream_with_context

# Import the core functionality from the app package
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.recipe_generator import RecipeGenerator
from app.tts_service import TTSService

# Initialize Flask app
app = Flask(__name__, 
            static_folder='../frontend/static',
            template_folder='../frontend/templates')

# Initialize services
recipe_generator = RecipeGenerator()
tts_service = TTSService()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    """
    Handle favicon.ico requests.
    Return a 204 No Content response to prevent 404 errors.
    """
    return '', 204

@app.route('/api/generate-recipe', methods=['POST'])
def generate_recipe():
    """
    Generate a recipe based on the provided ingredients and preferences.

    Expected JSON payload:
    {
        "ingredients": ["ingredient1", "ingredient2", ...],
        "dietary_preference": "optional preference",
        "goal": "optional goal"
    }
    """
    try:
        data = request.json
        ingredients = data.get('ingredients', [])
        dietary_preference = data.get('dietary_preference')
        goal = data.get('goal')

        if not ingredients:
            return jsonify({"error": "No ingredients provided"}), 400

        recipe = recipe_generator.generate_recipe(
            ingredients=ingredients,
            dietary_preference=dietary_preference,
            goal=goal
        )

        return jsonify(recipe)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stream-recipe', methods=['POST'])
def stream_recipe():
    """
    Stream a recipe generation response.

    Expected JSON payload:
    {
        "ingredients": ["ingredient1", "ingredient2", ...],
        "dietary_preference": "optional preference",
        "goal": "optional goal"
    }
    """
    try:
        data = request.json
        ingredients = data.get('ingredients', [])
        dietary_preference = data.get('dietary_preference')
        goal = data.get('goal')

        if not ingredients:
            return jsonify({"error": "No ingredients provided"}), 400

        def generate():
            for chunk in recipe_generator.generate_recipe(
                ingredients=ingredients,
                dietary_preference=dietary_preference,
                goal=goal,
                stream=True
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        return Response(stream_with_context(generate()), 
                       content_type='text/event-stream')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech and return the audio URLs.

    Expected JSON payload:
    {
        "text": "Text to convert to speech",
        "voice": "optional voice name"
    }

    Returns:
    {
        "audio_urls": ["url1", "url2", ...] - List of audio URLs for each segment
    }
    """
    try:
        data = request.json
        text = data.get('text', '')
        voice = data.get('voice', 'Ethan')

        if not text:
            return jsonify({"error": "No text provided"}), 400

        audio_urls = tts_service.text_to_speech(text=text, voice=voice)

        return jsonify({"audio_urls": audio_urls})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stream-tts', methods=['POST'])
def stream_tts():
    """
    Stream text-to-speech conversion.

    Expected JSON payload:
    {
        "text": "Text to convert to speech",
        "voice": "optional voice name"
    }
    """
    try:
        data = request.json
        text = data.get('text', '')
        voice = data.get('voice', 'Ethan')

        if not text:
            return jsonify({"error": "No text provided"}), 400

        def generate():
            for chunk in tts_service.text_to_speech(text=text, voice=voice, stream=True):
                yield chunk

        return Response(stream_with_context(generate()), 
                       content_type='audio/wav')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download-tts', methods=['POST'])
def download_tts():
    """
    Convert text to speech and provide a downloadable file.

    Expected JSON payload:
    {
        "text": "Text to convert to speech",
        "voice": "optional voice name"
    }
    """
    try:
        data = request.json
        text = data.get('text', '')
        voice = data.get('voice', 'Ethan')

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)

        try:
            # Generate the audio file
            tts_service.text_to_speech_file(text=text, output_path=temp_path, voice=voice)

            # Send the file
            return send_file(
                temp_path,
                as_attachment=True,
                download_name="recipe_audio.wav",
                mimetype="audio/wav"
            )
        finally:
            # Clean up the temporary file (this will execute after the response is sent)
            @app.after_request
            def remove_file(response):
                try:
                    os.remove(temp_path)
                except:
                    pass
                return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
