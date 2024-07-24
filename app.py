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
                {"role": "user", "content": f"Based on the description '{description}', provide the top 5 questions to start an interview. Format each question as 'Question X: [The question]'."}
            ]
        )

        questions = response.choices[0].message.content.split('\n')
        formatted_questions = {}
        for question in questions:
            if ':' in question:
                key, value = question.split(':', 1)
                formatted_questions[key.strip()] = value.strip()

        return jsonify(formatted_questions)

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

    role_mapping = {
        "interviewer": "user",
        "applicant": "assistant"
    }

    if not isinstance(conversations, list) or any('role' not in item or 'text' not in item for item in conversations):
        return jsonify({'error': 'Invalid input format'}), 400

    try:
        messages = [{"role": "system", "content": "You are an interviewer with context from the following conversation."}]
        for conversation in conversations:
            role = role_mapping.get(conversation['role'], "user")
            messages.append({"role": role, "content": conversation['text']})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages + [
                {"role": "user", "content": "Based on the given context, provide 5 additional questions to ask in this interview. Format each question as 'Question X: [The question]'."}
            ]
        )

        questions = response.choices[0].message.content.split('\n')
        formatted_questions = {}
        for question in questions:
            if ':' in question:
                key, value = question.split(':', 1)
                formatted_questions[key.strip()] = value.strip()

        return jsonify(formatted_questions)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    if client is None:
        return jsonify({'error': 'OpenAI client is not configured'}), 500

    data = request.get_json()

    if not data or 'conversations' not in data:
        return jsonify({'error': 'Invalid input: conversations missing'}), 400

    conversations = data['conversations']

    role_mapping = {
        "interviewer": "user",
        "applicant": "assistant"
    }

    if not isinstance(conversations, list) or any('role' not in item or 'text' not in item for item in conversations):
        return jsonify({'error': 'Invalid input format: conversations must be a list of dicts with "role" and "text" keys'}), 400

    try:
        messages = [{"role": "system", "content": "You are an interviewer analyzing the following conversation. Provide an analysis with four sections: 1) Overall rating, 2) Technical skills, 3) Communication skills, and 4) Cultural fit. For each section, provide a rating out of 10 and a brief comment."}]
        for conversation in conversations:
            role = role_mapping.get(conversation['role'], "user")
            messages.append({"role": role, "content": conversation['text']})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages + [
                {"role": "user", "content": "Please provide the analysis as requested, formatting your response exactly as follows:\nOverall Rating: [X/10]\nOverall Comment: [Your comment here]\nTechnical Skills Rating: [Y/10]\nTechnical Skills Comment: [Your comment here]\nCommunication Skills Rating: [Z/10]\nCommunication Skills Comment: [Your comment here]\nCultural Fit Rating: [W/10]\nCultural Fit Comment: [Your comment here]"}
            ]
        )

        analysis = response.choices[0].message.content
        lines = analysis.split('\n')

        def extract_rating_and_comment(lines, prefix):
            rating = "N/A"
            comment = "No comment provided"
            for line in lines:
                if line.startswith(f"{prefix} Rating:"):
                    rating = line.split(':')[1].strip()
                elif line.startswith(f"{prefix} Comment:"):
                    comment = line.split(':', 1)[1].strip()
            return rating, comment

        overall_rating, overall_comment = extract_rating_and_comment(lines, "Overall")
        technical_rating, technical_comment = extract_rating_and_comment(lines, "Technical Skills")
        communication_rating, communication_comment = extract_rating_and_comment(lines, "Communication Skills")
        cultural_fit_rating, cultural_fit_comment = extract_rating_and_comment(lines, "Cultural Fit")

        return jsonify({
            'overall_rating': {
                'rating': overall_rating,
                'comment': overall_comment
            },
            'technical_skills': {
                'rating': technical_rating,
                'comment': technical_comment
            },
            'communication_skills': {
                'rating': communication_rating,
                'comment': communication_comment
            },
            'cultural_fit': {
                'rating': cultural_fit_rating,
                'comment': cultural_fit_comment
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)