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
    return "Welcome to the Poem Generator API. Use the /generate-poem, /take-description, /new-questions, or /analyze endpoints."

@app.route('/generate-poem', methods=['POST'])
def generate_poem():
    if client is None:
        return jsonify({'error': 'OpenAI client is not configured'}), 500

    data = request.get_json()

    if not data or 'prompt' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    prompt = data['prompt']

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
                {"role": "user", "content": prompt}
            ]
        )

        return jsonify({
            'message': response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/take-description', methods=['POST'])
def take_description():
    if client is None:
        return jsonify({'error': 'OpenAI client is not configured'}), 500

    data = request.get_json()

    if not data or 'description' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    description = data['description']

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an interviewer who is skilled at conducting interviews based on the description provided."},
                {"role": "user", "content": f"Based on the description '{description}', provide the top 5 questions to start an interview."}
            ]
        )

        return jsonify({
            'questions': response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/new-questions', methods=['POST'])
def new_questions():
    if client is None:
        return jsonify({'error': 'OpenAI client is not configured'}), 500

    data = request.get_json()

    if not data or 'conversations' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    conversations = data['conversations']

    # Map roles to OpenAI's supported values
    role_mapping = {
        "interviewer": "user",
        "applicant": "assistant"
    }

    # Ensure conversations is a list of dicts with 'role' and 'text'
    if not isinstance(conversations, list) or any('role' not in item or 'text' not in item for item in conversations):
        return jsonify({'error': 'Invalid input format'}), 400

    try:
        messages = [{"role": "system", "content": "You are an interviewer with context from the following conversation."}]
        for conversation in conversations:
            role = role_mapping.get(conversation['role'], "user")  # Default to "user" if role is unknown
            messages.append({"role": role, "content": conversation['text']})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages + [
                {"role": "user", "content": "Based on the given context, provide additional questions to ask in this interview."}
            ]
        )

        return jsonify({
            'questions': response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    if client is None:
        return jsonify({'error': 'OpenAI client is not configured'}), 500

    data = request.get_json()

    if not data or 'conversations' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    conversations = data['conversations']

    # Map roles to OpenAI's supported values
    role_mapping = {
        "interviewer": "user",
        "applicant": "assistant"
    }

    # Ensure conversations is a list of dicts with 'role' and 'text'
    if not isinstance(conversations, list) or any('role' not in item or 'text' not in item for item in conversations):
        return jsonify({'error': 'Invalid input format'}), 400

    try:
        messages = [{"role": "system", "content": "You are an interviewer with context from the following conversation. Provide an analysis with the following parameters: overall rating, technical skills, communication, cultural fit, and a summary."}]
        for conversation in conversations:
            role = role_mapping.get(conversation['role'], "user")  # Default to "user" if role is unknown
            messages.append({"role": role, "content": conversation['text']})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages + [
                {"role": "user", "content": "Based on the given context, provide an analysis with the following parameters: overall rating, technical skills, communication, cultural fit, and a short summary of 3-4 lines."}
            ]
        )

        return jsonify({
            'analysis': response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
