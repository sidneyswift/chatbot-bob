from flask import Flask, request, render_template, jsonify
from openai import OpenAI
import logging
import os

app = Flask(__name__)

api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    app.logger.error('OPENAI_API_KEY environment variable not set')
client = OpenAI(api_key=api_key)

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET'])
def home():
    app.logger.debug('Home route accessed')
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    app.logger.debug(f"User input: {user_input}")
    if not user_input:
        app.logger.error('No message provided in request')
        return jsonify({'error': 'No message provided'}), 400
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        app.logger.debug(f"OpenAI response: {response}")
        message = response.choices[0].message.content.strip()
        return jsonify({'message': message})
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)