from flask import Flask, request, render_template, jsonify
from openai import OpenAI
import logging

app = Flask(__name__)

client = OpenAI(api_key='sk-proj-h0c2oGEfefX10VuPKsxUT3BlbkFJCibBAMprWdCo2oGdk0FV')

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    app.logger.debug(f"User input: {user_input}")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
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
    app.run(debug=True)