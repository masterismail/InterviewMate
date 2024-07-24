from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# Fetch the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    print("Warning: OPENAI_API_KEY is not set. Some functionality may be limited.")
    client = None

@app.route('/')
def index():
    return "Welcome to the Poem Generator API. Use the /generate-poem endpoint to generate a poem."

@app.route('/generate-poem', methods=['POST'])
def generate_poem():
    if client is None:
        return jsonify({'error': 'OpenAI client is not configured'}), 500

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