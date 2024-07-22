from flask import Flask, request, jsonify
import os
from openai import OpenAI

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
 
# Fetch the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

if OPENAI_API_KEY is None:
    raise ValueError("The OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")

# Set up OpenAI API key

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the Poem Generator API. Use the /generate-poem endpoint to generate a poem."

@app.route('/generate-poem', methods=['POST'])
def generate_poem():
    data = request.get_json()

    if not data or 'prompt' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    prompt = data['prompt']

    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
            {"role": "user", "content": prompt}
        ])

        return jsonify({
            'message': response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
