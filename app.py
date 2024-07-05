from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import logging
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler

app = Flask(__name__, static_folder='static')

api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    app.logger.error('OPENAI_API_KEY environment variable not set')

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

client = OpenAI(api_key=api_key)

assistant = client.beta.assistants.create(
    instructions="You are a weather bot. Use the provided functions to answer questions.",
    model="gpt-4o",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_current_temperature",
                "description": "Get the current temperature for a specific location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g., San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["Celsius", "Fahrenheit"],
                            "description": "The temperature unit to use. Infer this from the user's location."
                        }
                    },
                    "required": ["location", "unit"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_rain_probability",
                "description": "Get the probability of rain for a specific location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g., San Francisco, CA"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
)

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
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
        )

        class EventHandler(AssistantEventHandler):
            def __init__(self):
                self.response_text = ""

            @override
            def on_event(self, event):
                app.logger.debug(f"Event received: {event.event}")
                if event.event == 'thread.run.requires_action':
                    run_id = event.data.id
                    app.logger.debug(f"Run ID: {run_id}")
                    self.handle_requires_action(event.data, run_id)

            def handle_requires_action(self, data, run_id):
                tool_outputs = []

                for tool in data.required_action.submit_tool_outputs.tool_calls:
                    app.logger.debug(f"Tool call received: {tool.function.name}")
                    if tool.function.name == "get_current_temperature":
                        tool_outputs.append({"tool_call_id": tool.id, "output": "57"})
                    elif tool.function.name == "get_rain_probability":
                        tool_outputs.append({"tool_call_id": tool.id, "output": "0.06"})

                self.submit_tool_outputs(tool_outputs, run_id)

            def submit_tool_outputs(self, tool_outputs, run_id):
                with client.beta.threads.runs.submit_tool_outputs_stream(
                        thread_id=thread.id,
                        run_id=run_id,
                        tool_outputs=tool_outputs,
                        event_handler=self,
                ) as stream:
                    for text in stream.text_deltas:
                        app.logger.debug(f"Text delta received: {text}")
                        self.response_text += text
                    return self.response_text

        event_handler = EventHandler()
        with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                event_handler=event_handler
        ) as stream:
            stream.until_done()

        response_text = event_handler.response_text
        app.logger.debug(f"Assistant response: {response_text}")

        return jsonify({'message': response_text})
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