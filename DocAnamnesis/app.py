from flask import Flask, render_template, request, jsonify, url_for
from src import Anamnesis
from src import TTS
import os
app = Flask(__name__)
AUDIO_FOLDER = 'static/audio'

initial_greetings = ["Hello, what seems to be the issue today?",
"Good morning! How can I assist you with your health today?",
"Hi, what brings you to see me today?",
"Hello! What can I help you with today?",
"Good afternoon. What concerns do you have that you'd like to discuss?",
"Hi there! How can I support your health today?",
"Hello, what has brought you in today?",
"Good morning! How are you feeling, and what can I do for you?",
"Hi! What’s been bothering you that you'd like me to check out?",
"Good day. How can I be of assistance with your health concerns today?"]

@app.route('/')
def index():
    return render_template('index.html')

anamnesis = Anamnesis.Anamnesis()
last_question = ""
base_model = "gpt-4o-mini"

@app.route('/chat', methods=['POST'])
def chat():
    global last_question
    global base_model
    global anamnesis
    data = request.get_json()
    #last_question = data.get('last_question')
    answer = data.get('answer')
    model = data.get('model')

    if model and model != base_model:
        base_model = model
        # You might need to reinitialize the Anamnesis instance based on the model
        anamnesis = Anamnesis.Anamnesis(model=base_model)  # Pass the selected model if required


    # Process the customer's response and decide the next step
    result = anamnesis.process_response(last_question, answer)
    last_question = result['content']

    audio_filename = f"{AUDIO_FOLDER}/{result['type']}_response.mp3"
    with open(audio_filename, 'wb') as audio_file:
        audio_file.write(TTS.generate_audio(result['content']).getbuffer())

    # Include audio file URL in JSON response
    audio_url = url_for('static', filename=f'audio/{result["type"]}_response.mp3', _external=True)

    # Format and return the response to the web app
    if result['type'] == 'diagnosis':
        return jsonify({
            "message": "Diagnosis",
            "diagnosis": result['content'],
            "audio_url": audio_url
        })
    elif result['type'] == 'question':
        return jsonify({
            "message": "Next Question",
            "question": result['content'],
            "audio_url": audio_url
        })


if __name__ == '__main__':

    # check if the audio folder exists
    if not os.path.exists(AUDIO_FOLDER):
        os.makedirs(AUDIO_FOLDER)

    app.run(debug=True)
