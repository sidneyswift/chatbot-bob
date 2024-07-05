from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import logging

app = Flask(__name__, static_folder='static')

api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    app.logger.error('OPENAI_API_KEY environment variable not set')

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
        # Replace this with the correct OpenAI API call
        response = {
            "choices": [
                {"message": {"content": "You are a helpful assistant."}}
            ]
        }
        message = response['choices'][0]['message']['content'].strip()
        return jsonify({'message': message})
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

# Route for serving static files
@app.route('/static/<path:path>', methods=['GET'])
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)